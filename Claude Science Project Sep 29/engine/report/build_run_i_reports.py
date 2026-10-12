"""Standard run reports for core run I (next-i-*), footnoted plain (ASD-STE100) and technical, with run D's same family as overlay.
Usage: python build_run_i_reports.py RUN_I_DIR OUT_DIR [stratum ...]"""
import json, os, subprocess, sys
from itertools import combinations
import numpy as np
ENG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I, OUT = sys.argv[1], sys.argv[2]; only = sys.argv[3:]
D = "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/386151e9-859f-412a-8d9d-b8da48899575/out/next-run-d"
FLOOR = {4: 0.896, 6: 0.914, 8: 0.924}
FAM = {  # stratum: (run I dir, label, run D baseline dir, plain early-flight text)
 "free": ("next-i-free", "free flight", "next-d-free",
          "In the early flight, the speed and the direction can change freely. The speed is Mach 0.45 to 0.87 until 18:40, then Mach 0.70 to 0.87, always between 210 and 330 knots indicated air speed."),
 "waypoints": ("next-i-waypoints", "waypoints", "next-d-routes",
          "In the early flight, the aircraft flies VAMPI and MEKAR, then a random route through 26 published waypoints of 2014. It can turn before a waypoint or fly over it, and it can leave a leg early. Speeds are as for free flight."),
 "descent-climb": ("next-i-descent-climb", "descent and climb", "next-d-descent-climb",
          "In the early flight, the aircraft can descend to between 2,000 and 10,000 ft and then climb again, before 18:18. Speeds are as for free flight."),
 "repro": ("next-i-repro-radar", "Davey dynamics", "next-d-repro-radar",
          "In the early flight, the aircraft moves as in the Davey model, with Mach 0.73 to 0.84 throughout."),
}
os.makedirs(OUT, exist_ok=True)
for s, (d, lab, base, early) in FAM.items():
    if only and s not in only: continue
    run = f"{I}/{d}"; j = json.load(open(f"{run}/run.json")); reps = j["replicates"]
    seeds = sorted({r["seed"] for r in reps}); n = len(seeds)
    sm = json.load(open(f"{run}/summary.json")); c = sm["cases"][0]; step = sm["grid"]["step"]
    dens = [np.array(r["density"]) for r in c["replicates"]]
    ovs = []
    for half in combinations(range(n), n // 2):
        if 0 not in half: continue
        other = [i for i in range(n) if i not in half]
        ovs.append(float(np.minimum(np.mean([dens[i] for i in half], 0), np.mean([dens[i] for i in other], 0)).sum() * step))
    sh, lo, hi = float(np.mean(ovs)), float(np.min(ovs)), float(np.max(ovs)); floor = FLOOR.get(n, 0.90)
    conv = (f"The estimate is converged (split-half {sh:.3f}, above the floor of {floor} for {n} runs)." if sh >= floor else
            f"The estimate is not converged (split-half {sh:.3f}, below the floor of {floor} for {n} runs).")
    what = f"Core run I, family '{lab}'. {early} After 18:40 the model is Davey's, with the fuel model, radar and one-engine flight."
    plain = (f"Plain: {what} {conv} The physics of the one-engine phase is provisional. The latitude at 00:19 uses both BTO values and no BFO.")
    stack = " + ".join(os.path.basename(x).replace(".toml", "") for x in j.get("config_paths", []))
    tech = (f"Technical: run {j['config'].get('name')}; stack: run D stack + speed rule (see the method page); binary {j.get('code_revision')}, x86_64-linux (deskstar); "
            f"seeds {seeds[0]}-{seeds[-1]} x {sum(reps[0]['particles_per_mode']):,} particles; ln Z {c['log_evidence']:.2f}; "
            f"split-half mean over {len(ovs)} balanced partitions {sh:.3f} (range {lo:.3f}-{hi:.3f}) against the {n}-replicate floor {floor}; "
            "00:19 treatment: core, Davey both-BTO no-BFO; one-engine dynamics s7 + s8 hold-then-taper (PROVISIONAL); overlay: the same family in run D (4 seeds; for waypoints, run D's 48 airway routes); report built 12 Oct 2026.")
    env = dict(os.environ, REPORT_FOOTNOTE=plain + "\n\n" + tech, REPORT_WHAT=what, OMP_NUM_THREADS="2",
               BASELINE_LABEL="Same family in run D", BASELINE_NAME="the same family in run D")
    cmd = ["python", "report/build_report.py", run, f"{OUT}/run-i-{s}-report.pdf", "--baseline", f"{D}/{base}"]
    r = subprocess.run(cmd, cwd=ENG, env=env, capture_output=True, text=True)
    print(s, r.returncode, f"split-half {sh:.4f} ({lo:.3f}-{hi:.3f})", (r.stderr.strip().splitlines() or [""])[-1][:300], flush=True)
