"""How much of the waypoint stratum do the trajectories already generated cover?

Usage: python report/waypoint_coverage.py <out-dir> <run-dir> [<run-dir> ...]

Reads each run's routes.npy (per replicate, an equally weighted draw of `route_samples` POSTERIOR
paths, vertices every route_interval_s from the 18:01:49 prior), the declared phase-3 sampling
region (data/sampling-region-phase3.csv) and the fix table (data/waypoints.csv). Purely geometric:
no measurement is evaluated here, and the waypoint hypothesis is not tested.

Three measures, all in NM in a local tangent plane at each fix or leg (error under 3% over this
region, which spans 14N-14S):
  * nearest approach of each route to each fix (point-to-polyline);
  * whether a route FOLLOWS a leg between two fixes: every point of the leg, sampled every 2 NM,
    lies within a tolerance of the route (directed Hausdorff from the leg to the route);
  * the same for whole candidate waypoint paths built from the fixes in the region.
And one diagnostic of what the routes can represent at all: the number of distinct route
positions at each vertex time (rounded to 1 NM), which measures how many separate ancestries
survive resampling.
"""
import csv, itertools, json, pathlib, sys
import numpy as np

NM_PER_DEG = 60.0
TOLS = (10.0, 25.0, 50.0)


def load_fixes(data):
    rows = list(csv.DictReader(open(data / "waypoints.csv", encoding="utf-8-sig")))
    return {r["name"]: (float(r["lat_deg"]), float(r["lon_deg"])) for r in rows}


def load_region(data):
    rows = list(csv.DictReader(open(data / "sampling-region-phase3.csv", encoding="utf-8-sig")))
    return np.array([[float(r["lat_deg"]), float(r["lon_deg"])] for r in rows])


def inside(poly, lat, lon):
    # even-odd ray cast in (lon, lat)
    x, y = lon, lat
    c = False
    n = len(poly)
    for i in range(n):
        y1, x1 = poly[i]; y2, x2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            if x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
    return c


def to_plane(lat, lon, lat0, lon0):
    k = np.cos(np.deg2rad(lat0))
    return np.stack([(lon - lon0) * k * NM_PER_DEG, (lat - lat0) * NM_PER_DEG], axis=-1)


def point_to_polylines(p, routes_xy):
    """Distance (NM) from point p (2,) to each route polyline. routes_xy: (R, V, 2)."""
    a, b = routes_xy[:, :-1], routes_xy[:, 1:]
    ab = b - a
    t = np.clip(((p - a) * ab).sum(-1) / np.maximum((ab * ab).sum(-1), 1e-12), 0, 1)
    d = np.linalg.norm(a + t[..., None] * ab - p, axis=-1)
    return d.min(axis=1)


def leg_points(f1, f2, step_nm=2.0):
    (la1, lo1), (la2, lo2) = f1, f2
    k = np.cos(np.deg2rad(0.5 * (la1 + la2)))
    length = np.hypot((lo2 - lo1) * k, la2 - la1) * NM_PER_DEG
    n = max(2, int(np.ceil(length / step_nm)) + 1)
    s = np.linspace(0, 1, n)
    return np.stack([la1 + s * (la2 - la1), lo1 + s * (lo2 - lo1)], axis=1), length


def deviation(path_ll, routes_ll):
    """Max over path sample points of the distance to each route: (R,)."""
    lat0, lon0 = path_ll[:, 0].mean(), path_ll[:, 1].mean()
    r = to_plane(routes_ll[..., 0], routes_ll[..., 1], lat0, lon0)
    pts = to_plane(path_ll[:, 0], path_ll[:, 1], lat0, lon0)
    worst = np.zeros(len(r))
    for p in pts:
        worst = np.maximum(worst, point_to_polylines(p, r))
    return worst


def load_routes(run):
    parts = [np.load(f).astype(float) for f in sorted(run.glob("*/seed-*/routes.npy"))]
    meta = json.loads((run / "run.json").read_text())
    return np.concatenate(parts), meta


def unique_routes(routes, last_vertex):
    """Distinct routes over vertices 0..last_vertex, with how many of the equally weighted draws
    each stands for. Resampling makes many draws exact copies over the early flight."""
    clip = routes[:, : last_vertex + 1, :]
    u, inverse, counts = np.unique(clip.reshape(len(clip), -1), axis=0, return_inverse=True, return_counts=True)
    return u.reshape(-1, last_vertex + 1, 2), counts / counts.sum()


def main(out, runs):
    data = pathlib.Path(__file__).resolve().parents[1] / "data"
    fixes, region = load_fixes(data), load_region(data)
    fixes_in = {n: ll for n, ll in fixes.items() if inside(region, *ll) and not n.startswith("V_")}
    # Entry and the phase-2 box's reference fix are carried too, as candidates the path passes.
    for extra in ("NILAM", "LAGOG"):
        fixes_in.setdefault(extra, fixes[extra])
    # Candidate waypoint paths. Southbound stages, at most one fix per stage, stages may be
    # skipped; every path starts at NILAM (the last N571 fix before the boundary).
    stages = [["SAMAK", "IGOGU", "ANOKO", "NOPEK", "LAGOG"], ["BEDAX", "BULVA"], ["ISBIX", "POSOD"],
              ["MUTMI", "PIPOV"], ["BEBIM"]]
    stages = [[f for f in s if f in fixes_in] for s in stages]
    paths = []
    for pick in itertools.product(*[[None] + s for s in stages]):
        seq = [f for f in pick if f]
        if seq:
            paths.append(["NILAM"] + seq)
    legs = sorted({(a, b) for p in paths for a, b in zip(p, p[1:])})

    fix_rows, leg_rows, path_rows, div_rows = [], [], [], []
    for run in runs:
        routes, meta = load_routes(run)
        name = meta["config"]["name"]
        t0, dt = meta["prior_unix_s"], meta["route_interval_s"]
        # distinct ancestries per vertex
        for v in range(routes.shape[1]):
            q = np.round(routes[:, v, :] * NM_PER_DEG).astype(np.int64)
            div_rows.append((name, v, t0 + v * dt, len({tuple(x) for x in q})))
        # Only the flight through the region matters: vertices to the first one south of 16S,
        # deduplicated, each distinct route weighted by its share of the draws.
        south = np.where((routes[..., 0] < -16.0).all(axis=0))[0]
        last = int(south[0]) if len(south) else routes.shape[1] - 1
        routes, w = unique_routes(routes, last)
        share = lambda ok: round(float(w[ok].sum()), 4)
        for n, (la, lo) in sorted(fixes_in.items()):
            r = to_plane(routes[..., 0], routes[..., 1], la, lo)
            d = point_to_polylines(np.zeros(2), r)
            o = np.argsort(d); med = float(d[o][np.searchsorted(np.cumsum(w[o]), 0.5)])
            fix_rows.append([name, n, la, lo, inside(region, la, lo), round(float(d.min()), 1), round(med, 1)]
                            + [share(d <= t) for t in TOLS])
        leg_dev = {}
        for a, b in legs:
            pts, length = leg_points(fixes_in[a], fixes_in[b], step_nm=5.0)
            dev = leg_dev[(a, b)] = deviation(pts, routes)
            leg_rows.append([name, f"{a}-{b}", round(length, 1), round(float(dev.min()), 1)] + [share(dev <= t) for t in TOLS])
        for p in paths:
            dev = np.max([leg_dev[(a, b)] for a, b in zip(p, p[1:])], axis=0)
            path_rows.append([name, "-".join(p), round(float(dev.min()), 1)] + [share(dev <= t) for t in TOLS])
        print(name, len(w), "distinct routes to vertex", last, ";", len(paths), "paths;", len(legs), "legs")

    out.mkdir(parents=True, exist_ok=True)
    hdr_t = [f"share_within_{int(t)}nm" for t in TOLS]
    for fname, hdr, rows in [
        ("waypoint-coverage-fixes.csv", ["run", "fix", "lat", "lon", "in_region", "nearest_nm", "median_nm"] + hdr_t, fix_rows),
        ("waypoint-coverage-legs.csv", ["run", "leg", "length_nm", "best_route_max_dev_nm"] + hdr_t, leg_rows),
        ("waypoint-coverage-paths.csv", ["run", "path", "best_route_max_dev_nm"] + hdr_t, path_rows),
        ("route-ancestries.csv", ["run", "vertex", "unix_s", "distinct_positions_1nm"], div_rows),
    ]:
        with open(out / fname, "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(hdr); w.writerows(rows)
    return fixes, fixes_in, region, paths


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]), [pathlib.Path(p) for p in sys.argv[2:]])
