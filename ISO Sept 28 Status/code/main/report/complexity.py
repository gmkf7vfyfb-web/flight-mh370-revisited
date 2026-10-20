#!/usr/bin/env python3
"""Trajectory complexity versus arc latitude, and the sparse-filter test.

Usage: complexity.py RUN_7TH_ARC RUN_6TH_ARC SPARSE_RUN_DIRS... OUTPUT_PDF

RUN_7TH_ARC / RUN_6TH_ARC: runs made with output.history_after_epoch (history.npy),
e.g. config/sensitivity/complexity.toml and complexity-to-0011.toml. Complexity is the
number of manoeuvres after 18:40 (turns + speed changes + altitude changes), and the total
angle turned after 18:40. Probabilities are posterior weights, pooling replicates as one
sampler (P(mode) from replicate-averaged evidence; within a mode, replicates by evidence).
The prior complexity distribution is Davey et al.'s manoeuvre model: for each of the three
manoeuvre types a Poisson count with mean T/tau, tau ~ Jeffreys(0.1, 10 h), manoeuvre
durations neglected.
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402

HERE = Path(__file__).resolve().parent
DAVEY = HERE.parent / ".sources/davey-2016/fig10-3-bfo-latitude-pdf.csv"
INK, MUTED, OURS, DAVEY_COLOUR = "#0b0b0b", "#52514e", "#2a78d6", "#eb6834"
CLASSES = [(0, 0, "0"), (1, 2, "1–2"), (3, 4, "3–4"), (5, 999, "5 or more")]
CLASS_COLOURS = ["#c6dbef", "#6baed6", "#2171b5", "#08306b"]  # ordinal: light = simple, dark = complex
SHOULDER = (-36.5, -34.5)
GRID = np.arange(-45.0, -25.0 + 1e-9, 0.05)
plt.rcParams.update({
    "font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 8.5, "axes.titlesize": 9,
    "axes.labelsize": 8.5, "legend.fontsize": 7.5, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "axes.linewidth": 0.6, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "pdf.fonttype": 42,
})


def load(run_dir):
    """Latitude, pooled weight, total manoeuvres and degrees turned after 18:40, and arc time."""
    run = json.loads((run_dir / "run.json").read_text())
    cfg = run["config"]
    seeds = next(c.get("seeds") or cfg["seeds"] for c in cfg["cases"] if c["id"] == "bto-bfo")
    reps = []
    for s in seeds:
        d = run_dir / "bto-bfo" / f"seed-{s}"
        f = np.load(d / "final.npy")
        h = np.load(d / "history.npy")
        g = json.loads((d / "diagnostics.json").read_text())
        mode = f[:, 12 if f.shape[1] > 12 else 9].astype(int)  # stratum; older runs have only the final mode
        p = np.array([m["posterior_probability"] for m in g["modes"]])
        reps.append(dict(lat=f[:, 1], mode=mode, within=f[:, 0] / np.where(p > 0, p, 1)[mode], h=h, g=g))
    lz = np.array([[m["log_evidence"] for m in r["g"]["modes"]] for r in reps])
    z = np.exp(lz - lz.max())
    pm = z.mean(0) / z.mean(0).sum()
    share = z / z.sum(0)
    w = np.concatenate([r["within"] * (pm * share[i])[r["mode"]] for i, r in enumerate(reps)])
    h = np.concatenate([r["h"] for r in reps])
    last = run["epochs"][-1]
    t_arc = last["unix_s"]
    start = next(e["unix_s"] for e in run["epochs"] if e["id"] == cfg["output"]["history_after_epoch"])
    return dict(lat=np.concatenate([r["lat"] for r in reps]), w=w / w.sum(), n=h[:, :3].sum(1), turns=h[:, 0],
                speed=h[:, 1], alt=h[:, 2], deg=h[:, 3], hours=(t_arc - start) / 3600, arc=last["id"], seeds=seeds)


def prior_classes(hours):
    """P(total manoeuvres = k) under Davey's model over `hours`, k = 0..200."""
    tau = np.exp(np.linspace(np.log(0.1), np.log(10), 4000))
    w = np.full_like(tau, 1.0)  # Jeffreys: uniform in log(tau)
    w /= w.sum()
    k = np.arange(201)
    lam = 3 * hours / tau  # three independent manoeuvre types
    from math import lgamma
    lg = np.array([lgamma(i + 1) for i in k])
    pk = (w[None, :] * np.exp(k[:, None] * np.log(lam[None, :]) - lam[None, :] - lg[:, None])).sum(1)
    return pk


def density(lat, w):
    step = GRID[1] - GRID[0]
    h, _ = np.histogram(lat, bins=np.append(GRID - step / 2, GRID[-1] + step / 2), weights=w)
    k = np.arange(-0.4, 0.4 + 1e-9, step)
    ker = np.exp(-0.5 * (k / 0.1) ** 2)
    return np.convolve(h, ker / ker.sum(), mode="same") / step


def davey():
    raw = np.loadtxt(DAVEY, delimiter=",", skiprows=1)
    d = np.interp(GRID, raw[:, 0], raw[:, 1], left=0, right=0)
    return d / (d.sum() * (GRID[1] - GRID[0]))


def arc_name(r):
    return f"{'7th' if r['arc'].startswith('m0019') else '6th'} arc ({r['arc'][1:3]}:{r['arc'][3:5]} UTC)"


def in_class(n, c):
    return (n >= c[0]) & (n <= c[1])


def main():
    arc7, arc6 = load(Path(sys.argv[1])), load(Path(sys.argv[2]))
    sparse_dirs, out = [Path(p) for p in sys.argv[3:-1]], Path(sys.argv[-1])
    runs = [arc7, arc6]
    note = (f"Posterior weights pooled over replicates {', '.join(map(str, arc7['seeds']))} (7M particles each, BTO+BFO). "
            "Complexity = turns + speed changes + altitude changes after 18:40. Prior: Davey et al. manoeuvre model "
            "(Jeffreys tau on 0.1-10 h, Poisson counts, durations neglected).")

    with PdfPages(out, metadata={"Title": "MH370: trajectory complexity versus arc latitude"}) as pdf:
        # 1. Heat map with marginals.
        fig = plt.figure(figsize=(11.69, 8.27))
        fig.text(0.05, 0.955, "1. Complexity after 18:40 against arc latitude (posterior probability)", fontsize=12,
                 weight="bold", color=INK)
        for col, r in enumerate(runs):
            x0 = 0.06 + col * 0.48
            top = fig.add_axes([x0, 0.72, 0.30, 0.16])
            main_ax = fig.add_axes([x0, 0.12, 0.30, 0.58], sharex=top)
            side = fig.add_axes([x0 + 0.315, 0.12, 0.09, 0.58], sharey=main_ax)
            nmax = 12
            yb = np.arange(-0.5, nmax + 1.5, 1.0)
            xb = np.arange(-42, -28.9, 0.25)
            h, _, _ = np.histogram2d(r["lat"], np.minimum(r["n"], nmax + 1), bins=[xb, yb], weights=r["w"])
            h = np.ma.masked_less_equal(h, 0)
            mesh = main_ax.pcolormesh(xb, yb, h.T, cmap="Blues", norm=LogNorm(vmin=max(h.max() * 1e-4, 1e-9), vmax=h.max()),
                                      rasterized=True)
            main_ax.axvspan(*SHOULDER, color=DAVEY_COLOUR, alpha=0.08, lw=0)
            main_ax.set_xlim(-42, -29)
            main_ax.set_ylim(-0.5, nmax + 1.5)
            main_ax.set_yticks(range(0, nmax + 2, 2), [str(v) for v in range(0, nmax, 2)] + [f"{nmax}+"])
            main_ax.set_xlabel(f"Latitude at the {arc_name(r)} (°)")
            main_ax.set_ylabel("Manoeuvres after 18:40")
            d = density(r["lat"], r["w"])
            top.plot(GRID, d, color=OURS, lw=1.3, label="This estimate")
            if r is arc7:
                top.plot(GRID, davey(), color=DAVEY_COLOUR, ls=(0, (5, 2)), lw=1.1, label="Davey et al. Fig. 10.3")
            top.axvspan(*SHOULDER, color=DAVEY_COLOUR, alpha=0.08, lw=0)
            top.set_ylabel("pdf (per °)")
            top.legend(loc="upper left")
            top.set_title(arc_name(r), loc="left")
            plt.setp(top.get_xticklabels(), visible=False)
            post = np.array([r["w"][np.minimum(r["n"], nmax + 1) == k].sum() for k in range(nmax + 2)])
            pk = prior_classes(r["hours"])
            prior = np.append(pk[: nmax + 1], pk[nmax + 1:].sum())
            ks = np.arange(nmax + 2)
            side.barh(ks + 0.2, post, height=0.38, color=OURS, label="posterior")
            side.barh(ks - 0.2, prior, height=0.38, color="#bdbbb3", label="prior")
            side.set_xlabel("probability")
            side.legend(loc="lower right", fontsize=6.5)
            plt.setp(side.get_yticklabels(), visible=False)
            cb = fig.colorbar(mesh, ax=main_ax, orientation="horizontal", fraction=0.04, pad=0.14)
            cb.set_label("probability per cell (log)")
        fig.text(0.05, 0.02, note + " Shaded band: the published shoulder 34.5-36.5°S.", fontsize=7.5, color=MUTED, wrap=True)
        pdf.savefig(fig)
        plt.close(fig)

        # 2. Stacked decomposition by complexity class.
        fig, axes = plt.subplots(1, 2, figsize=(11.69, 5.2))
        for ax, r in zip(axes, runs):
            base = np.zeros_like(GRID)
            for c, colour in zip(CLASSES, CLASS_COLOURS):
                k = in_class(r["n"], c)
                d = density(r["lat"][k], r["w"][k])
                ax.fill_between(GRID, base, base + d, color=colour, lw=0.3, edgecolor="white",
                                label=f"{c[2]} manoeuvres ({r['w'][k].sum():.0%})")
                base = base + d
            if r is arc7:
                ax.plot(GRID, davey(), color=DAVEY_COLOUR, ls=(0, (5, 2)), lw=1.1, label="Davey et al. Fig. 10.3")
            ax.axvspan(*SHOULDER, color=DAVEY_COLOUR, alpha=0.06, lw=0)
            ax.set_xlim(-42, -29)
            ax.set_xlabel(f"Latitude at the {arc_name(r)} (°)")
            ax.set_ylabel("probability density (per °)")
            ax.set_title(f"2. Latitude pdf split by complexity after 18:40 — {arc_name(r)}", loc="left")
            ax.legend(loc="upper left")
        fig.text(0.05, 0.01, "Stacked: each band is that class's contribution to the pdf; legend shows its posterior share. "
                 + note, fontsize=7.5, color=MUTED, wrap=True)
        fig.tight_layout(rect=(0, 0.05, 1, 1))
        pdf.savefig(fig)
        plt.close(fig)

        # 3. Ridgeline: each class normalised on its own.
        fig, axes = plt.subplots(1, 2, figsize=(11.69, 6.0))
        for ax, r in zip(axes, runs):
            pk = prior_classes(r["hours"])
            for i, (c, colour) in enumerate(zip(CLASSES, CLASS_COLOURS)):
                k = in_class(r["n"], c)
                if r["w"][k].sum() <= 0:
                    continue
                d = density(r["lat"][k], r["w"][k])
                d = d / d.max() * 0.9
                ax.fill_between(GRID, i, i + d, color=colour, lw=0.8, edgecolor=INK if i == 3 else MUTED)
                cdf = np.cumsum(density(r["lat"][k], r["w"][k]))
                cdf /= cdf[-1]
                med = float(np.interp(0.5, cdf, GRID))
                sh = r["w"][k & (r["lat"] > SHOULDER[0]) & (r["lat"] < SHOULDER[1])].sum() / r["w"][k].sum()
                ax.plot([med, med], [i, i + 0.9], color=INK, lw=0.8)
                prior_share = pk[c[0]:min(c[1], 200) + 1].sum()
                ax.text(-41.8, i + 0.55, f"{c[2]} manoeuvres\nposterior {r['w'][k].sum():.1%}, prior {prior_share:.1%}\n"
                        f"median {med:.1f}°, shoulder {sh:.0%}", fontsize=7, color=INK, va="center")
            ax.axvspan(*SHOULDER, color=DAVEY_COLOUR, alpha=0.08, lw=0)
            ax.set_xlim(-42, -29)
            ax.set_yticks([])
            ax.set_xlabel(f"Latitude at the {arc_name(r)} (°)")
            ax.set_title(f"3. Latitude pdf of each complexity class (normalised) — {arc_name(r)}", loc="left")
        fig.text(0.05, 0.01, "Each ridge is normalised separately, so shape is visible regardless of weight; vertical tick: "
                 "median. 'Shoulder' is the class's own probability in 34.5-36.5°S. " + note, fontsize=7.5, color=MUTED, wrap=True)
        fig.tight_layout(rect=(0, 0.05, 1, 1))
        pdf.savefig(fig)
        plt.close(fig)

        # 4. Manoeuvre types against latitude.
        fig, axes = plt.subplots(1, 2, figsize=(11.69, 5.0))
        for ax, r in zip(axes, runs):
            bins = np.arange(-41, -29.9, 0.5)
            idx = np.digitize(r["lat"], bins)
            centres = 0.5 * (bins[:-1] + bins[1:])
            ax2 = ax.twinx()
            for column, name, colour in [("turns", "turns", "#eb6834"), ("speed", "speed changes", "#2a78d6"),
                                         ("alt", "altitude changes", "#1baf7a")]:
                m = [np.average(r[column][idx == b], weights=r["w"][idx == b]) if r["w"][idx == b].sum() > 1e-5 else np.nan
                     for b in range(1, len(bins))]
                ax.plot(centres, m, color=colour, lw=1.4, marker="o", ms=2.5, label=f"mean {name}")
            deg = [np.average(r["deg"][idx == b], weights=r["w"][idx == b]) if r["w"][idx == b].sum() > 1e-5 else np.nan
                   for b in range(1, len(bins))]
            ax2.plot(centres, deg, color=INK, lw=1.0, ls=(0, (3, 2)), label="mean degrees turned (right axis)")
            ax2.set_ylabel("degrees turned after 18:40")
            ax2.spines["right"].set_visible(True)
            ax.axvspan(*SHOULDER, color=DAVEY_COLOUR, alpha=0.08, lw=0)
            ax.set_xlabel(f"Latitude at the {arc_name(r)} (°)")
            ax.set_ylabel("mean count after 18:40")
            ax.set_title(f"4. Manoeuvres by type against latitude — {arc_name(r)}", loc="left")
            lines = ax.get_legend_handles_labels()
            lines2 = ax2.get_legend_handles_labels()
            ax.legend(lines[0] + lines2[0], lines[1] + lines2[1], loc="upper left")
        fig.text(0.05, 0.01, "Posterior-weighted means in 0.5° latitude bins with at least 1e-5 of the probability. "
                 + note, fontsize=7.5, color=MUTED, wrap=True)
        fig.tight_layout(rect=(0, 0.05, 1, 1))
        pdf.savefig(fig)
        plt.close(fig)

        # 5. Sparse-filter test.
        if sparse_dirs:
            fig, ax = plt.subplots(figsize=(11.69, 5.0))
            bins = np.linspace(0, 1, 41)
            colours = ["#08306b", "#2171b5", "#6baed6"]
            for d, colour in zip(sparse_dirs, colours):
                shares, origins = [], []
                seeds = sorted(int(p.name.split("-")[1]) for p in (d / "bto-bfo").glob("seed-*"))
                for s in seeds:
                    t = np.load(d / "bto-bfo" / f"seed-{s}" / "final.npy")
                    w = t[:, 0] / t[:, 0].sum()
                    shares.append(w[(t[:, 1] > SHOULDER[0]) & (t[:, 1] < SHOULDER[1])].sum())
                    g = json.loads((d / "bto-bfo" / f"seed-{s}" / "diagnostics.json").read_text())
                    origins.append(sum(m["distinct_origins"] for m in g["modes"]))
                shares = np.array(shares)
                n = sum(json.loads((d / "run.json").read_text())["config"]["particles_per_mode"])
                ax.hist(shares, bins=bins, histtype="step", lw=1.6, color=colour,
                        label=f"{n:,} particles (median {int(np.median(origins))} surviving root draws): "
                              f"{np.mean(shares >= 0.25):.0%} of {len(seeds)} runs ≥ 25%")
            ax.axvline(0.25, color=DAVEY_COLOUR, ls=(0, (5, 2)), lw=1.1, label="Davey et al.: 25%")
            ax.axvline(0.035, color=OURS, lw=1.1, label="Converged estimate (8 × 7M particles): 3.5%")
            ax.set_xlabel("Probability in 34.5-36.5°S at 00:19 in one run")
            ax.set_ylabel("number of runs")
            ax.set_title("5. How often a sparse filter reproduces Davey's shoulder by chance (base model, BTO+BFO)", loc="left")
            ax.legend(loc="upper right")
            fig.tight_layout(rect=(0, 0.03, 1, 1))
            pdf.savefig(fig)
            plt.close(fig)
    print(out)


if __name__ == "__main__":
    main()
