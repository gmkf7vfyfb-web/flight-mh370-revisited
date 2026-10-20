"""Position maps and latitude densities for output.handoff_epochs snapshots.

Usage: python report/snapshot_maps.py <run-dir> <out-dir> [epoch ...]   (default m2241 m0011)

A snapshot is the FILTERING distribution at its epoch: the posterior given the data up to and
including that epoch. It is drawn here from the hand-off rows (handoff.npy, weights summing to one
per replicate, replicates pooled with equal weight). For comparison the density figure also
shows where the paths of the final (00:19:37) posterior were at the same instant, read from
routes.npy - the SMOOTHING distribution, which has seen every later burst. The two are different
objects, and every figure says so in its footnote.
"""
import json, pathlib, sys
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from epoch_map import hpd_levels, latitude_density, positions_at, arc_label, utc, load_routes, LEVELS

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.linewidth": 0.6,
                     "xtick.major.width": 0.6, "ytick.major.width": 0.6, "pdf.fonttype": 42})
LATFMT = FuncFormatter(lambda v, _: f"{abs(v):.0f}°{'S' if v < 0 else 'N' if v > 0 else ''}")


MAP_GRID_DEG, MAP_SMOOTH_DEG = 0.05, 0.1


def density_grid(lat, lon, weights, pad=1.0):
    """As epoch_map.density_grid but finer (0.05 deg grid, 0.1 deg smoothing). A filtering
    distribution sits on its arc within a few NM; epoch_map's 0.3 deg smoothing would draw it
    as a band about a degree wide across the arc, which is the smoother, not the data."""
    from scipy.ndimage import gaussian_filter
    le = np.arange(lat.min() - pad, lat.max() + pad + MAP_GRID_DEG, MAP_GRID_DEG)
    oe = np.arange(lon.min() - pad, lon.max() + pad + MAP_GRID_DEG, MAP_GRID_DEG)
    c, _, _ = np.histogram2d(lat, lon, bins=[le, oe], weights=weights)
    d = gaussian_filter(c, MAP_SMOOTH_DEG / MAP_GRID_DEG, mode="constant")
    mid = lambda e: 0.5 * (e[:-1] + e[1:])
    return mid(le), mid(oe), d / d.sum()


def wrap(lines, width=118):
    import textwrap
    return [w for l in lines for w in textwrap.wrap(l, width)]


def wquant(x, w, q):
    i = np.argsort(x); c = np.cumsum(w[i]); c /= c[-1]
    return np.interp(q, c, x[i])


def load(run_dir, case, epoch):
    reps = []
    for d in sorted((run_dir / case).glob("seed-*")):
        a = np.load(d / f"handoff-{epoch}" / "handoff.npy")
        reps.append((a[:, 1], a[:, 2], a[:, 0] / a[:, 0].sum()))
    return reps


def smoothing(run_dir, case, meta, epoch):
    target = next(e["unix_s"] for e in meta["epochs"] if e["id"] == epoch)
    out = []
    for d in sorted((run_dir / case).glob("seed-*")):
        pos = positions_at(np.load(d / "routes.npy"), meta["prior_unix_s"], meta["route_interval_s"], target)
        out.append(pos[:, 0].astype(float))
    return out


def footnote(fig, lines, y=0.02):
    fig.text(0.02, y, "\n".join(wrap(lines)), fontsize=6.4, va="bottom", ha="left", color="#333333", linespacing=1.45)


def map_figure(run_dir, case, meta, epoch, out):
    reps = load(run_dir, case, epoch)
    lat = np.concatenate([r[0] for r in reps]); lon = np.concatenate([r[1] for r in reps])
    w = np.concatenate([r[2] for r in reps]) / len(reps)
    lat_c, lon_c, dens = density_grid(lat, lon, w)
    levels = hpd_levels(dens, LEVELS)
    rows, cols = np.where(dens >= levels[0])
    lat_lo, lat_hi, lon_lo, lon_hi = lat_c[rows.min()], lat_c[rows.max()], lon_c[cols.min()], lon_c[cols.max()]
    mid_lat, mid_lon = 0.5 * (lat_lo + lat_hi), 0.5 * (lon_lo + lon_hi)
    half_lat = max(1.2, 0.72 * (lat_hi - lat_lo)); half_lon = half_lat / np.cos(np.deg2rad(mid_lat))
    h = 4.6
    fig = plt.figure(figsize=(7.2, h + 1.5))
    ax = fig.add_axes([0.10, 0.30, 0.86, 0.63])
    step = 1.0 if 2 * half_lat < 6 else 2.0 if 2 * half_lat < 14 else 5.0
    ax.xaxis.set_major_locator(MultipleLocator(step)); ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.set_axisbelow(True); ax.grid(True, color="#e3e3e3", lw=0.6)
    shades = ["#dcdcdc", "#a8a8a8", "#6a6a6a"]
    ax.contourf(lon_c, lat_c, dens, levels=levels + [dens.max()], colors=shades)
    ax.contour(lon_c, lat_c, dens, levels=levels, colors="#2b2b2b", linewidths=[0.5, 0.7, 0.9])
    bands = [Patch(facecolor=c, edgecolor="#2b2b2b", lw=0.6, label=f"{int(f * 100)}% of probability")
             for c, f in zip(shades[::-1], (0.50, 0.90, 0.99))]
    for arc_id, style in {epoch: dict(lw=1.3, color="#b16286"), "m0019a": dict(lw=1.0, color="#4a6fa5", ls="--")}.items():
        arc = next((a for a in meta["reference_arcs"] if a["epoch"] == arc_id), None)
        p = np.asarray(arc["lat_lon"], float) if arc else np.empty((0, 2))
        inside = (abs(p[:, 0] - mid_lat) < half_lat) & (abs(p[:, 1] - mid_lon) < half_lon)
        if inside.any():  # an arc outside the frame is left out of the legend too
            ax.plot(p[:, 1], p[:, 0], label=f"{arc_label(arc_id, meta['epochs'])} arc, {utc(meta['epochs'], arc_id)} UTC", **style)
    ax.set_xlim(mid_lon - half_lon, mid_lon + half_lon); ax.set_ylim(mid_lat - half_lat, mid_lat + half_lat)
    ax.set_aspect(1 / np.cos(np.deg2rad(mid_lat)))
    ax.yaxis.set_major_formatter(LATFMT); ax.set_xlabel("longitude (°E)"); ax.set_ylabel("latitude")
    ax.set_title(f"Aircraft position at {utc(meta['epochs'], epoch)} UTC: hand-off to the end-of-flight stage", loc="left", fontsize=8.5)
    hl, _ = ax.get_legend_handles_labels()
    ax.legend(handles=bands + hl, loc="upper left", frameon=False, fontsize=6.5, handlelength=1.4, labelspacing=0.35)
    q = wquant(lat, w, [0.05, 0.25, 0.5, 0.75, 0.95])
    footnote(fig, [
        f"Filtering distribution at {utc(meta['epochs'], epoch)} UTC: conditioned on the data up to and including this arc only; it has not seen any later burst.",
        "It is not a slice of the 00:19:37 posterior. Drawn from the hand-off rows the end-of-flight stage starts from.",
        f"{len(lat):,} hand-off rows, {len(reps)} replicates pooled with equal weight. Contours enclose 50, 90 and 99% of probability (0.1° smoothing).",
        f"Latitude median {abs(q[2]):.2f}°S; 50% interval {abs(q[3]):.2f}–{abs(q[1]):.2f}°S; 90% interval {abs(q[4]):.2f}–{abs(q[0]):.2f}°S.",
        "Model: no-exhaustion-prior (7 Hz BFO, fuel model, no exhaustion-time prior), reproduced byte-identically as reference-snapshots.",
    ])
    for ext in ("pdf", "png"):
        fig.savefig(out / f"snapshot-position-{epoch}.{ext}", dpi=200)
    plt.close(fig)
    return q


def density_figure(run_dir, case, meta, epoch, out):
    reps = load(run_dir, case, epoch)
    grid = np.arange(-50.0, 50.0 + 0.05, 0.05)
    curves = [latitude_density(lat, w, grid) for lat, _, w in reps]
    pooled = np.mean(curves, axis=0)
    sm = smoothing(run_dir, case, meta, epoch)
    sm_curve = np.mean([latitude_density(x, np.ones_like(x), grid) for x in sm], axis=0)
    lat = np.concatenate([r[0] for r in reps]); w = np.concatenate([r[2] for r in reps]) / len(reps)
    q = wquant(lat, w, [0.05, 0.25, 0.5, 0.75, 0.95])
    sl = np.concatenate(sm); qs = np.quantile(sl, [0.05, 0.25, 0.5, 0.75, 0.95])
    lo, hi = min(q[0], qs[0]) - 1.5, max(q[4], qs[4]) + 1.5
    fig = plt.figure(figsize=(7.2, 5.6))
    ax = fig.add_axes([0.09, 0.40, 0.88, 0.54])
    for c in curves:
        ax.plot(grid, c, color="#b8b8b8", lw=0.6, zorder=1)
    ax.plot([], [], color="#b8b8b8", lw=0.6, label="Each replicate (filtering)")
    ax.plot(grid, pooled, color="black", lw=1.4, label=f"Hand-off at {utc(meta['epochs'], epoch)} UTC (filtering)", zorder=3)
    ax.plot(grid, sm_curve, color="#4a6fa5", lw=1.1, ls="--", label=f"Paths of the 00:19:37 posterior, at {utc(meta['epochs'], epoch)} UTC (smoothing)", zorder=2)
    ax.set_xlim(lo, hi); ax.set_ylim(bottom=0)
    ax.xaxis.set_major_locator(MultipleLocator(1.0 if hi - lo < 10 else 2.0)); ax.xaxis.set_major_formatter(LATFMT)
    ax.grid(True, axis="x", color="#ececec", lw=0.6); ax.set_axisbelow(True)
    ax.set_xlabel(f"latitude along the {arc_label(epoch, meta['epochs'])} arc"); ax.set_ylabel("probability density (per degree)")
    ax.set_title(f"Latitude density at {utc(meta['epochs'], epoch)} UTC", loc="left", fontsize=8.5)
    ax.legend(loc="upper left", frameon=False, fontsize=6.6, handlelength=2.2)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    footnote(fig, [
        f"Filtering (solid): the posterior given data up to and including the {utc(meta['epochs'], epoch)} UTC arc only. This is what the end-of-flight stage starts from.",
        f"Smoothing (dashed): where the trajectories of the final 00:19:37 posterior were at {utc(meta['epochs'], epoch)} UTC; it has also seen every later arc and burst.",
        "They are different distributions, not truncations of one another; neither is an impact location.",
        f"Filtering: median {abs(q[2]):.2f}°S, 50% interval {abs(q[3]):.2f}–{abs(q[1]):.2f}°S, 90% {abs(q[4]):.2f}–{abs(q[0]):.2f}°S ({len(lat):,} rows, {len(reps)} replicates).",
        f"Smoothing: median {abs(qs[2]):.2f}°S, 50% interval {abs(qs[3]):.2f}–{abs(qs[1]):.2f}°S, 90% {abs(qs[4]):.2f}–{abs(qs[0]):.2f}°S ({len(sl):,} route samples).",
        "Densities smoothed at 0.1°. Model: no-exhaustion-prior (7 Hz BFO, fuel model), reproduced byte-identically as reference-snapshots.",
    ])
    for ext in ("pdf", "png"):
        fig.savefig(out / f"snapshot-density-{epoch}.{ext}", dpi=200)
    plt.close(fig)
    return q, qs


if __name__ == "__main__":
    run_dir, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    meta = json.loads((run_dir / "run.json").read_text())
    case = meta["config"]["cases"][0]["id"]
    for ep in sys.argv[3:] or ["m2241", "m0011"]:
        qm = map_figure(run_dir, case, meta, ep, out)
        qf, qs = density_figure(run_dir, case, meta, ep, out)
        print(ep, "filtering q", np.round(qf, 2), "smoothing q", np.round(qs, 2))
