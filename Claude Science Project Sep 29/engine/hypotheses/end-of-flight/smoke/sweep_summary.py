"""Pooled multi-seed summary of an end-of-flight terminal sweep, in the project's reporting conventions
(mh370-run-reporting; report/epoch_map.py latitude density).

    python3 sweep_summary.py <out.json> <terminal-out-dir> [<dir> ...]

Per data option x log-on cause: ESS per seed and summed; pooled (equal weight per seed) median impact
latitude/longitude; highest-density latitude intervals at 50/90/99 % on the pooled latitude density; split-half
overlap of the impact-latitude density over EVERY balanced partition of the seeds (mean, min, max) against the
replicate-count floor (0.896 at 4, 0.914 at 6, 0.924 at 8); posterior divergent-spiral share; displacement from
the own 00:19:37 position, 50/90 %. Latitude density: weighted 0.1 deg histogram, Gaussian-smoothed 0.1 deg,
per degree, as epoch_map.latitude_density.
"""
import itertools, json, pathlib, sys
import numpy as np
from scipy.ndimage import gaussian_filter
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from displacement_hist import option_posteriors

STEP = 0.1
GRID_EDGES = np.arange(-50.0, -10.0 + 1e-9, STEP)
FLOORS = {4: 0.896, 6: 0.914, 8: 0.924}


def lat_density(lat, p):
    h, _ = np.histogram(lat, bins=GRID_EDGES, weights=p)
    d = gaussian_filter(h, 0.1 / STEP, mode="constant")
    return d / (d.sum() * STEP)


def partitions(n):
    return [(list(a), [i for i in range(n) if i not in a]) for a in itertools.combinations(range(n), n // 2) if 0 in a] if n % 2 == 0 else []


def hdi(dens, frac):
    c = 0.5 * (GRID_EDGES[1:] + GRID_EDGES[:-1]); o = np.argsort(dens)[::-1]
    keep = o[: int(np.searchsorted(np.cumsum(dens[o]) * STEP, frac)) + 1]
    return [float(c[keep].min()), float(c[keep].max())]


def wq(x, p, q):
    m = np.isfinite(x); o = np.argsort(x[m]); cc = np.cumsum(p[m][o]); return float(np.interp(q, cc / cc[-1], x[m][o]))


def main():
    out = pathlib.Path(sys.argv[1])
    srcs = [(pathlib.Path(d), s) for d in sys.argv[2:] for s in sorted(pathlib.Path(d, "bto-bfo").glob("seed-*")) if (s / "impacts.npy").exists()]
    per = {}
    for run, s in srcs:
        for k, p, c in option_posteriors(run, s):
            r = np.where(c["has"], np.hypot(c["dn"], c["de"]), np.nan)
            per.setdefault(k, []).append(dict(seed=f"{run.name}/{s.name}", ess=float(1 / np.sum(p ** 2)), dens=lat_density(c["lat"], p),
                                             lat=c["lat"], lon=c["lon"], p=p, div=float(p[c["spiral_divergent"] > 0.5].sum()), r=r))
    res = {"seeds": [f"{r.name}/{s.name}" for r, s in srcs], "lat_step_deg": STEP, "options": {}}
    for k, v in per.items():
        n = len(v); P = np.concatenate([x["p"] for x in v]) / n
        lat = np.concatenate([x["lat"] for x in v]); lon = np.concatenate([x["lon"] for x in v]); r = np.concatenate([x["r"] for x in v])
        pooled = np.mean([x["dens"] for x in v], axis=0)
        sh = [float(np.minimum(np.mean([v[i]["dens"] for i in a], 0), np.mean([v[i]["dens"] for i in b], 0)).sum() * STEP) for a, b in partitions(n)]
        res["options"][k] = {
            "ess_per_seed": {x["seed"]: x["ess"] for x in v}, "ess_total": float(sum(x["ess"] for x in v)),
            "median_lat_deg": wq(lat, P, 0.5), "median_lon_deg": wq(lon, P, 0.5),
            "median_lat_per_seed": [wq(x["lat"], x["p"], 0.5) for x in v],
            "hdi_lat_50_90_99": [hdi(pooled, f) for f in (0.5, 0.9, 0.99)],
            "split_half": None if not sh else {"n_partitions": len(sh), "mean": float(np.mean(sh)), "min": float(np.min(sh)), "max": float(np.max(sh)),
                                                "floor": FLOORS.get(n), "pass": (FLOORS.get(n) is not None and float(np.min(sh)) >= FLOORS[n])},
            "divergent_share": float(np.mean([x["div"] for x in v])),
            "displacement_nm_50_90": [wq(r, P, 0.5), wq(r, P, 0.9)],
        }
    out.write_text(json.dumps(res, indent=1)); print("wrote", out)


if __name__ == "__main__":
    main()
