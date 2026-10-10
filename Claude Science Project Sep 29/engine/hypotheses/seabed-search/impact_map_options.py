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
import displacement_hist as dh  # noqa: E402
from displacement_hist import option_posteriors  # noqa: E402
from displacement_greyscale import hpd_levels, LEVELS, SHADES, EDGE, EDGE_W  # noqa: E402

# End of flight's `option_posteriors` now reads every `loglik:` column from the run itself and derives
# the BTO-only arms (`derived_logliks`), so this script no longer widens their list or derives anything
# of its own: there is one definition of each, and it is theirs. It also takes the declared existence
# constraints (`+alive`, `+silent`), which are passed straight through.

# Kish effective sample size below which a 50/90/99 % area on a 0.02 deg grid is not estimable.
# A panel under this floor is drawn, because the speckle is the diagnostic, but it is labelled
# NOT ESTIMABLE and its numbers are reported as unconverged rather than as results.
ESS_FLOOR = 1000.0

BINARY = ROOT / "target" / "release" / "mh370"
GRID = 0.02          # degrees, as the house impact map
SMOOTH_DEG = 0.1     # 6 NM
R_KM = 6371.0072
# Latitude quantile histogram. Its range is deliberately WIDER than the plotted window: impacts lie
# outside LAT and a histogram clipped to the window would silently condition the median on what is
# drawn. 0.005 deg bins, far finer than the 0.1 deg smoothing.
QRANGE = (-70.0, -5.0)
QN = 13000
LAT = (-44.0, -26.0)
LON = (82.0, 100.0)
QLAT = None          # bin centres, set once LAT is known
QLAT = QRANGE[0] + (np.arange(QN) + 0.5) * (QRANGE[1] - QRANGE[0]) / QN
ARCS = {"m0011": dict(lw=1.2, color="#b16286", label="6th arc, 00:11 UTC"),
        "m0019a": dict(lw=1.0, color="#4a6fa5", ls="--", label="7th arc, 00:19 UTC")}
# The four arms of the comparison Pete asked for, in his order. The log-on cause is paired with the
# BFO model as Holland pairs them: his Hypothesis 1 is the start-up transient after a fuel-exhaustion
# power interruption, his Hypothesis 2 is some other log-on cause and no transient. Cross terms are
# computed and reported in the JSON but are not combinations Holland puts forward.
DEFAULT = ["none__other+alive", "r600_no-offset__other+alive",
           "both_startup-offset__fuel-exhaustion+alive", "both_no-offset__other+alive"]
TITLES = {
    "none__other+alive": "1. Held out\nno 00:19 observation, +alive",
    "r600_no-offset__other+alive": "2. R600 as observed\nBTO 18,400 µs + BFO 182 Hz, +alive",
    "both_startup-offset__fuel-exhaustion+alive": "3. Holland H1\nstart-up transient, fuel exhaustion, +alive",
    "both_no-offset__other+alive": "4. Holland H2\nboth BFOs raw, other cause, +alive",
    "none__other": "1. Held out\nno 00:19 observation at all",
    "r600-bto__other": "R600 BTO arc only\n(derived)",
    "r600_no-offset__other": "2. R600 as observed\nBTO 18,400 µs + BFO 182 Hz",
    "both_startup-offset__fuel-exhaustion": "3. Holland H1\nstart-up transient, fuel exhaustion",
    "both_no-offset__other": "4. Holland H2\nboth BFOs raw, other log-on cause",
    "both_inflated__fuel-exhaustion": "5. Inflated sensitivity\nindependent 34 Hz",
}


FOOTNOTE = """\
OBSERVATIONS  engine/data/satcom-observations.csv, from the released unredacted SITA/Inmarsat logs.  00:19:29.416 UTC, R600 log-on request: BTO 18,400 µs — the raw 23,000 µs less the standard −4,600 µs R600 log-on-channel
correction — sd 63 µs; BFO 182 Hz, tabulated sd 7 Hz.  00:19:37.443 UTC, R1200 log-on acknowledge: BFO −2 Hz, tabulated sd 7 Hz.  Its BTO (raw 49,660 µs, corrected by 4 × 7,820 µs after Davey §5.2 to 18,380 µs) is the anomalous
value and is EXCLUDED from every panel.  The constant BFO bias is Davey's 150 ± 25 Hz prior marginalised per particle, so the two 00:19 BFOs are scored JOINTLY and not as independent readings: ln L(both) − ln L(R600) − ln L(R1200)
is not a constant, ranging over ≈1,560 nats across seed 1.  The filter's effective BFO sd is 7.38 Hz (the tabulated 7 Hz variance plus a fixed 5.4 Hz²), recovered by exact reconstruction of the engine's log-likelihood (R² = 1).

PANELS, left to right.  (1) No 00:19 observation at all — neither BFO and not the BTO arc; everything up to and including the 00:11 arc, with the fuel, dynamics and control model.  (2) The 00:19:29 BTO and BFO at face value.
(3) Holland's Hypothesis 1 (arXiv:1702.02432v3 §V, §VI): the SDU oscillator warming up after a power interruption, putting the acknowledge 17–130 Hz and the request a further 0–6 Hz above a steady oscillator — uniform, positive and
shared between the bursts — paired with the fuel-exhaustion log-on cause, which also applies the §6 log-on lag density.  (4) Holland's Hypothesis 2: some other log-on cause (software failure, loss of a critical SDU input, or attitude
blocking the line of sight), so both BFOs at face value with no transient, and no lag density.  Panel 2 → panel 4 is the increment from adding the 00:19:37 BFO under H2; panel 3 against panel 4 is Holland's two hypotheses.
Holland himself used these bounds to bound the DESCENT RATE, not position; the ATSB took that result as the ±25 NM corridor width and a descent kernel, never as a likelihood along the arc, so no panel here reproduces the ATSB's use.

LOWER ROW, the seabed-search evidence.  ATSB Phase 2 union 120,486.5 km² (deep-tow side-scan, GO Phoenix and Dong Hai Jiu SAS, AUV side-scan) plus Bluefin-21/Artemis 771.4 km²; coverage rasterised at 0.01°; detection probability
q = 0.945 Phase 2 and 0.900 Bluefin-21, conditional on a detectable target; undetectable fraction ρ = 0.05; point target — the size response g(W) is not yet implemented; shared miss dependence where campaigns overlap.
Ocean Infinity 2018 and 2025–26 are NOT included.  {PRIOR}  Bands are 50/90/99 % highest-posterior-density regions on a
0.02° grid smoothed at 0.1° (6 NM); areas on the authalic sphere.  **+alive**: end of flight's declared existence constraint, PROVISIONAL-OVERNIGHT, that the aircraft was airborne at 00:19:37.443 so
that the log-on acknowledge could be sent at all — a datum separate from that burst's BTO and BFO values.  It binds only on the held-out arm, which otherwise puts 10.2 % of its weight before that burst.

CONVERGENCE  Each panel is an importance-weighted reading of the SAME impacts (count in the PRIOR line above), which were not drawn with the 00:19 bursts in hand, so a sharp 00:19 likelihood collapses the weights.  ESS is the Kish effective
sample size of those weights.  A panel below 1,000 effective impacts is labelled NOT ESTIMABLE: its bands are the few surviving particles, not a posterior, and its area, median and evidence are reported as unconverged, not as
results.  Fixing it needs a proposal that already carries the 00:19 data, which is end of flight's to build, not a longer run of this one."""


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
    ap.add_argument("run", type=str,
                    help="a run directory, or several as `dir:weight,dir:weight,...` to pool strata by "
                         "P(family). Pooling is the only correct way to get a mixture median or area: "
                         "Z and the mass shares combine linearly across strata, densities do not.")
    ap.add_argument("stem")
    ap.add_argument("--columns", default=",".join(DEFAULT))
    ap.add_argument("--arcs", type=pathlib.Path, default=None, help="run.json carrying reference_arcs")
    ap.add_argument("--labels", default="",
                    help="extra labels appended to the chart footnote, e.g. the labels architecture "
                         "requires of every result built on core's (b) run")
    ap.add_argument("--constraints", default="alive",
                    help="comma-separated existence constraints from end of flight's displacement_hist "
                         "(alive, silent); each adds a `+<name>` key beside the plain one")
    a = ap.parse_args()
    keys = a.columns.split(",")
    parts = []
    for spec in a.run.split(","):
        d, _, w = spec.partition(":")
        parts.append((pathlib.Path(d), float(w) if w else 1.0))
    tw = sum(w for _, w in parts)
    parts = [(d, w / tw) for d, w in parts]
    a.run = parts[0][0]
    meta = json.loads((parts[0][0] / "run.json").read_text())
    if any(c.startswith("seabed-search:") for c in meta["impact_columns"]):
        raise SystemExit(f"{a.run} already carries this module's likelihood: refusing to apply it twice.")
    arcs = {}
    src = a.arcs or (a.run / "run.json")
    try:
        arcs = {x["epoch"]: np.asarray(x["lat_lon"], float)
                for x in json.loads(pathlib.Path(src).read_text()).get("reference_arcs", [])}
    except Exception:
        arcs = {}

    seeds = [(s, w) for d, w in parts for s in sorted((d / "bto-bfo").glob("seed-*"))]
    nseed = {d: len(sorted((d / "bto-bfo").glob("seed-*"))) for d, _ in parts}
    scratch = ROOT / "runs" / "seabed-search-analysis" / "scratch-maps"
    scratch.mkdir(parents=True, exist_ok=True)
    # Every option end of flight's helper yields is accumulated, so the table covers the full range
    # Pete asked for; --columns chooses only which of them are drawn.
    blank = lambda: {"before": None, "after": None, "z": 0.0, "on_p2_before": 0.0, "on_p2_after": 0.0,
                     "ess_b": 0.0, "ess_a": 0.0,
                     "lat_b": np.zeros(QN), "lat_a": np.zeros(QN)}
    acc = {}
    cons = tuple(x for x in a.constraints.split(",") if x)
    for seed, wfam in seeds:
        share = wfam / nseed[seed.parent.parent]   # family weight spread over that stratum's seeds
        ll, cov = search_loglik(seed.parent.parent, seed, scratch)
        like = np.exp(ll)
        for key, p, c in option_posteriors(seed.parent.parent, seed, constraints=cons):
            acc.setdefault(key, blank())
            after = p * like
            z = float(after.sum())
            after = after / z
            s = acc[key]
            s["z"] += z * share
            s["on_p2_before"] += float((p * cov).sum()) * share
            s["on_p2_after"] += float((after * cov).sum()) * share
            # Kish effective sample size of the importance weights, summed over seeds: the honest
            # measure of how many of the 3.2e6 impacts per seed actually carry this option's posterior.
            s["ess_b"] += float(1.0 / np.sum(p ** 2))
            s["ess_a"] += float(1.0 / np.sum(after ** 2))
            for tag, w in (("before", p), ("after", after)):
                d = density(c["lat"], c["lon"], w) * share
                s[tag] = d if s[tag] is None else s[tag] + d
            for tag, w in (("lat_b", p), ("lat_a", after)):
                s[tag] += np.histogram(c["lat"], bins=QN, range=QRANGE, weights=w * share)[0]
        print(f"  {seed.name} done", flush=True)

    missing = [k for k in keys if k not in acc]
    if missing:
        raise SystemExit(f"not produced by end of flight's option_posteriors: {missing}\n"
                         f"available: {sorted(acc)}")
    report = {}
    for k in sorted(acc):
        s = acc[k]
        lat_b, w_b = QLAT, s["lat_b"]
        lat_a, w_a = QLAT, s["lat_a"]
        lv_b = hpd_levels(s["before"], LEVELS)
        lv_a = hpd_levels(s["after"], LEVELS)
        report[k] = {
            "evidence_z": s["z"], "mass_removed": 1.0 - s["z"],
            "on_phase2_before": s["on_p2_before"], "on_phase2_after": s["on_p2_after"],
            "median_lat_before": weighted_quantile(lat_b, w_b, 0.5),
            "median_lat_after": weighted_quantile(lat_a, w_a, 0.5),
            "hpd_km2_before": dict(zip(["99", "90", "50"], hpd_areas(s["before"], lv_b))),
            "hpd_km2_after": dict(zip(["99", "90", "50"], hpd_areas(s["after"], lv_a))),
            "ess_before": s["ess_b"], "ess_after": s["ess_a"],
            "converged": bool(s["ess_a"] >= ESS_FLOOR),
        }

    rows = sum(np.load(s / "impacts.npy", mmap_mode="r").shape[0] for s, _ in seeds)
    ny, nx = acc[keys[0]]["before"].shape
    lat_c = LAT[0] + (np.arange(ny) + 0.5) * GRID
    lon_c = LON[0] + (np.arange(nx) + 0.5) * GRID
    fig, axs = plt.subplots(2, len(keys), figsize=(3.55 * len(keys), 8.9), sharex=True, sharey=True)
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
            e = r["ess_after" if tag == "after" else "ess_before"]
            bad = e < ESS_FLOOR
            ax.text(0.97, 0.03, f"90 % area {area/1000:,.0f}k km²\nmedian {abs(med):.2f}°S\n"
                                f"ESS {e:,.0f} of {rows:,}",
                    transform=ax.transAxes, fontsize=6, color="#b02418" if bad else "#444444",
                    ha="right", va="bottom")
            if bad:
                for sp in ax.spines.values():
                    sp.set_color("#b02418"); sp.set_linewidth(1.4)
                ax.text(0.5, 0.955, "NOT ESTIMABLE FROM THIS SAMPLE", transform=ax.transAxes,
                        fontsize=6.5, color="#b02418", ha="center", va="top", weight="bold")
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
    fig.legend(handles=bands, loc="lower center", ncol=5, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, 0.182))
    src = (", ".join(f"{d.name} ({w:.1%})" for d, w in parts) + " — the supplied stratum weights renormalised to 1"
           if len(parts) > 1 else parts[0][0].name)
    prior = meta.get("config", {}).get("prior", {})
    track = prior.get("track_deg")
    tzero = prior.get("time_utc", "")
    prior_line = (f"PRIOR  {src}: "
                  + (f"{track}° initial track at {tzero}, " if track else "")
                  + f"{len(seeds)} seed files, {rows:,} impacts in all.")
    note = FOOTNOTE.replace("{PRIOR}", prior_line) + ("\n\nLABELS  " + a.labels if a.labels else "")
    fig.text(0.008, 0.172, note, fontsize=5.4, color="#333333", ha="left", va="top",
             linespacing=1.45, family="DejaVu Sans")
    fig.tight_layout(rect=(0, 0.20, 1, 1))
    fig.savefig(a.stem + ".pdf", bbox_inches="tight")
    fig.savefig(a.stem + ".png", dpi=200, bbox_inches="tight")
    pathlib.Path(a.stem + ".json").write_text(json.dumps(report, indent=1) + "\n")
    for k in sorted(report):
        r = report[k]
        print(f"{k:44s} Z {r['evidence_z']:.4f}  median {r['median_lat_before']:7.2f} -> {r['median_lat_after']:7.2f}"
              f"  90% area {r['hpd_km2_before']['90']/1000:7.1f}k -> {r['hpd_km2_after']['90']/1000:7.1f}k km2"
              f"  on P2 {r['on_phase2_before']:.3f} -> {r['on_phase2_after']:.3f}"
              f"  ESS {r['ess_before']:11,.0f} -> {r['ess_after']:11,.0f}"
              f"{'' if r['converged'] else '   UNCONVERGED'}")
    print("wrote", a.stem)


if __name__ == "__main__":
    main()
