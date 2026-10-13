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
# Plain-language (ASD-STE100) statement of each run, printed under the subheading and as the plain footnote.
EARLY = {
    "repro-radar": "In the early flight (after 18:01), the aircraft moves as in the Davey model.",
    "free": "In the early flight, the speed can change (Mach 0.45 to 0.87 until 18:40) and the aircraft can turn once at 18:22.",
    "routes": "In the early flight, the aircraft flies along one of 48 published airway routes through the waypoints.",
    "descent-climb": "In the early flight, the aircraft can descend to between 2,000 and 10,000 ft and then climb again, before 18:18.",
}
WHAT_BASE = ("Davey replica. This is the Davey et al. (2016) model with the Inmarsat satellite positions. "
             "It has no fuel model and no radar data after 18:01.")
def what_b(s):
    return ("Davey plus fuel model and radar: " + {"repro-radar": "Davey dynamics", "free": "free speed and turn",
            "routes": "airway routes", "descent-climb": "descent and climb"}[s] + ". " + EARLY[s] +
            " The aircraft must have fuel until 00:11. Two fuel tanks are recorded, but the aircraft always flies on two engines.")
def what_a(s):
    return ("Davey plus fuel model, radar and one-engine flight: " + {"repro-radar": "Davey dynamics", "free": "free speed and turn",
            "routes": "airway routes", "descent-climb": "descent and climb"}[s] + ". " + EARLY[s] +
            " When the first tank is empty, the aircraft flies on one engine and descends to the one-engine ceiling.")
PLAIN_TAIL = ("The one-engine fuel flow in this run is two times too high, so the one-engine time is too short. "
              "The result is provisional and is not converged.")
WHAT = {"davey-only-baseline": WHAT_BASE}
for s, _ in strata:
    WHAT[f"next-run-b-{s}"] = what_b(s); WHAT[f"next-run-a-{s}"] = what_a(s)
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
def seed4_rerun(name):
    return name in ('next-run-a-repro-radar', 'next-run-a-descent-climb')
only = sys.argv[1:]
for run, base, name, label in jobs:
    if only and name not in only:
        continue
    j = json.load(open(f"{run}/run.json"))
    p = j["config"].get("prior", {})
    reps = j["replicates"]
    seeds = j["config"].get("seeds", sorted({r["seed"] for r in reps}))
    stack = " + ".join(os.path.basename(x).replace(".toml", "") for x in j.get("config_paths", []))
    sh = json.load(open(f"{run}/summary.json"))["cases"]
    shc = [c for c in sh if c["case"] == "bto-bfo"][0].get("split_half_overlap")
    tech = (f"Technical: run {j['config'].get('name')}; stack {stack}; binary {j.get('code_revision')}, {j.get('platform') or 'x86_64-linux (deskstar)'}; "
            f"seeds {seeds[0]}-{seeds[-1]} x {sum(reps[0]['particles_per_mode']):,} particles; prior 18:01:49 "
            f"{p.get('latitude_deg', 0):.4f}N {p.get('longitude_deg', 0):.4f}E, track {p.get('track_deg')} +/- {p.get('track_sd_deg')} deg"
            + ("" if name == "davey-only-baseline" else
               "; one-engine dynamics s7 with live-engine flow from internal-v1 grid_inop as delivered (2x its tables)" if "next-run-a" in name else
               "; no one-engine dynamics (two tanks as bookkeeping); after the first tank is empty the other tank drains at internal-v1 grid_inop as delivered (2x its tables)")
            + ("; seed 4 re-run after a full-disk failure (same binary and configs)" if seed4_rerun(name) else "")
            + (f"; baseline overlay: {'Davey-only baseline' if base == BASE else 'same stratum in run (b)'}" if base else "")
            + "; PROVISIONAL-OVERNIGHT; report built 10 Oct 2026.")
    what = WHAT[name]
    first = what.split(". ")[0] + "."
    if name == "davey-only-baseline":
        plain = f"Plain: {first} The estimate is converged (split-half above the 0.896 floor). The result is provisional."
    else:
        conv = "This stratum is converged." if name == "next-run-a-routes" else "The estimate is not converged (split-half below the 0.896 floor)."
        if "next-run-a" in name:
            flow = "The one-engine fuel flow in this run is two times too high, so the one-engine time is too short."
        else:
            flow = ("The aircraft does not fly on one engine in this run. But after the first tank is empty, the fuel use from the "
                    "other tank is two times too high, so the last engine stops too early.")
        plain = f"Plain: {first} {flow} {conv} The result is provisional."
    foot = plain + "\n\n" + tech
    env = dict(os.environ, REPORT_FOOTNOTE=foot, REPORT_WHAT=what, OMP_NUM_THREADS="2")
    if base == BASE:
        env.update(BASELINE_LABEL="Davey-only baseline (full scale)", BASELINE_NAME="the Davey-only baseline")
    elif base:
        env.update(BASELINE_LABEL="Same stratum in run (b)", BASELINE_NAME="the same stratum in run (b)")
    cmd = ["python", "report/build_report.py", run, f"{OUT}/{name}-report.pdf"] + (["--baseline", base] if base else [])
    r = subprocess.run(cmd, cwd=ENG, env=env, capture_output=True, text=True)
    print(name, r.returncode, (r.stderr.strip().splitlines() or [""])[-1][:200])
