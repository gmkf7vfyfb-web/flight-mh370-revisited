"""Block 11 driver: 4 single-threaded worker subprocesses (one per run J seed + the supplement), staging dir, finaliser.
Finaliser checks every seed (rows equal impacts32's, NaN only where inputs are non-finite, finite share, quantiles), then
renames <out>.staging -> <out>, writes README.txt and, last, READY. Usage: python driver.py [n_proc]
"""
from __future__ import annotations
import json, os, pathlib, subprocess, sys, time
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import prereg as R

NPROC = int(sys.argv[1]) if len(sys.argv) > 1 else R.N_PROC
STATS_ONLY = os.environ.get("B11_STATS_ONLY") == "1"      # amendment A4: statistics-only re-run into stats-ramgrid/, no columns, no finaliser
out = R.STATS_DIR_RAMGRID if STATS_ONLY else pathlib.Path(os.environ.get("B11_OUT", str(R.EXCHANGE_OUT)))   # B11_OUT: product folder (A4 rewrite -> run-j-gated-v2)
stg = out if STATS_ONLY else pathlib.Path(str(out) + ".staging"); stg.mkdir(parents=True, exist_ok=True)
RAMGRID = os.environ.get("B11_IMOS_RAMGRID") == "1"
log = open(stg / "driver.log", "a")
def say(m): log.write(time.strftime("%Y-%m-%dT%H:%M:%SZ ", time.gmtime()) + m + "\n"); log.flush()
tasks = []
def seed_dirs(s):
    return sorted([p for p in (R.RUN_J / s).glob("seed-*") if p.is_dir() and (p / "impacts32.npy").exists()], key=lambda p: int(p.name.split("-")[1]))
for s in R.STRATA:
    for sd in seed_dirs(s):
        if True:
            k = int(sd.name.split("-")[1])
            if not (stg / "_parts" / f"{s}_{k}.json").exists(): tasks.append((s, str(k)))
if not (stg / "_parts" / "supplement.json").exists(): tasks.append(("supplement", "0"))
env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1")
say(f"start tasks={len(tasks)} nproc={NPROC}"); running = {}; failed = []; t0 = time.time()
while tasks or running:
    for key, (p, ts) in list(running.items()):
        if p.poll() is not None:
            del running[key]
            if p.returncode != 0: failed.append(key); say(f"FAILED {key} rc={p.returncode}")
            else: say(f"done {key} {time.time() - ts:.0f}s")
    while tasks and len(running) < NPROC:
        s, k = tasks.pop(0)
        p = subprocess.Popen([sys.executable, str(HERE / "worker.py"), s, k, str(stg)], env=env, cwd=HERE,
                             stdout=open(stg / f"_w_{s}_{k}.log", "w"), stderr=subprocess.STDOUT)
        running[(s, k)] = (p, time.time()); say(f"launch {s}/{k} running={len(running)}"); time.sleep(1)
    time.sleep(5)
say(f"all tasks ended in {time.time() - t0:.0f}s failed={failed}")
if failed: sys.exit(1)
if STATS_ONLY:
    (stg / "DONE").write_text(f"statistics-only re-run (amendment A4, RAM-grid IMOS TL) finished {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"); say("DONE (stats only)"); sys.exit(0)
# ---------------------------------------------------------------- finaliser
summ = {}; bad = []; rows = 0; nc = 0; short = []
for pj in sorted((stg / "_parts").glob("*.json")):
    if pj.stem == "supplement": continue
    d = json.loads(pj.read_text()); summ[f"{d['stratum']}/seed-{d['seed']}"] = d
for s in R.STRATA:
    for sd in seed_dirs(s):
        n = np.load(sd / "impacts32.npy", mmap_mode="r").shape[0]; od = stg / s / sd.name
        cols = (od / "COLUMNS.txt").read_text().split()
        if cols != R.COLUMNS: short.append(f"{s}/{sd.name}: {cols}")
        ref = None
        for c in cols:
            a = np.load(od / f"{c}.npy", mmap_mode="r")
            if len(a) != n or a.dtype != np.float32: bad.append(f"{s}/{sd.name}/{c}: len/dtype"); continue
            nan = np.isnan(a)
            if ref is None: ref = nan
            elif not np.array_equal(ref, nan): bad.append(f"{s}/{sd.name}/{c}: NaN pattern differs")
            if not np.all(np.isfinite(a[~nan])): bad.append(f"{s}/{sd.name}/{c}: non-finite")
        d = summ[f"{s}/{sd.name}"]; rows += n; nc += d["not_computed"]
        if int(ref.sum()) != d["not_computed"]: bad.append(f"{s}/{sd.name}: not_computed mismatch")
say(f"checks: {len(bad)} failing {bad[:5]}; short-written seeds {len(short)}")
if bad: sys.exit(2)
hdr = f"""Hydroacoustics block 11 (composition) on end of flight run J, all four strata (74 seeds). Written {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}.
{'PRODUCT v2 (amendment A4, prereg e13a32e): IMOS TL from the RAM-along-grid drop-in imos_tl_ram_arc.csv (G-TL1 closed on the offset-0 line); supersedes run-j-gated (old IMOS table).' if RAMGRID else 'IMOS TL: imos_tl_ramcorr_arc.csv (constant rule-2 correction, gap G-TL1).'}
Pre-registration prepare/composition_run_j/prereg.py (module branch, commit 90d7181{' + A4 e13a32e' if RAMGRID else ''}); worker.py / driver.py; {NPROC} single-thread workers.
Rows {rows:,}; not_computed (NaN) {nc}; the marginalised IMOS column (proposed default) is present for every seed; per-seed checks (rows equal end of flight's, float32, NaN only where inputs non-finite and identical
across columns, finite elsewhere, quantiles in _parts/*.json): all pass. Seeds with fewer than five columns (another process held the disk below the 20 GiB floor during the run; the marginalised IMOS
column was written, the other four were not): {len(short)} {short}
TOP-UP RECIPE (when >= 22 GiB free): B11_TOPUP=1 python worker.py <stratum> <seed> <this dir>  then  python driver.py  (finaliser only).

COLUMNS (float32, row i = row i of end-of-flight/run-j/<stratum>/seed-N/impacts32.npy):
  hydro-lnL-imos-eta1e-3.npy      ln L of the IMOS-gated term at coupling efficiency eta = 1e-3
  hydro-lnL-imos-eta2.1e-4.npy    ... at eta = 2.1e-4 (F-35A upper anchor, Brown et al. 2026)
  hydro-lnL-imos-eta1e-4.npy      ... at eta = 1e-4
  hydro-lnL-imos-margeta.npy      ... marginalised over a log-uniform prior on eta in [1e-6, 1e-2] (41 points, equal weights)  <- PROPOSED DEFAULT
  hydro-lnL-ims-proxy-margeta.npy SENSITIVITY: IMOS-gated term x H01W/H08S PROXY-background terms, eta marginalised. PREDICTIVE for IMS.
NaN = not computed (impact time, position, energy or tau not finite); never a default. 0.0 = computed, no information (no scored window at
any receiver). Rows south of 41 S carry TL clamped at the table edge (labelled; < 0.2 % of mass).

LABELS: GATE PASSED AT IMOS ONLY (3376, 3315, 3274, 3275: own real backgrounds, block 7). IMS PROXY = SENSITIVITY (H01W/H08S backgrounds
are IMOS 3376 shaped to Blackman 2003 medians, digitised; single hydrophone + 4.8 dB triad gain label). PREDICTIVE, NOT CALIBRATED.
Caveats C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not calibrated; eta over
four decades, F-35A upper anchor). Both Kadri times carried: text time 00:52:03, caption time 00:54:30. Detector M1b, false-alarm
level alpha = 0.05 per 55 s window (report level), beta = alpha / 55 s; matched candidates from the block 5 pre-registered tables
(IMOS M1b p <= 0.05: 3275 01:20:35 and 01:07:47, both louder than any impact could be at Portland, eta_needed 30 / 19 -- matching is
amplitude-blind, gap G11-1; H01W M1b p <= 0.05: 00:52:04 text time; H08S residual: none). TL = block 2 arc grid (41-20 S, offset 0,
10 m source; IMOS {'RAM along the grid, imos_tl_ram_arc.csv' if RAMGRID else 'RAM-corrected, G-TL1'}; IMS raw KRAKEN minus imp500 RAM delta). tau = end of flight tau90 (method 1). E = contact
kinetic energy (sidecar energy_transferred_j, an upper anchor). Calibration error N(0, 10 dB) per row shared by receivers.

RULING REQUEST (architecture, composer, Pete): may hydro-lnL-imos-margeta enter the composer as the module's likelihood (default), with
hydro-lnL-ims-proxy-margeta as the labelled sensitivity? Until ruled, the composer default remains lnL_gated = 0.0 in
mh370-exchange/hydroacoustics/run-j/primary-tau-eof (unchanged by this block).

Per-seed summary (rows, not_computed, columns written, free GiB at write, quantiles 0.1/1/50/99/99.9 %, share non-zero, scored share, seconds):
"""
(stg / "README.txt").write_text(hdr + json.dumps(summ, indent=1) + "\n")
if out.exists(): out.rename(str(out) + f".old-{int(time.time())}")
stg.rename(out)
(out / "READY").write_text(f"hydroacoustics block 11 gated columns written {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}; proposed default hydro-lnL-imos-margeta (ruling pending); see README.txt\n")
say("READY")
