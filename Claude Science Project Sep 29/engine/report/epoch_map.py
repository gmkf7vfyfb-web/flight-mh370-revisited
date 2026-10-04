"""Posterior position map at a named measurement epoch, with credible contours and arcs.

Draws where the aircraft is at one epoch as a density on latitude/longitude axes, with
highest-posterior-density contours and the relevant BTO arcs drawn over it. Works on any
completed run directory: the positions come from the stored route samples, which every run
writes, so this is retroactive and needs no re-run.

A note on what the sample is. Each replicate stores `route_samples` trajectories drawn by
systematic resampling across the autopilot modes in proportion to their posterior probability,
so the routes are an equally weighted draw from the pooled posterior and no further weighting
is applied here. They are recorded every `route_interval_s`, so a position at an epoch that
falls between two recorded points is linearly interpolated; over a ten-minute step at cruise
speed the departure from the great circle is well under a tenth of a nautical mile, which is
invisible at any sensible map resolution.

Usage: python report/epoch_map.py <run-dir> [<epoch-id> ...] [--out <dir>]
       default epochs: m0011 m0019a
"""

import json
import pathlib
import sys

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
from scipy.ndimage import gaussian_filter

# Credible levels drawn, outermost first.
LEVELS = (0.99, 0.90, 0.50)
GRID_DEG = 0.1
SMOOTH_DEG = 0.3


def load_routes(run_dir, case):
    """Every replicate's route samples, stacked: (n_routes, n_points, 2) as lat, lon."""
    parts = []
    for seed_dir in sorted((run_dir / case).glob("seed-*")):
        path = seed_dir / "routes.npy"
        if path.exists():
            parts.append(np.load(path))
    if not parts:
        raise SystemExit(f"{run_dir}: no routes.npy under {case}/")
    return np.concatenate(parts, axis=0)


def final_positions(run_dir, case, columns, cap=4_000_000):
    """Weighted positions at the last step, read from each replicate's final.npy.

    The route samples stop at the last recorded interval, which falls short of the final
    epoch; this is the exact state there, and far larger than the route sample, so the final
    arc's map is the sharpest of the set. Rows are thinned to a cap because the full set is
    tens of millions across replicates.
    """
    iw, ilat, ilon = (columns.index(c) for c in ("weight", "latitude_deg", "longitude_deg"))
    lats, lons, ws = [], [], []
    seeds = sorted((run_dir / case).glob("seed-*"))
    per_seed = max(1, cap // max(1, len(seeds)))
    for seed_dir in seeds:
        path = seed_dir / "final.npy"
        if not path.exists():
            continue
        a = np.load(path, mmap_mode="r")
        step = max(1, a.shape[0] // per_seed)
        chunk = np.asarray(a[::step])
        lats.append(chunk[:, ilat].astype(float))
        lons.append(chunk[:, ilon].astype(float))
        ws.append(chunk[:, iw].astype(float))
    if not lats:
        raise SystemExit(f"{run_dir}: no final.npy under {case}/")
    return np.concatenate(lats), np.concatenate(lons), np.concatenate(ws)


def positions_at(routes, prior_unix_s, interval_s, target_unix_s):
    """Linear interpolation of each route to one instant, dropping routes that end before it."""
    x = (target_unix_s - prior_unix_s) / interval_s
    lo = int(np.floor(x))
    if lo < 0 or lo + 1 >= routes.shape[1]:
        raise SystemExit(f"epoch at route index {x:.2f} is outside the stored {routes.shape[1]} points")
    frac = x - lo
    a, b = routes[:, lo, :], routes[:, lo + 1, :]
    pos = a + frac * (b - a)
    return pos[np.isfinite(pos).all(axis=1)]


def hpd_levels(density, fractions):
    """Density values enclosing each given fraction of the total mass."""
    flat = np.sort(density.ravel())[::-1]
    share = np.cumsum(flat) / flat.sum()
    return [float(flat[np.searchsorted(share, f)]) for f in fractions]


def density_grid(lat, lon, weights=None, pad=2.0):
    lat_edges = np.arange(lat.min() - pad, lat.max() + pad + GRID_DEG, GRID_DEG)
    lon_edges = np.arange(lon.min() - pad, lon.max() + pad + GRID_DEG, GRID_DEG)
    counts, _, _ = np.histogram2d(lat, lon, bins=[lat_edges, lon_edges], weights=weights)
    smoothed = gaussian_filter(counts, SMOOTH_DEG / GRID_DEG, mode="constant")
    centres = lambda e: 0.5 * (e[:-1] + e[1:])
    return centres(lat_edges), centres(lon_edges), smoothed / smoothed.sum()


def arc_label(epoch_id, epochs):
    """The arc's ordinal, counting the handshakes the way the investigation does."""
    ordinals = {"m1941": "3rd", "m2041": "4th", "m2141": "5th", "m2241": "5th",
                "m0011": "6th", "m0019a": "7th", "m0019b": "7th"}
    return ordinals.get(epoch_id)


def utc(epochs, epoch_id):
    """Epoch time to the nearest minute. 00:10:59 is the 00:11 handshake, not 00:10."""
    import datetime as dt

    t = next(e["unix_s"] for e in epochs if e["id"] == epoch_id)
    return dt.datetime.fromtimestamp(round(t / 60) * 60, dt.timezone.utc).strftime("%H:%M")


def per_replicate(run_dir, epoch_id, case):
    """Latitudes and weights at an epoch, one entry per replicate."""
    meta = json.loads((run_dir / "run.json").read_text())
    target = next((e["unix_s"] for e in meta["epochs"] if e["id"] == epoch_id), None)
    if target is None:
        raise SystemExit(f"{epoch_id}: not an epoch of this run")
    out = []
    seeds = sorted((run_dir / case).glob("seed-*"))
    iw, ilat = meta["final_columns"].index("weight"), meta["final_columns"].index("latitude_deg")
    for seed_dir in seeds:
        routes = np.load(seed_dir / "routes.npy")
        index = (target - meta["prior_unix_s"]) / meta["route_interval_s"]
        if index + 1 >= routes.shape[1]:
            a = np.load(seed_dir / "final.npy", mmap_mode="r")
            step = max(1, a.shape[0] // (4_000_000 // max(1, len(seeds))))
            chunk = np.asarray(a[::step])
            out.append((chunk[:, ilat].astype(float), chunk[:, iw].astype(float)))
        else:
            pos = positions_at(routes, meta["prior_unix_s"], meta["route_interval_s"], target)
            out.append((pos[:, 0].astype(float), np.ones(len(pos))))
    return out, meta


def latitude_density(lat, weights, grid, smooth_deg=0.1):
    """Weighted histogram on `grid`, Gaussian-smoothed, normalised to a density per degree."""
    step = grid[1] - grid[0]
    edges = np.concatenate([grid - step / 2, [grid[-1] + step / 2]])
    counts, _ = np.histogram(lat, bins=edges, weights=weights)
    dens = gaussian_filter(counts, smooth_deg / step, mode="constant")
    total = dens.sum() * step
    return dens / total if total > 0 else dens


def density_figure(run_dir, epoch_id, case, figsize=(7.2, 4.2)):
    """Latitude pdf at an epoch: pooled curve, each replicate behind it, Davey's where it applies.

    The same density the map contours, read as a marginal. Replicate curves are the honest
    display of sampling spread: where they separate, the pooled curve is not yet resolved.
    """
    reps, meta = per_replicate(pathlib.Path(run_dir), epoch_id, case)
    grid = np.arange(-50.0, 50.0 + 0.05, 0.05)
    curves = [latitude_density(lat, w, grid) for lat, w in reps]
    pooled = np.mean(curves, axis=0)

    fig, ax = plt.subplots(figsize=figsize)
    for c in curves:
        ax.plot(grid, c, color="#4a6fa5", lw=0.5, alpha=0.45)
    ax.plot(grid, pooled, color="#1f4e8c", lw=1.8,
            label=f"This recreation, pooled over {len(curves)} replicates (thin: each)")

    # Davey's published curve is the pdf at the final handshake, so it is only a fair overlay
    # against the final epoch.
    last = meta["epochs"][-1]["id"]
    ref = (json.loads((pathlib.Path(run_dir) / "summary.json").read_text()).get("reference") or {})
    if epoch_id in (last, "m0019a", "m0019b") and ref.get("density"):
        rgrid = np.linspace(-50, 50, len(ref["density"]))
        ax.plot(rgrid, ref["density"], color="#d1603d", lw=1.6, ls="--",
                label="Davey et al. (2016) Fig. 10.3, digitised")

    lo = min(grid[np.argmax(pooled > pooled.max() * 1e-3)], -41.0)
    hi = grid[len(pooled) - 1 - np.argmax(pooled[::-1] > pooled.max() * 1e-3)]
    ax.set_xlim(lo, max(hi + 1.0, -26.0))
    ax.set_ylim(bottom=0)
    ax.set_xlabel(f"latitude at {utc(meta['epochs'], epoch_id)} UTC (°)")
    ax.set_ylabel("probability density (per degree)")
    ax.set_title(f"Latitude pdf at {utc(meta['epochs'], epoch_id)} UTC — {meta['config']['name']}",
                 loc="left", fontsize=9)
    ax.legend(loc="upper right", frameon=False, fontsize=7)
    ax.grid(axis="y", color="#e8e8e8", lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def mass_figure(run_dir, epoch_id, case, figsize=(6.4, 4.0)):
    """Cumulative probability mass against latitude along the arc.

    The posterior at a handshake lies on that handshake's arc, so latitude is a single
    sufficient coordinate along it and the two-dimensional map collapses to one curve without
    losing anything. Reading a credible interval off this is exact at any level, where the map
    only shows the three contours that were drawn.
    """
    lat, weights, source, meta = positions_for(pathlib.Path(run_dir), epoch_id, case)
    w = np.ones_like(lat) if weights is None else weights
    order = np.argsort(lat)
    lat_s, w_s = lat[order], w[order]
    cum = np.cumsum(w_s) / w_s.sum()

    def at(p):
        return float(np.interp(p, cum, lat_s))

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(lat_s, 100 * cum, color="#2b2b2b", lw=1.3)

    # Central credible intervals, read straight off the curve.
    bands = [(0.50, "#6a6a6a"), (0.90, "#a8a8a8"), (0.99, "#dcdcdc")]
    rows = []
    for frac, colour in reversed(bands):
        lo, hi = at(0.5 - frac / 2), at(0.5 + frac / 2)
        ax.axvspan(lo, hi, color=colour, zorder=0, lw=0)
        rows.append((frac, lo, hi))
    for frac, lo, hi in rows:
        for v, p in ((lo, 50 - 50 * frac), (hi, 50 + 50 * frac)):
            ax.plot([v, v], [0, p], color="#2b2b2b", lw=0.5, ls=":", zorder=1)
    # Interval figures as a block rather than beside each band: an annotation anchored to the
    # 99 % bound sits at the edge of the data and overflows the axes.
    text = "\n".join(f"{int(f * 100):>2} %   {abs(hi):.2f}–{abs(lo):.2f}°S   ({abs(hi - lo):.2f}° wide)"
                     for f, lo, hi in rows)
    ax.text(0.985, 0.03, text, transform=ax.transAxes, fontsize=6.5, family="monospace",
            color="#2b2b2b", va="bottom", ha="right")

    ax.set_xlabel("latitude along the arc (°)")
    ax.set_ylabel("cumulative probability mass (%)")
    ax.set_title(f"Mass against latitude at {utc(meta['epochs'], epoch_id)} UTC\n{meta['config']['name']}",
                 loc="left", fontsize=9)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{abs(v):.0f}°{'S' if v < 0 else 'N' if v > 0 else ''}"))
    ax.set_xlim(at(0.001), at(0.999))
    ax.set_ylim(0, 103)
    ax.text(0.015, 0.97, source, transform=ax.transAxes, fontsize=6, color="#555555", va="top")
    fig.tight_layout()
    return fig


def positions_for(run_dir, epoch_id, case):
    """Latitudes and weights at an epoch, from routes or from the stored final state."""
    meta = json.loads((run_dir / "run.json").read_text())
    target = next((e["unix_s"] for e in meta["epochs"] if e["id"] == epoch_id), None)
    if target is None:
        raise SystemExit(f"{epoch_id}: not an epoch of this run")
    index = (target - meta["prior_unix_s"]) / meta["route_interval_s"]
    routes = load_routes(run_dir, case)
    if index + 1 >= routes.shape[1]:
        lat, _lon, weights = final_positions(run_dir, case, meta["final_columns"])
        return lat, weights, f"{len(lat):,} final-state particles", meta
    pos = positions_at(routes, meta["prior_unix_s"], meta["route_interval_s"], target)
    return pos[:, 0].astype(float), None, f"{len(pos):,} pooled route samples", meta


def trajectory_figure(run_dir, epoch_id, case, band, n_show=40, figsize=(7.0, 6.2)):
    """Whole flight paths of the particles that are inside a latitude band at one epoch.

    `band` is (south, north) in degrees. Drawn against a background sample of everything else,
    so the question the figure answers is not "what does a trajectory look like" but "what do
    these trajectories do differently".
    """
    run_dir = pathlib.Path(run_dir)
    meta = json.loads((run_dir / "run.json").read_text())
    target = next(e["unix_s"] for e in meta["epochs"] if e["id"] == epoch_id)
    routes = load_routes(run_dir, case)
    at_epoch = positions_at(routes, meta["prior_unix_s"], meta["route_interval_s"], target)
    keep = np.isfinite(routes[:, :, 0]).all(axis=1)
    lat_at = at_epoch[:, 0]
    sel = keep & (lat_at > band[0]) & (lat_at < band[1])
    other = keep & (lat_at < -34.5)
    rng = np.random.default_rng(0)
    pick = np.where(sel)[0]
    pick = rng.choice(pick, min(n_show, len(pick)), replace=False)
    bg = rng.choice(np.where(other)[0], min(220, int(other.sum())), replace=False)

    fig, ax = plt.subplots(figsize=figsize)
    for i in bg:
        ax.plot(routes[i, :, 1], routes[i, :, 0], color="#c9c9c9", lw=0.35, alpha=0.5, zorder=1)
    for i in pick:
        ax.plot(routes[i, :, 1], routes[i, :, 0], color="#b16286", lw=0.7, alpha=0.85, zorder=3)
    for arc_id, style in ((epoch_id, dict(lw=1.2, color="#1f4e8c")),):
        arc = next((a for a in meta["reference_arcs"] if a["epoch"] == arc_id), None)
        if arc:
            pts = np.asarray(arc["lat_lon"], dtype=float)
            ax.plot(pts[:, 1], pts[:, 0], label=f"{arc_label(arc_id, meta['epochs'])} arc, "
                    f"{utc(meta['epochs'], arc_id)} UTC", zorder=4, **style)
    ax.plot([], [], color="#b16286", lw=0.9,
            label=f"terminating {abs(band[1]):.0f}–{abs(band[0]):.0f}°S  ({len(np.where(sel)[0])} of {int(keep.sum()):,})")
    ax.plot([], [], color="#c9c9c9", lw=0.9, label="main body, south of 34.5°S")
    ax.scatter(routes[:, 0, 1][keep][:1], routes[:, 0, 0][keep][:1], s=18, color="#2b2b2b",
               zorder=5, label="18:01 prior")

    ax.set_xlabel("longitude (°E)")
    ax.set_ylabel("latitude (°)")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{abs(v):.0f}°{'S' if v < 0 else 'N' if v > 0 else ''}"))
    ax.set_title(f"Paths reaching the northern region at {utc(meta['epochs'], epoch_id)} UTC\n{meta['config']['name']}",
                 loc="left", fontsize=9)
    # Framed on the trajectories; the arc runs far beyond them and is simply clipped.
    plat = routes[np.concatenate([pick, bg])][:, :, 0]
    plon = routes[np.concatenate([pick, bg])][:, :, 1]
    ax.set_ylim(np.nanmin(plat) - 2.0, np.nanmax(plat) + 3.0)
    ax.set_xlim(np.nanmin(plon) - 2.0, np.nanmax(plon) + 2.0)
    ax.set_aspect(1 / np.cos(np.deg2rad(20)))
    ax.legend(loc="upper left", frameon=False, fontsize=7)
    fig.tight_layout()
    return fig


def draw(run_dir, epoch_id, case, out_dir):
    """Build the map and write it as PDF and PNG. Returns the PDF path."""
    out_dir = pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, build in (("position", figure), ("density", density_figure)):
        fig = build(pathlib.Path(run_dir), epoch_id, case)
        stem = out_dir / f"{name}-{epoch_id}"
        fig.savefig(f"{stem}.pdf")
        fig.savefig(f"{stem}.png", dpi=300)
        plt.close(fig)
        written.append(f"{stem}.pdf")
    return "  ".join(written)


def figure(run_dir, epoch_id, case, figsize=None):
    """The map as a matplotlib figure, so a report can place it on a page."""
    run_dir = pathlib.Path(run_dir)
    meta = json.loads((run_dir / "run.json").read_text())
    epochs = meta["epochs"]
    target = next((e["unix_s"] for e in epochs if e["id"] == epoch_id), None)
    if target is None:
        raise SystemExit(f"{epoch_id}: not an epoch of this run")

    # The last epoch falls past the final recorded route point, and is stored exactly anyway.
    index = (target - meta["prior_unix_s"]) / meta["route_interval_s"]
    routes = load_routes(run_dir, case)
    if index + 1 >= routes.shape[1]:
        lat, lon, weights = final_positions(run_dir, case, meta["final_columns"])
        source = f"{len(lat):,} final-state particles"
    else:
        pos = positions_at(routes, meta["prior_unix_s"], meta["route_interval_s"], target)
        lat, lon, weights = pos[:, 0].astype(float), pos[:, 1].astype(float), None
        source = f"{len(lat):,} pooled route samples"
    lat_c, lon_c, dens = density_grid(lat, lon, weights)
    levels = hpd_levels(dens, LEVELS)

    # A window framed on the posterior, with the longitude span widened by the latitude
    # cosine so a degree reads the same length on both axes, and the canvas shaped to match
    # so locking the aspect does not then inflate the frame with empty ocean.
    # Framed on the outermost contour actually drawn, not on the raw sample range, which a
    # handful of stray trajectories would otherwise stretch across half an ocean.
    inside = dens >= levels[0]
    rows, cols = np.where(inside)
    lat_lo, lat_hi = lat_c[rows.min()], lat_c[rows.max()]
    lon_lo, lon_hi = lon_c[cols.min()], lon_c[cols.max()]
    mid_lat, mid_lon = 0.5 * (lat_lo + lat_hi), 0.5 * (lon_lo + lon_hi)
    half_lat = max(1.2, 0.72 * (lat_hi - lat_lo))
    half_lon = half_lat / np.cos(np.deg2rad(mid_lat))
    height = 4.8
    fig, ax = plt.subplots(figsize=figsize or (height * half_lon / half_lat * 0.92, height))

    # Greyscale: darker is denser. Filled bands between the credible levels, then crisp edges.
    shades = ["#dcdcdc", "#a8a8a8", "#6a6a6a"]
    ax.contourf(lon_c, lat_c, dens, levels=levels + [dens.max()], colors=shades, antialiased=True)
    ax.contour(lon_c, lat_c, dens, levels=levels, colors="#2b2b2b", linewidths=[0.5, 0.7, 0.9])
    from matplotlib.patches import Patch

    bands = [Patch(facecolor=c, edgecolor="#2b2b2b", lw=0.6, label=f"{int(f * 100)} % credible")
             for c, f in zip(shades[::-1], (0.50, 0.90, 0.99))]

    # The arcs this map is read against: the one the posterior sits on and the final one.
    wanted = {epoch_id: dict(lw=1.3, color="#b16286")}
    wanted.setdefault("m0019a", dict(lw=1.0, color="#4a6fa5", ls="--"))
    for arc_id, style in wanted.items():
        arc = next((a for a in meta["reference_arcs"] if a["epoch"] == arc_id), None)
        if arc is None:
            continue
        pts = np.asarray(arc["lat_lon"], dtype=float)
        ordinal = arc_label(arc_id, epochs)
        ax.plot(pts[:, 1], pts[:, 0], label=f"{ordinal} arc, {utc(epochs, arc_id)} UTC", **style)

    ax.set_xlabel("longitude (°E)")
    ax.set_ylabel("latitude (°)")
    ax.set_title(f"Position at {utc(epochs, epoch_id)} UTC\n{meta['config']['name']}", loc="left", fontsize=9)
    fmt = FuncFormatter(lambda v, _: f"{abs(v):.0f}°{'S' if v < 0 else 'N' if v > 0 else ''}")
    ax.yaxis.set_major_formatter(fmt)
    ax.set_xlim(mid_lon - half_lon, mid_lon + half_lon)
    ax.set_ylim(mid_lat - half_lat, mid_lat + half_lat)
    ax.set_aspect(1 / np.cos(np.deg2rad(np.clip(mid_lat, -89, 89))))
    handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles=bands + handles, loc="upper left", frameon=False, fontsize=6.5,
              handlelength=1.4, handletextpad=0.5, labelspacing=0.35, borderpad=0.2)
    ax.text(0.985, 0.015, source, transform=ax.transAxes,
            fontsize=6, color="#555555", va="bottom", ha="right")
    fig.tight_layout()
    return fig


def main(argv):
    out_dir = None
    if "--out" in argv:
        at = argv.index("--out")
        out_dir = pathlib.Path(argv[at + 1])
        argv = argv[:at] + argv[at + 2:]
    args = [a for a in argv if not a.startswith("--")]
    run_dir = pathlib.Path(args[0])
    epoch_ids = args[1:] or ["m0011", "m0019a"]
    out_dir = out_dir or run_dir
    meta = json.loads((run_dir / "run.json").read_text())
    case = meta["config"]["cases"][0]["id"]
    for epoch_id in epoch_ids:
        print(draw(run_dir, epoch_id, case, out_dir))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1:])