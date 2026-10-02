"""Render the evidence ladder as a spatial progression: the posterior collapsing onto the arc.

Run inside a kernel that has applied the project's figure style:

    exec(open("report/ladder_progression.py").read())
    fig = progression(RUNGS, out="ladder-progression.png")

One map per rung, all on the same extent and the same colour scale so the panels are
comparable, with the 6th and 7th arcs drawn from the BTO forward model rather than traced from
a figure. A final panel puts each rung's 00:19 range error on one axis; for the rungs whose
likelihood stops at 00:11 that arc was never scored, so the sequence is out-of-sample
prediction error falling as evidence is added.

`rungs` is [(run, case, label), ...] in ladder order.
"""

import glob
import json

import numpy as np
from matplotlib.colors import LogNorm

C_KM_S = 299792.458
KM_PER_US = C_KM_S * 1e-6 / 2.0
LON_EDGES = np.arange(40.0, 145.01, 0.75)
LAT_EDGES = np.arange(-50.0, 45.01, 0.75)
ARC_RED = "#c1121f"
BLUE = "#1b4079"


def load_positions(run, case):
    r = json.load(open(f"runs/{run}/run.json"))
    ix = {k: i for i, k in enumerate(r["final_columns"])}
    parts = sorted(glob.glob(f"runs/{run}/{case}/seed-*/final.npy"))
    rows = np.concatenate([np.load(p, mmap_mode="r") for p in parts])
    w = np.asarray(rows[:, 0], np.float64)
    w /= w.sum()
    cols = [np.asarray(rows[:, ix[k]], np.float64) for k in ("latitude_deg", "longitude_deg", "altitude_ft")]
    return (*cols, w)


def progression(rungs, arcs, coast, residuals, out="ladder-progression.png", vmax=None):
    """`arcs` is (arc_lat, arc7_lon, arc6_lon); `residuals` maps label -> (res_km, weight)."""
    import matplotlib.pyplot as plt

    arc_lat, arc7, arc6 = arcs
    n = len(rungs)
    fig = plt.figure(figsize=(8.4, 2.3 * ((n + 1) // 2 + 1)))
    gs = fig.add_gridspec((n + 1) // 2 + 1, 2, hspace=0.38, wspace=0.18,
                          height_ratios=[1] * ((n + 1) // 2) + [0.85])

    def wmed(x, w):
        o = np.argsort(x)
        return float(x[o][np.searchsorted(np.cumsum(w[o]), 0.5)])

    grids, centres = [], []
    for run, case, label in rungs:
        lat, lon, alt, w = load_positions(run, case)
        H, _, _ = np.histogram2d(lon, lat, bins=[LON_EDGES, LAT_EDGES], weights=w)
        grids.append(np.ma.masked_where(H.T <= 0, H.T))
        # The weighted median position, and the fraction of weight inside 5 degrees of it. A
        # posterior that has collapsed onto the arc occupies a handful of cells and disappears
        # under the arc line at this extent, so the marker is what keeps it visible on a scale
        # shared with the diffuse rungs.
        mlat, mlon = wmed(lat, w), wmed(lon, w)
        near = float(w[(np.abs(lat - mlat) < 5.0) & (np.abs(lon - mlon) < 5.0)].sum())
        centres.append((mlon, mlat, near))
    top = vmax or max(float(g.max()) for g in grids)

    axes = []
    for k, ((run, case, label), H) in enumerate(zip(rungs, grids)):
        ax = fig.add_subplot(gs[k // 2, k % 2])
        for a in coast:
            ax.fill(a[:, 0], a[:, 1], facecolor="#f2f2f2", edgecolor="#cfcfcf", lw=0.25, zorder=1)
        pm = ax.pcolormesh(LON_EDGES, LAT_EDGES, H, norm=LogNorm(vmin=top * 1e-4, vmax=top),
                           cmap="Greys", zorder=2, shading="flat")
        ax.plot(arc7, arc_lat, color=ARC_RED, lw=1.2, zorder=5)
        ax.plot(arc6, arc_lat, color=ARC_RED, lw=0.7, ls="--", zorder=5)
        ax.plot([96.0], [6.5], "x", color=BLUE, mew=1.3, ms=5, zorder=6)
        mlon, mlat, near = centres[k]
        ax.plot([mlon], [mlat], "o", mfc="none", mec=BLUE, mew=1.4, ms=9, zorder=7)
        ax.set_xlim(40, 145)
        ax.set_ylim(-50, 45)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(f"{k + 1}. {label}\nmedian {abs(mlat):.1f}°{'S' if mlat < 0 else 'N'} "
                     f"{mlon:.1f}°E · {100 * near:.0f}% within 5°", loc="left")
        ax.set_xticks([60, 90, 120])
        ax.set_yticks([-40, -20, 0, 20, 40])
        if k % 2:
            ax.set_yticklabels([])
        if k // 2 != (n - 1) // 2:
            ax.set_xticklabels([])
        ax.spines[["top", "right"]].set_visible(False)
        axes.append((ax, pm))

    bx = fig.add_subplot(gs[-1, :])
    edges = np.arange(-4000, 3001, 50)
    for (run, case, label), colour in zip(rungs, ["#c9c9c9", "#9a9a9a", "#5f5f5f", BLUE][:len(rungs)]):
        res, w = residuals[label]
        bx.hist(res, bins=edges, weights=w, color=colour, histtype="step", lw=1.3,
                label=f"{label} — RMS {np.sqrt((w * res**2).sum()):,.0f} km", zorder=3)
    bx.axvline(0.0, color=ARC_RED, lw=1.3, zorder=4)
    bx.set_yscale("log")
    bx.set_ylim(1e-6, 3.0)
    bx.set_xlim(-4000, 3000)
    bx.set_xlabel("Range error against the 00:19 arc (km) — zero is on the arc")
    bx.set_ylabel("Posterior weight")
    bx.set_title("The 00:19 arc as a prediction: error falling as evidence is added", loc="left")
    bx.legend(frameon=False, fontsize=6.5, loc="upper left", handlelength=1.3, labelspacing=0.3)
    bx.spines[["top", "right"]].set_visible(False)

    cb = fig.colorbar(axes[0][1], ax=[a for a, _ in axes], fraction=0.020, pad=0.015)
    cb.ax.tick_params(labelsize=6)
    cb.set_label("posterior weight per 0.75° cell (shared scale)", fontsize=6.5)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    return fig
