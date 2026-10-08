"""Map of posterior routes against the waypoint stratum's fixes, shaded by coverage.

Usage: python report/waypoint_coverage_figure.py <coverage-dir> <run-dir> <out-stem>
"""
import csv, json, pathlib, sys
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator
from matplotlib.colors import Normalize
from matplotlib import cm
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from waypoint_coverage import load_fixes, load_region

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.linewidth": 0.6, "pdf.fonttype": 42})
cov, run, stem = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
data = pathlib.Path(__file__).resolve().parents[1] / "data"
fixes, region = load_fixes(data), load_region(data)
meta = json.loads((run / "run.json").read_text()); name = meta["config"]["name"]
rows = {r["fix"]: r for r in csv.DictReader(open(cov / "waypoint-coverage-fixes.csv")) if r["run"] == name}
paths = [r for r in csv.DictReader(open(cov / "waypoint-coverage-paths.csv")) if r["run"] == name]
anc = [int(r["distinct_positions_1nm"]) for r in csv.DictReader(open(cov / "route-ancestries.csv")) if r["run"] == name]
routes = np.concatenate([np.load(f) for f in sorted(run.glob("*/seed-*/routes.npy"))])
rng = np.random.default_rng(1)
show = routes[rng.choice(len(routes), 1500, replace=False)]

fig = plt.figure(figsize=(6.4, 9.4))
ax = fig.add_axes([0.06, 0.30, 0.74, 0.66])
for r in show:
    ax.plot(r[:, 1], r[:, 0], color="#9a9a9a", lw=0.25, alpha=0.25, zorder=1)
ax.plot([], [], color="#9a9a9a", lw=0.8, label="Posterior routes (1,500 of 16,000)")
poly = np.vstack([region, region[:1]])
ax.plot(poly[:, 1], poly[:, 0], color="black", lw=0.9, ls="--", zorder=2, label="Phase-3 sampling region")
norm = Normalize(0, 1); cmap = plt.get_cmap("viridis")
for n, r in rows.items():
    la, lo, s = float(r["lat"]), float(r["lon"]), float(r["share_within_25nm"])
    ax.scatter(lo, la, s=46, color=cmap(norm(s)), edgecolor="black", lw=0.6, zorder=4)
    # label offsets (deg): the FIR-boundary fixes stack on 94.42E, so they go right; NILAM below
    off = {"NILAM": (0.2, -0.55, "left"), "PIPOV": (-0.25, -0.15, "right"), "MUTMI": (0.25, 0.1, "left"),
           "BEDAX": (-0.25, 0.0, "right"), "LAGOG": (0.25, 0.1, "left")}.get(n, (0.3, -0.08, "left"))
    ax.annotate(n, (lo, la), xytext=(lo + off[0], la + off[1]), fontsize=6.6, ha=off[2], zorder=5)
ax.set_xlim(86.5, 100.5); ax.set_ylim(-16.0, 11.0)
ax.set_aspect(1.0)
ax.xaxis.set_major_locator(MultipleLocator(2)); ax.yaxis.set_major_locator(MultipleLocator(2))
ax.grid(True, color="#e6e6e6", lw=0.5); ax.set_axisbelow(True)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{abs(v):.0f}°{'S' if v < 0 else 'N' if v > 0 else ''}"))
ax.set_xlabel("longitude (°E)"); ax.set_ylabel("latitude")
ax.set_title("Waypoint fixes against the trajectories already generated", loc="left", fontsize=9)
ax.legend(loc="lower left", frameon=False, fontsize=6.6)
cax = fig.add_axes([0.71, 0.45, 0.022, 0.35])
cb = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
cb.set_label("share of posterior routes within 25 NM of the fix", fontsize=7); cb.ax.tick_params(labelsize=6.5)
n25 = sum(float(p["share_within_25nm"]) > 0 for p in paths); w25 = sum(float(p["share_within_25nm"]) >= 0.01 for p in paths)
n50 = sum(float(p["share_within_50nm"]) > 0 for p in paths)
lines = [
    f"Routes: {name}, 8 replicates x 2,000 posterior routes, one vertex every 10 min from 18:01:49 UTC, joined by straight chords. A chord cuts the corner of a turn, so 10 NM is below what the stored routes resolve; 25 NM is the working tolerance.",
    f"Fix shading: share of posterior routes passing within 25 NM. Every fix is labelled; LAGOG (phase-2 box reference) and NILAM (entry) lie outside the phase-3 region.",
    f"Candidate waypoint paths: {len(paths)} southbound sequences from NILAM, at most one fix per stage (FIR boundary / BEDAX-BULVA / ISBIX-POSOD / MUTMI-PIPOV / BEBIM). "
    f"Followed end to end within 25 NM by at least one route: {n25}; by at least 1% of the posterior: {w25}; within 50 NM by at least one route: {n50}. None within 10 NM.",
    f"Distinct route positions at 18:01, 18:11, 18:21, 18:31, 18:41 UTC: {', '.join(f'{a:,}' for a in anc[:5])}. The 16,000 routes descend from a few hundred ancestors through the turn region, so coverage there is thinner than the route count suggests.",
    "These are POSTERIOR routes: survivors of the BTO/BFO and fuel evidence. A fix no route reaches may be excluded by the data or may never have been proposed; the stored routes cannot tell the two apart.",
]
fig.text(0.02, 0.02, "\n".join(w for l in lines for w in textwrap.wrap(l, 112)), fontsize=6.3, va="bottom", ha="left", color="#333333", linespacing=1.4)
for ext in ("pdf", "png"):
    fig.savefig(f"{stem}.{ext}", dpi=200)
