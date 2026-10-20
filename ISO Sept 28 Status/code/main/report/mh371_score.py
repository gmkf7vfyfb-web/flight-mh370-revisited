#!/usr/bin/env python3
"""Score the MH371 known-flight control against the ACARS truth. The only code that reads the truth.

Usage: mh371_score.py summarise RUN_DIR SEED   (after each replicate; truth-free)
       mh371_score.py score RUN_DIR ACARS_XLSX

Replicates run one at a time (`make control`): each is reduced to arc-summary.npz, the
posterior along the final BTO arc as a histogram of azimuth about the sub-satellite point
(2e-4 rad bins, about 1 km), and its particle arrays are then deleted. Scoring reads only
those summaries and the sampled routes.

Fixed before the first run (committed with config/control/mh371.toml):
- Truth: the ACARS position at the final epoch, linear in time between the bracketing 5-min
  reports, and its reported altitude.
- Along-arc coordinate: the azimuth of a position seen from the sub-satellite point at the
  final epoch (the BTO arc is a circle about it), in km along the arc at the truth's range.
- Posterior: each replicate's weighted particles (the runner's weights, mode probabilities
  included), normalised to 1, replicates pooled with equal weight.
- Metrics: the truth's quantile in the posterior along-arc distribution (PIT), the distance
  from the posterior median, the 50 % and 95 % central intervals and their widths, the
  truth's BTO residual at the final epoch (checks the calibration and the ephemeris), and the
  split-half overlap of the along-arc density on 5 km bins (seeds 1-2 against 3-4).
- PASS: the truth lies inside the pooled 95 % interval and the split-half overlap is at
  least 0.8; otherwise FAIL. With BTO only the posterior is wide, so the interval width and
  median offset are reported beside the verdict: this tests calibration and convergence,
  not precision.
Writes RUN_DIR/score.json and RUN_DIR/score.png.
"""

import csv
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

R_EARTH = 6371.0
C_KM_S = 299792.458
A, F = 6378.137, 1 / 298.257223563
E2 = F * (2 - F)
GES = np.array([-2368.8, 4881.1, -3342.0])
OFFSET = 499962.0 - 4283.0
EDGES = np.linspace(-math.pi, math.pi, 31417)  # 2e-4 rad bins
BIN_KM = 5.0
ROOT = Path(__file__).resolve().parents[1]  # input paths in run.json are relative to the repository


def ecef(lat, lon, h_km):
    la, lo = math.radians(lat), math.radians(lon)
    n = A / math.sqrt(1 - E2 * math.sin(la) ** 2)
    return np.array([(n + h_km) * math.cos(la) * math.cos(lo), (n + h_km) * math.cos(la) * math.sin(lo),
                     (n * (1 - E2) + h_km) * math.sin(la)])


def azimuth(lat0, lon0, lat, lon):
    la0, lo0, la, lo = map(np.radians, (lat0, lon0, lat, lon))
    return np.arctan2(np.sin(lo - lo0) * np.cos(la), np.cos(la0) * np.sin(la) - np.sin(la0) * np.cos(la) * np.cos(lo - lo0))


def final_satellite(run):
    final = run["epochs"][-1]
    eph = next(r for r in csv.DictReader(open(ROOT / run["config"]["inputs"]["ephemeris"])) if r["epoch_id"] == final["id"])
    sat = np.array([float(eph[k]) for k in ("x_km", "y_km", "z_km")])
    sub = (math.degrees(math.atan2(sat[2], math.hypot(sat[0], sat[1]))), math.degrees(math.atan2(sat[1], sat[0])))
    return final, sat, sub


def summarise(run_dir, seed):
    run = json.loads((run_dir / "run.json").read_text())
    _, _, sub = final_satellite(run)
    d = run_dir / "bto-only" / f"seed-{seed}"
    f = np.load(d / "final.npy", mmap_mode="r")
    w = np.asarray(f[:, 0], float)
    hist, _ = np.histogram(azimuth(sub[0], sub[1], np.asarray(f[:, 1]), np.asarray(f[:, 2])), EDGES, weights=w / w.sum())
    np.savez(d / "arc-summary.npz", hist=hist, edges=EDGES, sub=np.array(sub))
    print(f"seed {seed}: arc summary written ({f.shape[0]} particles)")


def truth_at(path, unix_s):
    import openpyxl

    day = 1394150400.0  # 2014-03-07T00:00:00Z
    rows = openpyxl.load_workbook(path, read_only=True, data_only=True)["ACARS"].iter_rows(values_only=True)
    reports = sorted((r[11] + day, r[17], r[18], r[12]) for r in rows
                     if len(r) > 18 and all(isinstance(r[k], (int, float)) for k in (11, 12, 17, 18)))
    for (t0, la0, lo0, h0), (t1, la1, lo1, h1) in zip(reports, reports[1:]):
        if t0 <= unix_s <= t1:
            w = (unix_s - t0) / (t1 - t0)
            return la0 + w * (la1 - la0), lo0 + w * (lo1 - lo0), h0 + w * (h1 - h0), reports
    sys.exit("final epoch outside the ACARS reports")


def pooled(run_dir, seeds):
    return sum(np.load(run_dir / "bto-only" / f"seed-{s}" / "arc-summary.npz")["hist"] for s in seeds) / len(seeds)


def score(run_dir, acars):
    run = json.loads((run_dir / "run.json").read_text())
    final, sat, sub = final_satellite(run)
    lat_t, lon_t, alt_t, reports = truth_at(acars, final["unix_s"])
    a_t = float(azimuth(sub[0], sub[1], lat_t, lon_t))
    rng_km = R_EARTH * math.acos(math.sin(math.radians(sub[0])) * math.sin(math.radians(lat_t))
                                 + math.cos(math.radians(sub[0])) * math.cos(math.radians(lat_t))
                                 * math.cos(math.radians(lon_t - sub[1])))
    km = R_EARTH * math.sin(rng_km / R_EARTH)  # arc radius: along-arc km per radian of azimuth
    aircraft = ecef(lat_t, lon_t, alt_t * 0.0003048)
    bto_truth = 2 * (np.linalg.norm(sat - aircraft) + np.linalg.norm(sat - GES)) / C_KM_S * 1e6 - OFFSET

    seeds = sorted(int(p.parent.name.split("-")[1]) for p in (run_dir / "bto-only").glob("seed-*/arc-summary.npz"))
    hist = pooled(run_dir, seeds)
    x_edges = (EDGES - a_t) * km  # along-arc km from the truth, positive = clockwise (east of north)
    cdf = np.concatenate([[0.0], np.cumsum(hist)])
    cdf /= cdf[-1]
    q = {p: float(np.interp(p, cdf, x_edges)) for p in (0.025, 0.25, 0.5, 0.75, 0.975)}
    pit = float(np.interp(0.0, x_edges, cdf))
    group = max(1, round(BIN_KM / ((EDGES[1] - EDGES[0]) * km)))
    halves = [s for s in seeds if s <= len(seeds) // 2], [s for s in seeds if s > len(seeds) // 2]
    dens = []
    for h in halves:
        d = pooled(run_dir, h)
        d = d[: len(d) // group * group].reshape(-1, group).sum(1)
        dens.append(d / d.sum())
    overlap = float(np.minimum(*dens).sum())
    inside95 = q[0.025] <= 0 <= q[0.975]
    verdict = "PASS" if inside95 and overlap >= 0.8 else "FAIL"
    result = {
        "case": "bto-only", "final_epoch": final["id"], "truth": {"lat": lat_t, "lon": lon_t, "alt_ft": alt_t},
        "truth_bto_residual_us": final["bto_us"] - bto_truth, "pit": pit, "median_offset_km": q[0.5],
        "interval_50_km": [q[0.25], q[0.75]], "interval_95_km": [q[0.025], q[0.975]],
        "width_50_km": q[0.75] - q[0.25], "width_95_km": q[0.975] - q[0.025],
        "inside_50": q[0.25] <= 0 <= q[0.75], "inside_95": inside95, "split_half_overlap": overlap,
        "seeds": seeds, "verdict": verdict,
    }
    (run_dir / "score.json").write_text(json.dumps(result, indent=2))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    xc = (x_edges[:-1] + x_edges[1:]) / 2
    xc = xc[: len(xc) // group * group].reshape(-1, group).mean(1)
    step = (EDGES[1] - EDGES[0]) * km * group
    for h, d in zip(halves, dens):
        axes[0].plot(xc, d / step, lw=1.2, label=f"seeds {h[0]}-{h[-1]}")
    axes[0].axvline(0, color="k", lw=1, label="ACARS truth")
    for p in (0.025, 0.975):
        axes[0].axvline(q[p], color="grey", ls=":", lw=1)
    axes[0].set_xlim(q[0.025] - 300, q[0.975] + 300)
    axes[0].set_xlabel(f"along the {final['id']} BTO arc from the truth (km)")
    axes[0].set_ylabel("posterior density (per km)")
    axes[0].set_title(f"BTO only, {verdict}: truth at quantile {pit:.2f}; median {q[0.5]:+.0f} km; "
                      f"95% width {q[0.975] - q[0.025]:.0f} km; split-half {overlap:.2f}", fontsize=9)
    axes[0].legend(fontsize=8)
    routes = np.concatenate([np.load(run_dir / "bto-only" / f"seed-{s}" / "routes.npy") for s in seeds])
    for r in routes[np.random.default_rng(0).choice(len(routes), min(300, len(routes)), replace=False)]:
        axes[1].plot(r[:, 1], r[:, 0], color="#2a78d6", lw=0.3, alpha=0.3)
    tr = np.array([(la, lo) for _, la, lo, _ in reports])
    axes[1].plot(tr[:, 1], tr[:, 0], "k-", lw=1.5, label="ACARS track")
    axes[1].plot(lon_t, lat_t, "k*", ms=10, label=f"truth at {final['id']}")
    axes[1].set_xlabel("longitude (°E)")
    axes[1].set_ylabel("latitude (°N)")
    axes[1].legend(fontsize=8)
    axes[1].set_title("sampled posterior routes (blue) and the ACARS track", fontsize=9)
    fig.tight_layout()
    fig.savefig(run_dir / "score.png", dpi=100)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "summarise":
        summarise(Path(sys.argv[2]), int(sys.argv[3]))
    else:
        score(Path(sys.argv[2]), Path(sys.argv[3]))
