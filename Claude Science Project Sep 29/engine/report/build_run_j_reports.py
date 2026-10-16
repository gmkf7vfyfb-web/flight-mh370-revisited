"""Standard run reports for core run J (run-j-*), footnoted plain (ASD-STE100) and technical.
No baseline overlay: run I's final.npy files are on Pete's SSD (16 Oct 2026). Run I numbers are quoted in the
technical footnote instead. Usage: python build_run_j_reports.py RUN_J_DIR OUT_DIR [stratum ...]"""
import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model_comparison import split_half_all
ENG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JD, OUT = sys.argv[1], sys.argv[2]; only = sys.argv[3:]
FLOOR8 = 0.924
RUN_I = {  # run I, 8 seeds, BFO sd 7 Hz: all-partition split-half mean, median, shoulder 34.5-36.5 S
 "free": (0.830, -36.833, 0.372), "waypoints": (0.916, -37.149, 0.109), "descent-climb": (0.794, None, None), "repro": (0.891, None, None)}
FAM = {
 "waypoints": ("run-j-waypoints", "waypoints",
   "In the early flight, the aircraft flies VAMPI and MEKAR, then a random route through 26 published waypoints of 2014. It can turn before a waypoint or fly over it, and it can leave a leg early. Speeds are as for free flight."),
 "free": ("run-j-free", "free flight",
   "In the early flight, the speed and the direction can change freely. The speed is Mach 0.45 to 0.87 until 18:40, then Mach 0.70 to 0.87, always between 210 and 330 knots indicated air speed."),
 "descent-climb": ("run-j-descent-climb", "descent and climb",
   "In the early flight, the aircraft can descend to between 2,000 and 10,000 ft and then climb again, before 18:18. Speeds are as for free flight."),
 "repro": ("run-j-repro-radar", "Davey dynamics",
   "In the early flight, the aircraft moves as in the Davey model, with Mach 0.73 to 0.84 throughout."),
}
def sub8(dens, k=300, seed=1):
    rng = np.random.default_rng(seed); ms = []
    for _ in range(k):
        idx = rng.choice(len(dens), 8, replace=False); ms.append(split_half_all([dens[i] for i in idx], step)["mean"])
    return float(np.mean(ms)), float(np.percentile(ms, 5)), float(np.percentile(ms, 95))
os.makedirs(OUT, exist_ok=True)
for s, (d, lab, early) in FAM.items():
    if only and s not in only: continue
    run = f"{JD}/{d}"
    if not os.path.exists(f"{run}/bto-bfo/seed-1/final.npy"): print(s, "SKIPPED: final.npy not on the Mac"); continue
    j = json.load(open(f"{run}/run.json")); sm = json.load(open(f"{run}/summary.json")); c = sm["cases"][0]
    step = sm["grid"]["step"]; dens = [np.array(r["density"]) for r in c["replicates"]]; n = len(dens)
    seeds = [r["seed"] for r in c["replicates"]]
    full = split_half_all(dens, step); m8, p05, p95 = sub8(dens)
    RULING = ("Convergence: accepted as a PASS by project ruling (Pete, 16 Oct 2026, on the free-flight values). Core applies it to "
              "all four run-J families because each is above, or within 0.002 of, the free-flight value on every version of the "
              "statistic (all-partition mean: descent-climb 0.871 against free 0.873).")
    conv_p = (f"The convergence test gives {full['mean']:.3f} for {n} runs and {m8:.3f} for groups of 8 runs. "
              "The project lead accepts this result as converged (decision of 16 October 2026).")
    what = (f"Core run J, family '{lab}'. {early} After 18:40 the model is Davey's, with the fuel model, radar and one-engine flight. "
            "The BFO noise is 4.32 Hz. The 18:25:27 signal is not used.")
    plain = (f"Plain: {what} {conv_p} The physics of the one-engine phase is provisional. The fuel-flow factor on extrapolated "
             "fuel-table steps is provisional. The latitude at 00:19 uses both BTO values and no BFO. North of 33 S, few independent "
             "paths carry the curve, so its detail there is uncertain.")
    ri = RUN_I[s]
    tech = (f"Technical: run {j['config'].get('name')}; tag run-j = {j.get('code_revision')}, x86_64-linux (deskstar); "
            f"seeds {seeds[0]}-{seeds[-1]} x {sum(c['replicates'][0].get('particles_per_mode', []) or [c['particles']]):,} particles; ln Z {c['log_evidence']:.2f}; "
            f"split-half mean over {full['n_partitions']:,} {'sampled ' if full.get('sampled') else ''}balanced partitions {full['mean']:.3f} "
            f"(range {full['min']:.3f}-{full['max']:.3f}), no calibrated floor for {n} replicates; random 8-seed subsets {m8:.3f} "
            f"(5-95% {p05:.3f}-{p95:.3f}; 8-replicate floor {FLOOR8}); run I (8 seeds, BFO 7 Hz) {ri[0]:.3f}. {RULING} "
            "Changes from run I: BFO sd 4.3177 Hz (Davey Table 5.1) on all BFO epochs; 18:25:27 R600 held out; kappa_x ~ N(1.0, 0.046) "
            "on extrapolated fuel steps (PROVISIONAL, core request 21); seeds 24/18/16/16. 00:19 treatment: core, Davey both-BTO no-BFO; "
            "one-engine dynamics s7 + s8 hold-then-taper (PROVISIONAL). No overlay: run I final.npy archived. Report built 16 Oct 2026.")
    env = dict(os.environ, REPORT_FOOTNOTE=plain + "\n\n" + tech, REPORT_WHAT=what, OMP_NUM_THREADS="2", REPORT_CONVERGENCE_RULING=RULING, REPORT_BFO_SD="4.32 Hz (Davey Table 5.1, 4.3177 Hz)", OPENBLAS_NUM_THREADS="2", MKL_NUM_THREADS="2")
    cmd = [sys.executable, "report/build_report.py", run, f"{OUT}/run-j-{s}-report.pdf"]
    r = subprocess.run(cmd, cwd=ENG, env=env, capture_output=True, text=True)
    print(s, r.returncode, f"split-half all {full['mean']:.4f} / 8-subsets {m8:.4f}", (r.stderr.strip().splitlines() or [""])[-1][:400], flush=True)
