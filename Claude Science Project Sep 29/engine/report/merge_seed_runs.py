"""Merge single-seed run directories (one engine process per seed, same configuration) into one run directory the report
tools read: run.json with every replicate and seed, and bto-bfo/seed-<s> symlinks to the original seed folders (nothing in
them is changed or moved). Then `mh370 summarise <out> --root <engine>` writes the pooled summary.json.
Standard library only (deskstar). Usage: python3 merge_seed_runs.py OUT_DIR RUN_DIR [RUN_DIR ...]"""
import json, os, sys
out, runs = sys.argv[1], sys.argv[2:]
os.makedirs(os.path.join(out, "bto-bfo"), exist_ok=True)
base = None; reps = []; seeds = []
for r in runs:
    m = json.load(open(os.path.join(r, "run.json")))
    if base is None: base = m
    cfg = dict(m["config"]); cfg.pop("seeds", None); b = dict(base["config"]); b.pop("seeds", None)
    assert cfg == b, f"{r}: configuration differs from {runs[0]} (other than seeds)"
    assert m["code_revision"] == base["code_revision"], r
    for rep in m["replicates"]:
        s = rep["seed"]; reps.append(rep); seeds.append(s)
        link = os.path.join(out, "bto-bfo", f"seed-{s}")
        if not os.path.lexists(link): os.symlink(os.path.abspath(os.path.join(r, "bto-bfo", f"seed-{s}")), link)
merged = dict(base); merged["config"] = dict(base["config"]); merged["config"]["seeds"] = seeds; merged["replicates"] = reps
merged["runtime_s"] = sum(json.load(open(os.path.join(r, "run.json")))["runtime_s"] for r in runs)
merged["merged_from"] = [os.path.abspath(r) for r in runs]
json.dump(merged, open(os.path.join(out, "run.json"), "w"), indent=1)
print(f"merged {len(runs)} runs, seeds {seeds[0]}..{seeds[-1]} ({len(seeds)})")
