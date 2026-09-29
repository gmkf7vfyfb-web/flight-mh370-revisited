"""Convergence gate for a finished run: one machine-readable verdict per measurement case.

The runner already records everything needed (`crates/mh370/src/summary.rs` and each replicate's
`diagnostics.json`); this reads those and states, in one place, whether the run may be quoted.

Two checks decide the verdict, and both have a criterion stated elsewhere in the project rather
than chosen here:

`pooling_closure`
    The weights that pool replicates must form a probability distribution: for every stratum, the
    per-replicate pool factors must sum to one. The defect this catches is the one recorded in
    `status.md` under "Known defect", where rows were pooled by a particle's current autopilot
    mode instead of the mode run it belonged to and replicate weights summed to 0.92-0.96.

`split_half_overlap`
    Pooling half the replicates against the other half must overlap by at least 0.90, the
    threshold `report/build_report.py` uses to say that the pooled curve does not depend
    materially on the random seed.

Everything else is reported without a pass or fail, because this project has no published
threshold for it: pairwise replicate overlap, the spread of replicate medians, effective sample
size by epoch, and the number of distinct prior draws surviving in each mode filter (the static-
parameter collapse Davey et al. warn about in sec. 10.4).

Usage:  python report/convergence.py runs/<name> [--split-half-floor 0.90]
Writes `convergence.json` and `convergence.csv` into the run directory. Exits non-zero if a gate
fails, so it can stand in front of anything that quotes the run.
"""

import argparse
import json
import csv
from pathlib import Path

import numpy as np

CLOSURE_TOLERANCE = 1e-9
DEFAULT_SPLIT_HALF_FLOOR = 0.90


def overlap(p, q, step):
    """Integrated overlap of two densities on the shared latitude grid, in [0, 1]."""
    return float(np.minimum(np.asarray(p), np.asarray(q)).sum() * step)


def case_report(run_dir: Path, block: dict, step: float, split_half_floor: float) -> dict:
    """Gate results and diagnostics for one measurement case."""
    seeds = block["seeds"]
    factors = np.asarray(block["pool_factors"], dtype=float)  # [replicate][stratum]

    # Gate 1: the pooling weights of every stratum must sum to one across replicates.
    stratum_sums = factors.sum(axis=0)
    closure_error = float(np.abs(stratum_sums - 1.0).max())
    closure_ok = closure_error <= CLOSURE_TOLERANCE

    # Gate 2: split-half overlap, as computed by the runner.
    split_half = block.get("split_half_overlap")
    split_ok = split_half is not None and split_half >= split_half_floor

    # Reported only: replicate agreement.
    densities = [r["density"] for r in block["replicates"]]
    pairwise = [overlap(a, b, step) for i, a in enumerate(densities) for b in densities[i + 1:]]
    medians = [r["stats"]["median"] for r in block["replicates"]]

    # Reported only: effective sample size by epoch, and surviving prior draws by mode.
    ess = {}
    origins = {}
    for seed in seeds:
        diag = json.loads((run_dir / block["case"] / f"seed-{seed}" / "diagnostics.json").read_text())
        for mode, n in zip(diag["modes"], diag["particles_per_mode"]):
            origins.setdefault(mode["mode"], []).append(mode["distinct_origins"])
            for epoch in mode["epochs"]:
                ess.setdefault(epoch["epoch"], []).append(epoch["ess_after_update"] / n)
    ess_fraction = {e: float(np.mean(v)) for e, v in ess.items()}
    worst = sorted(ess_fraction.items(), key=lambda kv: kv[1])[:3]

    return {
        "case": block["case"],
        "seeds": seeds,
        "particles_per_replicate": block["particles"],
        "pooled_by": block["pooled_by"],
        "converged": bool(closure_ok and split_ok),
        "gates": {
            "pooling_closure": {"passed": bool(closure_ok), "max_abs_error": closure_error,
                                "tolerance": CLOSURE_TOLERANCE,
                                "stratum_sums": [float(s) for s in stratum_sums]},
            "split_half_overlap": {"passed": bool(split_ok), "value": split_half,
                                   "floor": split_half_floor},
        },
        "reported": {
            "replicate_pairwise_overlap": {"min": min(pairwise), "max": max(pairwise)} if pairwise else None,
            "replicate_median_span_deg": float(max(medians) - min(medians)),
            "reference_overlap": block.get("reference_overlap"),
            "log_evidence": block["log_evidence"],
            "ess_fraction_by_epoch": ess_fraction,
            "tightest_epochs": [{"epoch": e, "ess_fraction": v} for e, v in worst],
            "distinct_origins_by_mode": {m: {"min": int(min(v)), "max": int(max(v))} for m, v in origins.items()},
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("run", type=Path, help="run directory, e.g. runs/davey2016")
    parser.add_argument("--split-half-floor", type=float, default=DEFAULT_SPLIT_HALF_FLOOR,
                        help=f"minimum split-half overlap to call a case converged (default {DEFAULT_SPLIT_HALF_FLOOR})")
    args = parser.parse_args()

    summary_path = args.run / "summary.json"
    if not summary_path.is_file():
        raise SystemExit(f"{summary_path} is missing; rebuild it with: mh370 summarise {args.run}")
    summary = json.loads(summary_path.read_text())
    manifest = json.loads((args.run / "run.json").read_text())
    step = summary["grid"]["step"]

    cases = [case_report(args.run, block, step, args.split_half_floor) for block in summary["cases"]]
    verdict = {
        "run": str(args.run),
        "code_revision": manifest["code_revision"],
        "config_paths": manifest["config_paths"],
        "runtime_s": manifest["runtime_s"],
        "peak_memory_mib": manifest["peak_memory_mib"],
        "threads": manifest["threads"],
        "split_half_floor": args.split_half_floor,
        "converged": all(c["converged"] for c in cases),
        "cases": cases,
    }
    (args.run / "convergence.json").write_text(json.dumps(verdict, indent=1) + "\n")

    rows = [{"case": c["case"], "particles_per_replicate": c["particles_per_replicate"],
             "replicates": len(c["seeds"]),
             "pooling_closure_error": c["gates"]["pooling_closure"]["max_abs_error"],
             "split_half_overlap": c["gates"]["split_half_overlap"]["value"],
             "replicate_overlap_min": (c["reported"]["replicate_pairwise_overlap"] or {}).get("min"),
             "replicate_median_span_deg": c["reported"]["replicate_median_span_deg"],
             "reference_overlap": c["reported"]["reference_overlap"],
             "tightest_epoch": c["reported"]["tightest_epochs"][0]["epoch"],
             "tightest_ess_fraction": c["reported"]["tightest_epochs"][0]["ess_fraction"],
             "converged": c["converged"]} for c in cases]
    with (args.run / "convergence.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    for c in cases:
        g = c["gates"]
        print(f"{c['case']}: {'converged' if c['converged'] else 'NOT CONVERGED'}; "
              f"closure error {g['pooling_closure']['max_abs_error']:.2e}; "
              f"split-half {g['split_half_overlap']['value']:.3f} (floor {args.split_half_floor:.2f}); "
              f"tightest {c['reported']['tightest_epochs'][0]['epoch']} "
              f"ESS {c['reported']['tightest_epochs'][0]['ess_fraction']:.3%}")
    print(args.run / "convergence.json")
    raise SystemExit(0 if verdict["converged"] else 1)


if __name__ == "__main__":
    main()
