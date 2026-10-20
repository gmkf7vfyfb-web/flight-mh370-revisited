#!/usr/bin/env python3
"""Residual diagnostics PDF: what each autopilot mode's paths predict at each SATCOM arc.

Usage: residuals.py RUN_DIR [OUTPUT_PDF]

Needs a run made with output.residual_samples > 0 (e.g. config/sensitivity/residuals-to-0011.toml).
Each residuals/<Mode>-<epoch>.npy is an equally weighted sample from that mode's predictive
distribution at the epoch (weights before the epoch's update). Residual = measured - predicted.
A positive BTO residual means the measured delay is longer than predicted: the path is still
inside the arc (too close to the satellite). Replicates are pooled with equal weight.
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

MODES = ["TrueHeading", "MagneticHeading", "TrueTrack", "MagneticTrack", "LateralNavigation"]
LABELS = ["True heading", "Magnetic heading", "True track", "Magnetic track", "Lateral navigation"]
COLOURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
INK, MUTED = "#0b0b0b", "#52514e"
SHOULDER = (-36.5, -34.5)
plt.rcParams.update({
    "font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 8.5, "axes.titlesize": 9,
    "axes.labelsize": 8.5, "legend.fontsize": 7.5, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "axes.linewidth": 0.6, "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False, "pdf.fonttype": 42,
})


def label(epoch):
    return f"{epoch[1:3]}:{epoch[3:5]}"


def load(run_dir, case, seeds, columns):
    """{(mode, epoch): {column: array}} pooled over replicates."""
    out = {}
    for seed in seeds:
        for path in sorted((run_dir / case / f"seed-{seed}" / "residuals").glob("*.npy")):
            mode, epoch = path.stem.rsplit("-", 1)
            a = np.load(path)
            cols = {c: a[:, i] for i, c in enumerate(columns)}
            prev = out.get((mode, epoch))
            out[(mode, epoch)] = cols if prev is None else {c: np.concatenate([prev[c], cols[c]]) for c in columns}
    return out


def cumulative_evidence(run_dir, case, seeds):
    inc = []
    for seed in seeds:
        d = json.loads((run_dir / case / f"seed-{seed}" / "diagnostics.json").read_text())
        inc.append([[e["log_evidence_increment"] for e in m["epochs"]] for m in d["modes"]])
        epochs = [e["epoch"] for e in d["modes"][0]["epochs"]]
    inc = np.mean(inc, axis=0)
    return epochs, np.cumsum(inc - inc[MODES.index("TrueTrack")], axis=1)


def density(values, grid, bandwidth):
    v = values[np.isfinite(values)]
    h, _ = np.histogram(v, bins=np.append(grid - (grid[1] - grid[0]) / 2, grid[-1] + (grid[1] - grid[0]) / 2))
    k = np.arange(-4 * bandwidth, 4 * bandwidth + 1e-9, grid[1] - grid[0])
    kernel = np.exp(-0.5 * (k / bandwidth) ** 2)
    d = np.convolve(h, kernel / kernel.sum(), mode="same")
    return d / max(d.sum() * (grid[1] - grid[0]), 1e-300)


def main():
    run_dir = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else run_dir / "residuals.pdf"
    run = json.loads((run_dir / "run.json").read_text())
    columns = run["residual_columns"]
    cfg = run["config"]
    cases = {c["id"]: c.get("seeds") or cfg["seeds"] for c in cfg["cases"]}
    sd = {e["id"]: e for e in run["epochs"]}
    data = {c: load(run_dir, c, s, columns) for c, s in cases.items()}
    evid = {c: cumulative_evidence(run_dir, c, s) for c, s in cases.items()}
    late = ["m2041", "m2141", "m2241", "m0011"]
    excluded = ", ".join(cfg.get("exclude_epochs", [])) or "none"
    note = (f"Run {cfg['name']}; epochs excluded: {excluded}; replicates {', '.join(map(str, next(iter(cases.values()))))}; "
            f"{cfg['output']['residual_samples']:,} predictive particles per mode and arc per replicate.")

    with PdfPages(out) as pdf:
        # Page 1: where evidence is lost.
        fig, axes = plt.subplots(1, len(cases), figsize=(11.69, 4.6), sharey=True)
        for ax, (case, (epochs, rel)) in zip(np.atleast_1d(axes), evid.items()):
            for m, (lab, col) in enumerate(zip(LABELS, COLOURS)):
                ax.plot(range(len(epochs)), rel[m], color=col, marker="o", ms=3, lw=1.3, label=lab)
            ax.axhline(0, color=MUTED, lw=0.5)
            ax.set_xticks(range(len(epochs)), [label(e) for e in epochs], rotation=90)
            ax.set_title(f"{case}: cumulative log-evidence relative to true track", loc="left")
            ax.grid(axis="y", color="#e9e8e4", lw=0.5)
        np.atleast_1d(axes)[0].set_ylabel("log-evidence minus true track")
        np.atleast_1d(axes)[0].legend(loc="lower left")
        fig.text(0.06, 0.01, "Negative values: the mode explains the measurements up to that arc less well than true track. "
                 + note, fontsize=7.5, color=MUTED, wrap=True)
        fig.tight_layout(rect=(0, 0.04, 1, 1))
        pdf.savefig(fig)
        plt.close(fig)

        # Page 2: BTO residual predictive distributions by mode, late arcs.
        fig, axes = plt.subplots(len(cases), len(late), figsize=(11.69, 3.6 * len(cases)), squeeze=False)
        grid = np.arange(-600, 600.1, 2.0)
        for r, case in enumerate(cases):
            for c, epoch in enumerate(late):
                ax = axes[r, c]
                sigma = sd[epoch]["bto_sd_us"]
                ax.axvspan(-sigma, sigma, color="#eceae4", lw=0)
                for m, (mode, col) in enumerate(zip(MODES, COLOURS)):
                    cols = data[case].get((mode, epoch))
                    if cols is not None:
                        ax.plot(grid, density(cols["bto_residual_us"], grid, 6.0), color=col, lw=1.2, label=LABELS[m])
                ax.set_title(f"{case}, {label(epoch)} arc (shaded: ±{sigma:.0f} µs)", loc="left")
                ax.set_xlabel("BTO residual, measured − predicted (µs)")
                ax.set_yticks([])
        axes[0, 0].legend(loc="upper left")
        fig.text(0.06, 0.01, "Predictive distribution of each mode's paths arriving at the arc (before its update). "
                 "Positive: the path is still inside the arc (too close to the satellite). " + note, fontsize=7.5, color=MUTED, wrap=True)
        fig.tight_layout(rect=(0, 0.03, 1, 1))
        pdf.savefig(fig)
        plt.close(fig)

        # Page 3: BFO innovations (BTO+BFO case).
        if "bto-bfo" in data:
            bfo_epochs = [e for e in ["m2141", "m2241", "m2315", "m0011"] if sd[e].get("bfo_hz") is not None]
            fig, axes = plt.subplots(1, len(bfo_epochs), figsize=(11.69, 3.8), squeeze=False)
            grid = np.arange(-80, 80.1, 0.5)
            for c, epoch in enumerate(bfo_epochs):
                ax = axes[0, c]
                ax.axvspan(-7, 7, color="#eceae4", lw=0)
                for m, (mode, col) in enumerate(zip(MODES, COLOURS)):
                    cols = data["bto-bfo"].get((mode, epoch))
                    if cols is not None:
                        ax.plot(grid, density(cols["bfo_innovation_hz"], grid, 1.5), color=col, lw=1.2, label=LABELS[m])
                ax.set_title(f"bto-bfo, {label(epoch)} (shaded: ±7 Hz)", loc="left")
                ax.set_xlabel("BFO innovation, measured − predicted − bias (Hz)")
                ax.set_yticks([])
            axes[0, 0].legend(loc="upper left")
            fig.text(0.06, 0.01, "Innovation relative to each path's current bias estimate; its predictive s.d. also includes "
                     "the bias uncertainty. " + note, fontsize=7.5, color=MUTED, wrap=True)
            fig.tight_layout(rect=(0, 0.04, 1, 1))
            pdf.savefig(fig)
            plt.close(fig)

        # Page 4: at 00:11, BTO residual and ground speed against latitude.
        fig, axes = plt.subplots(len(cases), 2, figsize=(11.69, 3.9 * len(cases)), squeeze=False)
        for r, case in enumerate(cases):
            for c, (column, name) in enumerate([("bto_residual_us", "BTO residual (µs)"), ("ground_speed_kt", "Ground speed (kt)")]):
                ax = axes[r, c]
                ax.axvspan(*SHOULDER, color="#f3e9dc", lw=0)
                for m, (mode, col) in enumerate(zip(MODES, COLOURS)):
                    cols = data[case].get((mode, "m0011"))
                    if cols is None:
                        continue
                    lat, y = cols["latitude_deg"], cols[column]
                    bins = np.arange(-42, -26.9, 0.5)
                    idx = np.digitize(lat, bins)
                    centres, med, lo, hi = [], [], [], []
                    for b in range(1, len(bins)):
                        v = y[idx == b]
                        if len(v) >= 200:
                            centres.append(0.5 * (bins[b - 1] + bins[b]))
                            q = np.quantile(v, [0.25, 0.5, 0.75])
                            lo.append(q[0]), med.append(q[1]), hi.append(q[2])
                    if centres:
                        ax.plot(centres, med, color=col, lw=1.3, label=LABELS[m])
                        ax.fill_between(centres, lo, hi, color=col, alpha=0.12, lw=0)
                if column == "bto_residual_us":
                    s = sd["m0011"]["bto_sd_us"]
                    ax.axhspan(-s, s, color="#eceae4", lw=0, zorder=0)
                ax.set_xlim(-40.5, -31)
                if column == "bto_residual_us":
                    ax.set_ylim(-600, 600)
                ax.set_xlabel("Latitude at 00:11 (°)")
                ax.set_ylabel(name)
                ax.set_title(f"{case}, 00:11: {name.split(' (')[0].lower()} by latitude (median, interquartile)", loc="left")
        axes[0, 0].legend(loc="best")
        fig.text(0.06, 0.01, f"Shaded vertical band: the published shoulder {SHOULDER[1]}° to {SHOULDER[0]}°. Particles from each mode's "
                 "predictive distribution at 00:11; bins with fewer than 200 particles omitted. " + note, fontsize=7.5, color=MUTED, wrap=True)
        fig.tight_layout(rect=(0, 0.03, 1, 1))
        pdf.savefig(fig)
        plt.close(fig)

        # Page 5: summary table.
        fig = plt.figure(figsize=(11.69, 8.27))
        fig.text(0.05, 0.95, "Predictive residual summary by mode and arc", fontsize=12, weight="bold", color=INK)
        header = ["case", "arc", "mode", "BTO mean (µs)", "BTO s.d. (µs)", "within ±1σ", "BFO mean (Hz)", "BFO s.d. (Hz)",
                  "ground speed (kt)", "median lat"]
        rows = []
        for case in cases:
            for epoch in late:
                for m, mode in enumerate(MODES):
                    cols = data[case].get((mode, epoch))
                    if cols is None:
                        continue
                    b = cols["bto_residual_us"]
                    f = cols["bfo_innovation_hz"]
                    has_bfo = np.isfinite(f).any()
                    s = sd[epoch]["bto_sd_us"]
                    rows.append([case, label(epoch), LABELS[m], f"{b.mean():+.0f}", f"{b.std():.0f}",
                                 f"{np.mean(np.abs(b) < s):.0%}", f"{np.nanmean(f):+.1f}" if has_bfo else "–",
                                 f"{np.nanstd(f):.1f}" if has_bfo else "–", f"{cols['ground_speed_kt'].mean():.0f}",
                                 f"{np.median(cols['latitude_deg']):.1f}"])
        xs = [0.05, 0.12, 0.17, 0.30, 0.39, 0.48, 0.56, 0.65, 0.74, 0.85]
        y = 0.91
        for x, h in zip(xs, header):
            fig.text(x, y, h, fontsize=7.5, weight="bold", color=MUTED)
        for row in rows:
            y -= 0.0215
            for x, v in zip(xs, row):
                fig.text(x, y, v, fontsize=7.2, color=INK)
        fig.text(0.05, 0.02, note, fontsize=7.5, color=MUTED, wrap=True)
        pdf.savefig(fig)
        plt.close(fig)
    print(out)


if __name__ == "__main__":
    main()
