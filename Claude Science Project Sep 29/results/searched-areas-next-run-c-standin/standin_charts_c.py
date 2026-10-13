#!/usr/bin/env python3
"""Charts for the run C stand-in (searched areas). Reads standin-runc.json and the mixture densities.

    python standin_charts_c.py <engine dir> <out dir>
"""
import json
import pathlib
import sys
import textwrap

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator

ENGINE = pathlib.Path(sys.argv[1]).resolve()
OUT = pathlib.Path(sys.argv[2]).resolve()
sys.path.insert(0, str(ENGINE / "hypotheses" / "seabed-search"))
import impact_map_options as imo  # noqa: E402

R = json.loads((OUT / "standin-runc.json").read_text())
D = np.load(OUT / "standin-runc-mixture-densities.npz")
KEYS = R["keys"]
NAMES = {"none__other+alive": "Held Out", "r600-bto__other+alive": "R600 BTO Only",
         "r600_no-offset__other+alive": "R600 BTO + Raw BFO",
         "both_startup-offset__fuel-exhaustion+alive": "Holland H1", "both_no-offset__other+alive": "Holland H2"}
STRATA = {"next-c-free": "free", "next-c-repro-radar": "Davey dynamics + radar", "next-c-descent-climb": "descent-climb",
          "next-c-routes": "routes"}
UNCONV = "run C NOT CONVERGED (free split-half 0.918 vs 0.924)"
FS = (8, 7, 6)
plt.rcParams.update({"font.size": FS[0], "axes.titlesize": FS[0], "axes.labelsize": FS[0], "xtick.labelsize": FS[2],
                     "ytick.labelsize": FS[2], "legend.fontsize": FS[1], "font.family": "DejaVu Sans"})

COMMON_TECH = (f"{UNCONV}. Source: end of flight's run C sweep (4 strata x 8 seeds, {sum(v['rows'] for s in R['seeds'].values() for v in s.values()):,} impacts) "
               "on core run C 00:11 hand-offs. Core P(family) passed in: free 0.589, Davey dynamics + radar 0.252, descent-climb 0.135, routes 0.024. "
               "Search likelihood: module run.toml (ATSB Phase 2 + Bluefin-21, detection probability 0.945 / 0.900, undetectable fraction rho 0.05, point target, "
               "Ocean Infinity excluded). 00:19 options with end of flight's +alive constraint (Holland H1: start-up offset, fuel-exhaustion log-on). "
               "End-of-flight labels: rapid descents above 6,500 ft/min and unloading not reachable by the model; residual roll P(left) 0.8 PROVISIONAL; "
               "trim at loss and two-tank takeover not applied. Compact impacts rebuilt for mh370 evaluate by the Pleiades stub (position only). "
               "No wreckage-field coverage (no run C settling samples). Architecture stand-in run; module to review.")


def footer(fig, plain, tech, top=0.22):
    """Two footnotes inside the bottom `top` fraction of the figure (<= 25 %), and the convergence tag top right."""
    fig.text(0.99, 0.995, "PROVISIONAL: " + UNCONV, ha="right", va="top", fontsize=FS[1], color="#b02418")
    w = int(fig.get_figwidth() * 19)
    fig.text(0.01, top - 0.01, "\n".join(textwrap.wrap("IN SIMPLE WORDS. " + plain, w)), fontsize=FS[2], va="top",
             ha="left", color="#222222", linespacing=1.35)
    n_plain = len(textwrap.wrap("IN SIMPLE WORDS. " + plain, w))
    y2 = top - 0.01 - n_plain * FS[2] * 1.35 / 72 / fig.get_figheight() - 0.012
    fig.text(0.01, y2, "\n".join(textwrap.wrap("TECHNICAL. " + tech, int(w * 1.12))), fontsize=FS[2] - 0.5, va="top",
             ha="left", color="#555555", linespacing=1.3)


# ---------- Figure 1: maps, re-weighted mixture, contact speed <= 212 m/s ----------
arcs = {x["epoch"]: np.asarray(x["lat_lon"], float)
        for x in json.loads((ENGINE / "runs" / "fixture-8" / "run.json").read_text()).get("reference_arcs", [])}
fig, axs = plt.subplots(2, 5, figsize=(15, 8.6), sharex=True, sharey=True)
ny, nx = D[f"{KEYS[0]}|v212|reweighted|before"].shape
lat_c = imo.LAT[0] + (np.arange(ny) + 0.5) * imo.GRID
lon_c = imo.LON[0] + (np.arange(nx) + 0.5) * imo.GRID
for j, k in enumerate(KEYS):
    m = R["mixtures"][k]["v212"]["reweighted"]
    for i, tag in enumerate(["before", "after"]):
        ax = axs[i, j]
        d = D[f"{k}|v212|reweighted|{tag}"].astype(float)
        lv = imo.hpd_levels(d, imo.LEVELS)
        ax.grid(True, color="#e3e3e3", lw=0.6); ax.set_axisbelow(True)
        ax.contourf(lon_c, lat_c, d, levels=lv + [d.max()], colors=imo.SHADES)
        ax.contour(lon_c, lat_c, d, levels=lv, colors=imo.EDGE, linewidths=imo.EDGE_W)
        for e, sty in imo.ARCS.items():
            if e in arcs:
                ax.plot(arcs[e][:, 1], arcs[e][:, 0], **{a: v for a, v in sty.items() if a != "label"})
        ax.set_xlim(*imo.LON); ax.set_ylim(*imo.LAT)
        ax.xaxis.set_major_locator(MultipleLocator(4)); ax.yaxis.set_major_locator(MultipleLocator(4))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}°E"))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{abs(v):.0f}°S"))
        area = m[f"hpd_km2_{tag}"]["90"]; med = m[f"median_lat_{tag}"]
        e = m["ess_before" if tag == "before" else "ess_after"]
        bad = not m["estimable"]
        ax.text(0.97, 0.03, f"90 % region {area / 1e3:,.0f}k km²\nmedian {abs(med):.2f}°S\nESS {e:,.0f}",
                transform=ax.transAxes, fontsize=FS[1], ha="right", va="bottom", color="#b02418" if bad else "#333333")
        if bad:
            for sp in ax.spines.values():
                sp.set_color("#b02418"); sp.set_linewidth(1.4)
            ax.text(0.5, 0.96, "not estimable: too few\neffective samples", transform=ax.transAxes, fontsize=FS[1],
                    color="#b02418", ha="center", va="top")
        if i == 0:
            ax.set_title(f"00:19 {NAMES[k]}", loc="left")
        if j == 0:
            ax.set_ylabel("Impact, before the seabed searches" if tag == "before" else "Impact, after the searches (no find)")
bands = [Patch(facecolor=s, edgecolor=imo.EDGE, lw=0.6, label=f"{int(f * 100)} % of probability")
         for s, f in zip(imo.SHADES[::-1], imo.LEVELS[::-1])]
bands += [plt.Line2D([], [], color=s["color"], lw=s["lw"], ls=s.get("ls", "-"), label=s["label"]) for e, s in imo.ARCS.items() if e in arcs]
fig.legend(handles=bands, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, 0.235))
fig.suptitle("Where the aircraft hit the water, before and after the seabed searches, for each 00:19 data option "
             "\n(contact speeds of 212 m/s or less, groups weighted by the 00:19 data)", x=0.01, y=0.995, ha="left", fontsize=FS[0])
fig.tight_layout(rect=(0, 0.26, 1, 0.95))
footer(fig, "Each column uses the 00:19 radio data in a different way. The top row shows where the aircraft hit the water. "
            "The bottom row shows the same after the seabed searches, which found nothing. Dark to light, the bands hold 50, 90 and 99 per cent "
            "of the probability. The searches take probability away from the searched ground, so the region usually gets larger. "
            "Impacts faster than 212 m/s are removed, because the model has no limit for structural failure. Columns 4 and 5 do not have "
            "sufficient samples. The calculation is not yet stable, so all values are provisional.",
       COMMON_TECH + " This page: contact speed |v| <= 212 m/s (1.25 VMO, ruling 20:35 -0600 10 Oct), weights re-normalised per seed; "
       "strata mixed by P_core x Zhat_00:19(stratum, option, ~v212) from end of flight's family_evidence.per_seed. 50/90/99 % HPD on a 0.02 deg grid "
       "smoothed at 0.1 deg; areas on the authalic sphere. ESS = Kish effective sample size of impacts, summed over seeds; not estimable if "
       "impact ESS or effective parents < 1,000.", top=0.215)
fig.savefig(OUT / "fig1-maps-reweighted-v212.png", dpi=200)
fig.savefig(OUT / "fig1-maps-reweighted-v212.pdf")
plt.close(fig)

# ---------- Figure 2: Z and 90 % region across the four mixture versions ----------
VERS = [("all", "fixed", "all impacts, core group weights", "#9a9a9a", "o"),
        ("all", "reweighted", "all impacts, weighted by 00:19 data", "#4a6fa5", "s"),
        ("v212", "fixed", "212 m/s or less, core group weights", "#d9a441", "D"),
        ("v212", "reweighted", "212 m/s or less, weighted by 00:19 data", "#b16286", "^")]
fig, axs = plt.subplots(1, 2, figsize=(11, 5.6))
y = np.arange(len(KEYS))[::-1]
for vi, (var, mix, lab, col, mk) in enumerate(VERS):
    off = (vi - 1.5) * 0.17
    zs = [R["mixtures"][k][var][mix]["evidence_z"] for k in KEYS]
    ar = [R["mixtures"][k][var][mix]["hpd_km2_after"]["90"] / 1e3 for k in KEYS]
    est = [R["mixtures"][k][var][mix]["estimable"] for k in KEYS]
    for yy, z, a, ok in zip(y + off, zs, ar, est):
        axs[0].plot(z, yy, mk, color=col, mfc=col if ok else "white", ms=5)
        axs[1].plot(a, yy, mk, color=col, mfc=col if ok else "white", ms=5)
    axs[0].plot([], [], mk, color=col, label=lab)
for k, yy in zip(KEYS, y):
    zz = [R["strata"][s][k]["v212"]["evidence_z"] for s in STRATA]
    axs[0].plot([min(zz), max(zz)], [yy - 0.42, yy - 0.42], color="#333333", lw=1.0)
axs[0].plot([], [], color="#333333", lw=1.0, label="range over the 4 groups (212 m/s or less)")
axs[0].plot([], [], "o", color="#777777", mfc="white", label="open marker: not estimable")
for ax in axs:
    ax.set_yticks(y); ax.set_yticklabels([f"00:19 {NAMES[k]}" for k in KEYS]); ax.margins(x=0.06, y=0.06)
    ax.grid(True, axis="x", color="#e3e3e3")
axs[1].set_yticklabels([])
axs[0].set_xlabel("Probability that the searches missed the aircraft (Z)")
axs[1].set_xlabel("Area of the 90 % region after the searches (thousand km²)")
axs[0].set_title("49-77 % of the probability is left after the searches\nfor the three estimable options", loc="left")
axs[1].set_title("The speed limit and the 00:19 weighting change the 90 % area\nby at most 7 % for the three estimable options", loc="left")
axs[0].legend(loc="lower right", frameon=False, fontsize=FS[2])
fig.tight_layout(rect=(0, 0.25, 1, 0.96))
footer(fig, "For each 00:19 data option, the left panel shows the probability that is left after the seabed searches, which found nothing. "
            "The right panel shows the area that holds 90 per cent of the probability after the searches. Four versions are shown: with all "
            "impacts or only impacts at 212 m/s or less, and with the groups of flight paths weighted by the core model only or also by the 00:19 data. "
            "Open markers are not estimable. All values are provisional.",
       COMMON_TECH + " Z = sum over impacts of posterior weight x P(no find); mixture Z linear in stratum weights. Fixed, <=212: P_core x kept fraction. "
       "Re-weighted: P_core x Zhat_00:19 (end of flight's per_seed; matches the published run C family-evidence ln Zhat for 3 strata, routes not published).",
       top=0.24)
fig.savefig(OUT / "fig2-z-area-versions.png", dpi=200)
fig.savefig(OUT / "fig2-z-area-versions.pdf")
plt.close(fig)

# ---------- Figure 3: weight above 212 m/s by family ----------
FAMS = [("A1", "#4a6fa5"), ("A2", "#d9a441"), ("B", "#b16286"), ("code 6 (deliberate onset, no intervention)", "#7a7a7a")]
FLAB = {"A1": "A1: fuel exhaustion, no control", "A2": "A2: fuel exhaustion, controlled descent",
        "B": "B: deliberate descent before exhaustion", "code 6 (deliberate onset, no intervention)": "deliberate start, no control (code 6)"}
fig, ax = plt.subplots(figsize=(9, 4.8))
for k, yy in zip(KEYS, y):
    left = 0.0
    wr = R["mixtures"][k]["all"]["fixed"]["weight_above_212_by_family"]
    for f, col in FAMS:
        v = wr.get(f, 0.0)
        ax.barh(yy, v, left=left, color=col, height=0.6, label=FLAB[f] if k == KEYS[0] else None)
        left += v
    ax.text(left + 0.004, yy, f"{wr['all']:.1%}", va="center", fontsize=FS[1])
ax.set_yticks(y); ax.set_yticklabels([f"00:19 {NAMES[k]}" for k in KEYS])
ax.set_xlabel("Share of the posterior weight with contact speed above 212 m/s (before the searches)")
ax.set_title("10-12 % of the weight is faster than 212 m/s for the estimable options (mostly A1);\n44-47 % for Holland H1 and H2 (mostly B)", loc="left")
ax.set_xlim(0, 0.56); ax.grid(True, axis="x", color="#e3e3e3")
ax.legend(loc="upper right", frameon=False, fontsize=FS[2])
fig.tight_layout(rect=(0, 0.25, 1, 0.96))
footer(fig, "The bars show how much of the probability belongs to impacts faster than 212 m/s, for each 00:19 data option. "
            "The colours show the type of flight end. The model has no limit for structural failure, so these impacts are not credible. "
            "They are removed in the other charts marked 212 m/s or less. All values are provisional.",
       COMMON_TECH + " Weight = posterior under the option (+alive), core P(family) fixed, before the search likelihood; family = end of flight's "
       "family4_code (1 A1, 2 A2, 3 B, 6 deliberate-no-intervention).", top=0.24)
fig.savefig(OUT / "fig3-weight-above-212.png", dpi=200)
fig.savefig(OUT / "fig3-weight-above-212.pdf")
plt.close(fig)
print("charts written")
