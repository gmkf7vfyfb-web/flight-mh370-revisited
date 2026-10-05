"""Compare finished runs on the quantities the paper actually quotes.

`report/convergence.py` is the pass/fail gate and reports the split-half overlap the runner
stored, which is one arbitrary partition — first half of the replicates against the second. The
project convention is to quote the **mean and range over every balanced partition**, because the
statistic is noisy in itself: at four replicates there are three distinct balanced partitions and
one ladder rung spanned 0.780-0.878 across them. This script computes all of them, and puts the
posterior summaries beside the convergence numbers so one table carries everything.

The floor is replicate-count dependent (`results/split-half-threshold.md`): 0.896 at four
replicates, 0.914 at six, 0.924 at eight. It is this project's own threshold, calibrated as the
5th percentile of a converged reference at matched replicate count. Davey et al. published no
quantitative convergence criterion at all, so there is no precedent to appeal to.

Usage:  python report/model_comparison.py runs/best-model runs/tempered-1839-1941 runs/davey2016
        python report/model_comparison.py --csv out/model-comparison.csv runs/*
"""

import argparse
import csv
import itertools
import json
from pathlib import Path

import numpy as np

# 5th percentile of a converged reference at matched replicate count.
SPLIT_HALF_FLOOR = {4: 0.896, 6: 0.914, 8: 0.924}

# The northern shoulder, the feature of Davey Fig. 10.3 no run of ours has reproduced.
SHOULDER_BAND = (-36.5, -34.5)


def overlap(p, q, step):
    """Integrated overlap of two densities on the shared grid, in [0, 1]."""
    return float(np.minimum(np.asarray(p), np.asarray(q)).sum() * step)


def balanced_partitions(n):
    """Every way of splitting n replicates into two equal halves, each counted once."""
    if n % 2:
        return []
    idx = range(n)
    seen = []
    for half in itertools.combinations(idx, n // 2):
        if 0 not in half:          # fix replicate 0 in the first half to avoid counting A|B twice
            continue
        seen.append((list(half), [i for i in idx if i not in half]))
    return seen


def split_half_all(densities, step):
    """Mean, min and max split-half overlap over every balanced partition."""
    parts = balanced_partitions(len(densities))
    if not parts:
        return None
    vals = []
    for a, b in parts:
        pa = np.mean([densities[i] for i in a], axis=0)
        pb = np.mean([densities[i] for i in b], axis=0)
        vals.append(overlap(pa, pb, step))
    return {"n_partitions": len(vals), "mean": float(np.mean(vals)),
            "min": float(np.min(vals)), "max": float(np.max(vals))}


def band_mass(density, grid, lo, hi, step):
    """Probability mass of a density between two latitudes.

    Trapezoid rule, to stay comparable with the shoulder figures already quoted in
    `results/shoulder-comparison.md`. The rectangle rule gives 0.2460 for Davey Fig. 10.3 against
    the 0.2406 recorded there, and a 2% difference in the reference would quietly shift every
    ratio computed against it.
    """
    sel = (grid >= lo) & (grid <= hi)
    return float(np.trapezoid(np.asarray(density)[sel], dx=step))


def interval(density, grid, step, frac):
    """Narrowest interval containing `frac` of the mass (highest-density interval)."""
    d = np.asarray(density, dtype=float)
    order = np.argsort(d)[::-1]
    csum = np.cumsum(d[order]) * step
    k = int(np.searchsorted(csum, frac)) + 1
    inside = np.sort(grid[order[:k]])
    return float(inside.min()), float(inside.max())


def report(run_dir: Path):
    summary = json.loads((run_dir / "summary.json").read_text())
    manifest = json.loads((run_dir / "run.json").read_text())
    grid = np.asarray(summary["grid"]["values"] if "values" in summary["grid"] else
                      np.arange(summary["grid"]["min"],
                                summary["grid"]["max"] + summary["grid"]["step"] / 2,
                                summary["grid"]["step"]), dtype=float)
    step = summary["grid"]["step"]

    out = []
    for block in summary["cases"]:
        densities = [np.asarray(r["density"], dtype=float) for r in block["replicates"]]
        pooled = np.asarray(block["density"], dtype=float) if "density" in block \
            else np.mean(densities, axis=0)
        medians = [r["stats"]["median"] for r in block["replicates"]]
        pairwise = [overlap(a, b, step) for i, a in enumerate(densities) for b in densities[i + 1:]]
        sh = split_half_all(densities, step)
        n = len(densities)
        floor = SPLIT_HALF_FLOOR.get(n)
        ref = summary.get("reference", {}).get("density")

        row = {
            "run": run_dir.name,
            "case": block["case"],
            "replicates": n,
            "particles_per_replicate": block["particles"],
            "runtime_h": round(manifest["runtime_s"] / 3600, 2),
            "log_evidence": block["log_evidence"],
            "split_half_mean": sh and round(sh["mean"], 4),
            "split_half_min": sh and round(sh["min"], 4),
            "split_half_max": sh and round(sh["max"], 4),
            "split_half_partitions": sh and sh["n_partitions"],
            "split_half_floor": floor,
            "converged": None if (sh is None or floor is None) else bool(sh["min"] >= floor),
            "replicate_pairwise_min": round(min(pairwise), 4) if pairwise else None,
            "replicate_pairwise_max": round(max(pairwise), 4) if pairwise else None,
            "replicate_median_span_deg": round(float(max(medians) - min(medians)), 4),
            "median_deg": round(block["stats"]["median"], 4),
            "mode_deg": round(block["stats"]["mode"], 4),
            "shoulder": round(band_mass(pooled, grid, *SHOULDER_BAND, step), 4),
            "reference_overlap": block.get("reference_overlap"),
            "reference_shoulder": round(band_mass(ref, grid, *SHOULDER_BAND, step), 4) if ref else None,
        }
        for frac in (0.50, 0.90, 0.99):
            lo, hi = interval(pooled, grid, step, frac)
            row[f"hdi{int(frac*100)}_lo"] = round(lo, 3)
            row[f"hdi{int(frac*100)}_hi"] = round(hi, 3)
        out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--csv", type=Path, help="also write the rows to this CSV")
    args = ap.parse_args()

    rows = []
    for r in args.runs:
        if not (r / "summary.json").is_file():
            print(f"{r}: no summary.json, skipped")
            continue
        rows += report(r)
    if not rows:
        raise SystemExit("no finished runs given")

    hdr = f"{'run':<26} {'reps':>4} {'split-half (mean, range)':>28} {'floor':>6} {'conv':>5} " \
          f"{'median':>8} {'span':>6} {'overlap':>8} {'shoulder':>9}"
    print(hdr)
    print("-" * len(hdr))
    for d in rows:
        sh = f"{d['split_half_mean']:.4f} [{d['split_half_min']:.4f}-{d['split_half_max']:.4f}]" \
            if d["split_half_mean"] is not None else "n/a"
        ov = f"{d['reference_overlap']:.4f}" if d["reference_overlap"] is not None else "n/a"
        print(f"{d['run']:<26} {d['replicates']:>4} {sh:>28} "
              f"{(d['split_half_floor'] or 0):>6.3f} {str(d['converged']):>5} "
              f"{d['median_deg']:>8.3f} {d['replicate_median_span_deg']:>6.3f} {ov:>8} "
              f"{d['shoulder']:>9.4f}")
    if rows[0]["reference_shoulder"] is not None:
        print(f"\nDavey Fig. 10.3 shoulder over {SHOULDER_BAND[0]} to {SHOULDER_BAND[1]} deg: "
              f"{rows[0]['reference_shoulder']:.4f}")

    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(args.csv)


if __name__ == "__main__":
    main()
