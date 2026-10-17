import json, ast, textwrap, statistics as st, numpy as np, matplotlib as mpl, matplotlib.pyplot as plt
W = "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/370552c2-5cc9-44d0-86c9-507ea022948e"
R = W + "/repo/Claude Science Project Sep 29/results/"
mpl.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.titlelocation": "left", "figure.dpi": 300,
                     "savefig.dpi": 300, "font.family": "DejaVu Sans"})
FCOL = {"A1": "#E69F00", "A2": "#9a9a9a", "B": "#332288"}
DS = ["D0", "D1", "D2", "D3", "D4", "D5"]
DSH = {"D0": "No 00:19\nvalues", "D1": "Timing\nonly", "D2": "Timing +\nfirst\nfrequency", "D3": "Timing +\nboth\nfrequencies",
       "D4": "Both\nfrequencies,\ntransient\nbias", "D5": "Both\nfrequencies,\nsecond\noffset"}
def fam(path, D):
    c = json.load(open(path))["cells"][f"{D} total q=0.333 (C2 silent)"]["families"]
    if isinstance(c, str): c = ast.literal_eval(c)
    return {k: c[k]["share"] for k in ("A1", "A2", "B")}
runI = {D: fam(R + "eof-run-i-dive-oct13/table-0019-mixture.json", D) for D in DS}
runJ = {D: fam(R + "eof-run-j-oct17/table-0019-mixture.json", D) for D in DS}
for D in ("D3", "D4"):   # better-sampled supplementary pass for the both-burst cells
    runJ[D] = fam(R + "eof-run-j-waypoints-oct16/table-0019-supplementary-8.json", D)
fig = plt.figure(figsize=(7.2, 4.2))
a1 = fig.add_axes([0.07, 0.44, 0.56, 0.44]); a2 = fig.add_axes([0.74, 0.44, 0.24, 0.44])
for i, D in enumerate(DS):
    for j, (lab, src) in enumerate((("I", runI), ("J", runJ))):
        x = i + (j - 0.5) * 0.36; bot = 0
        for f in ("A1", "A2", "B"):
            v = src[D][f]; a1.bar(x, v, 0.32, bottom=bot, color=FCOL[f], edgecolor="white", lw=0.5)
            if v > 0.12: a1.text(x, bot + v / 2, f"{v:.2f}", ha="center", va="center", fontsize=5.5, color="white" if f != "A2" else "#222222")
            bot += v
        a1.text(x, 1.015, "run " + lab, ha="center", fontsize=5.5, color="#444444")
a1.set_xticks(range(6)); a1.set_xticklabels([DSH[D] for D in DS], fontsize=6); a1.set_ylim(0, 1.06); a1.set_xlim(-0.6, 5.6)
a1.set_ylabel("Family share")
a1.set_title("Family shares in the impact set from 00:11", pad=26)
for k, (f, l) in enumerate([("A1", "Fuel ends, no input"), ("A2", "Fuel ends, controlled"), ("B", "Planned descent after 00:11")]):
    a1.text(0.0 + k * 0.30, 1.065, "■ " + l, color=FCOL[f], fontsize=6.5, transform=a1.transAxes)
seeds_J = range(1, 17); seeds_I = range(1, 9)
def bshare(dirn, seeds, pr):
    return [json.load(open(f"{dirn}/seed-{k}.json"))["cells"]["D0"][pr]["B"]["share"] for k in seeds]
dI = R + "eof-order-b-oct15/onset-uniform"; dJ = R + "eof-run-j-joined-v2-oct17/onset-uniform"
rng = np.random.default_rng(2)
for j, (lab, d, ss) in enumerate((("run I", dI, seeds_I), ("run J", dJ, seeds_J))):
    for m, (pr, col, fill) in enumerate((("fe_tied", "#332288", True), ("uniform_U1", "#44AA99", True))):
        v = np.array(bshare(d, ss, pr)); xc = j + (m - 0.5) * 0.34
        a2.plot(xc + rng.uniform(-0.06, 0.06, len(v)), v, "o", ms=2.8, color=col, alpha=0.85)
        a2.plot([xc - 0.11, xc + 0.11], [np.median(v)] * 2, color=col, lw=2)
a2.set_xticks([0, 1]); a2.set_xticklabels(["run I\n(8 seeds)", "run J\n(16 seeds)"]); a2.set_xlim(-0.6, 1.6); a2.set_ylim(0, 0.40)
a2.set_ylabel("Planned-descent share, no 00:19 values")
a2.set_title("Joined estimate from 22:41", pad=26)
a2.text(0.02, 0.97, "● fuel-tied start (headline)", color="#332288", fontsize=6.5, transform=a2.transAxes, va="top")
a2.text(0.02, 0.91, "● uniform start (sensitivity)", color="#44AA99", fontsize=6.5, transform=a2.transAxes, va="top")
a1.text(-0.09, 1.13, "a", transform=a1.transAxes, fontsize=9, fontweight="bold"); a2.text(-0.30, 1.13, "b", transform=a2.transAxes, fontsize=9, fontweight="bold")
plain = ("Panel a: for each way of using the 00:19 data, the share of the three end-of-flight families in the earlier run (I) and the "
         "new run (J), in the impact set that starts at 00:11; there the planned-descent share is mostly set by the prior, so panel a is not a test of the families. Panel b: the share of planned descents when the 00:19 data are not used; each point is one independent run seed, "
         "the bar is the median. This joined estimate starts at 22:41 and is the one to quote. Both start-time rules give a higher planned-descent share on run J than on run I.")
tech = ("Two-factor totals, log-on cause mixture q = 1/3, cause C2 silent, transmission imposed; strata mixed by core P(family) (run J: "
        "waypoints 0.9982). Run I = run-i-dive (production laws, 90 deg cap); run J = round-3 laws + bank limit U[52, 90] deg (Pete 16 Oct), "
        "core inputs 24 seeds, BFO 4.32 Hz, kx. Run J D3/D4 from the 256-descent supplementary pass (8 seeds; ESS 6.3k / 44k). Panel b: joined V2 "
        "(22:41 + 00:11 arms), waypoints stratum; run J with the clock-time onset proposal window; U1 = onset uniform on [22:41, min(00:11, P)] "
        "(Pete's ruling). Run I vs J differences mix core-input and descent-law changes. D3 A1 sub-population ~400 effective impacts. "
        "The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all three rounds. Impact energy, attitude, "
        "flight-path angle and energy-transfer duration from this arm are a labelled sensitivity on uncalibrated dynamics, not a physical prediction.")
lines = textwrap.wrap("Plain words: " + plain, 160) + textwrap.wrap("Technical: " + tech, 160)
fig.text(0.01, 0.008, "\n".join(lines), fontsize=6, va="bottom", color="#333333", linespacing=1.25)
fig.savefig(W + "/figs/fig7-run-i-vs-run-j.png")
r = fig.canvas.get_renderer(); T = [(t, t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
fb = fig.bbox; print("outside", [t.get_text()[:30] for t, b in T if b.x0 < fb.x0 - 1 or b.x1 > fb.x1 + 1 or b.y0 < fb.y0 - 1 or b.y1 > fb.y1 + 1])
print("overlaps", [(a.get_text()[:20], c.get_text()[:20]) for i, (a, ba) in enumerate(T) for c, bc in T[i + 1:] if ba.overlaps(bc)])
print({D: (round(runI[D]["B"], 3), round(runJ[D]["B"], 3)) for D in DS})
