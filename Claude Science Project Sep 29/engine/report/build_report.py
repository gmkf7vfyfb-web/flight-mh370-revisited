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
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402

HERE = Path(__file__).resolve().parent
LAND = HERE / "ne_110m_land.geojson"

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


def save_page(pdf, fig, out):
    """Each page goes to the PDF and, for viewers that cannot open PDFs, to <out>-png/page-<n>.png."""
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
    hyp_text = "; ".join(f"{h['name']} ({', '.join(f'{k} = {v}' for k, v in h['parameters'].items())})" for h in hyps)
    wind_scale = run["config"].get("environment", {}).get("wind_scale", 1.0)
    sensitivity = wind_scale != 1.0
    conditions = " ".join(filter(None, [
        f"Hypotheses enabled: {hyp_text}." if hyps else "",
        f"Sensitivity run: nominal ERA5 wind scaled by {wind_scale:g} (wind-error process kept)." if sensitivity else "",
    ])) or "Base estimate: no hypotheses enabled."
    if "stratum" not in run["final_columns"]:
        conditions += (" Pooled by final autopilot mode (run predates the stratum column; biased for "
                       "lateral-navigation paths that reverted to heading hold).")
    variant = bool(hyps) or sensitivity
    COLUMNS = run["final_columns"]
    cfg = run["config"]
    case_seeds = {c["id"]: c.get("seeds") or cfg["seeds"] for c in cfg["cases"]}
    seeds = case_seeds["bto-bfo"]
    cases = {c: load_case(run_dir, c, s) for c, s in case_seeds.items()}
    bfo, bto = cases["bto-bfo"], cases.get("bto-only")
    base = None
    if args.baseline:
        base_run = json.loads((args.baseline / "run.json").read_text())
        base_cfg = base_run["config"]
        base_seeds = next(c.get("seeds") or base_cfg["seeds"] for c in base_cfg["cases"] if c["id"] == "bto-bfo")
        base = load_case(args.baseline.resolve(), "bto-bfo", base_seeds)
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
    split = bfo["split_half_overlap"]
    stability = (f". Pooling half of the replicates against the other half gives {split:.0%} overlap, so the "
                 "pooled curve does not depend materially on the random seed" if split >= 0.9 else
                 f". Pooling half of the replicates against the other half gives only {split:.0%} overlap, so "
                 "the pooled curve is not yet converged at this particle count")
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
        base_text = (f"\n\nRelative to the base estimate, the median moves {abs(shift):.2f}° "
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
        fig.text(0.08, 0.914, conditions, fontsize=9, color=INK if variant else MUTED, style="italic")
        y = text_block(fig, 0.08, 0.893, f"""
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
            ax2.plot(GRID, base["density"], color=MUTED, ls=(0, (1, 1.5)), lw=1.2, label="Base estimate (no hypotheses)")
        ax2.set_title("(b) BTO and BFO, compared with the published curve (note expanded scale)", loc="left", color=INK)
        ax2.legend(loc="upper right")
        for ax in (ax1, ax2):
            ax.set_ylabel("Probability density (per degree)")
            ax.set_ylim(bottom=0)
            ax.grid(axis="y", color="#e9e8e4", lw=0.5)
        ax2.set_xlim(-42, -32)
        ax2.set_xlabel("Latitude at 00:19 UTC (°)")
        text_block(fig, 0.08, 0.085, f"""
            Figure 1. Latitude pdf of the aircraft at 00:19:37 UTC, the form of Davey et al. Fig. 10.3. (a) BTO only.
            (b) BTO and BFO, with the published curve. Densities are weighted particle histograms smoothed with a {SMOOTH_DEG}° Gaussian;
            each particle carries its own altitude. Evidence: BTO at every epoch except the 18:39 and 23:15 C-channel
            calls; BFO (bottom only) at 18:28, 18:39, 19:41–22:41, 23:15 and 00:11. No fuel, debris, drift, search
            or end-of-flight evidence is used. {conditions}""", size=8, colour=MUTED, width=128)
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

        # Page 3: posterior checks against the book.
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

        # Page 4: method, convergence and reproduction.
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
    print(out)


if __name__ == "__main__":
    main()
