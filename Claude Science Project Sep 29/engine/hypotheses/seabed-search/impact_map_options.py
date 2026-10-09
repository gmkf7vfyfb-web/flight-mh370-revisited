#!/usr/bin/env python3
"""Greyscale 50/90/99 % impact maps, before and after the seabed-search evidence, per 00:19 option.

    python hypotheses/seabed-search/impact_map_options.py <run-dir> <out-stem> [--columns k1,k2,...]

The project-convention map (greyscale highest-posterior-density bands with dark contour edges, the
6th and 7th arcs) for each 00:19 data option in turn, with the same option's posterior reweighted by
this module's non-detection likelihood beneath it. It answers two questions in one page: what the
search evidence does, and how much of the impact PDF's width is the 00:19 interpretation rather than
the search.

Two things are imported rather than copied, so there is one definition of each:
  * `option_posteriors` from end of flight's `smoke/displacement_hist.py` - the per-option weighting
    (hand-off weight x burst likelihood x the log-on lag density for the fuel-exhaustion cause). It is
    their contract, not mine, and drift reads it the same way.
  * the band shades, edge colours and HPD helper from their `smoke/displacement_greyscale.py`.
If either file moves this script fails loudly rather than drifting into a second house style.

**The search likelihood is computed once per seed, not once per option.** It is a function of impact
position alone, so every option reweights the same `seabed-search:loglik` column.

Writes <stem>.pdf, <stem>.png and <stem>.json (per option: evidence, median, HPD areas, mass on
searched ground, before and after).
"""

import argparse
import json
import pathlib
import subprocess
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator
from scipy.ndimage import gaussian_filter

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
EOF_SMOKE = ROOT / "hypotheses" / "end-of-flight" / "smoke"
if not (EOF_SMOKE / "displacement_hist.py").is_file():
    raise SystemExit(f"{EOF_SMOKE}/displacement_hist.py is missing: the option weighting is end of "
                     "flight's and is imported, not copied. Fix the path rather than duplicating it.")
sys.path.insert(0, str(EOF_SMOKE))
from displacement_hist import option_posteriors  # noqa: E402
from displacement_greyscale import hpd_levels, LEVELS, SHADES, EDGE, EDGE_W  # noqa: E402

BINARY = ROOT / "target" / "release" / "mh370"
GRID = 0.02          # degrees, as the house impact map
SMOOTH_DEG = 0.1     # 6 NM
R_KM = 6371.0072
LAT = (-44.0, -26.0)
LON = (82.0, 100.0)
ARCS = {"m0011": dict(lw=1.2, color="#b16286", label="6th arc, 00:11 UTC"),
        "m0019a": dict(lw=1.0, color="#4a6fa5", ls="--", label="7th arc, 00:19 UTC")}
# End of flight's OPTIONS list carries eight of the ten loglik columns in impacts.npy: both/no-offset
# and both/startup-offset are not among them, so "both" is shown with the inflated model.
DEFAULT = ["none__other", "r600_no-offset__fuel-exhaustion", "r600_startup-offset__fuel-exhaustion",
           "r1200_startup-offset__fuel-exhaustion", "both_inflated__fuel-exhaustion"]
TITLES = {"none__other": "Held out\n(no 00:19 data)",
          "r600_no-offset__fuel-exhaustion": "R600, raw",
          "r1200_no-offset__fuel-exhaustion": "R1200, raw",
          "both_no-offset__fuel-exhaustion": "Both, raw",
          "r600_startup-offset__fuel-exhaustion": "R600, Holland\nstart-up offset",
          "r1200_startup-offset__fuel-exhaustion": "R1200, Holland\nstart-up offset",
          "both_startup-offset__fuel-exhaustion": "Both, Holland\nstart-up offset",
          "r600_inflated__fuel-exhaustion": "R600, inflated",
          "r1200_inflated__fuel-exhaustion": "R1200, inflated",
          "both_inflated__fuel-exhaustion": "Both, inflated"}


def search_loglik(run, seed_dir, scratch):
    """This module's ln P(no find) for every impact of one seed, and its Phase 2 covered fraction."""
    out = scratch / f"evaluate-{seed_dir.name}"
    subprocess.run([str(BINARY), "evaluate", str(HERE / "run.toml"), str(seed_dir / "impacts.npy"), str(out)],
                   check=True, capture_output=True, cwd=ROOT)
    cols = json.loads((out / "evaluate.json").read_text())["columns"]
    v = np.load(out / "evaluate.npy")
    idx = {c: i for i, c in enumerate(cols)}
    ll = np.asarray(v[:, idx["seabed-search:loglik"]], float)
    cov = np.asarray(v[:, idx["seabed-search:covered_fraction_phase2-2014-2017"]], float)
    return ll, cov


def density(lat, lon, w):
    ny = int(round((LAT[1] - LAT[0]) / GRID))
    nx = int(round((LON[1] - LON[0]) / GRID))
    h, _, _ = np.histogram2d(lat, lon, bins=[ny, nx], range=[LAT, LON], weights=w)
    d = gaussian_filter(h, SMOOTH_DEG / GRID, mode="constant")
    s = d.sum()
    return d / s if s > 0 else d


def cell_area_km2():
    """Area of one grid cell per latitude row, on the authalic sphere."""
    ny = int(round((LAT[1] - LAT[0]) / GRID))
    edges = np.radians(LAT[0] + np.arange(ny + 1) * GRID)
    return (R_KM ** 2 * np.radians(GRID) * np.diff(np.sin(edges)))[:, None]


def hpd_areas(dens, levels):
    a = cell_area_km2()
    return [float((a * (dens >= lv)).sum()) for lv in levels]


def weighted_quantile(x, p, q):
    o = np.argsort(x)
    c = np.cumsum(p[o])
    return float(np.interp(q, c / c[-1], x[o]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run", type=pathlib.Path)
    ap.add_argument("stem")
    ap.add_argument("--columns", default=",".join(DEFAULT))
    ap.add_argument("--arcs", type=pathlib.Path, default=None, help="run.json carrying reference_arcs")
    a = ap.parse_args()
    keys = a.columns.split(",")
    meta = json.loads((a.run / "run.json").read_text())
    if any(c.startswith("seabed-search:") for c in meta["impact_columns"]):
        raise SystemExit(f"{a.run} already carries this module's likelihood: refusing to apply it twice.")
    arcs = {}
    src = a.arcs or (a.run / "run.json")
    try:
        arcs = {x["epoch"]: np.asarray(x["lat_lon"], float)
                for x in json.loads(pathlib.Path(src).read_text()).get("reference_arcs", [])}
    except Exception:
        arcs = {}

    seeds = sorted((a.run / "bto-bfo").glob("seed-*"))
    scratch = ROOT / "runs" / "seabed-search-analysis" / "scratch-maps"
    scratch.mkdir(parents=True, exist_ok=True)
    # Every option end of flight's helper yields is accumulated, so the table covers the full range
    # Pete asked for; --columns chooses only which of them are drawn.
    blank = lambda: {"before": None, "after": None, "z": 0.0, "on_p2_before": 0.0, "on_p2_after": 0.0,
                     "lat_b": [], "lat_a": [], "w_b": [], "w_a": []}
    acc = {}
    for seed in seeds:
        ll, cov = search_loglik(a.run, seed, scratch)
        like = np.exp(ll)
        for key, p, c in option_posteriors(a.run, seed):
            acc.setdefault(key, blank())
            after = p * like
            z = float(after.sum())
            after = after / z
            s = acc[key]
            s["z"] += z / len(seeds)
            s["on_p2_before"] += float((p * cov).sum()) / len(seeds)
            s["on_p2_after"] += float((after * cov).sum()) / len(seeds)
            for tag, w in (("before", p), ("after", after)):
                d = density(c["lat"], c["lon"], w) / len(seeds)
                s[tag] = d if s[tag] is None else s[tag] + d
            s["lat_b"].append(c["lat"]); s["w_b"].append(p / len(seeds))
            s["lat_a"].append(c["lat"]); s["w_a"].append(after / len(seeds))
        print(f"  {seed.name} done", flush=True)

    missing = [k for k in keys if k not in acc]
    if missing:
        raise SystemExit(f"not produced by end of flight's option_posteriors: {missing}\n"
                         f"available: {sorted(acc)}")
    report = {}
    for k in sorted(acc):
        s = acc[k]
        lat_b = np.concatenate(s["lat_b"]); w_b = np.concatenate(s["w_b"])
        lat_a = np.concatenate(s["lat_a"]); w_a = np.concatenate(s["w_a"])
        lv_b = hpd_levels(s["before"], LEVELS)
        lv_a = hpd_levels(s["after"], LEVELS)
        report[k] = {
            "evidence_z": s["z"], "mass_removed": 1.0 - s["z"],
            "on_phase2_before": s["on_p2_before"], "on_phase2_after": s["on_p2_after"],
            "median_lat_before": weighted_quantile(lat_b, w_b, 0.5),
            "median_lat_after": weighted_quantile(lat_a, w_a, 0.5),
            "hpd_km2_before": dict(zip(["99", "90", "50"], hpd_areas(s["before"], lv_b))),
            "hpd_km2_after": dict(zip(["99", "90", "50"], hpd_areas(s["after"], lv_a))),
        }

    ny, nx = acc[keys[0]]["before"].shape
    lat_c = LAT[0] + (np.arange(ny) + 0.5) * GRID
    lon_c = LON[0] + (np.arange(nx) + 0.5) * GRID
    fig, axs = plt.subplots(2, len(keys), figsize=(3.1 * len(keys), 7.4), sharex=True, sharey=True)
    axs = np.atleast_2d(axs)
    for j, k in enumerate(keys):
        for i, tag in enumerate(["before", "after"]):
            ax = axs[i, j]
            d = acc[k][tag]
            lv = hpd_levels(d, LEVELS)
            ax.grid(True, color="#e3e3e3", lw=0.6)
            ax.set_axisbelow(True)
            ax.contourf(lon_c, lat_c, d, levels=lv + [d.max()], colors=SHADES, antialiased=True)
            ax.contour(lon_c, lat_c, d, levels=lv, colors=EDGE, linewidths=EDGE_W)
            for e, st in ARCS.items():
                if e in arcs:
                    ax.plot(arcs[e][:, 1], arcs[e][:, 0], **{m: v for m, v in st.items() if m != "label"})
            ax.set_xlim(*LON)
            ax.set_ylim(*LAT)
            ax.xaxis.set_major_locator(MultipleLocator(4))
            ax.yaxis.set_major_locator(MultipleLocator(2))
            ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}°E"))
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{abs(v):.0f}°S"))
            ax.tick_params(labelsize=6)
            r = report[k]
            area = r["hpd_km2_after" if tag == "after" else "hpd_km2_before"]["90"]
            med = r["median_lat_after" if tag == "after" else "median_lat_before"]
            ax.text(0.97, 0.03, f"90 % area {area/1000:,.0f}k km²\nmedian {abs(med):.2f}°S",
                    transform=ax.transAxes, fontsize=6, color="#444444", ha="right", va="bottom")
            if i == 0:
                ax.set_title(TITLES.get(k, k), fontsize=7.5)
            if j == 0:
                ax.set_ylabel(("Impact PDF\n(no search evidence)" if tag == "before"
                               else "After the seabed searches\n(Phase 2 + Bluefin-21, ρ = 0.05)"), fontsize=7)
    bands = [Patch(facecolor=s, edgecolor=EDGE, lw=0.6, label=f"{int(f * 100)} % of probability")
             for s, f in zip(SHADES[::-1], LEVELS[::-1])]
    for e, st in ARCS.items():
        if e in arcs:
            bands.append(plt.Line2D([], [], color=st["color"], lw=st["lw"], ls=st.get("ls", "-"), label=st["label"]))
    fig.legend(handles=bands, loc="lower center", ncol=5, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, -0.005))
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(a.stem + ".pdf", bbox_inches="tight")
    fig.savefig(a.stem + ".png", dpi=200, bbox_inches="tight")
    pathlib.Path(a.stem + ".json").write_text(json.dumps(report, indent=1) + "\n")
    for k in sorted(report):
        r = report[k]
        print(f"{k:44s} Z {r['evidence_z']:.4f}  median {r['median_lat_before']:7.2f} -> {r['median_lat_after']:7.2f}"
              f"  90% area {r['hpd_km2_before']['90']/1000:7.1f}k -> {r['hpd_km2_after']['90']/1000:7.1f}k km2"
              f"  on P2 {r['on_phase2_before']:.3f} -> {r['on_phase2_after']:.3f}")
    print("wrote", a.stem)


if __name__ == "__main__":
    main()
