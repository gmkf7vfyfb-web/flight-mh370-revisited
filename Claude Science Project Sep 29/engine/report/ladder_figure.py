"""Render the evidence ladder: what each measurement set adds to the posterior.

Run inside a kernel that has already applied the project's figure style, e.g.

    exec(open("report/ladder_figure.py").read())
    fig = ladder_figure(RUNGS, out="ladder.png")

Panel (a) is the 7th-arc latitude posterior for each rung, against the digitised published
curve. Panel (b) is the 00:19 BTO residual, recomputed from each rung's own saved final
positions rather than read from the run: for the rungs whose likelihood stops at 00:11 that
residual is out of sample, so the panel reads as a prediction check rather than a fit statistic.
The measurement standard deviation is drawn as the band a correct model should sit inside.
"""

import json

import numpy as np
from matplotlib.lines import Line2D

GRID = np.linspace(-50.0, 50.0, 2001)
SHOULDER = (-36.5, -34.5)


def _density(run, case):
    s = json.load(open(f"runs/{run}/summary.json"))
    c = next(x for x in s["cases"] if x["case"] == case)
    return np.asarray(c["density"], float), c


def ladder_figure(rungs, ladder_json="runs/ladder.json", out="ladder.png", reference_run="davey2016"):
    """`rungs` is [(run, case, label, colour), ...] in ladder order."""
    import matplotlib.pyplot as plt

    recs = {(r["run"], r["case"]): r for r in json.loads(open(ladder_json).read())}
    ref = np.asarray(json.load(open(f"runs/{reference_run}/summary.json"))["reference"]["density"], float)

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.6, 3.5),
                                 gridspec_kw=dict(width_ratios=[1.5, 1.0], wspace=0.33))

    ax.axvspan(*SHOULDER, color="#c1121f", alpha=0.07, lw=0, zorder=0)
    ax.fill_between(GRID, 0, ref, color="#e4e4e4", zorder=1, lw=0)
    ax.plot(GRID, ref, color="#9a9a9a", lw=1.0, zorder=2)
    top = 0.0
    for run, case, label, colour in rungs:
        d, _ = _density(run, case)
        ax.plot(GRID, d, color=colour, lw=1.8, zorder=4, label=label)
        top = max(top, d.max())
    ax.set_xlim(-44.0, -28.0)
    ax.set_ylim(0, top * 1.28)
    t = np.arange(-44, -27, 4)
    ax.set_xticks(t)
    ax.set_xticklabels([f"{abs(v):.0f}" for v in t])
    ax.set_xlabel("Latitude where the 7th arc is crossed (°S)")
    ax.set_ylabel("Posterior density (per degree)")
    ax.set_title("Each measurement set added in turn", loc="left")
    ax.legend(frameon=False, loc="upper left", fontsize=7, handlelength=1.5,
              borderpad=0.1, labelspacing=0.3)
    ax.text(np.mean(SHOULDER), top * 1.17, "shoulder", color="#c1121f", fontsize=7, ha="center")

    # Panel b: the 00:19 arc as a prediction check.
    sd = next((r.get("bto0019_sd_us") for r in recs.values() if r.get("bto0019_sd_us")), 43.0)
    bx.axhspan(-sd, sd, color="#d8d8d8", alpha=0.55, lw=0, zorder=0)
    bx.axhline(0.0, color="#9a9a9a", lw=0.8, zorder=1)
    xs, labels = [], []
    for i, (run, case, label, colour) in enumerate(rungs):
        r = recs.get((run, case))
        if not r or r.get("bto0019_mean_us") is None:
            continue
        m, rms = r["bto0019_mean_us"], r["bto0019_rms_us"]
        bx.errorbar([i], [m], yerr=[[rms], [rms]], fmt="o", ms=6, color=colour,
                    elinewidth=1.4, capsize=3, zorder=3)
        xs.append(i)
        labels.append(label.split("+")[-1].strip() if "+" in label else label)
    bx.set_xticks(xs)
    bx.set_xticklabels(labels, rotation=30, ha="right")
    bx.set_ylabel("00:19 BTO residual (µs)")
    bx.set_title("The 00:19 arc, predicted not fitted\n(band: measurement s.d.)", loc="left")
    for a in (ax, bx):
        a.spines[["top", "right"]].set_visible(False)
    panel_letter(ax, "a")
    panel_letter(bx, "b")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    return fig
