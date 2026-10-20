"""Compare the 23:15 + 00:11 log-evidence increment from the 22:41 hand-off: core filter (difference of the m0011 and m2241 hand-off
[stop] log_evidence, both mode-mixed) against the terminal stage (terminal.json 'm0011' column of runs/CHK-V1b-s<k>, arm V1b, every
child cruising on the core dynamics). Also splits the stage figure into m2315-bfo and the remainder. SMOKE SCALE.
Usage: python check_0011_increment.py OUT_JSON"""
import gzip, json, re, sys, pathlib
CORE = pathlib.Path("/Users/pete/Downloads/mh370-exchange/core/run-i/next-i-waypoints/bto-bfo")
RUNS = pathlib.Path(__file__).resolve().parents[3] / "runs"
def stop_lnz(p):
    with gzip.open(p, "rt") as f:
        for line in f:
            m = re.match(r"log_evidence = (\S+)", line)
            if m: return float(m.group(1))
rows = []
for k in range(1, 9):
    tj = RUNS / f"CHK-V1b-s{k}" / "bto-bfo" / f"seed-{k}" / "terminal.json"
    if not tj.exists(): continue
    c = {x["column"]: x for x in json.load(open(tj))["columns"]}
    f = stop_lnz(CORE / f"seed-{k}" / "handoff-m0011" / "handoff.toml.gz") - stop_lnz(CORE / f"seed-{k}" / "handoff-m2241" / "handoff.toml.gz")
    rows.append(dict(seed=k, filter=f, stage=c["m0011"]["log_evidence_increment"], stage_m2315=c["m2315-bfo"]["log_evidence_increment"],
                     stage_ess_rows=c["m0011"]["ess_rows"], stage_ess_parents=c["m0011"]["ess_parents"]))
for r in rows: r["stage_minus_filter"] = r["stage"] - r["filter"]
json.dump(rows, open(sys.argv[1], "w"), indent=1)
for r in rows: print(f"seed {r['seed']}: filter {r['filter']:.3f}  stage {r['stage']:.3f}  diff {r['stage_minus_filter']:+.3f}  (stage m2315 {r['stage_m2315']:.3f}; ESS rows {r['stage_ess_rows']:.0f}, parents {r['stage_ess_parents']:.0f})")
import statistics as s
d = [r["stage_minus_filter"] for r in rows]
if len(d) > 1: print(f"mean diff {s.mean(d):+.3f}  sd {s.stdev(d):.3f}  n {len(d)}")
