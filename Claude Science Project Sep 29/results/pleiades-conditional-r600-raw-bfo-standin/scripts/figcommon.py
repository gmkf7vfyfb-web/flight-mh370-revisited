"""Shared figure helpers for the stand-in note: Pléiades house elements (closeup_styles / closeup_figure, imported
read-only) and Pete's two-version footnote (STE100 + technical, together at most the bottom 25 % of the image)."""
import json
import sys
import textwrap
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

WS = Path(__file__).resolve().parents[1]
PREP = WS / "repo" / "Claude Science Project Sep 29" / "engine" / "hypotheses" / "pleiades" / "prepare"
sys.path.insert(0, str(PREP))
import closeup_figure as cf  # noqa: E402
import closeup_styles as cs  # noqa: E402
from branch_figure import hdr_level  # noqa: E402

GEO = json.loads((WS / "geom" / "search_footprints.geojson").read_text())
import pandas as pd  # noqa: E402
T5 = pd.read_csv(PREP.parent / "data/targets-3km.csv").query("arm == 'rating5'")
CC = pd.read_csv(PREP.parent / "data/cosmo-contacts.csv")
DENS_CMAP = matplotlib.colors.LinearSegmentedColormap.from_list(
    "dens", [(1, 1, 1, 0), (0.776, 0.859, 0.937, 0.75), "#6baed6", "#2171b5", "#08306b"])
UNCONV = "UNCONVERGED (core (b) split-half not converged)"


def style():
    matplotlib.rcParams.update({"font.size": 6, "axes.titlesize": 6.5, "axes.labelsize": 6, "xtick.labelsize": 5.5,
                                "ytick.labelsize": 5.5, "legend.fontsize": 5.5, "font.family": "DejaVu Sans"})


def footnotes(fig, ste, tech, top=0.235, width=190, fs=5.0):
    """Two footnote blocks, (i) STE100 then (ii) technical, inside the bottom `top` fraction of the figure."""
    t1 = "\n".join(textwrap.wrap("(i) " + ste, width))
    t2 = "\n".join(textwrap.wrap("(ii) " + tech, width))
    fig.text(0.01, top - 0.005, t1 + "\n" + t2, ha="left", va="top", fontsize=fs, color="#333333", linespacing=1.18)


def searches(ax, oi=True, zorder=1, alpha_scale=1.0):
    from matplotlib.patches import Polygon
    for fid, col, al, _ in cs.SEARCH_FILL:
        if not oi and fid.startswith("oi"):
            continue
        for p in cf.polygons(GEO, fid):
            ax.add_patch(Polygon(p[:, :2], closed=True, fc=col, ec=col, alpha=al * alpha_scale, lw=0.6, zorder=zorder))


def arc7(ax, zorder=4):
    arc = cf.polygons(GEO, "seventh_arc_fl400")[0]
    ax.plot(arc[:, 0], arc[:, 1], color="#333333", lw=0.7, ls=":", zorder=zorder)


def objects(ax, zorder=6):
    ax.plot(T5.lon, T5.lat, "x", ms=3.2, color="#d62728", mew=0.9, zorder=zorder)
    ax.plot(CC.longitude, CC.latitude, "o", ms=3.2, mfc="white", mec="#e6550d", mew=0.9, zorder=zorder)


def points_bg(ax, m, lat, lon, n=6000, colour="#222222", zorder=2, seed=0):
    """House background (closeup_styles.flight_background, mode 'points'): n points drawn in proportion to the
    cell mass and jittered within each cell."""
    m = m / m.sum()
    rng = np.random.default_rng(seed)
    k = rng.choice(m.size, size=n, p=m.ravel())
    i, j = np.unravel_index(k, m.shape)
    step = float(lat[1] - lat[0])
    y = lat[i] + rng.uniform(-step / 2, step / 2, len(k)); x = lon[j] + rng.uniform(-step / 2, step / 2, len(k))
    ax.scatter(x, y, s=1.0, c=colour, alpha=0.5, linewidths=0, zorder=zorder, rasterized=True)


def density(ax, m, area, lat, lon, zorder=3):
    m = m / m.sum(); dn = m / area
    ax.pcolormesh(lon, lat, dn / dn.max(), cmap=DENS_CMAP, vmin=0, vmax=1, shading="auto", rasterized=True, zorder=zorder)
    lv = [hdr_level(dn, m, q) for q in (0.9, 0.5)]
    ax.contour(lon, lat, dn, levels=lv, colors=["#08306b", "#08306b"], linewidths=[0.7, 1.4], zorder=zorder + 2)


def frame(ax, lon=(88, 96), lat=(-38, -32)):
    ax.set_xlim(*lon); ax.set_ylim(*lat); ax.set_aspect(1 / np.cos(np.radians(35)))
    ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°)")
