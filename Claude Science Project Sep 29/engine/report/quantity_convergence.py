#!/usr/bin/env python3
"""Per-quantity convergence: how far apart two halves of a run put each reported number.

A single split-half overlap gate answers one question for the whole posterior, and it answers it
badly in both directions. On this project's runs the pooled median moves 0.06 degrees while the
overlap statistic moves 0.031, so the gate is far too harsh on the median; and the shoulder mass
swings by a tenth of its own value between halves, so the same gate is too lenient on the
quantity the paper actually argues about.

This script replaces one verdict with one verdict per reported number. For every balanced
partition of the replicates into two halves, it pools each half, evaluates each quantity on both,
and reports the mean and worst absolute difference. A quantity whose halves agree to within the
precision the paper quotes it at is converged, whatever the overlap gate says about the run.

Two measures of mode-probability stability appear in this project and they do not agree, so both
are reported and the difference matters:

  * `mean half-difference` compares two POOLED halves. It is the measure tied to split-half
    overlap, because split-half pools halves too.
  * `min-max range` compares INDIVIDUAL replicates. It is the measure in
    results/tempering-is-not-the-fix.md.

Pooling averages out replicate noise, so the two can move in opposite directions between runs.
Quote the half-difference when arguing about convergence of a reported number, and the min-max
range when arguing about how much an individual replicate can wander.

Usage: python report/quantity_convergence.py <run-dir> [<run-dir> ...] [--csv <path>]
"""

import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np

SHOULDER_BAND = (-36.5, -34.5)
PEAK_BAND = (-38.5, -37.0)


def load(run: Path):
    s = json.loads((run / "summary.json").read_text())
    grid = s["grid"]
    lat = grid["min"] + np.arange(grid["points"]) * grid["step"]
    case = s["cases"][0]
    reps = [np.array(r["density"]) for r in case["replicates"]]
    mode_p = np.array([r["mode_probability"] for r in case["replicates"]])
    names = [m.get("mode") for m in case["modes"]]
    return lat, grid["step"], reps, mode_p, names, np.array(case["density"])


def median_of(lat, step, d):
    return float(np.interp(0.5, np.cumsum(d) * step, lat))


def band_of(lat, d, lo, hi):
    m = (lat >= lo) & (lat <= hi)
    return float(np.trapezoid(d[m], lat[m]))


def hdi_of(lat, step, d, frac):
    order = np.argsort(d)[::-1]
    k = int(np.searchsorted(np.cumsum(d[order]) * step, frac)) + 1
    sel = np.sort(lat[order[:k]])
    return float(sel[0]), float(sel[-1])


def quantities(lat, step):
    """Each reported number, as a function of a pooled density."""
    return {
        "median (deg)": lambda d: median_of(lat, step, d),
        "mode (deg)": lambda d: float(lat[int(np.argmax(d))]),
        "HDI50 north (deg)": lambda d: hdi_of(lat, step, d, 0.50)[1],
        "HDI50 south (deg)": lambda d: hdi_of(lat, step, d, 0.50)[0],
        "HDI90 north (deg)": lambda d: hdi_of(lat, step, d, 0.90)[1],
        "HDI90 south (deg)": lambda d: hdi_of(lat, step, d, 0.90)[0],
        "shoulder mass": lambda d: band_of(lat, d, *SHOULDER_BAND),
        "peak mass": lambda d: band_of(lat, d, *PEAK_BAND),
    }


def table(run: Path):
    lat, step, reps, mode_p, names, pooled = load(run)
    n = len(reps)
    if n < 4 or n % 2:
        raise SystemExit(f"{run}: need an even number of replicates, at least four; found {n}")
    # One representative per complementary pair: fix replicate 0 in the first half.
    parts = [h for h in combinations(range(n), n // 2) if 0 in h]
    rows = []
    for label, f in quantities(lat, step).items():
        diffs = []
        for h in parts:
            a = np.mean([reps[i] for i in h], axis=0)
            b = np.mean([reps[i] for i in range(n) if i not in h], axis=0)
            diffs.append(abs(f(a) - f(b)))
        diffs = np.array(diffs)
        value = f(pooled)
        rows.append({
            "run": run.name, "quantity": label, "pooled": value,
            "mean_half_diff": diffs.mean(), "max_half_diff": diffs.max(),
            "mean_half_diff_pct": abs(diffs.mean() / value) * 100 if value else float("nan"),
            "replicate_min_max_pct": float("nan"),
        })
    for i, name in enumerate(names):
        diffs = []
        for h in parts:
            a = mode_p[list(h), i].mean()
            b = mode_p[[j for j in range(n) if j not in h], i].mean()
            diffs.append(abs(a - b))
        diffs = np.array(diffs)
        value = mode_p[:, i].mean()
        rows.append({
            "run": run.name, "quantity": f"P({name})", "pooled": value,
            "mean_half_diff": diffs.mean(), "max_half_diff": diffs.max(),
            "mean_half_diff_pct": diffs.mean() / value * 100,
            "replicate_min_max_pct": (mode_p[:, i].max() - mode_p[:, i].min()) / value * 100,
        })
    return rows, len(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--csv", type=Path)
    args = ap.parse_args()

    all_rows = []
    for run in args.runs:
        rows, n_parts = table(run)
        all_rows += rows
        print(f"\n{run.name}  ({n_parts} balanced partitions)")
        print(f"{'quantity':24s} {'pooled':>10s} {'mean |A-B|':>11s} {'worst':>9s} {'mean %':>8s} {'rep range %':>12s}")
        for r in rows:
            rng = "" if np.isnan(r["replicate_min_max_pct"]) else f"{r['replicate_min_max_pct']:11.1f}%"
            print(f"{r['quantity']:24s} {r['pooled']:10.4f} {r['mean_half_diff']:11.4f} "
                  f"{r['max_half_diff']:9.4f} {r['mean_half_diff_pct']:7.1f}% {rng:>12s}")

    if args.csv:
        import csv
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(all_rows[0]))
            w.writeheader()
            w.writerows(all_rows)
        print(f"\n{args.csv}")


if __name__ == "__main__":
    main()
