#!/usr/bin/env python3
"""Manoeuvres of the paths that end north of the main peak, as PNG images.

Usage: northern_paths.py RUN_DIR [BASE_RUN_DIR]

RUN_DIR and BASE_RUN_DIR must be runs made with output.history_after_epoch (history.npy),
e.g. runs/complex-manoeuvres and runs/complexity (the base model). Writes into RUN_DIR:
  turns-by-band.png   posterior distribution of turns and degrees turned after 18:40, by
                      final-latitude band (north of 34.5 S, shoulder 34.5-36.5 S, south)
  northern-paths.png  sampled posterior routes ending north of 34.5 S, with the points where
                      the track changes by more than 15 deg between 10-min route snapshots
Replicates are pooled with equal weight (each normalised to 1).
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

BANDS = [("north of 34.5°S", -34.5, 90.0, "#d6452a"), ("shoulder 34.5–36.5°S", -36.5, -34.5, "#e8a33d"),
         ("south of 36.5°S", -90.0, -36.5, "#2a78d6")]


def load(run):
    lat, w, hist, routes = [], [], [], []
    for d in sorted((Path(run) / "bto-bfo").glob("seed-*")):
        f = np.load(d / "final.npy", mmap_mode="r")
        ww = np.asarray(f[:, 0], float)
        w.append(ww / ww.sum())
        lat.append(np.asarray(f[:, 1]))
        hist.append(np.load(d / "history.npy"))
        routes.append(np.load(d / "routes.npy"))
    n = len(w)
    return np.concatenate(lat), np.concatenate(w) / n, np.concatenate(hist), np.concatenate(routes)


def band_stats(lat, w, hist, label):
    out = []
    for name, lo, hi, _ in BANDS:
        m = (lat > lo) & (lat <= hi)
        p = w[m].sum()
        turns = hist[m, 0]
        deg = hist[m, 3]
        ww = w[m] / p
        mean_turns = float((turns * ww).sum())
        p0 = float(ww[turns == 0].sum())
        p3 = float(ww[turns >= 3].sum())
        mean_deg = float((deg * ww).sum())
        out.append((name, p, mean_turns, p0, p3, mean_deg))
        print(f"{label:20s} {name:22s} P={p:.3f}  mean turns {mean_turns:.2f}  P(0 turns) {p0:.2f}  "
              f"P(>=3) {p3:.2f}  mean deg turned {mean_deg:.0f}")
    return out


def turns_png(runs, out):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for k, (label, (lat, w, hist, _)) in enumerate(runs):
        for b, (name, lo, hi, colour) in enumerate(BANDS):
            m = (lat > lo) & (lat <= hi)
            if w[m].sum() == 0:
                continue
            ww = w[m] / w[m].sum()
            x = np.arange(0, 11)
            h = np.array([ww[np.minimum(hist[m, 0], 10) == i].sum() for i in x])
            axes[0].plot(x + (b - 1) * 0.12, h, "o-" if k == 0 else "s--", color=colour, ms=3, lw=1,
                         label=f"{label}: {name}")
            edges = np.arange(0, 721, 30)
            hd, _ = np.histogram(np.minimum(hist[m, 3], 719), edges, weights=ww)
            axes[1].step(edges[:-1], hd, where="post", color=colour, ls="-" if k == 0 else "--", lw=1.2)
    axes[0].set_xlabel("turns after 18:40 (10 = 10 or more)")
    axes[0].set_ylabel("probability within band")
    axes[0].legend(fontsize=7)
    axes[1].set_xlabel("total degrees turned after 18:40 (30° bins)")
    axes[1].set_ylabel("probability within band")
    fig.suptitle("Manoeuvres after 18:40 by where the path ends (solid: first run, dashed: second)", fontsize=10)
    fig.tight_layout()
    fig.savefig(out, dpi=110)


def turn_points(route, min_deg=15.0):
    """Indices where the track changes by more than min_deg between successive 10-min legs."""
    lat, lon = np.radians(route[:, 0]), np.radians(route[:, 1])
    dlon = np.diff(lon)
    brg = np.degrees(np.arctan2(np.sin(dlon) * np.cos(lat[1:]),
                                np.cos(lat[:-1]) * np.sin(lat[1:]) - np.sin(lat[:-1]) * np.cos(lat[1:]) * np.cos(dlon)))
    change = (np.diff(brg) + 180) % 360 - 180
    return np.nonzero(np.abs(change) > min_deg)[0] + 1


def paths_png(routes, out, label, n_show=12, first_after=None):
    end = routes[:, -1, 0]
    north = routes[end > -34.5]
    south = routes[end <= -36.5]
    rng = np.random.default_rng(0)
    fig, axes = plt.subplots(1, 2, figsize=(12, 7))
    ax = axes[0]
    for r in south[rng.choice(len(south), min(150, len(south)), replace=False)]:
        ax.plot(r[:, 1], r[:, 0], color="#2a78d6", lw=0.4, alpha=0.25)
    for r in north:
        ax.plot(r[:, 1], r[:, 0], color="#d6452a", lw=0.5, alpha=0.5)
    ax.set_title(f"{label}: all {len(north)} of {len(routes)} sampled routes ending north of 34.5°S (red)\n"
                 "with 150 ending south of 36.5°S (blue)", fontsize=9)
    ax = axes[1]
    pick = north[rng.choice(len(north), min(n_show, len(north)), replace=False)]
    cmap = plt.cm.tab20.colors
    for i, r in enumerate(pick):
        ax.plot(r[:, 1], r[:, 0], color=cmap[i % 20], lw=1.1)
        tp = turn_points(r)
        tp = tp[tp >= (first_after or 0)]
        ax.plot(r[tp, 1], r[tp, 0], "o", color=cmap[i % 20], ms=4, mec="k", mew=0.4)
    ax.set_title(f"{len(pick)} of them; dots: track change > 15° between 10-min points after 18:40", fontsize=9)
    for a in axes:
        a.set_xlabel("longitude (°E)")
        a.set_ylabel("latitude (°)")
        a.grid(lw=0.3, alpha=0.5)
    axes[0].set_aspect(1 / np.cos(np.radians(20)))
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    counts = [len(turn_points(r)[turn_points(r) >= (first_after or 0)]) for r in north]
    # When the visible turns happen: route index i is 18:01:49 + 10 i min.
    times = np.concatenate([turn_points(r)[turn_points(r) >= (first_after or 0)] for r in north]) * 600 + 18 * 3600 + 109
    edges = [18.68, 19.68, 20.68, 21.68, 22.68, 23.25, 24.18, 24.4]
    names = ["18:41-19:41", "19:41-20:41", "20:41-21:41", "21:41-22:41", "22:41-23:15", "23:15-00:11", "00:11-00:19"]
    h, _ = np.histogram(times / 3600, edges)
    print("  when their visible turns happen: " + ", ".join(f"{n} {c / h.sum():.0%}" for n, c in zip(names, h)))
    print(f"{label}: routes ending north of 34.5S have {np.mean(counts):.1f} visible turns (>15 deg per 10 min) on average; "
          f"{np.mean(np.array(counts) == 0):.0%} none, {np.mean(np.array(counts) <= 2):.0%} two or fewer")


def main():
    run = Path(sys.argv[1])
    runs = [(run.name, load(run))]
    if len(sys.argv) > 2:
        runs.append((Path(sys.argv[2]).name, load(sys.argv[2])))
    for label, (lat, w, hist, _) in runs:
        band_stats(lat, w, hist, label)
    turns_png(runs, run / "turns-by-band.png")
    # Route snapshots start at the 18:01:49 prior, every 600 s: index 4 is 18:41:49.
    paths_png(runs[0][1][3], run / "northern-paths.png", run.name, first_after=4)
    print(f"wrote {run / 'turns-by-band.png'} and {run / 'northern-paths.png'}")


if __name__ == "__main__":
    main()
