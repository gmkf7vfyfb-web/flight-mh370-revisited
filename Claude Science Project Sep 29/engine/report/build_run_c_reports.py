"""Standard run reports for run C (next-c-*), footnoted plain (ASD-STE100) and technical, with run (a) as overlay.
Usage: python build_run_c.py RUN_C_DIR [stratum ...]"""
import json, os, subprocess, sys
import numpy as np
W = "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/386151e9-859f-412a-8d9d-b8da48899575"
ENG = f"{W}/repo/Claude Science Project Sep 29/engine"
OUT = f"{W}/out/reports"
A = f"{W}/out/next-run-a"
FLOOR = {4: 0.896, 6: 0.914, 8: 0.924}   # report/model_comparison.py SPLIT_HALF_FLOOR
C = sys.argv[1]
only = sys.argv[2:]
NAMES = {"repro-radar": "Davey dynamics", "free": "free speed and turn", "routes": "airway routes", "descent-climb": "descent and climb"}
EARLY = {
    "repro-radar": "In the early flight (after 18:01), the aircraft moves as in the Davey model.",
    "free": "In the early flight, the speed can change (Mach 0.45 to 0.87 until 18:40) and the aircraft can turn once at 18:22.",
    "routes": "In the early flight, the aircraft flies along one of 48 published airway routes through the waypoints.",
    "descent-climb": "In the early flight, the aircraft can descend to between 2,000 and 10,000 ft and then climb again, before 18:18.",
}
STACK = ("Stack: davey2016-inmarsat + no-exhaustion-prior + fuel fixes s1-s6 (internal-v1 with temperature term, kappa N(1.0004, 0.0196), "
         "43,800 - kappa x 7,228 kg, weight-dependent ceiling, hard reject, two tanks) + reference-snapshots + radar-full + family overlay "
         "+ s7 one-engine dynamics + s8 hold-then-taper + inop-flow-fix (grid_inop x 0.5)")
for s, lab in NAMES.items():
    name = f"next-run-c-{s}"
    if only and s not in only:
        continue
    run = f"{C}/next-c-{s}"
    if not os.path.exists(f"{run}/run.json"):
        print(name, "missing"); continue
    j = json.load(open(f"{run}/run.json"))
    reps = j["replicates"]; seeds = j["config"].get("seeds", sorted({r["seed"] for r in reps}))
    p = j["config"].get("prior", {})
    case = [c for c in json.load(open(f"{run}/summary.json"))["cases"] if c["case"] == "bto-bfo"][0]
    # Split-half over EVERY balanced partition (mh370-run-reporting trap 1): summary.json's
    # split_half_overlap is a single first-half/second-half partition and must not be quoted.
    from itertools import combinations
    dens = [np.asarray(r["density"], float) for r in case["replicates"]]; n = len(dens); step = 0.05
    grid = json.load(open(f"{run}/summary.json")).get("grid") or {}
    step = float(grid.get("step", step)) if isinstance(grid, dict) else step
    ovs = []
    for half in combinations(range(n), n // 2):
        if 0 not in half: continue
        other = [i for i in range(n) if i not in half]
        ovs.append(float(np.minimum(np.mean([dens[i] for i in half], 0), np.mean([dens[i] for i in other], 0)).sum() * step))
    sh, sh_lo, sh_hi = float(np.mean(ovs)), float(np.min(ovs)), float(np.max(ovs))
    floor = FLOOR.get(n, 0.90)
    converged = sh >= floor
    what = (f"Davey plus fuel model, radar and one-engine flight: {lab}. {EARLY[s]} When the first tank is empty, the aircraft "
            "flies on one engine. It keeps its height while its speed decreases. Then it descends more and more slowly and stops "
            "about 1,000 ft above the one-engine ceiling.")
    first = what.split(". ")[0] + "."
    conv = (f"This stratum is converged (split-half {sh:.3f}, above the {n}-replicate floor of {floor})." if converged else
            f"The estimate is not converged (split-half {sh:.3f}, below the {n}-replicate floor of {floor}).")
    plain = (f"Plain: {first} The one-engine fuel flow is correct in this run. {conv} "
             "The physics of the one-engine phase is provisional.")
    stack = " + ".join(os.path.basename(x).replace(".toml", "") for x in j.get("config_paths", []))
    tech = (f"Technical: run {j['config'].get('name')}; stack {stack}; binary {j.get('code_revision')}, {j.get('platform') or 'x86_64-linux (deskstar)'}; "
            f"seeds {seeds[0]}-{seeds[-1]} x {sum(reps[0]['particles_per_mode']):,} particles; prior 18:01:49 "
            f"{p.get('latitude_deg', 0):.4f}N {p.get('longitude_deg', 0):.4f}E, track {p.get('track_deg')} +/- {p.get('track_sd_deg')} deg; "
            "one-engine dynamics s7 + s8 hold-then-taper (PROVISIONAL); live-engine flow internal-v1 grid_inop x inop_flow_scale 0.5 (= source tables); "
            f"split-half mean over {len(ovs)} balanced partitions {sh:.3f} (range {sh_lo:.3f}-{sh_hi:.3f}) against the {n}-replicate floor {floor}; outputs compacted (tanks32, gzipped hand-offs; final.npy unchanged); "
            "baseline overlay: same stratum in run (a); report built 10-11 Oct 2026.")
    env = dict(os.environ, REPORT_FOOTNOTE=plain + "\n\n" + tech, REPORT_WHAT=what, OMP_NUM_THREADS="2",
               BASELINE_LABEL="Same stratum in run (a)", BASELINE_NAME="the same stratum in run (a)")
    base = f"{A}/next-a-{s}"
    cmd = ["python", "report/build_report.py", run, f"{OUT}/{name}-report.pdf", "--baseline", base]
    r = subprocess.run(cmd, cwd=ENG, env=env, capture_output=True, text=True)
    print(name, r.returncode, f"split-half {sh:.4f} ({sh_lo:.3f}-{sh_hi:.3f}) floor {floor}", (r.stderr.strip().splitlines() or [""])[-1][:200])
