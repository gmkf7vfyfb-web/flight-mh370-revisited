"""Standard run report for the run-J northern supplement seeds (1001-1016), footnoted plain (ASD-STE100) and technical.
Usage: python build_supplement_report.py MERGED_RUN_DIR OUT_PDF"""
import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_comparison import split_half_all
ENG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
run, out = sys.argv[1], sys.argv[2]
FLOOR8 = 0.924
j = json.load(open(f"{run}/run.json")); sm = json.load(open(f"{run}/summary.json")); c = sm["cases"][0]
step = sm["grid"]["step"]; dens = [np.array(r["density"]) for r in c["replicates"]]; n = len(dens); seeds = [r["seed"] for r in c["replicates"]]
full = split_half_all(dens, step)
rng = np.random.default_rng(1); ms = [split_half_all([dens[i] for i in rng.choice(n, 8, replace=False)], step)["mean"] for _ in range(300)]
m8, p05, p95 = float(np.mean(ms)), float(np.percentile(ms, 5)), float(np.percentile(ms, 95))
ppm = j["config"]["particles_per_mode"]
what = ("Northern supplement to core run J, family 'waypoints'. In the early flight, the aircraft flies VAMPI and MEKAR, then a "
        "random route through 26 published waypoints of 2014. After 18:40 the model is Davey's, with the fuel model, radar and "
        "one-engine flight. The BFO noise is 4.32 Hz. The 18:25:27 signal is not used. These 16 runs put more particles in the "
        "magnetic autopilot modes than run J does. This changes the random error only, not the result.")
plain = (f"Plain: {what} The convergence test gives {full['mean']:.3f} for {n} runs and {m8:.3f} for groups of 8 runs. "
         "The physics of the one-engine phase is provisional. The fuel-flow factor on extrapolated fuel-table steps is provisional. "
         "The latitude at 00:19 uses both BTO values and no BFO. No search areas, drift or end-of-flight data are applied. "
         "The other three early-flight families are not in these runs.")
tech = (f"Technical: run {j['config'].get('name')}; revision {j.get('code_revision')} (run J stack, tag run-j chain + "
        "output.handoff_supplement), x86_64-linux (deskstar), job b6389957; "
        f"seeds {seeds[0]}-{seeds[-1]} x {sum(ppm):,} particles, per mode [TH, MH, TT, MT, LN] = {[f'{p/1e6:.1f}M' for p in ppm]} "
        "(run J [1.0, 0.5, 2.5, 0.5, 2.5]M; mixture weighted by mode evidence, so the target is unchanged); "
        f"ln Z {c['log_evidence']:.2f} (pooled); split-half mean over {full['n_partitions']:,} {'sampled ' if full.get('sampled') else ''}"
        f"balanced partitions {full['mean']:.3f} (range {full['min']:.3f}-{full['max']:.3f}), no calibrated floor for {n} replicates; "
        f"random 8-seed subsets {m8:.3f} (5-95% {p05:.3f}-{p95:.3f}; 8-replicate floor {FLOOR8}). Prior: 18:01 radar prior, route "
        "sampler over 2014 waypoints. 00:19: both BTO, no BFO (Davey treatment). kappa_x ~ N(1.0, 0.046) on extrapolated fuel steps "
        "and one-engine dynamics s7 + s8 hold-then-taper are PROVISIONAL. 18:25:27 R600 held out. Search case: none; ocean models: "
        "none. Reference: Davey et al. (2016), Fig. 10.3, vector-recovered curve (5315fde). Seeds merged from 16 single-seed runs "
        "(report/merge_seed_runs.py); summary.json rebuilt by mh370 summarise. No convergence ruling covers these 16 runs (no calibrated floor for 16); "
        "the run J ruling (PASS, Pete 16 Oct 2026) is not affected. Report built 19 Oct 2026.")
env = dict(os.environ, REPORT_FOOTNOTE=plain + "\n\n" + tech, REPORT_WHAT=what, OMP_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2",
           MKL_NUM_THREADS="2", REPORT_BFO_SD="4.32 Hz (Davey Table 5.1, 4.3177 Hz)",
           REPORT_RUN_LABEL="Northern supplement, 16 runs, early-flight family 'waypoints'",
           REPORT_REPRODUCE="engine/scripts/job-run-j-supplement.sh (runs, deskstar), then engine/scripts/job-supplement-report.sh (this report)")
r = subprocess.run([sys.executable, "report/build_report.py", run, out], cwd=ENG, env=env, capture_output=True, text=True)
print("report", r.returncode, f"split-half all {full['mean']:.4f} ({full['n_partitions']} partitions) / 8-subsets {m8:.4f}")
print(r.stdout[-2000:], r.stderr[-3000:])
json.dump({"split_half_all": full, "subsets8": [m8, p05, p95], "seeds": seeds, "log_evidence": c["log_evidence"]},
          open(os.path.splitext(out)[0] + "-convergence.json", "w"), indent=1)
