"""Figure for results/searched-areas-run-j-a1branch (work order overnight-2026-10-19 B3). Run in a kernel where the figure-style
helpers (apply_figure_style, panel_letter) are loaded:  exec(open('make_figure.py').read())   with HERE, EXCH set."""
import json, pathlib, textwrap
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

R = json.loads((HERE / "a1branch-reduced.json").read_text())
PT = json.loads((EXCH / "point_terms.json").read_text())["seeds"]
DS = ["D0", "D1", "D2", "D3", "D4", "D5"]
TICK = {"D0": "00:19 held out", "D1": "R600 BTO only", "D2": "R600 BTO\n+ R600 BFO", "D3": "Both BFOs\nas recorded",
        "D4": "Both BFOs,\nHolland transient\nbias added", "D5": "R600 BFO + R1200\nBFO, Holland\ntransient bias added"}
BLUE, GREY = "#1f5aa6", "#8c8c8c"


def seed_se_A1(d):
    def sz(src, sub):
        z, w = [], []
        for s in PT:
            if s["check"]["src"] != src: continue
            t = s["terms"][d][sub]
            if t["m"] > 0: z.append(t["base_rho0.05"]["mP"] / t["m"]); w.append(t["m"])
        z, w = np.array(z), np.array(w); Z = (z * w).sum() / w.sum(); n = len(z)
        return float(np.sqrt(np.sum((w / w.sum()) ** 2 * (z - Z) ** 2) * n / (n - 1))), w.sum()
    sb, mb = sz("pass", "pass_all"); so, mo = sz("prod", "strat_A1")
    mb *= R["checks"]["SCALE"]; fb = mb / (mb + mo)
    return float(np.hypot(fb * sb, (1 - fb) * so))


apply_figure_style(sizes=(8, 7, 6))
TICK = {"D0": "00:19 data held out", "D1": "R600 BTO only", "D2": "R600 BTO + R600 BFO", "D3": "Both BFOs as recorded",
        "D4": "Both BFOs, Holland\ntransient bias added", "D5": "R600 BFO + R1200 BFO,\nHolland transient bias added"}
fig = plt.figure(figsize=(7.2, 6.4))
gs = fig.add_gridspec(1, 4, left=0.205, right=0.985, top=0.86, bottom=0.47, wspace=0.10)
ax = [fig.add_subplot(gs[0, j]) for j in range(4)]
y = -np.arange(6.0)
H = dict(s=16, zorder=3)
# a: the gate
a = ax[0]
rj = [R["point"][d]["base_rho0.05"]["run_j_published_waypoints"]["A1"]["ess_after"] for d in DS]
st = [R["point"][d]["base_rho0.05"]["stratified"]["A1"]["row_ess_after"] for d in DS]
pa = [R["point"][d]["base_rho0.05"]["stratified"]["A1"]["parent_ess_after"] for d in DS]
a.axvspan(100, 500, color="#c0392b", alpha=0.08, lw=0); a.axvline(500, color="#c0392b", lw=0.8, ls="--"); a.axvline(1000, color="#c0392b", lw=0.8, ls=":")
a.text(530, -5.5, "500", ha="left", fontsize=6, color="#c0392b"); a.text(1080, 0.62, "1,000", ha="left", fontsize=6, color="#c0392b")
a.scatter(rj, y + 0.15, color=GREY, marker="o", **H)
a.scatter(st, y - 0.15, color=BLUE, marker="o", **H)
a.scatter(pa, y - 0.15, facecolor="white", edgecolor=BLUE, marker="o", **H)
a.set_xscale("log"); a.set_xlim(150, 4e6)
a.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, _: {1e3: "1k", 1e4: "10k", 1e5: "100k", 1e6: "1M"}.get(v, "")))
a.set_xlabel("A1 effective sample\nsize after the searches")
a.set_title("A1 now passes the\n1,000 gate everywhere", loc="left")
# b: Z(A1)
b = ax[1]
zr = [R["point"][d]["base_rho0.05"]["run_j_published_waypoints"]["A1"]["Z"] for d in DS]
zs = [R["point"][d]["base_rho0.05"]["stratified"]["A1"]["Z"] for d in DS]
se = np.array([seed_se_A1(d) for d in DS])
zrs = [R["settled"][d]["A1"]["run_j_settled_published"]["Z_settled"] for d in DS]
zss = [R["settled"][d]["A1"]["scalar"]["base_rho0.05"]["Z_settled"] for d in DS]
b.scatter(zr, y + 0.27, color=GREY, marker="o", **H); b.scatter(zrs, y + 0.09, color=GREY, marker="s", **H)
b.errorbar(zs, y - 0.09, xerr=2 * se, fmt="o", color=BLUE, ms=4, lw=0.8, capsize=0, zorder=3); b.scatter(zss, y - 0.27, color=BLUE, marker="s", **H)
b.set_xlim(0.095, 0.15); b.set_xticks([0.10, 0.12, 0.14])
b.set_xlabel("A1 probability of\nno find, Z")
b.set_title("A1 search result: no\nchange beyond noise", loc="left")
# c: share on searched ground after the searches
c = ax[2]
for f, mk in (("A1", "o"), ("all", "D")):
    r_ = [R["settled"][d][f]["run_j_settled_published"]["on_searched_after_settled"] for d in DS]
    s_ = [R["settled"][d][f]["scalar"]["base_rho0.05"]["on_searched_after_settled"] for d in DS]
    c.scatter(r_, y + 0.15, color=GREY, marker=mk, **H); c.scatter(s_, y - 0.15, color=BLUE, marker=mk, **H)
c.set_xlim(0.2, 1.05)
c.set_xlabel("Share on searched\nseabed, after searches")
c.set_title("A1 stays on searched\nseabed; all types less", loc="left")
# d: per-cell field, A1, settled
dax = ax[3]
VV = [("V3_optimistic", "^"), ("V0_scalar", "o"), ("V1_central", "s"), ("V2_pessimistic", "v")]
for v, mk in VV:
    s_ = [R["settled"][d]["A1"]["variants"][v]["Z"] for d in DS]
    r_ = [R["settled"][d]["A1"]["run_j_spatial_published_mixture"][v]["Z"] for d in DS]
    dax.scatter(r_, y + 0.15, color=GREY, marker=mk, **H); dax.scatter(s_, y - 0.15, color=BLUE, marker=mk, **H)
dax.set_xlim(0.0, 0.4)
dax.set_xlabel("A1 Z, by\ndetection model")
dax.set_title("Detection level sets\nthe A1 result size", loc="left")
for i, axx in enumerate(ax):
    axx.set_ylim(-5.6, 0.95); axx.set_yticks(y)
    axx.set_yticklabels([TICK[d] for d in DS] if i == 0 else [])
    for yy in y[:-1] - 0.5: axx.axhline(yy, color="0.92", lw=0.5, zorder=0)
    panel_letter(axx, "abcd"[i], dx=-0.10 if i else -0.62, dy=1.16)
ax[0].text(-0.06, 1.02, "Use of the 00:19\nsatellite data", transform=ax[0].transAxes, fontsize=7, ha="right", va="bottom", color="0.3")
from matplotlib.lines import Line2D
L = lambda **k: Line2D([], [], ls="none", **k)
h1 = [L(marker="o", color=GREY, ms=4), L(marker="o", color=BLUE, ms=4), L(marker="o", mfc="white", mec=BLUE, ms=4)]
l1 = ["grey: run J main samples (both-BFO rows: both-burst supplement)", "blue: with the extra A1 run (stratified); bar = ±2 s.e. over seeds", "open: distinct parent tracks (a)"]
h2 = [L(marker="o", color="0.4", ms=4), L(marker="s", color="0.4", ms=4), L(marker="D", color="0.4", ms=4)]
l2 = ["circle: A1 at the impact point (a, b); A1 on the seabed (c)", "square: wreckage on the seabed (b)", "diamond: all flight-end types (c)"]
h3 = [L(marker=m, color="0.4", ms=4) for _, m in VV]
l3 = ["(d) per-cell, optimistic", "(d) one value per campaign", "(d) per-cell, central", "(d) per-cell, pessimistic"]
fig.legend(h1 + h2, l1 + l2, frameon=False, loc="upper left", bbox_to_anchor=(0.01, 0.395), ncol=2, fontsize=6, handletextpad=0.3, columnspacing=1.2)
fig.legend(h3, l3, frameon=False, loc="upper left", bbox_to_anchor=(0.01, 0.325), ncol=4, fontsize=6, handletextpad=0.3, columnspacing=1.2)
ste = ("Simplified English: A1 is a cruise to fuel exhaustion, then no control. A2 is a cruise to fuel exhaustion, then a controlled descent. "
       "B is a planned descent with a ditching approach that starts before fuel exhaustion. The main run J samples had too few A1 flights when both "
       "00:19 frequency values are used. An extra flight-end run sampled only the most important A1 case. We used its results in place of that part "
       "of the main samples, with a known scale factor. Now A1 has enough samples for every use of the 00:19 data (panel a). The search result for A1 "
       "and for all types together does not change by more than the sampling noise (b, c). The level of detection in each searched area changes the "
       "result much more than the samples do (d). The Ocean Infinity search areas come from community tracings and are a best estimate. Some parts of "
       "the flight-end physics are provisional.")
tech = ("Technical: Z = E[P(no find)] under the end-of-flight posterior; P = rho + (1 - rho) prod_k (1 - q_k f_k c_k), base = ATSB Phase 2 (q 0.945) + "
        "Bluefin-21 (0.9) + Ocean Infinity 2018 (0.9, f 0.889) + Ocean Infinity 2025-26 outboard band (0.9, f 0.7808), rho 0.05: Ocean Infinity "
        "coverage inferred (grade C), included as best estimate; planned next Ocean Infinity area not evidence. Source posterior: core run J (split-half "
        "accepted as a pass by project ruling, 16 Oct 2026), prior track = waypoint routes stratum only (core share 0.9982); end of flight run J "
        "production (24 seeds, 153.6 M rows) + A1-branch conditional pass (onset flame-out-associated, no intervention; 8 seeds, 13.4 M rows, seeds 2-8 "
        "Horvitz-Thompson thinned), stratified estimator, settling's single measure: pass mass x 0.14108, production branch rows 0, P_D0'(branch) = "
        "0.0935. Row mass option_table_0019 seed_terms, both log-on causes q = 1/3, C2 silent; held out = impact after 00:19:37.443 imposed; D4/D5 "
        "Holland transient bias added. Uncontrolled-arm dynamics not calibrated (Boeing leave-one-out gate failed); in-flight structural outcome and "
        "pitch-down PROVISIONAL. (a) Kish row ESS of m x P; parents = distinct hand-off parents; run J for both-BFO cells (3rd and 4th) from the "
        "both-burst supplement (8 seeds), else production. (b) impact point over all rows; seabed = settling run-j-a1branch (GLORYS12V1, ERA5, TEOS-10, "
        "AusSeabed/GEBCO_2026; breakup rows settled from the intact impact point; afloat pieces excluded), field 'mean', Z = point Z + paired difference. "
        "(c) settled. (d) per-cell model (q from ATSB 2017 Fig. 73 lower-confidence fraction, rho terrain-weighted, OI density from AIS); grey = run J "
        "spatial (four-strata mixture). Drift, hydroacoustic and other evidence not used.")
fig.text(0.015, 0.005, textwrap.fill(ste, 160) + "\n\n" + textwrap.fill(tech, 168), fontsize=6, ha="left", va="bottom", color="0.25")
for ext in ("png", "pdf"):
    fig.savefig(HERE / f"searched-areas-a1branch-gate.{ext}", dpi=300)
