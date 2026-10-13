"""Run H close-up of the waypoint region: re-flown fly-by paths for the four ISBIX-end routes (100 s spacing)."""
import json, textwrap, numpy as np, matplotlib as mpl, pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.backends.backend_agg import FigureCanvasAgg

W = "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/386151e9-859f-412a-8d9d-b8da48899575"
ENG = f"{W}/repo/Claude Science Project Sep 29/engine"
TH = pd.read_csv(f"{W}/rung/out/run-h-per-route.csv").set_index("route")
TT = pd.read_csv(f"{W}/rung/out/run-h-turn-geometry.csv").set_index("route")
DN = {r: np.load(f"/tmp/dense/o-{r}/bto-bfo/seed-1/routes.npy").astype(float) for r in (43, 19, 3, 11)}
WP = {k: v for k, v in {"VAMPI": (6.1822, 97.5856), "MEKAR": (6.5039, 96.4911), "NILAM": (6.7564, 95.9767), "ANOKO": (7.1361, 94.4161),
      "IGOGU": (7.5169, 94.4167), "NOPEK": (6.6039, 94.4167), "SAMAK": (7.9783, 94.4167), "BULVA": (4.5667, 94.0), "BEDAX": (5.3643, 93.7876)}.items()}
COL = {43: "#1f5fa8", 19: "#7fa7d6", 3: "#c97d00", 11: "#4d9a4d"}
LAB = {43: "MEKAR – SAMAK – ISBIX", 19: "NILAM – SAMAK – ISBIX", 3: "NILAM – IGOGU – ISBIX (N571)", 11: "NILAM – ANOKO – ISBIX"}

def land(ax, box):
    for f in json.load(open(f"{ENG}/report/ne_110m_land.geojson"))["features"]:
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for p in polys:
            a = np.array(p[0])
            if a[:, 0].max() < box[0] or a[:, 0].min() > box[1] or a[:, 1].max() < box[2] or a[:, 1].min() > box[3]: continue
            ax.add_patch(Polygon(a, closed=True, fc="#ececec", ec="#bdbdbd", lw=0.4, zorder=0))

def build(png, pdf):
    apply_figure_style(sizes=(8, 7, 6))
    fig = plt.figure(figsize=(7.2, 8.6)); FigureCanvasAgg(fig)
    ax = fig.add_axes([0.09, 0.40, 0.86, 0.55])
    box = (93.3, 97.9, 4.3, 8.6); land(ax, box)
    ax.plot([94.4167, 94.4167], [6.0, 8.6], color="#888888", lw=0.8, ls=(0, (4, 3)), zorder=1)
    ax.text(94.45, 8.48, "FIR boundary", fontsize=6, color="#666666", va="top")
    rng = np.random.default_rng(3)
    for r in (11, 3, 19, 43):
        P = DN[r]; idx = rng.choice(len(P), 120, replace=False)
        for i in idx: ax.plot(P[i, :, 1], P[i, :, 0], color=COL[r], lw=0.4, alpha=0.35, zorder=2 if r != 43 else 3)
    for k, (la, lo) in WP.items():
        ax.plot(lo, la, marker="^", ms=4.5, mfc="white", mec="black", mew=0.7, zorder=6)
        dx, dy, ha = {"VAMPI": (0, -0.12, "center"), "MEKAR": (0, -0.12, "center"), "NILAM": (0, 0.11, "center"), "ANOKO": (-0.07, -0.06, "right"),
                      "IGOGU": (-0.07, 0.0, "right"), "NOPEK": (-0.07, 0.0, "right"), "SAMAK": (-0.07, 0.05, "right"), "BULVA": (-0.07, 0, "right"),
                      "BEDAX": (-0.07, 0, "right")}[k]
        ax.text(lo + dx, la + dy, k, fontsize=6, ha=ha, va="center", zorder=7)
    ax.plot(96.3410, 6.5779, marker="o", ms=4, mfc="black", mec="black", zorder=7)
    ax.text(96.36, 6.66, "last radar\n18:22:12", fontsize=6, ha="left", va="bottom", zorder=7)
    c = TT.loc[43]
    ax.annotate(f"leaves the inbound leg {c.nm_before_fix_when_xt_0p5:.0f} NM\nbefore SAMAK ({c.t_when_xt_0p5[:5]}); passes\n{c.closest_approach_nm:.1f} NM from it", xy=(94.62, 7.73), xytext=(95.25, 8.25),
                fontsize=6, arrowprops=dict(arrowstyle="-", lw=0.6, color="#333333"), zorder=8)
    ax.set_xlim(box[:2]); ax.set_ylim(box[2:]); ax.set_aspect(1 / np.cos(np.radians(7)))
    ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)")
    ax.set_title("SAMAK routes turn south well before SAMAK, then join the boundary leg to ISBIX", loc="left")
    hs = [mpl.lines.Line2D([], [], color=COL[r], lw=1.6) for r in (43, 3, 19, 11)]
    ax.legend(hs, [f"{LAB[r]}  (share {TH.share_mean[r]:.3f}, ln Z {TH.log_evidence[r]:.1f})" for r in (43, 3, 19, 11)],
              loc="lower right", frameon=False, fontsize=7)
    plain = ("Plain note (ASD-STE100): This chart shows paths of the aircraft that follow named airway points, from the last radar point to "
             "about 19:00. Each colour is one route. In this model the aircraft starts each turn before the point (a fly-by turn), "
             "as a flight management computer does. The aircraft on the SAMAK routes does not reach SAMAK. It starts to turn south about "
             "23 to 27 NM before SAMAK, at about 18:37, and passes about 13 NM from it. Then it flies south near the FIR boundary to ISBIX. "
             "The two routes that end at BULVA are not shown: the data give them almost no probability. The chart shows only the "
             "airway points in our table. The published chart has more points in this area that we did not sample.")
    tech = ("Technical note: paths re-flown locally for display (binary 409192d, fly_by + track_legs + turn_backs, run H stack: "
            "davey2016-inmarsat, no-exhaustion-prior, s1-s6 fuel, reference-snapshots, radar-full, s7/s8 PROVISIONAL, inop-flow-fix), "
            "1 seed x 84k particles per route, 400 posterior route samples per route at 100 s spacing (120 drawn), observations after "
            "m1941 excluded and fuel power required to m1941 only, to allow 100 s spacing under the 64-vertex limit; geometry only, "
            "not used for evidence. Shares and ln Z in the legend are run H (8 seeds x 3M, route identifier, equal prior 1/6 over "
            "routes 10, 11, 3, 2, 19, 43). Turn start: first point after 18:31:49 more than 0.5 NM off the inbound great-circle leg (SAMAK routes 23.3-23.7 NM before the fix at 18:37:06-18:37:11; back-projected along a 13 NM arc, 26-27 NM at 18:36:40-18:36:45); closest approach from paths subdivided 40x between vertices; theoretical fly-by "
            "anticipation R tan(dpsi/2) with R = 13 NM (15 deg bank, ~490 kt): SAMAK 120 deg 22.6 NM, IGOGU 110 deg 18.6 NM, ANOKO "
            "97 deg 14.7 NM; closest approach R(sec(dpsi/2) - 1): 13.0 / 9.7 / 6.6 NM against 13.5 / 9.5 / 6.8 NM measured. "
            "Waypoints: engine/data/waypoints.csv (third-party navdata, current cycle, epoch not verified for 2014). FIR boundary drawn "
            "along 094 deg 25 min E. Land: Natural Earth 1:110m.")
    y = 0.315
    for t in (plain, tech):
        txt = fig.text(0.09, y, textwrap.fill(t, 150), fontsize=6, va="top", ha="left", linespacing=1.35)
        bb = txt.get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted()); y = bb.y0 - 0.018
    fig.savefig(png, dpi=300); fig.savefig(pdf)
    return fig
