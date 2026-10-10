#!/usr/bin/env python3
"""Architecture stand-in (10 Oct 2026): run searched areas' UNCHANGED field_coverage_check.py on settling's own core-set
wreckage samples on core (b) (tag `nrb`, settling hypothesis/settling 5b595bf, results/settling-core-set-next-run-b/).

    cd engine && python ../results/searched-areas-next-run-b-rho-eq11-2-coverage-standin/standin_field_coverage_b.py \
        <settling field dir> <out dir>

INPUT ADAPTATION ONLY. The module's script reads <dir>/{A}_impacts.f64, {A}_elements.f64 and {A}_draws.npz (rows_0, draws_0)
and requires that the element file holds exactly the outcomes listed in rows_0/draws_0. Settling's `nrb` layout holds Held
Out in set A and four options in set B, with per-option `fixed_j` / `reweighted_j` masks selecting each mixture's
equally-weighted outcomes. For every (option, mixture) this wrapper therefore writes, in a temporary directory:
  A_impacts.f64   copy of settling's nrb{A|B}_impacts.f64 (unchanged)
  A_draws.npz     rows_0 / draws_0 = rows_j[mask] / draws_j[mask]
  A_elements.f64  settling's element rows whose (row, draw) is in that selection, in settling's order
and runs the module's script on it. Nothing in the coverage arithmetic is touched; the script's own assertion against the
module's no_find_probability column still runs. Temporary element files are deleted after each run.
"""
import json, shutil, subprocess, sys
from pathlib import Path
import numpy as np

ENGINE = Path.cwd()
SCRIPT = ENGINE / "hypotheses" / "seabed-search" / "field_coverage_check.py"
SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
TAG = "nrb"
info = json.loads((SRC / f"{TAG}_info.json").read_text())
z = np.load(SRC / f"{TAG}_draws.npz")
names = list(info["options"])
EL = {s: np.memmap(SRC / f"{TAG}{s}_elements.f64", dtype="<f8", mode="r").reshape(-1, 8) for s in "AB"}
KEY = {s: EL[s][:, 0].astype(np.int64) * 1000 + EL[s][:, 1].astype(np.int64) for s in "AB"}
# consistency: every listed outcome of a set has elements, and every element belongs to a listed outcome
for s, js in (("A", [0]), ("B", [1, 2, 3, 4])):
    listed = np.unique(np.concatenate([z[f"rows_{j}"].astype(np.int64) * 1000 + z[f"draws_{j}"].astype(np.int64) for j in js]))
    have = np.unique(KEY[s])
    assert np.array_equal(listed, have), f"set {s}: draws file and element file disagree ({len(listed)} vs {len(have)})"
results = {"source": str(SRC), "tag": TAG, "constraint": info["constraint"], "runs": {}}
tmp = OUT / "tmp"
for j, name in enumerate(names):
    s = "A" if j == 0 else "B"
    step = 5 if j == 0 else 1   # module's step 5 on Held Out (200,000 outcomes); step 1 on the 40,000-outcome options
    for mix in ("reweighted", "fixed"):
        m = z[f"{mix}_{j}"].astype(bool)
        rows, draws = z[f"rows_{j}"][m].astype(np.int64), z[f"draws_{j}"][m].astype(np.int64)
        sel = rows * 1000 + draws
        if draws.max() >= 1000:
            # the module's script keys outcomes as row * 1000 + draw; an impact drawn >= 1000 times breaks that key
            results["runs"][f"{name} | {mix}"] = {"option": name, "mixture": mix, "not_run": True,
                "reason": "module key row*1000+draw overflows", "max_draws_per_impact": int(draws.max()) + 1,
                "distinct_impacts": int(len(np.unique(rows))), "outcomes_in_mixture": int(m.sum()),
                "ess_mixture_kish": info["options"][name][mix]["ess_mixture_kish"]}
            print(f"{name:28s} {mix:10s} NOT RUN: {int(draws.max()) + 1} draws of one impact, {len(np.unique(rows))} distinct impacts", flush=True)
            continue
        assert len(np.unique(sel)) == len(sel)
        keep = np.isin(KEY[s], sel)
        if tmp.exists():
            shutil.rmtree(tmp)
        tmp.mkdir()
        shutil.copyfile(SRC / f"{TAG}{s}_impacts.f64", tmp / "A_impacts.f64")  # copy: the sandbox refuses a cross-workspace symlink
        np.savez(tmp / "A_draws.npz", rows_0=rows, draws_0=draws)
        np.asarray(EL[s][keep]).astype("<f8").tofile(tmp / "A_elements.f64")
        r = subprocess.run([sys.executable, str(SCRIPT), "--dir", str(tmp), "--set", "A", "--step", str(step)],
                           cwd=ENGINE, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f"{name} {mix}: {r.stderr[-2000:]}")
        rep = json.loads((ENGINE / "runs" / "seabed-search-analysis" / "field-coverage-check.json").read_text())
        rep.update({"option": name, "mixture": mix, "outcomes_in_mixture": int(m.sum()),
                    "p_family": info["options"][name][mix]["p_family"],
                    "ess_mixture_kish": info["options"][name][mix]["ess_mixture_kish"]})
        results["runs"][f"{name} | {mix}"] = rep
        print(f"{name:28s} {mix:10s} outcomes {rep['outcomes']:6d} elements {rep['settled_elements']:9,d} "
              f"Z point {rep['point']['Z']:.4f} mean {rep['mean']['Z']:.4f} any {rep['any']['Z']:.4f}", flush=True)
        shutil.rmtree(tmp)
(OUT / "field-coverage-b.json").write_text(json.dumps(results, indent=1) + "\n")
print("wrote", OUT / "field-coverage-b.json")
