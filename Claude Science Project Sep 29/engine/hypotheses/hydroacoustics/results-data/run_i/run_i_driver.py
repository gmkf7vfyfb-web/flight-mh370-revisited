import os, subprocess, time, json, pathlib, shutil, numpy as np, sys
PREP = r"""/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d74bf70e-a424-46a9-8149-902d027e782a/hydro-wt/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"""; EOFR = "/Users/pete/Downloads/mh370-exchange/hydroacoustics/session-staging-2026-10-12/eof-ri"; X = pathlib.Path("/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i")
OUT = pathlib.Path("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-i"); OUT.mkdir(parents=True, exist_ok=True)
LOG = open(OUT / "driver.log", "a")
def log(*a): print(time.strftime("%H:%M:%SZ", time.gmtime()), *a, file=LOG, flush=True)
env = dict(os.environ, OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2", MKL_NUM_THREADS="2", PYTHONPATH=".:exploratory/pleiades_test:" + EOFR)
strata = ["next-i-waypoints", "next-i-free", "next-i-descent-climb", "next-i-repro-radar"]; done = []
sys.path.insert(0, EOFR); import compact_impacts as C
while len(done) < len(strata):
    for s in strata:
        if s in done or not (X / s / "READY").exists() or (OUT / s / "READY").exists():
            if (OUT / s / "READY").exists() and s not in done: done.append(s)
            continue
        work = OUT / f".work-{s}"; shutil.rmtree(work, ignore_errors=True); t0 = time.time(); log("start", s)
        r = subprocess.run([sys.executable, "per_impact_lnl.py", "..", str(X), str(work), "../results-data/kadri2a/kadri_table1_geometry.csv",
                            "--compact-reader", EOFR + "/compact_impacts.py", "--strata", s], cwd=PREP, env=env, capture_output=True, text=True)
        (OUT / f"{s}.log").write_text(r.stdout + r.stderr)
        if r.returncode != 0: log("FAILED", s, r.returncode); done.append(s); continue
        if (OUT / s).exists(): shutil.rmtree(OUT / s)
        shutil.move(str(work / s), str(OUT / s)); shutil.move(str(work / "README.txt"), str(OUT / s / "README_module.txt")); shutil.rmtree(work, ignore_errors=True)
        cov = {}; rows = 0; nc = 0; bad = 0
        for sd in sorted((OUT / s).glob("seed-*")):
            a = np.load(sd / "hydro-lnL.npy", mmap_mode="r"); meta, g = C.load(X / s / sd.name); n = len(np.asarray(g("unix_s")))
            ok = (len(a) == n) and np.all(a["row"] == np.arange(n)) and float(np.abs(a["lnL_gated"]).max()) == 0.0
            rows += len(a); nc += int(a["not_computed"].sum()); bad += (not ok)
            cov[sd.name] = dict(rows=int(len(a)), not_computed=int(a["not_computed"].sum()), aligned_and_gated_zero=bool(ok))
        txt = f"""Hydroacoustics on end of flight run I, stratum {s} (written {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}).
Writer: prepare/per_impact_lnl.py (hypothesis/hydroacoustics, amendments 1-7), 2 threads outside the lock, {time.time()-t0:.0f} s.
Per seed: seed-k/hydro-lnL.npy, row-aligned with end-of-flight/run-i/{s}/seed-k (row, parent).
COMPOSER USE: lnL_gated = 0.0 in every row IS the module likelihood (predictive mode; the P_D gate is not passed).
lnL_soft / lnL_soft_imos / lnL_soft_h01w are labelled SENSITIVITIES only ("hydroacoustics low-power, NOT CALIBRATED;
calibration-error model; borrowed IMS P_D").
Labels: TL not calibrated (audit C6); IMS P_D borrowed (IMOS 3274 + 4.8 dB); H08S periodic impulses on 8 Mar 2014;
H08N blocked for MH370 impacts (K4); ridge paths cutting the sound-channel axis are a reach gap (G-N2); in-flight breakup
rows carry the intact impact point (end of flight G-bf): levels are an intact-impact upper bound; tau from the scenario
prior (run I carries no tau90 sidecar used here); survival factor and 00:19 weighting are applied by the composer, not here.

COVERAGE
(a) Feasible set: every impact end of flight writes for this stratum (all families, 00:19 options and D x C cells; its
    own COVERAGE section declares its gaps, e.g. A1 under D3/D5 x C1 below the 1,000 gate, C2-silent cells below the gate).
(b) Model reach: SOFAR branch, intact single impact, near-surface source 2/10/30 m, KRAKEN TL tables (stage B), 5-40 Hz;
    fragmentation, AGW below about 0.25 Hz and 3-D diffraction are not reachable (declared gaps G-H1, G-bf, G-N1, G-N2).
(c) Proposal coverage: every row is scored; not_computed rows {nc} of {rows} ({100*nc/max(rows,1):.4f} %); seeds failing
    the alignment / lnL_gated = 0 check: {bad}. ESS per option and family is end of flight's (this module adds no weights).
Per seed: {json.dumps(cov)}
"""
        (OUT / s / "README.txt").write_text(txt)
        if bad == 0: (OUT / s / "READY").write_text("ok\n")
        log("done", s, rows, nc, bad); done.append(s)
    time.sleep(60)
top = [f"{s}: {'READY' if (OUT/s/'READY').exists() else 'NOT READY'}" for s in strata]
(OUT / "README.txt").write_text("Hydroacoustics on end of flight run I (module likelihood lnL_gated = 0.0; see per-stratum README.txt incl. COVERAGE).\n" + "\n".join(top) + "\n")
if all((OUT/s/"READY").exists() for s in strata): (OUT / "READY").write_text("ok\n")
log("all done", top)
