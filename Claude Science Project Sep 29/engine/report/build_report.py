#!/usr/bin/env python3
"""Build the report PDF from a completed run directory.

Usage: build_report.py RUN_DIR [OUTPUT_PDF] [--baseline BASE_RUN_DIR]

Writes OUTPUT_PDF and a PNG of each page in OUTPUT_PDF's directory under <name>-png/.

With --baseline (used for hypothesis runs) the base estimate is overlaid for comparison.

Reads only the run artifacts: run.json, summary.json, and each replicate's final.npy and
routes.npy. The latitude densities, the pooling that combines replicates and the published
comparison curve come from summary.json, which the runner writes, so the report and the
app quote one set of numbers. Nothing here is hand-edited.
"""

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path


# Keys whose difference is structural rather than a modelling choice: the case list
# carries per-case ids and seed lists, and the run name and output path identify the
# run rather than describing it.
DEVIATION_SKIP_TOP = ("name", "output", "cases")

# The name carried by config/davey2016.toml. Used only to warn when a non-base run is
# reported without a --baseline to diff against.
BASE_CONFIG_NAME = "davey2016-fig10-3"


def config_deviations(base_cfg, cfg):
    """Every declared difference between two run configurations.

    Returns [(dotted_path, base_value, run_value)]. Input paths are compared by
    basename so that the same file reached through a different relative prefix is
    not reported as a difference. Used to label a sensitivity report with what it
    actually varied: a run that changes an input file or a prior bound enables no
    hypothesis and would otherwise be indistinguishable from the base estimate.
    """
    out = []

    def walk(a, b, path):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in sorted(set(a) | set(b)):
                if not path and k in DEVIATION_SKIP_TOP:
                    continue
                walk(a.get(k), b.get(k), f"{path}.{k}" if path else k)
            return
        if path.startswith("inputs"):
            a = os.path.basename(a) if isinstance(a, str) else a
            b = os.path.basename(b) if isinstance(b, str) else b
        if a != b:
            out.append((path, a, b))

    walk(base_cfg, cfg, "")
    return out


def describe_deviations(cfg, deviations, n_seeds, base_n_seeds):
    """One sentence naming the run and what it varied from the base configuration."""
    def show(v):
        # A key absent from one configuration is not the value None; say so, because a
        # reader cannot otherwise tell "the base set this to null" from "the base never
        # declared it and the default applied".
        return "(not declared)" if v is None else repr(v)

    # The replicate count already states the seed difference, so the seed lists
    # themselves are dropped: they are long and carry nothing extra.
    # "to" rather than an arrow: the report's serif font has no U+2192 glyph, so an
    # arrow renders as a missing-character box in the PDF.
    def clip(t, n=60):
        return t if len(t) <= n else t[:n - 3] + "..."
    hyp_paths = sorted({p.split(".")[1] for p, a, b in deviations if p.startswith("hypotheses.")})
    parts = [f"{p.rsplit('.', 1)[-1]} {clip(show(a))} to {clip(show(b))}"
             for p, a, b in deviations if p != "seeds" and not p.startswith("hypotheses")]
    if hyp_paths:
        parts.append("hypotheses " + ", ".join(hyp_paths))
    if n_seeds != base_n_seeds:
        parts.append(f"replicates {base_n_seeds} to {n_seeds}")
    if not parts:
        return ""
    return f"Sensitivity run {cfg.get('name', '?')!r}, varying " + "; ".join(parts) + "."

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

from matplotlib.colors import LogNorm  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
LAND = HERE / "ne_110m_land.geojson"

sys.path.insert(0, str(HERE))
import epoch_map  # noqa: E402
import parameters  # noqa: E402  (sibling module: the parameter table shared with parameters.csv)

MODES = ["True heading", "Magnetic heading", "True track", "Magnetic track", "Lateral navigation"]
OURS, DAVEY = "#2a78d6", "#eb6834"
MODE_COLOURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
INK, MUTED = "#0b0b0b", "#52514e"
GRID = np.arange(-50.0, 50.0 + 1e-9, 0.05)  # latitude grid, degrees
SMOOTH_DEG = 0.1  # Gaussian display kernel for latitude densities

plt.rcParams.update({
    "font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 9,
    "axes.titlesize": 9.5, "axes.labelsize": 9, "legend.fontsize": 8, "xtick.labelsize": 8,
    "ytick.labelsize": 8, "axes.linewidth": 0.6, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "pdf.fonttype": 42, "lines.linewidth": 1.4,
})
COLUMNS = None  # set from run.json


# Columns kept in memory per replicate (compact dtypes; the tables are memory-mapped on load).
KEEP = {"latitude_deg": np.float32, "longitude_deg": np.float32, "mach": np.float32, "tau_h": np.float32,
        "turns": np.uint8, "accelerations": np.uint8, "mode": np.uint8}


def load_summary(run_dir):
    """The run's display statistics, as written by the runner (crates/mh370/src/summary.rs)."""
    path = run_dir / "summary.json"
    if not path.is_file():
        raise SystemExit(f"{path} is missing; rebuild it with: cargo run --release -- summarise {run_dir}")
    summary = json.loads(path.read_text())
    grid = summary["grid"]
    if grid["points"] != len(GRID) or abs(grid["step"] - (GRID[1] - GRID[0])) > 1e-12 or grid["smoothing_deg"] != SMOOTH_DEG:
        raise SystemExit(f"{path}: latitude grid differs from this report's")
    return summary


def overlap(p, q):
    return float(np.minimum(p, q).sum() * (GRID[1] - GRID[0]))


def load_case(run_dir, case, seeds):
    """One case: per-replicate particles with the pooled weights from summary.json."""
    block = next(c for c in load_summary(run_dir)["cases"] if c["case"] == case)
    if block["seeds"] != list(seeds):
        raise SystemExit(f"{run_dir}/summary.json lists seeds {block['seeds']} for {case}, not {list(seeds)}")
    factors = np.array(block["pool_factors"])
    reps = []
    for i, seed in enumerate(seeds):
        d = run_dir / case / f"seed-{seed}"
        table = np.load(d / "final.npy", mmap_mode="r")
        cols = {k: np.asarray(table[:, COLUMNS.index(k)], dtype=t) for k, t in KEEP.items()}
        # Pool by the mode filter a particle belongs to; runs made before the column have only `mode`.
        stratum = np.asarray(table[:, COLUMNS.index("stratum" if "stratum" in COLUMNS else "mode")], dtype=np.uint8)
        reps.append({"seed": seed, "cols": cols, "routes": np.load(d / "routes.npy"),
                     "diag": json.loads((d / "diagnostics.json").read_text()),
                     "density": np.array(block["replicates"][i]["density"]),
                     "stats": block["replicates"][i]["stats"],
                     "pooled_weight": np.asarray(table[:, 0]) * factors[i][stratum]})
        del table
    return {"reps": reps, "density": np.array(block["density"]), "p_mode": np.array(block["mode_probability"]),
            "stats": block["stats"], "split_half_overlap": block["split_half_overlap"]}


def pooled_hist(case, name, bins):
    """Pooled weighted histogram (probability per bin) of a kept column."""
    return sum(np.histogram(r["cols"][name], bins=bins, weights=r["pooled_weight"])[0] for r in case["reps"])


def pooled_probability(case, name, predicate):
    return float(sum(r["pooled_weight"][predicate(r["cols"][name])].sum() for r in case["reps"]))


def text_block(fig, x, y, text, width=104, size=9, colour=INK, spacing=1.35, **kw):
    """Place wrapped paragraphs; return the y below the block (figure coordinates)."""
    lines = []
    for paragraph in text.strip().split("\n\n"):
        lines += textwrap.wrap(" ".join(paragraph.split()), width) + [""]
    fig.text(x, y, "\n".join(lines[:-1]), va="top", ha="left", fontsize=size, color=colour,
             linespacing=spacing, **kw)
    return y - len(lines) * size * spacing / 72 / fig.get_figheight()


def land_polygons():
    shapes = []
    for feature in json.loads(LAND.read_text())["features"]:
        geom = feature["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        shapes += [np.array(p[0]) for p in polys]
    return shapes


def draw_map(ax, case, routes, arcs, prior, extent):
    for poly in land_polygons():
        ax.fill(poly[:, 0], poly[:, 1], color="#e4e3df", lw=0.4, ec="#b9b8b2", zorder=1)
    for arc in arcs:
        pts = np.array(arc["lat_lon"])
        if len(pts):
            ax.plot(pts[:, 1], pts[:, 0], color="#8a8983", lw=0.5, ls=(0, (4, 3)), zorder=2)
    for r in routes[:: max(1, len(routes) // 400)]:
        ax.plot(r[:, 1], r[:, 0], color=OURS, lw=0.25, alpha=0.18, zorder=3)
    xe = np.arange(extent[0], extent[1] + 0.25, 0.25)
    ye = np.arange(extent[2], extent[3] + 0.25, 0.25)
    h = sum(np.histogram2d(r["cols"]["longitude_deg"], r["cols"]["latitude_deg"], bins=[xe, ye],
                           weights=r["pooled_weight"])[0] for r in case["reps"])
    h = np.ma.masked_less_equal(h / h.sum() / 0.0625, 0)  # probability per square degree
    mesh = ax.pcolormesh(xe, ye, h.T, cmap="Blues", norm=LogNorm(vmin=max(h.max() * 1e-3, 1e-6), vmax=h.max()),
                         zorder=4, rasterized=True)
    ax.plot(prior[1], prior[0], marker="D", ms=4, color=INK, zorder=5)
    ax.set_xlim(extent[:2])
    ax.set_ylim(extent[2:])
    ax.set_aspect(1 / np.cos(np.radians(np.mean(extent[2:]))))
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°)")
    return mesh


def hpd_levels(density, cell_area, fractions):
    """Density thresholds enclosing each requested posterior mass.

    Sorts cells by density and walks down the cumulative mass, so the contour at the returned
    level bounds the smallest region holding that much probability — a highest-posterior-density
    region, not a quantile of either coordinate. Returns one level per fraction, ascending, with
    duplicates nudged apart so `contour` accepts them.
    """
    flat = np.sort(density.ravel())[::-1]
    mass = np.cumsum(flat) * cell_area
    total = mass[-1]
    levels = []
    for f in fractions:
        i = int(np.searchsorted(mass, f * total))
        levels.append(float(flat[min(i, len(flat) - 1)]))
    levels = sorted(levels)
    for i in range(1, len(levels)):
        if levels[i] <= levels[i - 1]:
            levels[i] = levels[i - 1] * (1 + 1e-6) + 1e-30
    return levels


def arc_polyline(arcs, epoch):
    """The reference BTO arc for one epoch as (lon, lat), or None if the run has no such arc."""
    for a in arcs:
        if a["epoch"] == epoch and a.get("lat_lon"):
            pts = np.asarray(a["lat_lon"], dtype=float)
            return pts[:, 1], pts[:, 0]
    return None


def clip_text(s, n):
    """Truncate to `n` characters with an ellipsis, for fixed-width table cells."""
    s = str(s)
    return s if len(s) <= n else s[: n - 1] + "\u2026"


def dm_label(value, axis):
    """Latitude/longitude tick text in the navigation convention: 34.5 -> 34.5°S."""
    if axis == "lat":
        return f"{abs(value):g}°{'S' if value < 0 else 'N'}"
    return f"{abs(value):g}°{'W' if value < 0 else 'E'}"


def run_summary_lines(run_json, case, arc_summary):
    """The right-hand column: what this run did differently, then what it concluded.

    Differences come from the same `parameters.compare` rows as the parameter page, so the two
    cannot disagree; only the rows marked DIFFERS are listed, which is what a reader scanning
    for "how is this not Davey" wants.
    """
    rows = parameters.compare(run_json)
    diff = [r for r in rows if str(r.get("verdict", "")).upper().startswith("DIFFER")]
    lines = [("head", "DIFFERENCES FROM DAVEY")]
    if not diff:
        lines.append(("body", "None: this is the base estimate."))
    for r in diff:
        name = r["parameter"]
        run_v, book_v = str(r["this_run"]), str(r["davey"])
        # Input rows carry a resolved path; the file name is the informative part.
        if "/" in run_v:
            run_v = run_v.rsplit("/", 1)[-1]
        for a, b in ((" standard deviation", " sd"), ("Altitude after a vertical manoeuvre, uniform on", "Altitude range")):
            name = name.replace(a, b)
        lines.append(("item", f"{name}: {clip_text(run_v, 26)}"))
        lines.append(("sub", f"book: {clip_text(book_v, 30)}"))
    lines.append(("gap", ""))
    lines.append(("head", "POSTERIOR AT 00:19"))
    s = case["stats"]
    lines.append(("body", f"median {abs(s['median']):.2f}°S, mode {abs(s['mode']):.2f}°S"))
    lines.append(("body", f"95% {abs(s['q975']):.2f}–{abs(s['q025']):.2f}°S"))
    lines.append(("body", f"replicates {len(case['reps'])}, split-half {case['split_half_overlap']:.3f}"))
    # Largest share of the posterior carried by one prior draw: a sampling diagnostic, not a
    # property of the posterior, and the first thing to check when a region looks lumpy.
    biggest = 0.0
    for r in case["reps"]:
        pw = np.asarray(r["pooled_weight"], dtype=float)
        if pw.sum() > 0:
            biggest = max(biggest, float(pw.max() / pw.sum() / len(case["reps"])))
    lines.append(("body", f"largest single draw {biggest * 100:.2f}% of weight"))
    if arc_summary:
        for f, a in zip(arc_summary["fractions"], arc_summary["area_nm2"]):
            lines.append(("body", f"{int(round(f * 100))}% region {a:,.0f} NM²"))
    return lines


# The right-hand column on the 00:19 close-up page must stop above the caption (which starts at
# y = 0.225), so long "differences" lists no longer run into it.
SIDE_COLUMN_FLOOR = 0.245


def side_column_height(lines):
    """Figure-fraction height the column drawing loop below uses for these lines."""
    h = 0.0
    for kind, text in lines:
        if kind == "gap":
            h += 0.016
            continue
        h += 0.0125 * len(textwrap.wrap(text, 34 if kind != "sub" else 33) or [""])
        h += 0.004 if kind == "sub" else 0.006
    return h


def fit_side_column(lines, top, floor):
    """Shorten the column to fit between `top` and `floor`. First drop the "book:" sub-lines,
    then keep as many difference items as fit and say how many more the parameter page lists.
    The posterior block (from the first "gap") is always kept whole."""
    if side_column_height(lines) <= top - floor:
        return lines
    split = next((i for i, (k, _) in enumerate(lines) if k == "gap"), len(lines))
    head, items, tail = lines[:1], [l for l in lines[1:split] if l[0] != "sub"], lines[split:]
    if side_column_height(head + items + tail) <= top - floor:
        return head + items + [("sub", "book values: see the parameter page")] + tail
    n = len([l for l in items if l[0] == "item"])
    for keep in range(n, -1, -1):
        more = [("sub", f"+ {n - keep} more on the parameter page")]
        trial = head + items[:keep] + more + tail
        if side_column_height(trial) <= top - floor:
            return trial
    return head + more + tail


def page_arc_closeup(pdf, case, arcs, out, run_json=None, bin_deg=0.05, fractions=(0.5, 0.9, 0.95, 0.99)):
    """Close-up of the 00:19 (7th) arc over the region holding 99.9% of the posterior.

    Contours are highest-posterior-density regions of the joint latitude-longitude posterior, so
    the 50% curve bounds the smallest area holding half the probability. Shown as contours rather
    than a pixel mesh because the mesh's visual extent depends on the colour floor, which is a
    plotting choice, whereas an HPD contour is a property of the posterior.
    """
    lon = np.concatenate([np.asarray(r["cols"]["longitude_deg"], dtype=float) for r in case["reps"]])
    lat = np.concatenate([np.asarray(r["cols"]["latitude_deg"], dtype=float) for r in case["reps"]])
    w = np.concatenate([np.asarray(r["pooled_weight"], dtype=float) for r in case["reps"]])
    w = w / w.sum()

    # View: the bounding box of the 99% highest-posterior-density region, not the central 99% of
    # each coordinate. The posterior has a sparse northern tail; a per-coordinate span is
    # stretched by it, which flattens the inner contours into an unreadable sliver. The HPD
    # region drops those low-density cells. Computed on a coarse pass over the full extent, then
    # re-binned on the result.
    cx = np.arange(lon.min() - bin_deg, lon.max() + 2 * bin_deg, bin_deg)
    cy = np.arange(lat.min() - bin_deg, lat.max() + 2 * bin_deg, bin_deg)
    coarse, _, _ = np.histogram2d(lon, lat, bins=[cx, cy], weights=w)
    keep = coarse / (bin_deg * bin_deg) >= hpd_levels(coarse / (bin_deg * bin_deg), bin_deg * bin_deg, [0.99])[0]
    ix, iy = np.where(keep)
    x0, x1 = float(cx[ix.min()]) - bin_deg, float(cx[ix.max() + 1]) + bin_deg
    y0, y1 = float(cy[iy.min()]) - bin_deg, float(cy[iy.max() + 1]) + bin_deg

    xe = np.arange(x0, x1 + bin_deg, bin_deg)
    ye = np.arange(y0, y1 + bin_deg, bin_deg)
    h, _, _ = np.histogram2d(lon, lat, bins=[xe, ye], weights=w)
    cell = bin_deg * bin_deg
    dens = h / cell
    # Light smoothing so the contours describe the posterior rather than the bin lattice. Box
    # kernel over 3x3 bins = 0.15 deg, well inside the posterior's own width.
    k = np.ones((3, 3)) / 9.0
    pad = np.pad(dens, 1, mode="constant")
    sm = sum(k[i, j] * pad[i:i + dens.shape[0], j:j + dens.shape[1]] for i in range(3) for j in range(3))
    sm *= dens.sum() / sm.sum() if sm.sum() > 0 else 1.0

    levels = hpd_levels(sm, cell, fractions)
    xc, yc = (xe[:-1] + xe[1:]) / 2, (ye[:-1] + ye[1:]) / 2

    fig = plt.figure(figsize=(8.27, 11.69))
    ax = fig.add_axes([0.075, 0.545, 0.595, 0.395])
    ax.set_axisbelow(True)
    ax.grid(True, color="#e9e9e6", lw=0.5, zorder=0)
    for poly in land_polygons():
        ax.fill(poly[:, 0], poly[:, 1], color="#ebeae6", lw=0.4, ec="#c3c2bc", zorder=1)
    # Greyscale shading, darkest at the densest region.
    ax.contourf(xc, yc, sm.T, levels=levels + [sm.max() * (1 + 1e-9)],
                colors=["#ededed", "#d2d2d2", "#ababab", "#7d7d7d"], zorder=2)
    cs = ax.contour(xc, yc, sm.T, levels=levels, colors="#3f3f3f", linewidths=[0.6, 0.7, 0.8, 1.0], zorder=3)
    ax.clabel(cs, fmt={lv: f"{int(round(f * 100))}%" for lv, f in zip(levels, sorted(fractions, reverse=True))},
              fontsize=6.5, inline=True, inline_spacing=2)
    med = (float(np.average(lon, weights=w)), float(np.average(lat, weights=w)))
    ax.plot(*med, marker="+", ms=8, mew=1.3, color=INK, zorder=8)
    handles = [Line2D([], [], marker="+", ls="", ms=8, mew=1.3, color=INK, label="Coordinate means")]
    drawn = []
    for epoch, label, style in (("m0011", "6th arc, 00:11", (0, (6, 3))), ("m0019a", "7th arc, 00:19", None)):
        p = arc_polyline(arcs, epoch)
        if p is None:
            continue
        inview = (p[0] >= x0 - 2) & (p[0] <= x1 + 2) & (p[1] >= y0 - 2) & (p[1] <= y1 + 2)
        if inview.sum() < 2:
            continue
        colour = DAVEY if style is None else "#8a8983"
        ax.plot(p[0][inview], p[1][inview], color=colour,
                lw=1.3 if style is None else 1.0, ls=style or "-", zorder=5)
        handles.append(Line2D([], [], color=colour, lw=1.3 if style is None else 1.0,
                              ls=style or "-", label=label))
        drawn.append(label)
    ax.legend(handles=handles, loc="lower left", frameon=True, framealpha=0.9, edgecolor="#c3c2bc",
              fontsize=6.8, labelspacing=0.4, borderpad=0.4)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect(1 / np.cos(np.radians((y0 + y1) / 2)))
    ax.xaxis.set_major_formatter(lambda v, _: dm_label(v, "lon"))
    ax.yaxis.set_major_formatter(lambda v, _: dm_label(v, "lat"))
    ax.tick_params(labelsize=7)
    ax.set_title("a   Position at 00:19 UTC, over the 99% region", loc="left", fontsize=10.5, pad=8)

    area_nm2 = []
    for lv in levels:
        cells = int((sm >= lv).sum())
        area_nm2.append(cells * cell * 3600.0 * float(np.cos(np.radians((y0 + y1) / 2))))

    # Right-hand column: what this run varied and what it concluded.
    if run_json is not None:
        summary = {"fractions": sorted(fractions, reverse=True), "area_nm2": sorted(area_nm2, reverse=True)}
        y = 0.935
        for kind, text in fit_side_column(run_summary_lines(run_json, case, summary), y, SIDE_COLUMN_FLOOR):
            if kind == "gap":
                y -= 0.016
                continue
            size, colour, weight = {
                "head": (8.0, INK, "bold"),
                "item": (7.0, INK, "normal"),
                "sub": (6.4, MUTED, "normal"),
                "body": (7.0, INK, "normal"),
            }[kind]
            x = 0.715 if kind != "sub" else 0.725
            for j, piece in enumerate(textwrap.wrap(text, 34 if kind != "sub" else 33) or [""]):
                fig.text(x if j == 0 else x + 0.01, y, piece, fontsize=size, color=colour,
                         weight=weight, va="top", ha="left")
                y -= 0.0125
            y -= 0.004 if kind == "sub" else 0.006

    # Panel b: the same posterior in arc-relative coordinates. The region is a ribbon roughly
    # 0.3 deg wide and 15 deg long, so on an aspect-true map the inner contours collapse to a
    # line. Plotting east-west offset from the arc against latitude separates the two scales
    # without distorting either.
    arc7 = arc_polyline(arcs, "m0019a") or arc_polyline(arcs, "m0019b")
    panel_b = None
    if arc7 is not None:
        alon, alat = arc7
        order = np.argsort(alat)
        off_nm = (lon - np.interp(lat, alat[order], alon[order])) * 60.0 * np.cos(np.radians(lat))
        inside = (lat >= y0) & (lat <= y1)
        lim = max(4.0, float(np.percentile(np.abs(off_nm[(lat >= y0) & (lat <= y1)]), 99.9)))
        ob, lb = np.linspace(-lim, lim, 101), np.arange(y0, y1 + bin_deg, bin_deg)
        h2, _, _ = np.histogram2d(off_nm[inside], lat[inside], bins=[ob, lb], weights=w[inside])
        cell2 = (ob[1] - ob[0]) * bin_deg
        d2 = h2 / cell2
        pad2 = np.pad(d2, 1, mode="constant")
        s2 = sum(k[i, j] * pad2[i:i + d2.shape[0], j:j + d2.shape[1]] for i in range(3) for j in range(3))
        if s2.sum() > 0:
            s2 *= d2.sum() / s2.sum()
            lv2 = hpd_levels(s2, cell2, fractions)
            ax2 = fig.add_axes([0.075, 0.275, 0.595, 0.195])
            oc, lc = (ob[:-1] + ob[1:]) / 2, (lb[:-1] + lb[1:]) / 2
            ax2.set_axisbelow(True)
            ax2.grid(True, color="#e9e9e6", lw=0.5, zorder=0)
            ax2.contourf(oc, lc, s2.T, levels=lv2 + [s2.max() * (1 + 1e-9)],
                         colors=["#ededed", "#d2d2d2", "#ababab", "#7d7d7d"], zorder=2)
            ax2.contour(oc, lc, s2.T, levels=lv2, colors="#3f3f3f", linewidths=[0.6, 0.7, 0.8, 1.0], zorder=3)
            ax2.axvline(0.0, color=DAVEY, lw=1.2, zorder=4)
            ax2.yaxis.set_major_formatter(lambda v, _: dm_label(v, "lat"))
            ax2.tick_params(labelsize=7)
            ax2.set_xlim(oc.min(), oc.max())
            ax2.set_ylim(y0, y1)
            ax2.set_xlabel("East–west offset from the 00:19 arc at the same latitude (NM)")
            ax2.set_ylabel("Latitude (°)")
            ax2.set_title("b   The same posterior, measured from the arc", loc="left", fontsize=10.5, pad=6)
            panel_b = {"levels": lv2, "offset_nm_p95": float(np.percentile(np.abs(off_nm[inside]), 95))}

    shown = ", ".join(f"{int(round(f*100))}% {a:,.0f}" for f, a in
                      zip(sorted(fractions, reverse=True), area_nm2))
    text_block(fig, 0.075, 0.225, f"""
        Figure 3. Joint latitude-longitude posterior at 00:19 UTC, drawn as highest-posterior-density
        regions: the {int(round(min(fractions)*100))}% curve bounds the smallest area holding
        {int(round(min(fractions)*100))}% of the probability, and so on outward, so a region here
        is the smallest place to look for that confidence rather than an interval in either
        coordinate alone. Binned at {bin_deg:g}° and smoothed over three bins. Panel a spans the
        bounding box of the 99% region, so sparse outlying cells are excluded; enclosed areas
        (NM², at the view's mean latitude) are {shown}. Panel b replots the same particles against
        their east-west offset from the 00:19 arc, because the region is about 0.3° wide and
        {y1 - y0:.0f}° long and the inner contours are not separable at a true aspect ratio.
        {'Arcs are the reference BTO loci at 35,000 ft; 00:19 is the 7th.' if drawn else ''}
        Land: Natural Earth 1:110m.""", size=8, colour=MUTED, width=128)
    save_page(pdf, fig, out)
    plt.close(fig)
    return {"view": [x0, x1, y0, y1], "levels": levels, "area_nm2": area_nm2, "panel_b": panel_b}


def page_parameters(pdf, run_json, out):
    """Every parameter and model choice beside Davey et al. (2016), differences marked.

    Rows come from report/davey_reference.json via report/parameters.py, so the page and the
    run's parameters.csv cannot disagree. Long prose is truncated here; the CSV carries the full
    text, the book citation and the note for each row.
    """
    rows = parameters.compare(run_json)
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.text(0.06, 0.955, "Parameters and model choices against Davey et al. (2016)",
             fontsize=13, weight="bold", color=INK, va="top")
    n_diff = sum(r["verdict"] == "DIFFERS" for r in rows)
    text_block(fig, 0.06, 0.928,
               f"{len(rows)} parameters and choices. {len(rows) - n_diff} match the published "
               f"model; {n_diff} differ and are marked. A difference is not by itself a defect: "
               "some are deliberate and documented (ERA5 for the unavailable ACCESS-G, IGRF-14 "
               "for NOAA, the sampler), some are the subject of the run (a widened Mach range), "
               "and some are worth fixing. Page numbers refer to the book; the full table with "
               "citations and notes is written beside this report as parameters.csv.",
               width=112, size=8, colour=MUTED)

    x = {"mark": 0.055, "name": 0.075, "run": 0.395, "book": 0.655}
    y, dy = 0.845, 0.0138
    header = {"name": "Parameter", "run": "This run", "book": "Davey et al. (2016)"}
    for key, label in header.items():
        fig.text(x[key], y, label, fontsize=7.5, weight="bold", color=INK, va="top")
    y -= dy * 1.1
    fig.lines.append(plt.Line2D([0.055, 0.945], [y + dy * 0.45] * 2, color=MUTED, lw=0.5,
                                transform=fig.transFigure))
    y -= dy * 0.35

    def clip(text, n):
        text = text or "-"
        return text if len(text) <= n else text[: n - 1].rstrip() + "…"

    area = None
    for r in rows:
        if r["area"] != area:
            area = r["area"]
            y -= dy * 0.55
            fig.text(x["mark"], y, area, fontsize=7.5, weight="bold", color=OURS, va="top")
            y -= dy
        differs = r["verdict"] == "DIFFERS"
        colour = DAVEY if differs else INK
        if differs:
            fig.text(x["mark"], y, "▸", fontsize=6, color=DAVEY, va="top")
        unit = f" ({r['unit']})" if r["unit"] else ""
        fig.text(x["name"], y, clip(r["parameter"] + unit, 52), fontsize=6.4, color=colour, va="top")
        fig.text(x["run"], y, clip(r["this_run"], 40), fontsize=6.4, color=colour, va="top")
        fig.text(x["book"], y, clip(r["davey"], 44), fontsize=6.4, color=colour, va="top")
        y -= dy

    text_block(fig, 0.06, y - dy,
               "▸ marks a difference. Rows whose value is prose or a file identifier cannot be "
               "compared by string match; for those the reference file asserts the relationship "
               "explicitly and parameters.csv records why. Quantities held per epoch rather than "
               "per run — the BTO and BFO measurement standard deviations — are in "
               "data/satcom-observations.csv and are compared in the note column of the CSV.",
               width=112, size=7, colour=MUTED)
    save_page(pdf, fig, out)
    plt.close(fig)


def added_evidence(run_json):
    """What this run adds beyond the satellite data, read from its own configuration (not assumed)."""
    cfg = (run_json or {}).get("config", {})
    added = []
    hyps = cfg.get("hypotheses") or {}
    if "radar-fix" in hyps:
        added.append("primary-radar positions and track segments 18:04-18:22 scored as measurements")
    for name in sorted(hyps):
        if name != "radar-fix":
            added.append(f"hypothesis overlay '{name}'")
    f = cfg.get("fuel")
    if f:
        bits = [f"fuel model {f.get('model') or 'tables'}"]
        if f.get("tanks") == 2:
            bits.append("two tanks")
        if f.get("single_engine"):
            bits.append(f"one-engine flight after the first flame-out ({f.get('single_engine_profile') or 'constant'} drift-down)")
        if f.get("hard_reject"):
            bits.append("paths dry before 00:11 rejected")
        added.append(", ".join(bits))
    return added


def evidence_sentence(run_json):
    added = added_evidence(run_json)
    if not added:
        return "No fuel, debris, drift, search or end-of-flight evidence is used."
    return "This run also uses: " + "; ".join(added) + ". No debris, drift, search or end-of-flight evidence is used."


def save_page(pdf, fig, out):
    """Each page goes to the PDF and, for viewers that cannot open PDFs, to <out>-png/page-<n>.png.
    With REPORT_FOOTNOTE set, every page carries it at the foot (run, platform, stack, labels)."""
    foot = os.environ.get("REPORT_FOOTNOTE", "").strip()
    if foot:
        # Squeeze the page's content into the top (1 - band) so the footnote never overlaps it.
        lines = [l for para in foot.split("\n\n") for l in textwrap.wrap(para, 190)]
        band = (0.34 + 0.095 * len(lines)) / fig.get_size_inches()[1]  # physical height, whatever the page size
        for ax in fig.axes:
            p = ax.get_position()
            ax.set_position([p.x0, band + p.y0 * (1 - band), p.width, p.height * (1 - band)])
        for t in fig.texts:
            x, y = t.get_position()
            t.set_position((x, band + y * (1 - band)))
        fig.text(0.06, 0.04 / fig.get_size_inches()[1], "\n".join(lines), fontsize=5.4, color="#6b6b6b", va="bottom", ha="left")
    pdf.savefig(fig)
    pages = Path(out).parent / f"{Path(out).stem}-png"
    pages.mkdir(exist_ok=True)
    fig.savefig(pages / f"page-{pdf.get_pagecount()}.png", dpi=100)


def main():
    global COLUMNS
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--baseline", type=Path, help="base-estimate run to overlay")
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    out = args.output or run_dir / "report.pdf"
    run = json.loads((run_dir / "run.json").read_text())
    hyps = run.get("hypotheses", [])
    def _short(v, n=48):
        t = str(v)
        return t if len(t) <= n else t[:n - 3] + "..."
    hyp_text = "; ".join(f"{h['name']} ({', '.join(f'{k} = {_short(v)}' for k, v in h['parameters'].items())})" for h in hyps)
    if len(hyp_text) > 120:  # long parameter lists (radar fixes, waypoint tables) name only
        hyp_text = "; ".join(h["name"] for h in hyps) + " (parameters in run.json)"
    wind_scale = run["config"].get("environment", {}).get("wind_scale", 1.0)
    sensitivity = wind_scale != 1.0
    COLUMNS = run["final_columns"]
    cfg = run["config"]
    case_seeds = {c["id"]: c.get("seeds") or cfg["seeds"] for c in cfg["cases"]}
    # The run's primary case. `bto-bfo` for the base estimate and most sensitivities, but the
    # evidence-ladder rungs name their own case after the measurements they admit ("fuel-only",
    # "bto"), so the id is taken from the configuration rather than assumed. The secondary
    # BTO-only panel is drawn only when a run actually carries that case.
    primary = "bto-bfo" if "bto-bfo" in case_seeds else cfg["cases"][0]["id"]
    seeds = case_seeds[primary]
    cases = {c: load_case(run_dir, c, s) for c, s in case_seeds.items()}
    bfo, bto = cases[primary], cases.get("bto-only")
    base = None
    base_cfg = None
    base_seeds = None
    if args.baseline:
        base_run = json.loads((args.baseline / "run.json").read_text())
        base_cfg = base_run["config"]
        base_primary = "bto-bfo" if any(c["id"] == "bto-bfo" for c in base_cfg["cases"]) else base_cfg["cases"][0]["id"]
        base_seeds = next(c.get("seeds") or base_cfg["seeds"] for c in base_cfg["cases"] if c["id"] == base_primary)
        base = load_case(args.baseline.resolve(), base_primary, base_seeds)

    # What this run varied. A run that changes an input file or a prior bound enables
    # no hypothesis and leaves wind_scale at 1, so neither of those flags alone can
    # tell a sensitivity run from the base estimate; the configuration diff can.
    deviations = config_deviations(base_cfg, cfg) if base_cfg else []
    dev_text = describe_deviations(cfg, deviations, len(seeds), len(base_seeds or seeds)) if base_cfg else ""
    unlabelled = not args.baseline and cfg.get("name") != BASE_CONFIG_NAME
    conditions = " ".join(filter(None, [
        f"Hypotheses enabled: {hyp_text}." if hyps else "",
        f"Sensitivity run: nominal ERA5 wind scaled by {wind_scale:g} (wind-error process kept)." if sensitivity else "",
        dev_text,
        (f"Run {cfg.get('name', '?')!r} is not the base configuration, but no --baseline was given, "
         "so the differences from it are not stated here.") if unlabelled else "",
    ])) or "Base estimate: no hypotheses enabled."
    if "stratum" not in run["final_columns"]:
        conditions += (" Pooled by final autopilot mode (run predates the stratum column; biased for "
                       "lateral-navigation paths that reverted to heading hold).")
    variant = bool(hyps) or sensitivity or bool(deviations) or unlabelled
    reference = load_summary(run_dir).get("reference")
    if not reference:
        raise SystemExit(f"{run_dir}/summary.json has no published comparison curve; rebuild it with: "
                         f"cargo run --release -- summarise {run_dir}")
    davey = np.array(reference["density"])
    s_dav = reference["stats"]
    s_ours = bfo["stats"]
    ov = overlap(bfo["density"], davey)
    rep_ov = [overlap(r["density"], davey) for r in bfo["reps"]]
    rep_med = [r["stats"]["median"] for r in bfo["reps"]]
    pairwise = [overlap(a["density"], b["density"]) for i, a in enumerate(bfo["reps"]) for b in bfo["reps"][i + 1:]]
    # `summary.json`'s `split_half_overlap` is the engine's SINGLE first-half-against-second-half
    # value, and it is noisy: at eight replicates it is one draw from 35 balanced partitions whose
    # range can span 0.13. Quoting it against a flat 0.90 has reported runs as converged that the
    # project's own statistic fails. Use the all-partition mean against the replicate-count
    # calibrated floor, which is what `report/model_comparison.py` and `results/
    # split-half-threshold.md` define as the verdict.
    from model_comparison import SPLIT_HALF_FLOOR, split_half_all
    n_reps = len(bfo["reps"])
    sh_all = split_half_all([np.asarray(r["density"]) for r in bfo["reps"]], GRID[1] - GRID[0])
    if sh_all is None:                      # odd replicate count: no balanced partition exists
        sh_all = {"mean": bfo["split_half_overlap"], "min": bfo["split_half_overlap"],
                  "max": bfo["split_half_overlap"], "n_partitions": 1}
    split, split_lo, split_hi = sh_all["mean"], sh_all["min"], sh_all["max"]
    floor = SPLIT_HALF_FLOOR.get(n_reps)
    verdict = floor is None or split >= floor
    against = f" against the {n_reps}-replicate floor of {floor:.3f}" if floor is not None else ""
    stability = (f". Over all balanced partitions of the {n_reps} replicates the split-half overlap averages "
                 f"{split:.1%} (range {split_lo:.1%} to {split_hi:.1%}){against}, so the pooled curve does not "
                 "depend materially on the random seed" if verdict else
                 f". Over all balanced partitions of the {n_reps} replicates the split-half overlap averages only "
                 f"{split:.1%} (range {split_lo:.1%} to {split_hi:.1%}){against}, so the pooled curve is NOT "
                 "converged at this particle count and quantities read off it carry that caveat")
    shoulder = (GRID > -36.5) & (GRID < -34.5)
    shoulder_ours = float(bfo["density"][shoulder].sum() * (GRID[1] - GRID[0]))
    shoulder_dav = float(davey[shoulder].sum() * (GRID[1] - GRID[0]))
    p_tau1 = pooled_probability(bfo, "tau_h", lambda x: x > 1)
    p_tau2 = pooled_probability(bfo, "tau_h", lambda x: x > 2)
    mach_edges = np.linspace(0.73, 0.84, 441)
    mach_cdf = np.cumsum(pooled_hist(bfo, "mach", mach_edges))
    mach_med = float(np.interp(0.5 * mach_cdf[-1], mach_cdf, mach_edges[1:]))
    p_north_bto = pooled_probability(bto, "latitude_deg", lambda x: x > 0) if bto else float("nan")
    north_mode = float(GRID[GRID > 0][np.argmax(bto["density"][GRID > 0])]) if bto else float("nan")
    mode_prob = np.array([[m["posterior_probability"] for m in r["diag"]["modes"]] for r in bfo["reps"]])
    pooled_mode_prob = bfo["p_mode"]
    n_total = sum(cfg["particles_per_mode"])
    reproduce = f"make hypothesis H={hyps[0]['name']}" if len(hyps) == 1 else "make report"
    persist_text = ("" if variant else " The difference persists at every particle count tried, so it reflects inputs the book "
                    "does not publish (ACCESS-G weather, the numerical radar prior, autopilot-mode weights) rather than "
                    "sampling noise.")
    base_text = ""
    if base:
        s_base = base["stats"]
        shoulder_base = float(base["density"][shoulder].sum() * (GRID[1] - GRID[0]))
        shift = s_ours["median"] - s_base["median"]
        base_text = (f"\n\nRelative to {os.environ.get('BASELINE_NAME', 'the base estimate')}, the median moves {abs(shift):.2f}° "
                     f"{'north' if shift > 0 else 'south'}, the 34.5–36.5°S shoulder holds {shoulder_ours:.0%} of probability "
                     f"(base {shoulder_base:.0%}), and the two curves overlap by {overlap(bfo['density'], base['density']):.0%}.")
    bto_text = ("" if not bto else
                f" Without BFO the pdf is bimodal: {p_north_bto:.0%} of probability lies in a narrow northern mode centred at "
                f"{north_mode:.1f}°N, matching the narrow mode near 45°N in the book's BTO-only panel (read from the figure, "
                "not digitised). The BFO removes the northern mode, as reported by Davey et al.")
    runtime_min = run["runtime_s"] / 60
    # Older runs, and runs made where the platform reports no high-water mark, carry a null here.
    # The manifest line states that rather than failing to format it.
    peak_memory = (f"{run['peak_memory_mib']:,.0f} MiB" if run.get("peak_memory_mib") is not None
                   else "not recorded by this run")
    prior = (cfg["prior"]["latitude_deg"], cfg["prior"]["longitude_deg"])

    with PdfPages(out, metadata={"Title": "MH370 aircraft position pdf at 00:19 UTC: a reproduction of Davey et al. (2016)",
                                 "Subject": f"run {cfg['name']}, code {run['code_revision']}"}) as pdf:
        # Page 1: headline result.
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.08, 0.955, "Where was MH370 at 00:19 UTC?", fontsize=17, weight="bold", color=INK)
        fig.text(0.08, 0.932, "A reproduction of the DSTG Bayesian aircraft-position pdf (Davey et al. 2016, Fig. 10.3)",
                 fontsize=11, color=MUTED)
        # Wrapped: a deviation list naming two or three configuration keys overruns one
        # line at this font size, and an unwrapped fig.text is clipped at the figure edge
        # rather than shrunk, which silently truncates what the run actually varied. The
        # body below starts one line lower per extra subtitle line, so a long deviation
        # list pushes the text down instead of overprinting it.
        # REPORT_WHAT: one plain-language (ASD-STE100) statement of what this run is, so the reader
        # does not have to decode the configuration. The technical conditions follow in smaller type.
        what = os.environ.get("REPORT_WHAT", "").strip()
        y0 = 0.920
        if what:
            what_lines = textwrap.wrap(what, 100)
            fig.text(0.08, y0, "\n".join(what_lines), fontsize=9.5, va="top", linespacing=1.35, color=INK, weight="bold")
            y0 -= 0.0145 * len(what_lines) + 0.006
            c_size, c_wrap, c_spacing, c_step = 8, 130, 1.3, 0.0125
        else:
            c_size, c_wrap, c_spacing, c_step = 9, 112, 1.5, 0.0155
        if what:
            # The technical conditions are already on page 7 ("Run.") and in the technical footnote.
            start = y0 - 0.008
        else:
            cond_lines = textwrap.wrap(conditions, c_wrap) or [""]
            fig.text(0.08, y0, "\n".join(cond_lines), fontsize=c_size, va="top",
                     linespacing=c_spacing, color=INK if variant else MUTED, style="italic")
            start = y0 - 0.027 - c_step * (len(cond_lines) - 1)
        y = text_block(fig, 0.08, start, f"""
            This report recreates the probability density function (pdf) of the aircraft's latitude at the final
            satellite handshake, 00:19 UTC on 8 March 2014, from the model published by Davey, Gordon, Holland,
            Rutten and Williams, Bayesian Methods in the Search for MH370 (Springer, 2016). The aircraft state is
            filtered from the penultimate radar point at 18:01:49 UTC through all Inmarsat burst timing (BTO) and
            burst frequency (BFO) measurements, using the published cruise, manoeuvre and measurement models.

            With BTO and BFO the recreated pdf has median {-s_ours['median']:.2f}°S and mode {-s_ours['mode']:.2f}°S,
            with 95% of probability between {-s_ours['q975']:.2f}°S and {-s_ours['q025']:.2f}°S. The published curve has
            median {-s_dav['median']:.2f}°S, mode {-s_dav['mode']:.2f}°S and 95% range {-s_dav['q975']:.2f}–{-s_dav['q025']:.2f}°S.
            The two densities overlap by {ov:.0%}. This curve is centred {abs(s_ours['median'] - s_dav['median']):.1f}°
            further {'south' if s_ours['median'] < s_dav['median'] else 'north'} and carries {shoulder_ours:.0%} of
            probability in the published northern shoulder between 34.5°S and 36.5°S ({shoulder_dav:.0%} in the book).
            {persist_text}{bto_text}{base_text}

            The curve pools {len(seeds)} independent replicates of {n_total:,} particles. Single replicates
            overlap each other by {min(pairwise):.0%}–{max(pairwise):.0%} and their medians span
            {max(rep_med) - min(rep_med):.2f}°{stability}.""")
        # Panel (a) takes whatever height the text leaves above panel (b).
        ax1 = fig.add_axes([0.11, 0.425, 0.82, max(0.08, min(0.15, y - 0.04 - 0.425))])
        ax2 = fig.add_axes([0.11, 0.15, 0.82, 0.2])
        if bto:
            for r in bto["reps"]:
                ax1.plot(GRID, r["density"], color=OURS, lw=0.5, alpha=0.45)
            ax1.plot(GRID, bto["density"], color=OURS, label="This recreation (pooled)")
            ax1.set_title("(a) BTO only (no BFO): the arcs alone admit northern and southern routes", loc="left", color=INK)
        else:
            ax1.text(0.5, 0.5, "BTO-only case not run in this configuration", transform=ax1.transAxes,
                     ha="center", va="center", color=MUTED)
            ax1.set_title("(a) BTO only (no BFO)", loc="left", color=INK)
        ax1.set_xlim(-50, 50)
        ax1.set_xlabel("Latitude at 00:19 UTC (°, north positive)")
        for r in bfo["reps"]:
            ax2.plot(GRID, r["density"], color=OURS, lw=0.5, alpha=0.45)
        ax2.plot(GRID, bfo["density"], color=OURS, label=f"This recreation, pooled over {len(seeds)} replicates (thin: each)")
        ax2.plot(GRID, davey, color=DAVEY, ls=(0, (5, 2)), label="Davey et al. (2016) Fig. 10.3, digitised")
        if base:
            ax2.plot(GRID, base["density"], color=MUTED, ls=(0, (1, 1.5)), lw=1.2, label=os.environ.get("BASELINE_LABEL", "Base estimate (no hypotheses)"))
        ax2.set_title("(b) BTO and BFO, compared with the published curve (note expanded scale)", loc="left", color=INK)
        ax2.legend(loc="upper right")
        for ax in (ax1, ax2):
            ax.set_ylabel("Probability density (per degree)")
            ax.set_ylim(bottom=0)
            ax.grid(axis="y", color="#e9e8e4", lw=0.5)
        ax2.set_xlim(-42, -32)
        # Finer latitude ticks (1 deg labelled, 0.25 deg minor) with faint vertical grid lines.
        from matplotlib.ticker import MultipleLocator
        ax2.xaxis.set_major_locator(MultipleLocator(1.0))
        ax2.xaxis.set_minor_locator(MultipleLocator(0.25))
        ax2.tick_params(axis="x", which="minor", length=2.5, width=0.5)
        ax2.set_axisbelow(True)
        ax2.grid(axis="x", which="major", color="#e4e3df", lw=0.55)
        ax2.grid(axis="x", which="minor", color="#f1f0ec", lw=0.45)
        ax2.set_xlabel("Latitude at 00:19 UTC (°)")
        text_block(fig, 0.08, 0.085, f"""
            Figure 1. Latitude pdf of the aircraft at 00:19:37 UTC, the form of Davey et al. Fig. 10.3. (a) BTO only.
            (b) BTO and BFO, with the published curve. Densities are weighted particle histograms smoothed with a {SMOOTH_DEG}° Gaussian;
            each particle carries its own altitude. Evidence: BTO at every epoch except the 18:39 and 23:15 C-channel
            calls; BFO (bottom only) at 18:28, 18:39, 19:41–22:41, 23:15 and 00:11. {evidence_sentence(run)} {conditions if len(conditions) < 160 else "Run conditions as stated at the top of this page."}""", size=8, colour=MUTED, width=128)
        save_page(pdf, fig, out)
        plt.close(fig)

        # Page 2: map.
        fig = plt.figure(figsize=(8.27, 11.69))
        ax = fig.add_axes([0.08, 0.27, 0.78, 0.69])
        mesh = draw_map(ax, bfo, bfo["reps"][0]["routes"], run["reference_arcs"], prior, (76, 110, -44, 12))
        cax = fig.add_axes([0.80, 0.42, 0.014, 0.4])
        cb = fig.colorbar(mesh, cax=cax)
        cb.set_label("Probability per square degree at 00:19")
        cb.outline.set_linewidth(0.4)
        ax.text(prior[1] + 0.6, prior[0] + 0.4, "18:01:49 radar prior", fontsize=8, color=INK)
        text_block(fig, 0.08, 0.205, f"""
            Figure 2. Posterior aircraft position at 00:19 UTC with BTO and BFO, pooled over {len(seeds)} replicates
            (blue shading, logarithmic), and {min(400, len(bfo['reps'][0]['routes']))} routes drawn in proportion to
            posterior weight from replicate seed {seeds[0]} (thin lines, 10-minute vertices). Dashed grey curves are
            the BTO arcs at a reference altitude of 35,000 ft; they are drawn for orientation only. Land: Natural
            Earth 1:110m.""", size=8, colour=MUTED, width=128)
        save_page(pdf, fig, out)
        plt.close(fig)

        # Page 3: close-up of the 7th arc, as credible regions rather than a pixel mesh.
        arc_summary = page_arc_closeup(pdf, bfo, run["reference_arcs"], out, run_json=run)

        # Position maps at the sixth and seventh arcs: where the aircraft is on latitude and
        # longitude axes, as credible regions rather than the latitude marginal the rest of
        # the report works in. Drawn for every run so the two views are always side by side.
        for epoch_id in ("m0011", "m0019a"):
            try:
                fig = epoch_map.figure(run_dir, epoch_id, primary, figsize=(8.27, 7.6))
                save_page(pdf, fig, out)
            except SystemExit as exc:
                print(f"  position map {epoch_id}: skipped ({exc})")

        # Page 4: posterior checks against the book.
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.08, 0.955, "Posterior behaviour compared with the book", fontsize=13, weight="bold", color=INK)
        axes = [fig.add_axes(r) for r in ([0.1, 0.70, 0.36, 0.2], [0.58, 0.70, 0.36, 0.2],
                                           [0.1, 0.42, 0.36, 0.2], [0.58, 0.42, 0.36, 0.2])]
        a = axes[0]
        edges = np.linspace(0.73, 0.84, 23)
        a.hist(edges[:-1], bins=edges, weights=pooled_hist(bfo, "mach", edges), density=True, color=OURS,
               rwidth=0.9, label="Posterior")
        a.axhline(1 / 0.11, color=MUTED, ls=(0, (4, 2)), lw=0.8, label="Prior (uniform)")
        a.set_xlabel("Mach set point at 00:19")
        a.set_ylabel("Density")
        a.set_title("(a) Speed: book reports a preference for high Mach", loc="left")
        a.legend(loc="upper left")
        a = axes[1]
        bins = np.arange(0, 10.01, 0.25)
        a.hist(bins[:-1], bins=bins, weights=pooled_hist(bfo, "tau_h", bins), density=True, color=OURS, rwidth=0.9,
               label="Posterior")
        g = np.linspace(0.1, 10, 300)
        a.plot(g, 1 / (g * np.log(100)), color=MUTED, ls=(0, (4, 2)), lw=0.8, label="Jeffreys prior")
        a.set_xlabel("Mean time between manoeuvres τ (h)")
        a.set_title(f"(b) τ > 1 h: {p_tau1:.0%} (book 97%); > 2 h: {p_tau2:.0%} (book 83%)", loc="left")
        a.legend(loc="upper right")
        a = axes[2]
        k = np.arange(0, 7)
        for off, name, col in ((-0.2, "turns", OURS), (0.2, "accelerations", "#1baf7a")):
            counts = pooled_hist(bfo, name, np.arange(-0.5, 7.5, 1.0))
            a.bar(k + off, counts, width=0.38, color=col, label=name.capitalize())
        a.set_xlabel("Number of manoeuvres, 18:01–00:19")
        a.set_ylabel("Posterior probability")
        a.set_title("(c) Manoeuvre counts (cf. book Fig. 10.4)", loc="left")
        a.legend(loc="upper right")
        a = axes[3]
        x = np.arange(len(MODES))
        for j, r in enumerate(mode_prob):
            a.scatter(x + (j - (len(mode_prob) - 1) / 2) * 0.08, r, s=12, color=OURS, zorder=3)
        a.bar(x, pooled_mode_prob, width=0.6, color="#cfe0f5", zorder=2)
        a.set_xticks(x, [m.replace(" ", "\n") for m in MODES], fontsize=7.5)
        a.set_ylabel("Posterior probability")
        a.set_title("(d) Autopilot mode (bars: pooled; dots: replicates)", loc="left")
        rows = [("", "This recreation", "Davey et al. (2016)"),
                ("Median latitude", f"{-s_ours['median']:.2f}°S", f"{-s_dav['median']:.2f}°S"),
                ("Mode", f"{-s_ours['mode']:.2f}°S", f"{-s_dav['mode']:.2f}°S"),
                ("95% interval", f"{-s_ours['q975']:.2f}–{-s_ours['q025']:.2f}°S", f"{-s_dav['q975']:.2f}–{-s_dav['q025']:.2f}°S"),
                ("95% width", f"{s_ours['q975'] - s_ours['q025']:.2f}°", f"{s_dav['q975'] - s_dav['q025']:.2f}°"),
                ("Overlap with published pdf", f"{ov:.0%} (replicates {min(rep_ov):.0%}–{max(rep_ov):.0%})", "—"),
                ("Median Mach at 00:19", f"{mach_med:.3f}", "upper part of 0.73–0.84"),
                ("P(north of equator), BTO only", f"{p_north_bto:.0%}" if bto else "not run", "northern mode present")]
        tab = fig.add_axes([0.08, 0.17, 0.84, 0.18])
        tab.axis("off")
        for i, row in enumerate(rows):
            yy = 1 - i / len(rows)
            for xx, cell in zip((0.0, 0.42, 0.74), row):
                tab.text(xx, yy, cell, fontsize=8.5, color=INK if i else MUTED, weight="bold" if i == 0 else "normal",
                         va="top")
            if i in (0, len(rows) - 1):
                tab.axhline(yy - 0.1 if i == 0 else yy - 0.12, color=MUTED, lw=0.5)
        text_block(fig, 0.08, 0.14, """
            Figure 3 and Table 1. Posterior summaries with BTO and BFO, pooled over replicates, alongside the
            statements in Davey et al. (2016), sec. 10.2–10.4. Book values of the latitude pdf come from the
            digitised Fig. 10.3 (bottom); other book values are quoted from the text.""", size=8, colour=MUTED, width=128)
        save_page(pdf, fig, out)
        plt.close(fig)

        # Page 5: method, convergence and reproduction.
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.08, 0.955, "Method, convergence and reproduction", fontsize=13, weight="bold", color=INK)
        ax = fig.add_axes([0.1, 0.70, 0.36, 0.2])
        epochs = [e["epoch"] for e in bfo["reps"][0]["diag"]["modes"][0]["epochs"]]
        for m, colour in enumerate(MODE_COLOURS):
            ess = np.mean([[e["ess_after_update"] for e in r["diag"]["modes"][m]["epochs"]] for r in bfo["reps"]], axis=0)
            ax.plot(range(len(epochs)), ess / cfg["particles_per_mode"][m], color=colour, marker="o", ms=2.5, lw=1,
                    label=MODES[m])
        ax.set_yscale("log")
        ax.set_xticks(range(len(epochs)), [e[1:3] + ":" + e[3:5] for e in epochs], rotation=90, fontsize=7)
        ax.set_ylabel("ESS / particles after update")
        ax.set_title("(a) Effective sample size by epoch", loc="left")
        ax.legend(fontsize=6.5, loc="lower left")
        ax = fig.add_axes([0.58, 0.70, 0.36, 0.2])
        step = GRID[1] - GRID[0]
        for r in bfo["reps"]:
            ax.plot(GRID, np.cumsum(r["density"]) * step, color=OURS, lw=0.8)
        ax.plot(GRID, np.cumsum(davey) * step, color=DAVEY, ls=(0, (5, 2)), lw=1.0)
        ax.set_xlim(-41, -32)
        ax.set_xlabel("Latitude at 00:19 (°)")
        ax.set_ylabel("Cumulative probability")
        ax.set_title("(b) Replicate CDFs (blue) and book (orange, dashed)", loc="left")
        diffs = [np.max(np.abs(np.cumsum(a["density"] - b["density"]) * step))
                 for i, a in enumerate(bfo["reps"]) for b in bfo["reps"][i + 1:]]
        text_block(fig, 0.08, 0.62, f"""
            Figure 4. (a) Effective sample size after each measurement update, averaged over replicates, per
            autopilot-mode filter. The narrowest bottlenecks are the 18:39 C-channel BFO (the southward turn) and the
            19:41 BTO arc. (b) Latitude CDFs of the {len(seeds)} independent replicates; the largest
            difference between any two is {max(diffs):.3f} (Kolmogorov distance).""", size=8, colour=MUTED, width=128)
        y = text_block(fig, 0.08, 0.53, f"""
            Model. The state, dynamics and likelihood follow Davey et al. (2016) chapters 4–8: prior at 18:01:49 UTC
            with 0.5 NM position and 1° track uncertainty, Mach uniform on 0.73–0.84, altitude on 1,000 ft levels
            from 25,000 to 43,000 ft; five autopilot modes (true/magnetic heading, true/magnetic track, lateral
            navigation with a one-off reversion to heading hold); Ornstein–Uhlenbeck fluctuations of Mach, control
            angle and wind error with the published rates; turns, speed changes and climbs arriving with exponential
            gaps of common mean τ (Jeffreys prior on 0.1–10 h) at 15° bank, 0.1 Mach per minute and 4,000 ft per
            minute. BTO is Gaussian with the tabulated per-message errors (29, 43 or 63 µs); BFO has 7 Hz noise and
            an unknown constant bias (prior 150 ± 25 Hz) marginalised exactly per particle with a Kalman filter.

            Substitutions. The book's ACCESS-G weather is replaced by ERA5 winds and temperatures; magnetic
            declination is IGRF-14. The prior mean position and track are reconstructed from the book's radar
            figures because they are not tabulated. Davey et al. used variable-rate branching; this recreation uses
            fixed-size particle filters with systematic resampling when ESS falls below
            {cfg['resample_ess_fraction']:.0%} of the particles. The book warns that conventional resampling
            collapses static parameters (sec. 10.4). Both are therefore handled exactly: one filter per autopilot
            mode, combined in proportion to its estimated marginal likelihood, and a Gibbs refresh of τ from its path
            conditional after every resampling step. Without them, a plain bootstrap filter of one million
            particles retained only about one hundred distinct prior draws, and an earlier recreation in this
            project found tails and turn counts that changed with the random seed.

            Run. Configuration {cfg['name']}; particles per mode {', '.join(f"{n:,}" for n in cfg['particles_per_mode'])}
            (order as in Figure 3d), {n_total:,} per replicate; BTO+BFO seeds {', '.join(map(str, seeds))}; BTO-only
            seeds {', '.join(map(str, case_seeds.get('bto-only', [])))}; code revision {run['code_revision']}; {run['threads']} threads;
            total runtime {runtime_min:.1f} min; peak memory {peak_memory}. {conditions}

            Reproduce with one command from the repository root:  {reproduce}""", size=8.5, width=118)
        save_page(pdf, fig, out)
        plt.close(fig)

        # Page 6: parameters and model choices against the book. Written for every run, and
        # emitted beside the report as parameters.csv so the paper can cite the same rows.
        page_parameters(pdf, run, out)
        parameters.write_csv(run_dir / "parameters.csv", parameters.compare(run))
    print(out)


if __name__ == "__main__":
    main()
