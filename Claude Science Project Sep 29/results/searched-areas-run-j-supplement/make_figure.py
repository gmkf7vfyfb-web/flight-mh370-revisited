"""Figure for results/searched-areas-run-j-supplement (work order overnight-2026-10-20 B3). Run where the figure-style helpers
(apply_figure_style, panel_letter) are loaded:  HERE = <this folder>; exec(open(HERE / 'make_figure.py').read())"""
import json, textwrap
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

R = json.loads((HERE / "supplement-reduced.json").read_text())
CELLS = ["D0", "D1", "D2", "D3", "D4", "D5", "D3s", "D4s", "D5s"]
TICK = {"D0": "00:19 data held out", "D1": "R600 BTO only", "D2": "R600 BTO + R600 BFO", "D3": "Both BFOs as recorded",
        "D4": "Both BFOs, Holland\ntransient bias added", "D5": "R600 BFO + R1200 BFO,\nHolland transient bias added",
        "D3s": "Both BFOs as recorded,\nother log-on cause only", "D4s": "Both BFOs, Holland bias added,\nother log-on cause only",
        "D5s": "R600 + R1200 BFO, Holland bias\nadded, other log-on cause only"}
BLUE, GREY = "#1f5aa6", "#8c8c8c"
SPLIT = ["searched", "north_of_25S", "beyond_25NM", "near_arc_unsearched"]
SPLITC = {"searched": "#1f5aa6", "north_of_25S": "#d95f02", "beyond_25NM": "#bdbdbd", "near_arc_unsearched": "#7570b3"}
SPLITL = {"searched": "on searched seabed", "north_of_25S": "north of 25 S, not searched", "beyond_25NM": "more than 25 NM from the arc, not searched",
          "near_arc_unsearched": "near the arc south of 25 S, not searched"}

apply_figure_style(sizes=(8, 7, 6))
fig = plt.figure(figsize=(7.2, 7.4))
gs = fig.add_gridspec(1, 4, left=0.215, right=0.985, top=0.885, bottom=0.44, wspace=0.16)
ax = [fig.add_subplot(gs[0, j]) for j in range(4)]
y = -np.arange(len(CELLS), dtype=float); H = dict(s=15, zorder=3)
pt = lambda d: R["point"][d]["scen"]["base_rho0.05"]

# a: Z, all families
a = ax[0]
for i, d in enumerate(CELLS):
    q = pt(d); rj = R["point"][d].get("run_j_alone_a8e819f")
    zs = R["settled"][d]["a1-stratified:all" if d in ("D3", "D4", "D5", "D3s", "D4s", "D5s") else "ruleB-waypoints:all"]["base_rho0.05"]["Z_settled"]
    zr = rj["all"]["Z"] if rj else q["alone_all"]["Z"]
    rjs = R["settled"][d].get("run_j_alone_a8e819f")
    a.scatter([zr], [y[i] + 0.2], color=GREY, marker="o", **H)
    if rjs: a.scatter([rjs["all"]["Z_settled"]], [y[i] + 0.07], color=GREY, marker="s", **H)
    a.scatter([q["all_eof_convention"]["Z"]], [y[i] - 0.07], color=BLUE, marker="o", **H)
    a.scatter([zs], [y[i] - 0.2], color=BLUE, marker="s", **H)
a.set_xlim(0.11, 0.33); a.set_xticks([0.15, 0.20, 0.25, 0.30])
a.set_xlabel("Z, probability of no\nfind (all types)")
a.set_title("The search result\nchanges little", loc="left")

# b: northern mass after the searches
b = ax[1]
for i, d in enumerate(CELLS):
    q = pt(d)
    for band, mk, dy in (("north33S", "o", 0.14), ("25-20S", "^", -0.14)):
        al, rb = q["alone_all"]["bands"][band]["after"], q["all_eof_convention"]["bands"][band]["after"]
        ia, ib = q["boot_alone_all"]["after"][band], q["boot_all_eof_convention"]["after"][band]
        b.errorbar([al], [y[i] + dy + 0.06], xerr=[[al - ia[0]], [ia[1] - al]], fmt=mk, color=GREY, ms=3.5, lw=0.7, capsize=0, zorder=2)
        b.errorbar([rb], [y[i] + dy - 0.06], xerr=[[rb - ib[0]], [ib[1] - rb]], fmt=mk, color=BLUE, ms=3.5, lw=0.7, capsize=0, zorder=3)
b.set_xlim(0, 0.105)
b.set_xlabel("Remaining share\nin the north")
b.set_title("North of 33 S gains in\n7 of 9 uses of the data", loc="left")

# c: band ESS after the searches (paths)
c = ax[2]
c.axvline(1000, color="#c0392b", lw=0.8, ls=":"); c.axvspan(10, 1000, color="#c0392b", alpha=0.06, lw=0)
for i, d in enumerate(CELLS):
    q = pt(d)
    for band, mk, dy in (("35-30S", "s", 0.22), ("30-25S", "D", 0.0), ("25-20S", "^", -0.22)):
        c.scatter([q["alone_all"]["bands"][band]["state_ess_after"]], [y[i] + dy], color=GREY, marker=mk, s=12, zorder=2)
        v = q["all_unstratified"]["bands"][band]["state_ess_after"]
        c.scatter([v], [y[i] + dy], color=BLUE, marker=mk, s=12, zorder=3, facecolor=BLUE if v >= 1000 else "white")
c.set_xscale("log"); c.set_xlim(15, 1.2e5)
c.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: {1e2: "100", 1e3: "1k", 1e4: "10k", 1e5: "100k"}.get(v, "")))
c.text(1080, 0.62, "1,000", fontsize=6, color="#c0392b", ha="left")
c.set_xlabel("Effective sample size\nafter searches (paths)")
c.set_title("Some northern bands\nstay below 1,000", loc="left")

# d: four-way split after the searches, rule B, base
dax = ax[3]
for i, d in enumerate(CELLS):
    s = pt(d)["all_eof_convention"]["split_after"]; left = 0.0
    for k in SPLIT:
        dax.barh(y[i], s[k], left=left, height=0.55, color=SPLITC[k], lw=0); left += s[k]
dax.set_xlim(0, 1.0); dax.set_xticks([0.5, 1.0])
dax.set_xlabel("Remaining share\n(all types)")
dax.set_title("Where the remaining\nprobability is", loc="left")

for i, axx in enumerate(ax):
    axx.set_ylim(y[-1] - 0.6, 0.85); axx.set_yticks(y)
    axx.set_yticklabels([TICK[d] for d in CELLS] if i == 0 else [])
    for yy in y[:-1] - 0.5: axx.axhline(yy, color="0.92", lw=0.5, zorder=0)
    panel_letter(axx, "abcd"[i], dx=-0.10 if i else -0.75, dy=1.15)
ax[0].text(-0.06, 1.02, "Use of the 00:19\nsatellite data", transform=ax[0].transAxes, fontsize=7, ha="right", va="bottom", color="0.3")
L = lambda **k: Line2D([], [], ls="none", **k)
h1 = [L(marker="o", color=GREY, ms=4), L(marker="o", color=BLUE, ms=4), L(marker="o", mfc="white", mec=BLUE, ms=4)]
l1 = ["grey: run J main samples alone", "blue: with the full northern supplement", "open: below 1,000 (c)"]
h2 = [L(marker="o", mfc="white", mec="black", ms=4), L(marker="^", mfc="white", mec="black", ms=4)]
l2 = ["(a) circle: impact point; square: wreckage on the seabed", "(b) circle: north of 33 S; triangle: 25-20 S; bar: 95 % seed interval"]
h3 = [L(marker="s", mfc="white", mec="black", ms=4), L(marker="D", mfc="white", mec="black", ms=4), L(marker="^", mfc="white", mec="black", ms=4)]
l3 = ["(c) 35-30 S", "(c) 30-25 S", "(c) 25-20 S"]
h4 = [mpl.patches.Patch(color=SPLITC[k]) for k in SPLIT]; l4 = [f"(d) {SPLITL[k]}" for k in SPLIT]
fig.legend(h1 + h2, l1 + l2, frameon=False, loc="upper left", bbox_to_anchor=(0.01, 0.375), ncol=2, fontsize=6, handletextpad=0.3, columnspacing=1.0)
fig.legend(h3 + h4, l3 + l4, frameon=False, loc="upper left", bbox_to_anchor=(0.01, 0.315), ncol=4, fontsize=6, handletextpad=0.3, columnspacing=0.8)

ste = ("Simplified English: The end-of-flight run now has extra samples of flights that end north of about 34 S. This chart shows the "
       "result of the seabed searches with and without these extra samples. The extra samples change the search result by a small amount (a). "
       "After the searches, more of the remaining probability is north of 33 S for most uses of the 00:19 data (b). In some northern bands the extra samples are still not "
       "sufficient when both 00:19 frequency values are used, mostly between 25 S and 20 S (c). Most of the remaining probability is either on "
       "searched seabed or more than 25 NM from the arc (d). A1 (cruise to fuel exhaustion, then no control) comes from two extra runs that "
       "sample only that type. The Ocean Infinity search areas come from community tracings and are a best estimate. Some parts of the "
       "flight-end physics are provisional.")
tech = ("Technical: Z = E[P(no find)]; P = rho + (1 - rho) prod_k (1 - q_k f_k c_k); base = ATSB Phase 2 (q 0.945) + Bluefin-21 (0.9) + OI 2018 (0.9, "
        "f 0.889) + OI 2025-26 outboard (0.9, f 0.7808), rho 0.05: Ocean Infinity coverage inferred (grade C), included as best estimate; planned "
        "next OI area not evidence. Source posterior: core run J (split-half accepted as a pass by project ruling, 16 Oct 2026), waypoint routes "
        "stratum only; end of flight rule B over all rows (n1 = 2,399,999 run J, n2 = 1,600,003 supplement, r_hat from core), reduced table "
        "impacts-ruleB.npz (2,408,038 rows, thinned with Horvitz-Thompson weights). A1 from end of flight's two conditional strata (no "
        "intervention: run J + first-half supplement pass; recovery attempted: run J paths only), end of flight's normalisation. Row mass: both "
        "log-on causes q = 1/3 with C2 silent, or 'other cause only' (C2 silent); D4/D5 Holland transient bias added. Uncontrolled-arm dynamics not "
        "calibrated; in-flight structural outcome PROVISIONAL. Grey: run J alone (all 153.6 M rows, A1 stratified, commit a8e819f) in (a); "
        "production alone on the reduced table in (b, c) and for the 'other cause only' rows. (b) seed bootstrap, 2,000 replicates, row weights "
        "fixed. (c) open = below 1,000 after the searches: both BFOs 35-30 S and 25-20 S, Holland bias 25-20 S, and 25-20 S under other cause only for both BFOs and Holland bias; paths = distinct hand-off rows per replicate (end of flight's distinct-state count is lower by up to 17 %). (d) impact point, "
        "arc distance from a 0.02 deg grid of end-of-flight values (p99 error 0.4 NM). Seabed: settling run-j-supplement (GLORYS12V1, ERA5, "
        "TEOS-10, AusSeabed/GEBCO_2026), field 'mean'. Drift, hydroacoustic and other evidence not used.")
fig.text(0.015, 0.005, textwrap.fill(ste, 160) + "\n\n" + textwrap.fill(tech, 160), fontsize=6, ha="left", va="bottom", color="0.25")
for ext in ("png", "pdf"):
    fig.savefig(HERE / f"searched-areas-supplement.{ext}", dpi=300)
