"""Deliverable 4 figure: conditional impact PDF under H reported WITH its tension measurement.

    python d4_figure.py <rerun-measured dir> <rerun-declared dir> <rerun-pt1h dir> <targets-3km.csv> <out stem>

Inputs are the outputs of rerun_reference.py (gitignored run tree): rerun-reference.csv and
fields-eof2f.npz (pooled eof-2f fields, rho4-0 / equal arm). Writes <out stem>.png and .pdf.
Panels: (a) unconditional impact PDF; (b) H-alone likelihood (ocean-model marginal); (c) conditional
PDF under H, with the unconditional 90% HDR outlined; (d) tension: Handley & Lemos (2019) p for
every spread x ocean-model field, pooled with the eight-seed range.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KERNEL = "eof-2f PROVISIONAL-OVERNIGHT"


def hdr_level(dens, mass, level=0.9):
    o = np.argsort(dens.ravel())[::-1]
    c = np.cumsum(mass.ravel()[o])
    return dens.ravel()[o][min(np.searchsorted(c, level), len(o) - 1)]


def load_fields(d):
    z = np.load(Path(d) / "fields-eof2f.npz", allow_pickle=False)
    return {k: z[k] for k in z.files}


def tension_rows(dirs):
    rows = []
    for tag, d in dirs:
        x = pd.read_csv(Path(d) / "rerun-reference.csv")
        x = x[(x.kernel == KERNEL) & x.field.str.startswith("module") & (x.object_rating == "rho4-0") & (x.cluster_weight == "equal")]
        for f, g in x.groupby("field"):
            model = f.replace("module D3 (", "").rstrip(")")
            model = "marginal" if model.startswith("marginal") else model.split("+")[0]
            pooled = g[g.replicate == "pooled"].iloc[0]
            seeds = g[g.replicate != "pooled"]
            rows.append(dict(spread=tag, model=model, p=pooled.tension_p, p_lo=seeds.tension_p.min(), p_hi=seeds.tension_p.max(),
                             lnS=pooled.ln_S, d=pooled.d_shared, shift=pooled.mean_shift_nm, n_seeds=len(seeds)))
    return pd.DataFrame(rows)


def make(measured, declared, pt1h, targets_csv, out, plt):
    F = load_fields(measured)
    lat, lon, area, unc = F["lat"], F["lon"], F["area"], F["uncond"]
    labels = list(F["labels"])
    im = [i for i, l in enumerate(labels) if l.startswith("marginal")][0]
    L = F["L"][im]
    pu = unc / unc.sum()
    pH = L * area / (L * area).sum()
    pj = pu * L / (pu * L).sum()
    dens = [pu / area, pH / area, pj / area]
    mass = [pu, pH, pj]
    T = pd.read_csv(targets_csv)
    T5 = T[(T.arm == "rating5")]
    ext = [lon[0], lon[-1], lat[0], lat[-1]]
    fig, axs = plt.subplots(1, 4, figsize=(7.1, 2.6), gridspec_kw=dict(width_ratios=[1, 1, 1, 0.9], wspace=0.28))
    titles = ["Flight posterior", "Pléiades likelihood", "Conditional on H"]
    cmap = "Greys"
    for k in range(3):
        ax = axs[k]
        dn = dens[k] / dens[k].max()
        ax.imshow(dn, origin="lower", extent=ext, cmap=cmap, vmin=0, vmax=1, aspect=1 / np.cos(np.radians(36)), interpolation="nearest")
        ax.contour(lon, lat, dens[k], levels=[hdr_level(dens[k], mass[k])], colors=["#1f5fa8"], linewidths=0.9)
        if k == 2:
            ax.contour(lon, lat, dens[0], levels=[hdr_level(dens[0], mass[0])], colors=["#888888"], linewidths=0.7, linestyles="--")
        ax.contour(lon, lat, F["cross"], levels=[0.0], colors=["#c07020"], linewidths=0.7)
        if k >= 1:
            ax.plot(T5.lon, T5.lat, "o", ms=2.5, mfc="none", mec="#b03030", mew=0.7)
        ax.set_title(titles[k], loc="left")
        ax.set_xlabel("Longitude (°E)")
        if k == 0:
            ax.set_ylabel("Latitude (°)")
        ax.set_xlim(88, 95.5)
        ax.set_ylim(-39.5, -32)
        ax.set_yticks(range(-39, -32))
        if k > 0:
            ax.set_yticklabels([])
    R = tension_rows([("declared", declared), ("measured", measured), ("measured, hourly GlobCurrent", pt1h)])
    order = [("declared", "glorys12v1"), ("declared", "globcurrent-my-pt1h"), ("declared", "marginal"),
             ("measured", "glorys12v1"), ("measured", "globcurrent-my-p1d"), ("measured", "marginal"),
             ("measured, hourly GlobCurrent", "globcurrent-my-pt1h")]
    names = {"glorys12v1": "GLORYS12", "globcurrent-my-pt1h": "GlobCurrent hourly", "globcurrent-my-p1d": "GlobCurrent daily", "marginal": "both products"}
    ax = axs[3]
    ys, yl = [], []
    for i, (s, m) in enumerate(order):
        r = R[(R.spread == s) & (R.model == m)]
        if r.empty:
            continue
        r = r.iloc[0]
        y = len(order) - i
        col = "#1f5fa8" if s.startswith("measured") else "#999999"
        ax.plot([r.p_lo, r.p_hi], [y, y], "-", color=col, lw=1.2)
        ax.plot(r.p, y, "o", color=col, ms=3.5)
        ys.append(y)
        yl.append(names[m])
    ax.axvline(0.05, color="#b03030", lw=0.7, ls=":")
    ax.text(0.047, min(ys) - 0.55, "p = 0.05", fontsize=6, color="#b03030", va="center", ha="right")
    ax.set_yticks(ys)
    ax.set_yticklabels(yl)
    ax.set_xscale("log")
    ax.set_xlim(0.02, 1.0)
    ax.set_xticks([0.02, 0.05, 0.1, 0.2, 0.5, 1.0])
    ax.set_xticklabels(["0.02", "0.05", "0.1", "0.2", "0.5", "1"])
    ax.set_ylim(min(ys) - 0.9, max(ys) + 0.9)
    ax.set_xlabel("Tension probability p")
    ax.set_title("No significant tension", loc="left")
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    for y0, y1, lab in [(5, 7, "declared spread"), (1, 4, "measured spread")]:
        yy = [y for y in ys if y0 <= y <= y1]
        if yy:
            ax.text(0.98, max(yy) + 0.45, lab, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=6, color="#1f5fa8" if lab.startswith("measured") else "#777777")
    fig.savefig(str(out) + ".png", dpi=300, bbox_inches="tight")
    fig.savefig(str(out) + ".pdf", bbox_inches="tight")
    return fig, axs, R


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    make(*sys.argv[1:6], plt=plt)
