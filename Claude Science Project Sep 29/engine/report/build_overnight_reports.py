"""Build the standard run report (report/build_report.py) for the overnight runs, each page footnoted."""
import json, os, subprocess, sys
W = "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/386151e9-859f-412a-8d9d-b8da48899575"
ENG = f"{W}/repo/Claude Science Project Sep 29/engine"
OUT = f"{W}/out/reports"
BASE = f"{W}/hpc/d74e5b9d-3c00-4cf6-95e7-e4de43b50b12/baseline/davey-inmarsat-baseline"
B, A = f"{W}/out/next-run-b", f"{W}/out/next-run-a"
INOP = ("One-engine live-engine flow from internal-v1 grid_inop AS DELIVERED, 2x its source tables (core finding 10 Oct): "
        "one-engine phases are about half their true length.")
STACK = ("Stack: davey2016-inmarsat + no-exhaustion-prior + fuel fixes s1-s6 (internal-v1 with temperature term, kappa N(1.0004, 0.0196), "
         "43,800 - kappa x 7,228 kg, weight-dependent ceiling, hard reject, two tanks) + reference-snapshots + radar-full + family overlay")
strata = [("repro-radar", "Davey dynamics + radar"), ("free", "free"), ("routes", "routes"), ("descent-climb", "descent-climb")]
jobs = [(BASE, None, "davey-only-baseline",
         "Run davey-inmarsat-baseline (full-scale Davey-only baseline): Davey et al. (2016) model with Inmarsat satellite states; no fuel, radar "
         "or extensions. The paper's without-fuel comparison. PROVISIONAL-OVERNIGHT.")]
for s, lab in strata:
    jobs.append((f"{B}/next-{s}", BASE, f"next-run-b-{s}",
                 f"Run next-run (b), stratum {lab}. {STACK}; two tanks as bookkeeping only (no one-engine dynamics). {INOP} "
                 "Baseline overlay: Davey-only baseline. Split-half not converged. PROVISIONAL-OVERNIGHT."))
for s, lab in strata:
    seed4 = " Seed 4 re-run after a full-disk failure (same binary and configs)." if s in ("repro-radar", "descent-climb") else ""
    jobs.append((f"{A}/next-a-{s}", f"{B}/next-{s}", f"next-run-a-{s}",
                 f"Run next-run (a), stratum {lab}. {STACK} + C-7(a) one-engine dynamics (s7: constant drift-down U(300, 1000) ft/min to the "
                 f"one-engine ceiling at LRC INOP Mach; PROVISIONAL).{seed4} {INOP} Baseline overlay: the same stratum in (b). "
                 + ("Split-half converged (0.946). " if s == "routes" else "Split-half not converged. ") + "PROVISIONAL-OVERNIGHT."))
only = sys.argv[1:]
for run, base, name, label in jobs:
    if only and name not in only:
        continue
    j = json.load(open(f"{run}/run.json"))
    p = j["config"].get("prior", {})
    reps = j["replicates"]
    plat = j.get("platform", "?")
    prior = p if isinstance(p, dict) else {}
    pr = ", ".join(f"{k} {prior[k]}" for k in ("latitude_deg", "longitude_deg", "track_deg", "track_sd_deg") if k in prior)
    foot = (f"{name}: {label} Binary {j.get('code_revision')}, {plat}, seeds {', '.join(str(x) for x in j['config'].get('seeds', sorted({r['seed'] for r in reps})))}, "
            f"{sum(reps[0]['particles_per_mode']):,} particles per seed. Prior 18:01:49 ({pr}). Report built 10 Oct 2026.")
    env = dict(os.environ, REPORT_FOOTNOTE=foot, OMP_NUM_THREADS="2")
    if base == BASE:
        env.update(BASELINE_LABEL="Davey-only baseline (full scale)", BASELINE_NAME="the Davey-only baseline")
    elif base:
        env.update(BASELINE_LABEL="Same stratum in run (b)", BASELINE_NAME="the same stratum in run (b)")
    cmd = ["python", "report/build_report.py", run, f"{OUT}/{name}-report.pdf"] + (["--baseline", base] if base else [])
    r = subprocess.run(cmd, cwd=ENG, env=env, capture_output=True, text=True)
    print(name, r.returncode, (r.stderr.strip().splitlines() or [""])[-1][:200])
