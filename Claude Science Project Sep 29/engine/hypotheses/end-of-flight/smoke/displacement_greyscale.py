"""Project-convention (report/epoch_map.py) figure of impact displacement from the own 00:19:37 position:
greyscale highest-posterior-density bands at 50/90/99 % with dark contour edges, one row per run, one column
per data option.

    python3 displacement_greyscale.py <out-stem> "<title>" <row-label>=<terminal-out-dir> ...
        [--extent 160] [--options none__other,r600_inflated__fuel-exhaustion,r1200_inflated__fuel-exhaustion]

Density: weighted 1 NM histogram of (delta-east, delta-north), Gaussian-smoothed (sigma 2 NM), HPD levels
from the smoothed density as epoch_map.hpd_levels does. Weights are displacement_hist.option_posteriors
(seed 1), so the figure, the histograms and the sensitivity tables share one definition. Writes
<out-stem>.pdf and <out-stem>.png, and <out-stem>.json with the enclosed-mass check per panel.
"""
import argparse, json, pathlib, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from scipy.ndimage import gaussian_filter
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from displacement_hist import option_posteriors

LEVELS = (0.99, 0.90, 0.50)
SHADES = ["#dcdcdc", "#a8a8a8", "#6a6a6a"]          # epoch_map.py: 99 %, 90 %, 50 %
EDGE, EDGE_W = "#2b2b2b", [0.5, 0.7, 0.9]
TITLES = {"none__other": "Held out (no 00:19 data)", "r600_inflated__fuel-exhaustion": "R600, fuel-exhaustion log-on",
          "r1200_inflated__fuel-exhaustion": "R1200, fuel-exhaustion log-on"}


def hpd_levels(dens, fractions):
    flat = np.sort(dens.ravel())[::-1]; mass = np.cumsum(flat); out = []
    for f in fractions:
        out.append(float(flat[min(int(np.searchsorted(mass, f * mass[-1])), len(flat) - 1)]))
    out = sorted(out)
    for i in range(1, len(out)):
        if out[i] <= out[i - 1]:
            out[i] = np.nextafter(out[i - 1], np.inf)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stem"); ap.add_argument("title"); ap.add_argument("rows", nargs="+")
    ap.add_argument("--extent", type=float, default=160.0)
    ap.add_argument("--options", default="none__other,r600_inflated__fuel-exhaustion,r1200_inflated__fuel-exhaustion")
    a = ap.parse_args(); opts = a.options.split(",")
    edges = np.arange(-a.extent, a.extent + 1e-9, 1.0); c = 0.5 * (edges[1:] + edges[:-1])
    fig, axs = plt.subplots(len(a.rows), len(opts), figsize=(2.35 * len(opts) + 0.4, 2.35 * len(a.rows) + 0.6),
                            sharex=True, sharey=True, squeeze=False, gridspec_kw=dict(wspace=0.06, hspace=0.10))
    check = {}
    for i, spec in enumerate(a.rows):
        label, d = spec.split("=", 1)
        dirs = [pathlib.Path(x) for x in d.split(",")]
        if len(dirs) == 1:  # one directory: its first seed (the relay convention)
            srcs = [(dirs[0], sorted(p for p in (dirs[0] / "bto-bfo").glob("seed-*") if (p / "impacts.npy").exists())[0])]
        else:               # several: every seed, equal weight per seed
            srcs = [(r, p) for r in dirs for p in sorted((r / "bto-bfo").glob("seed-*")) if (p / "impacts.npy").exists()]
        acc = {}
        for r, sd in srcs:
            for k, p, cc in option_posteriors(r, sd):
                if k in opts:
                    acc.setdefault(k, []).append((p, {f: cc[f] for f in ("dn", "de", "has")}))
        post = {k: (np.concatenate([q[0] for q in v]) / len(v),
                    {f: np.concatenate([q[1][f] for q in v]) for f in ("dn", "de", "has")}) for k, v in acc.items()}
        ess_of = {k: float(sum(1.0 / np.sum(q[0] ** 2) for q in v)) for k, v in acc.items()}
        seed = type("S", (), {"name": ",".join(f"{r.name}/{p.name}" for r, p in srcs)})
        for j, k in enumerate(opts):
            ax = axs[i, j]; p, cc = post[k]; h = cc["has"]
            H, _, _ = np.histogram2d(cc["dn"][h], cc["de"][h], bins=[edges, edges], weights=p[h])
            inside = H.sum() / p[h].sum()
            dens = gaussian_filter(H, 2.0, mode="constant"); dens = dens / dens.sum()
            lv = hpd_levels(dens, LEVELS)
            ax.grid(True, color="#e3e3e3", lw=0.6); ax.set_axisbelow(True)
            ax.contourf(c, c, dens, levels=lv + [dens.max()], colors=SHADES, antialiased=True)
            ax.contour(c, c, dens, levels=lv, colors=EDGE, linewidths=EDGE_W)
            ax.plot(0, 0, marker="+", color="black", ms=7, mew=1.0, zorder=5)
            ess = ess_of[k]
            ax.text(0.97, 0.03, f"ESS {ess:,.0f}", transform=ax.transAxes, fontsize=6, color="#555555", ha="right", va="bottom")
            ax.set_aspect("equal"); ax.set_xlim(-a.extent, a.extent); ax.set_ylim(-a.extent, a.extent)
            ax.set_xticks([-100, -50, 0, 50, 100]); ax.set_yticks([-100, -50, 0, 50, 100]); ax.tick_params(labelsize=6)
            if i == 0: ax.set_title(TITLES.get(k, k), fontsize=7.5, loc="left")
            if i == len(a.rows) - 1: ax.set_xlabel("Δ east from 00:19:37 position (NM)", fontsize=7)
            if j == 0: ax.set_ylabel(f"{label}\nΔ north (NM)", fontsize=7)
            enc = [float(dens[dens >= l].sum()) for l in lv]
            check[f"{label}/{k}"] = {"seed": seed.name, "ess": float(ess), "share_with_0019_position": float(p[h].sum()),
                                     "share_inside_extent": float(inside), "enclosed_mass_99_90_50": enc}
    bands = [Patch(facecolor=s, edgecolor=EDGE, lw=0.6, label=f"{int(f * 100)} % of probability")
             for s, f in zip(SHADES[::-1], LEVELS[::-1])]
    bands.append(plt.Line2D([], [], marker="+", color="black", ls="none", ms=7, label="own 00:19:37 position"))
    fig.legend(handles=bands, loc="lower center", ncol=4, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle(a.title, fontsize=8, x=0.02, ha="left", y=0.995)
    fig.savefig(a.stem + ".pdf", bbox_inches="tight"); fig.savefig(a.stem + ".png", dpi=200, bbox_inches="tight")
    pathlib.Path(a.stem + ".json").write_text(json.dumps(check, indent=1)); print("wrote", a.stem)


if __name__ == "__main__":
    main()
