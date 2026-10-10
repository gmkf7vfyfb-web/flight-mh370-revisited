#!/usr/bin/env python3
"""Seabed-search pages: what the negative search evidence does to a run's impact samples.

    .venv/bin/python hypotheses/seabed-search/report.py [RUN] [--option OPTION]

RUN is a run with impact samples (default runs/fixture, from `make fixture`). Every likelihood
and coverage value comes from the module: for each scenario the script writes a small override
of run.toml and runs `mh370 evaluate` on each replicate's impacts.npy. The scenarios are the
rho sweep (the headline: rho decides how much probability stays on searched ground), the
Phase 2 detection probability q, the inferred Ocean Infinity 2018 layer (a labelled variant;
committed under coverage/, inferred and grade C), and each campaign alone and
added in the order the searches happened (rho 0).

Weights: each replicate's impact weights times exp(loglik:<OPTION>), the chosen 00:19 data
option (default none); replicates are pooled by adding their reweighted impacts, and the two
halves of the replicates give the split-half agreement. Impacts from the arc-kernel
placeholder are plumbing, and every page says so.

Writes runs/seabed-search-analysis/search-evidence.pdf and a PNG of each page.
"""

import argparse
import json
import shutil
import subprocess
import tomllib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "runs" / "seabed-search-analysis"
BINARY = ROOT / "target" / "release" / "mh370"
MODULE = "seabed-search"
OI_OVERRIDE = HERE / "ocean-infinity-2018.toml"
OI25_OVERRIDE = HERE / "ocean-infinity-2025.toml"
# Committed since Pete's ruling of 9 Oct 2026 (~18:30 UTC); see coverage/PROVENANCE.md for the
# grade-C inferred-coverage footnote every use of these two layers must carry.
OI_LAYER = HERE / "coverage" / "ocean-infinity-2018.cov"
OI25_LAYER = HERE / "coverage" / "ocean-infinity-2025.cov"
RHO_MEANING = ("rho is the chance that the wreck could not have been found even where the sonar looked: hidden by "
               "terrain, buried, or imaged but dismissed. ATSB's detection ratings (q) cover data quality; rho is what they do not.")
GRID = np.arange(-50.0, 50.0 + 1e-9, 0.05)  # summary.rs latitude grid
SMOOTH_DEG = 0.1  # summary.rs display kernel
RHO_SWEEP = [0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]
# Phase 2 as its four sensor campaigns rather than their union, for the repeat-search pair. The
# ATSB rated detection by region, not by sensor, so each carries run.toml's q: a declared
# assumption, not a measurement.
PER_SENSOR = [{"name": f"phase2-{s}", "layer": f"phase2-{s}", "detection_probability": 0.945}
              for s in ("deep-tow", "go-phoenix", "dhj", "auv")]
R_KM = 6371.0072  # authalic radius, as in prepare/build_coverage.py
# Planning detection probability for Davey eq. (11.2). 0.9 is Stone et al. (2014)'s deliberate cap
# on sensor detection probabilities, because estimates from specifications and operators "tend to be
# optimistic"; it is a planning assumption for ground not yet searched, not this module's q.
PLANNING_PD = 0.9


def override(rho=None, campaigns=None, dependence=None):
    """TOML text overriding the module's rho, miss dependence and/or campaign list (arrays replace)."""
    lines = [f"[hypotheses.{MODULE}]"]
    if rho is not None:
        lines.append(f"undetectable_probability = {rho!r}")
    if dependence is not None:
        lines.append(f"miss_dependence = {json.dumps(dependence)}")
    for c in campaigns or []:
        lines.append(f"[[hypotheses.{MODULE}.campaigns]]")
        lines += [f"{k} = {json.dumps(v)}" for k, v in c.items()]  # JSON scalars are valid TOML
    return "\n".join(lines) + "\n"


def scenarios(params, oi_campaigns, oi25=False):
    """(label, override text or path or None, kind). The first is run.toml itself."""
    base = params["campaigns"]
    with_q = lambda q: [dict(c, detection_probability=q) if c["layer"] == "phase2" else c for c in base]
    out = [("run.toml", None, "main")]
    out += [(f"rho {r:g}", override(rho=r), "rho") for r in RHO_SWEEP if r != params["undetectable_probability"]]
    out += [("Phase 2 q 0.90", override(campaigns=with_q(0.90)), "q"), ("Phase 2 q 0.98", override(campaigns=with_q(0.98)), "q")]
    # Repeat search: the same Phase 2 ground as four sensor campaigns instead of one union, so
    # that the 17,391 km2 the union hides is swept twice. The arms differ only there.
    split = PER_SENSOR + [c for c in base if c["layer"] != "phase2"]
    out.append(("Phase 2 split, shared misses", override(campaigns=split, dependence="shared"), "repeat"))
    out.append(("Phase 2 split, independent misses", override(campaigns=split, dependence="independent"), "repeat"))
    if oi25:
        out.append(("+ OI 2025-26 inferred, outboard band only", OI25_OVERRIDE, "oi25"))
    if oi_campaigns:
        out.append(("+ OI 2018 inferred, coverage 0.889", OI_OVERRIDE, "oi"))
        high = [dict(c, coverage_fraction=0.952) if c["name"] == "ocean-infinity-2018" else c for c in oi_campaigns]
        out.append(("+ OI 2018 inferred, coverage 0.952", override(campaigns=high), "oi"))
    # Each campaign alone and cumulatively, in the order the searches happened, at rho 0.
    order = sorted(oi_campaigns or base, key=lambda c: {"bluefin-2014": 0, "phase2-2014-2017": 1}.get(c["name"], 2))
    for k, c in enumerate(order):
        out.append((f"alone: {c['name']}", override(rho=0.0, campaigns=[c]), "alone"))
        out.append((f"adding, in order: {c['name']}", override(rho=0.0, campaigns=order[:k + 1]), "cumulative"))
    return out


def evaluate(impacts, extra, scratch):
    """Run the module on one impacts.npy; returns {column: values} for its columns."""
    configs = [str(HERE / "run.toml")]
    if isinstance(extra, str):
        path = scratch / "override.toml"
        path.write_text(extra)
        configs.append(str(path))
    elif extra is not None:
        configs.append(str(extra))
    out = scratch / "evaluate"
    subprocess.run([str(BINARY), "evaluate", *configs, str(impacts), str(out)], check=True, capture_output=True, cwd=ROOT)
    columns = json.loads((out / "evaluate.json").read_text())["columns"]
    values = np.load(out / "evaluate.npy")
    shutil.rmtree(out)
    return {c[len(MODULE) + 1:]: values[:, i] for i, c in enumerate(columns) if c.startswith(MODULE + ":")}


def candidate_areas(hist, bins, block=5, p_d=None):
    """Davey eq. (11.2), printed p. 101: for an area A searched with constant P_D,

        P(find during search of A) = P_D * integral_A p(x_final | Z) dx_final

    `hist` is a weighted 2-D histogram of the impacts (longitude, latitude) on the 0.1 deg
    `bins`; areas are square blocks of `block` cells. Returns the blocks sorted by probability
    of success, with their area on the authalic sphere, so the cumulative curve answers the
    planner's question: what chance of finding it, for how much ground.
    """
    p_d = PLANNING_PD if p_d is None else p_d
    xe, ye = bins
    nx, ny = (len(xe) - 1) // block, (len(ye) - 1) // block
    mass = hist[:nx * block, :ny * block].reshape(nx, block, ny, block).sum(axis=(1, 3))
    mass = mass / hist.sum()
    step = float(np.round(np.diff(ye)[0] * block, 6))
    south = ye[:ny * block:block]
    row_area = R_KM**2 * np.radians(step) * (np.sin(np.radians(south + step)) - np.sin(np.radians(south)))
    order = np.argsort(mass, axis=None)[::-1]
    out = []
    for flat in order[: (mass > 0).sum()]:
        i, j = np.unravel_index(flat, mass.shape)
        out.append({"west": float(xe[i * block]), "south": float(south[j]), "degrees": step,
                    "mass": float(mass[i, j]), "p_find": float(p_d * mass[i, j]), "km2": float(row_area[j])})
    return out


def smooth(hist):
    """summary.rs smooth_to_density: 0.05 deg histogram, 0.1 deg Gaussian, normalised."""
    k = np.arange(-8, 9) * 0.05
    kernel = np.exp(-0.5 * (k / SMOOTH_DEG) ** 2)
    d = np.convolve(hist, kernel / kernel.sum(), mode="same")
    return d / (d.sum() * 0.05)


def stats(d):
    cdf = np.cumsum(d) * 0.05
    q = lambda p: float(np.interp(p, np.r_[0.0, cdf], np.r_[GRID[0] - 0.025, GRID + 0.025]))
    return {"q025": q(0.025), "median": q(0.5), "q975": q(0.975)}


def overlap(p, q):
    return float(np.minimum(p, q).sum() * 0.05)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("run", nargs="?", type=Path, default=ROOT / "runs" / "fixture")
    parser.add_argument("--option", default="none", help="00:19 data option: a loglik:<option> column of impacts.npy")
    parser.add_argument("--cause", default="other", choices=["other", "fuel-exhaustion"],
                        help="log-on cause; fuel-exhaustion adds end of flight's section 6 log-on lag density")
    parser.add_argument("--constraint", default="", choices=["", "alive", "silent"],
                        help="end of flight's declared existence constraint, imported read-only from their "
                             "smoke/displacement_hist.py (PROVISIONAL-OVERNIGHT)")
    args = parser.parse_args()
    run = json.loads((args.run / "run.json").read_text())
    columns = run["impact_columns"]
    # Double-application guard (brief section 8). The residual PDF is a view over a source
    # posterior; applying this module to a posterior that already carries its own likelihood would
    # count the search evidence twice, and the result would look entirely normal.
    already = [c for c in columns if c.startswith(MODULE + ":")]
    if already:
        raise SystemExit(f"{args.run} already carries this module's likelihood ({', '.join(already)}): "
                         "it is a composed posterior, not a source. Refusing to apply the search evidence twice.")
    terminal = run["config"]["terminal"]["module"]
    label = (f"{terminal} impacts, a placeholder: plumbing, not evidence" if terminal == "arc-kernel"
             else f"impacts from end-of-flight module {terminal}")
    label += f"; 00:19 data option {args.option}, log-on cause {args.cause}"
    label += f", constraint +{args.constraint} (PROVISIONAL-OVERNIGHT)" if args.constraint else ""
    replicates = sorted((args.run / "bto-bfo").glob("seed-*/impacts.npy"), key=lambda p: int(p.parent.name[5:]))
    params = tomllib.loads((HERE / "run.toml").read_text())["hypotheses"][MODULE]
    oi = tomllib.loads(OI_OVERRIDE.read_text())["hypotheses"][MODULE]["campaigns"] if OI_LAYER.is_file() else None
    if oi is None:
        print(f"no {OI_LAYER}: the inferred Ocean Infinity 2018 variants are left out (run prepare/build_coverage.py)")
    cases = scenarios(params, oi, OI25_LAYER.is_file())
    subprocess.run(["cargo", "build", "--release", "-q"], check=True, cwd=ROOT)
    scratch = OUT / "scratch"
    scratch.mkdir(parents=True, exist_ok=True)

    half = len(replicates) // 2
    acc = {name: {"z": 0.0, "w2": 0.0, "hist": np.zeros((2, len(GRID))), "north_33": 0.0, "south_39_5": 0.0,
                  "on_p2": 0.0, "off_south": 0.0} for name in ["before"] + [c[0] for c in cases]}
    map_bins = [np.arange(82, 106.01, 0.1), np.arange(-44, -12.99, 0.1)]
    maps = {"before": 0.0, "run.toml": 0.0}
    samples = 0
    for i, path in enumerate(replicates):
        table = np.load(path)
        col = lambda name: table[:, columns.index(name)]
        lat, lon = col("latitude_deg"), col("longitude_deg")
        extra = 0.0
        if args.cause == "fuel-exhaustion" or args.constraint:
            import sys as _sys
            _sys.path.insert(0, str(ROOT / "hypotheses" / "end-of-flight" / "smoke"))
            import displacement_hist as _dh  # end of flight's definitions, imported not copied
            from scipy.special import gammaln as _gammaln
            logon = run["config"]["hypotheses"]["end-of-flight"]["logon"]
            if args.cause == "fuel-exhaustion":
                lag = logon["logon_unix_s"] - col("latent:realised_flameout_unix_s")
                with np.errstate(divide="ignore", invalid="ignore"):
                    lfe = ((logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"]
                           - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - _gammaln(logon["lag_shape"]))
                extra = extra + np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
            if args.constraint:
                extra = extra + _dh.constraint_log_factor(col, logon, args.cause, args.constraint)
        ll = col(f"loglik:{args.option}") + extra
        w = col("weight") * np.exp(ll - np.max(ll[np.isfinite(ll)]))
        w /= w.sum()
        runs = {name: evaluate(path, extra, scratch) for name, extra, _ in cases}
        cover = runs["run.toml"]["covered_fraction_phase2-2014-2017"]
        south, bins = lat < -39.5, np.floor((lat + 50.025) / 0.05).astype(np.int64)
        for name, like in [("before", np.ones_like(w))] + [(n, np.exp(r["loglik"])) for n, r in runs.items()]:
            if np.isnan(like).any():
                raise SystemExit(f"{name}: {np.isnan(like).sum()} samples not computed")
            wl = w * like
            a = acc[name]
            a["z"] += wl.sum() / len(replicates)
            a["w2"] += np.sum(wl**2)
            a["hist"][int(i >= half)] += np.bincount(bins, weights=wl, minlength=len(GRID))[:len(GRID)]
            a["north_33"] += wl[lat > -33.0].sum()
            a["south_39_5"] += wl[south].sum()
            a["on_p2"] += np.sum(wl * cover)
            a["off_south"] += np.sum((wl * (1 - cover))[south])
            if name in maps:
                maps[name] = maps[name] + np.histogram2d(lon, lat, bins=map_bins, weights=wl)[0]
        samples += len(w)
        print(f"  {path.parent.name}: {len(w):,} impacts, {len(cases)} evaluations", flush=True)
    shutil.rmtree(scratch)

    def result(name):
        a = acc[name]
        total = a["hist"].sum()
        d = smooth(a["hist"].sum(axis=0))
        halves = overlap(smooth(a["hist"][0]), smooth(a["hist"][1])) if half else float("nan")
        return {"z": a["z"], "density": d, "stats": stats(d), "split_half": halves, "ess": total**2 / a["w2"],
                **{k: a[k] / total for k in ("north_33", "south_39_5", "on_p2", "off_south")}}

    before = result("before")
    results = [(name, extra, kind, result(name)) for name, extra, kind in cases]
    lines = [label.upper(),
             f"Run {args.run.name}: {len(replicates)} replicates, {samples:,} impacts; before: median {before['stats']['median']:.2f}, "
             f"95% {before['stats']['q025']:.2f} to {before['stats']['q975']:.2f}; split-half {before['split_half']:.3f}; "
             f"Kish ESS {before['ess']:,.0f}; on Phase 2 coverage {before['on_p2']:.3f}", "",
             "Mass removed at rho 0 (1 - evidence):"]
    lines += [f"  {name:<44} {1 - r['z']:7.4f}" for name, _, kind, r in results if kind in ("alone", "cumulative")]
    lines += ["", f"{'scenario':<36} {'Z':>7} {'median':>7} {'q025':>7} {'q975':>7} {'N of 33S':>8} {'S of 39.5':>9} "
                  f"{'on P2':>6} {'ESS':>9} {'split':>6} {'vs before':>9}"]
    for name, _, kind, r in results:
        if kind in ("main", "rho", "q", "oi", "oi25", "repeat"):
            lines.append(f"{name:<36} {r['z']:7.4f} {r['stats']['median']:7.2f} {r['stats']['q025']:7.2f} {r['stats']['q975']:7.2f} "
                         f"{r['north_33']:8.3f} {r['south_39_5']:9.3f} {r['on_p2']:6.3f} {r['ess']:9,.0f} "
                         f"{r['split_half']:6.3f} {overlap(r['density'], before['density']):9.3f}")
    # The residual-PDF view: the same source posterior with the search evidence disabled and
    # applied, and Davey eq. (11.2) for every candidate area of either, ranked.
    areas = {"disabled": candidate_areas(maps["before"], map_bins),
             "residual": candidate_areas(maps["run.toml"], map_bins)}
    lines.append("")
    lines.append(f"Residual PDF view. Source posterior: {args.run.name}, 00:19 option {args.option}; search evidence")
    lines.append(f"applied with run.toml. Davey eq. 11.2 at a planning P_D of {PLANNING_PD:g} on {areas['residual'][0]['degrees']:g} deg blocks:")
    lines.append("rank  candidate area            residual mass  P(find)   km2   | same block, search disabled")
    disabled = {(a["west"], a["south"]): a for a in areas["disabled"]}
    for k, a in enumerate(areas["residual"][:8], 1):
        was = disabled.get((a["west"], a["south"]), {"mass": 0.0})["mass"]
        lines.append(f"{k:4d}  {a['south']:+6.2f} {a['west']:7.2f} E {a['degrees']:4.2f} deg "
                     f"{a['mass']:13.4f} {a['p_find']:8.4f} {a['km2']:6.0f}   | {was:.4f}")
    cum = np.cumsum([a["p_find"] for a in areas["residual"]])
    km2 = np.cumsum([a["km2"] for a in areas["residual"]])
    for target in (0.25, 0.5, 0.75):
        i = int(np.searchsorted(cum, target))
        if i < len(cum):
            lines.append(f"      P(find) {target:.0%} needs the best {i + 1} blocks, {km2[i]:,.0f} km2")
    print("\n".join(lines))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "search-evidence.json").write_text(json.dumps({
        "label": label, "run": str(args.run), "option": args.option, "planning_p_d": PLANNING_PD,
        "before": {k: v for k, v in before.items() if k != "density"},
        "scenarios": [{"label": n, "kind": kind, **{k: v for k, v in r.items() if k != "density"}} for n, _, kind, r in results],
        "candidate_areas": {k: v[:40] for k, v in areas.items()},
    }, indent=1) + "\n")
    pages(label, params, maps, map_bins, results, before, lines, areas)


def pages(label, params, maps, map_bins, results, before, lines, areas):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.colors import LogNorm

    by_name = {name: r for name, _, _, r in results}
    rho_main = params["undetectable_probability"]
    by_rho = {rho_main: by_name["run.toml"], **{float(n[4:]): r for n, _, kind, r in results if kind == "rho"}}
    main = by_name["run.toml"]
    base_style = dict(color="#52514e", ls=(0, (1, 1.5)), lw=1.2, label="Before (no search evidence)")
    warn = dict(fontsize=9.5, color="#b3261e")
    lat_range = (-44, -14)

    def save(fig, name, pdf):
        fig.savefig(OUT / f"search-evidence-{name}.png", dpi=110)
        pdf.savefig(fig)
        plt.close(fig)

    with PdfPages(OUT / "search-evidence.pdf") as pdf:
        # Page 1, the headline: rho decides how much probability stays on searched ground.
        fig, axs = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={"width_ratios": [1.35, 1]})
        ax = axs[0]
        ax.plot(GRID, before["density"], **base_style)
        for rho, colour in [(0.0, "#9cc3ec"), (rho_main, "#2a78d6"), (0.1, "#1d5aa6"), (0.2, "#0f3566")]:
            ax.plot(GRID, by_rho[rho]["density"], color=colour, lw=2.0 if rho == rho_main else 1.2,
                    label=f"rho {rho:g}" + (" (run.toml)" if rho == rho_main else ""))
        ax.set(xlim=lat_range, xlabel="Impact latitude (deg)", ylabel="Density (per deg)",
               title="Impact latitude with the Phase 2 and Bluefin searches as evidence")
        ax.legend(fontsize=7.5, loc="upper right")
        ax.grid(alpha=0.25, lw=0.5)
        ax = axs[1]
        rho = np.array(sorted(by_rho))
        on = np.array([by_rho[r]["on_p2"] for r in rho])
        off_south = np.array([by_rho[r]["off_south"] for r in rho])
        ax.stackplot(rho, 100 * on, 100 * off_south, 100 * (1 - on - off_south), colors=["#2a78d6", "#eb6834", "#1baf7a"],
                     edgecolor="white", linewidth=1.5,
                     labels=["on ground Phase 2 searched", "unsearched, south of 39.5 S", "unsearched, elsewhere"])
        ax.axvline(rho_main, color="#52514e", ls=(0, (1, 1.5)), lw=1)
        ax.text(rho_main + 0.006, 50, f"run.toml (rho {rho_main:g}):\n{100 * main['on_p2']:.0f}% on searched ground",
                fontsize=7.5, color="white", va="center")
        ax.set(xlim=(0, rho.max()), ylim=(0, 100), xlabel="rho", ylabel="Share of the probability (%)",
               title=f"Where the probability goes (before: {100 * before['on_p2']:.0f}% on searched ground)")
        ax.legend(fontsize=7.5, loc="lower right", framealpha=0.9)
        fig.suptitle(label, **warn)
        why = (f"At rho 0, {100 * by_rho[0.0]['on_p2']:.0f}% stays on searched ground; {100 * (1 - before['on_p2']):.1f}% "
               "of the impacts before the search lie off it.")
        fig.text(0.5, 0.005, RHO_MEANING + "\n" + why, ha="center", va="bottom", fontsize=8, color="#52514e")
        fig.tight_layout(rect=(0, 0.07, 1, 0.96))
        save(fig, "rho", pdf)

        # Page 2: the detection probability q and the inferred Ocean Infinity 2018 layer.
        fig, ax = plt.subplots(figsize=(11, 5.2))
        ax.plot(GRID, before["density"], **base_style)
        ax.fill_between(GRID, by_name["Phase 2 q 0.90"]["density"], by_name["Phase 2 q 0.98"]["density"],
                        color="#2a78d6", alpha=0.18, lw=0, label="Phase 2 q from 0.90 to 0.98")
        ax.plot(GRID, main["density"], color="#2a78d6", lw=2.0, label=f"run.toml: Phase 2 q 0.945, Bluefin q 0.9, rho {rho_main:g}")
        for name, colour in [("+ OI 2018 inferred, coverage 0.889", "#eb6834"), ("+ OI 2018 inferred, coverage 0.952", "#1baf7a")]:
            if name in by_name:
                ax.plot(GRID, by_name[name]["density"], color=colour, lw=1.3, label=name + " (q 0.9)")
        ax.set(xlim=lat_range, xlabel="Impact latitude (deg)", ylabel="Density (per deg)",
               title="Detection probability q, and the inferred Ocean Infinity 2018 layer (labelled variant)")
        ax.legend(fontsize=7.5, loc="upper right")
        ax.grid(alpha=0.25, lw=0.5)
        fig.suptitle(label, **warn)
        fig.tight_layout()
        save(fig, "variants", pdf)

        # Page 3: impacts before and after (run.toml), with the Phase 2 coverage outline.
        fig, axs = plt.subplots(1, 2, figsize=(13, 6.5), sharex=True, sharey=True)
        xe, ye = map_bins
        for ax, h, title in [(axs[0], maps["before"], "Before"), (axs[1], maps["run.toml"], "After (run.toml)")]:
            h = h / h.sum()
            im = ax.imshow(np.ma.masked_less(h.T, 1e-7), origin="lower", extent=[xe[0], xe[-1], ye[0], ye[-1]],
                           cmap="magma_r", norm=LogNorm(1e-6, 3e-2), interpolation="nearest",
                           aspect=1 / np.cos(np.radians(33)))
            ax.set(title=f"{title}: share of impacts per 0.1 deg cell", xlabel="Longitude (deg E)",
                   xlim=(83, 98), ylim=(-41.5, -31.5))
        axs[0].set_ylabel("Latitude (deg)")
        fig.colorbar(im, ax=axs, shrink=0.8, label="share of the probability per 0.1 deg cell")
        fig.suptitle(label, **warn)
        save(fig, "map", pdf)

        # Page 4, the residual-PDF view: what the search leaves, and Davey eq. (11.2) over it.
        fig, axs = plt.subplots(1, 2, figsize=(13, 5.6))
        ax = axs[0]
        for key, colour, name in [("disabled", "#52514e", "search evidence disabled"),
                                  ("residual", "#2a78d6", "residual (search evidence applied)")]:
            cum = np.cumsum([a["p_find"] for a in areas[key]])
            km2 = np.cumsum([a["km2"] for a in areas[key]])
            ax.plot(km2 / 1000.0, cum, color=colour, lw=1.8 if key == "residual" else 1.2,
                    ls="-" if key == "residual" else (0, (1, 1.5)), label=name)
        ax.set(xlim=(0, 400), ylim=(0, 1), xlabel="Ground searched, best areas first (thousand km2)",
               ylabel="P(find)", title=f"Davey eq. 11.2: probability of success, planning P_D {PLANNING_PD:g}")
        ax.legend(fontsize=7.5, loc="lower right")
        ax.grid(alpha=0.25, lw=0.5)
        ax = axs[1]
        top = areas["residual"][:12]
        disabled = {(a["west"], a["south"]): a["mass"] for a in areas["disabled"]}
        y = np.arange(len(top))[::-1]
        ax.barh(y + 0.18, [disabled.get((a["west"], a["south"]), 0.0) for a in top], height=0.36,
                color="#b9b8b4", label="before (search disabled)")
        ax.barh(y - 0.18, [a["mass"] for a in top], height=0.36, color="#2a78d6", label="residual")
        ax.set_yticks(y)
        ax.set_yticklabels([f"{a['south']:+.1f} {a['west']:.1f}E" for a in top], fontsize=7)
        ax.set(xlabel=f"Share of the probability in a {top[0]['degrees']:g} deg block",
               title="The best candidate areas, and what the search did to them")
        ax.legend(fontsize=7.5, loc="lower right")
        ax.grid(alpha=0.25, lw=0.5, axis="x")
        fig.suptitle(label, **warn)
        fig.text(0.5, 0.005, "A residual view, not a second pipeline: the same source posterior with this module's "
                 "likelihood column applied and withheld. It names its source and must never be run on a posterior "
                 "that already carries the column.", ha="center", va="bottom", fontsize=8, color="#52514e")
        fig.tight_layout(rect=(0, 0.05, 1, 0.95))
        save(fig, "residual", pdf)

        fig = plt.figure(figsize=(12, 7.5))
        fig.text(0.02, 0.97, "Seabed search evidence: numbers", fontsize=12, va="top")
        fig.text(0.02, 0.91, "\n".join(lines), family="monospace", fontsize=7.2, va="top")
        save(fig, "numbers", pdf)
    print(f"wrote {OUT / 'search-evidence.pdf'}")


if __name__ == "__main__":
    main()
