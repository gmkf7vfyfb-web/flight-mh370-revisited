"""Figure for results/routes-finding-audit-architecture.md (reads the CSVs written by audit_routes_finding.py)."""
import os, sys, textwrap
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE
ep = pd.read_csv(os.path.join(HERE, "per-epoch-log-evidence.csv"), index_col=0).drop("TOTAL")
ctl = pd.read_csv(os.path.join(HERE, "pseudo-fix-control-smoke.csv"))
ev = pd.read_csv(os.path.join(HERE, "evidence-by-run.csv")).set_index("run")

label = {"r0414": "18:04", "r0515": "18:05", "r0716": "18:07", "r1336": "18:13", "b1815": "18:15", "b1817": "18:17",
         "b1819": "18:19", "b1821": "18:21", "r1822": "18:22", "m1825": "18:25", "m1828a": "18:28a", "m1828b": "18:28b",
         "m1839": "18:39", "m1941": "19:41", "m2041": "20:41", "m2141": "21:41", "m2241": "22:41", "m2315": "23:15",
         "m0011": "00:11", "m0019a": "00:19a", "m0019b": "00:19b"}
FOCAL, RADAR, GREY = "#1f5fa8", "#9aa7b4", "#6b6b6b"
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
                     "legend.fontsize": 7, "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(7.4, 6.6))
axa = fig.add_axes([0.09, 0.33, 0.39, 0.55])
axb = fig.add_axes([0.585, 0.33, 0.385, 0.55])

d = ep["route 11 minus free"]
xs = np.arange(len(d))
col = [RADAR if k[0] in "rb" else FOCAL for k in d.index]
axa.bar(xs, d.values, color=col, width=0.75)
axa.axhline(0, color=GREY, lw=0.6)
axa.set_xticks(xs, [label[k] for k in d.index], rotation=90)
axa.set_ylabel("Log-evidence difference, published route\nminus free-turn model (nats)")
axa.set_title("a  The gain comes at 19:41 and from the radar track", loc="left")
radar_sum = d[[k for k in d.index if k[0] in "rb"]].sum(); sat_sum = d[[k for k in d.index if k[0] == "m"]].sum()
axa.text(4, 4.4, f"radar times: +{radar_sum:.1f}", color="#4d5a66", ha="center", fontsize=7)
axa.text(17.5, 4.4, f"satellite times: +{sat_sum:.1f}", color=FOCAL, ha="center", fontsize=7)
axa.set_ylim(-2.6, 5.3); axa.margins(x=0.02)

g = ctl.groupby("offset_east_of_ANOKO_nm").logZ
axb.scatter(ctl.offset_east_of_ANOKO_nm, ctl.logZ, s=12, color=FOCAL, alpha=0.6, zorder=3, label="one run (50k particles)")
m = g.mean()
axb.plot(m.index, m.values, color=FOCAL, lw=1.2, zorder=2)
free = ev.loc["run D free", "logZ_logmeanexp"]
fam = -131.594
axb.axhline(free, color=GREY, ls="--", lw=0.9); axb.text(41, free + 0.35, "free-turn model", ha="right", color=GREY, fontsize=7)
axb.axhline(fam, color=GREY, ls=":", lw=0.9); axb.text(41, fam + 0.35, "all 48 published routes, equal prior", ha="right", color=GREY, fontsize=7)
axb.annotate("ANOKO\n(published\nwaypoint)", xy=(0, m.loc[0.0]), xytext=(-13.5, -128.3), fontsize=7, arrowprops=dict(arrowstyle="-", lw=0.6, color=GREY))
axb.annotate("flown path lies on\nthe published leg\nANOKO to ISBIX", xy=(10, m.loc[10.0]), xytext=(17, -125.0), fontsize=7,
             arrowprops=dict(arrowstyle="-", lw=0.6, color=GREY))
axb.set_xlabel("Turn point east of ANOKO (NM)")
axb.set_ylabel("Log-evidence (nats)")
axb.set_title("b  Evidence follows the turn point, not the name", loc="left")
axb.set_ylim(-141, -122.2); axb.set_xlim(-18, 43)

fig.text(0.08, 0.955, "Published-route result for 18:22 to 19:41: audit of the turn-south gain (UNCONVERGED)", fontsize=9, weight="bold")

ste = ("STE100: (a) The bars show how much better a published route (west to ANOKO, then south to ISBIX) predicts each "
       "measurement than the model with random turns. Grey bars are radar times. Blue bars are satellite times. "
       "(b) We moved the turn point along the westbound track and did the calculation again. The best turn point is "
       "10 NM east of ANOKO. There, the aircraft flies on the published leg. The free-turn model also has these paths, "
       "but with less prior probability. The results are not converged. Use them only to compare.")
tech = ("Technical: core early-flight evidence (no end-of-flight or impact modules), 18:01:49 radar prior, satellite BTO/BFO 18:25 to 00:19 "
        "(00:19a/b as in runs C/D), radar 18:04 to 18:22 in the likelihood; run C fuel stack; Davey (2016) dynamics, "
        "15 deg bank; mode prior 1/5. (a) per-epoch increments of the 5-mode mixture log-evidence, mean of seeds: pilot "
        "route 11 with turn_backs (200k, 2 seeds, ad50) minus run D free (7M, 4 seeds). (b) audit smoke, 50k, seeds 1-2, "
        "pseudo-fix on the NILAM-ANOKO geodesic then ISBIX, turn_backs, binary 861e4408-dirty; run D free -135.90; "
        "routes family (48 routes, log-mean-exp) -131.59. Split-half not converged; numbers provisional.")
y = 0.205
for txt, w in [(ste, 150), (tech, 150)]:
    for line in textwrap.wrap(txt, w):
        fig.text(0.04, y, line, fontsize=6, color="#333333"); y -= 0.0165
    y -= 0.008
fig.savefig(os.path.join(OUT, "routes-finding-audit-fig1.png"), dpi=200)
fig.savefig(os.path.join(OUT, "routes-finding-audit-fig1.pdf"))
print("bottom of footnotes at", round(y, 3))
