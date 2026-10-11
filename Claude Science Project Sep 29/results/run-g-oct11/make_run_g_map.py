"""Run G (six waypoint routes) map: early turns and arc crossings. Uses apply_figure_style from the figure-style kernel."""
import json, textwrap, numpy as np, matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

W = "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/386151e9-859f-412a-8d9d-b8da48899575"
ENG = f"{W}/repo/Claude Science Project Sep 29/engine"
G = f"{W}/rung/small/next-g-routes"
d = np.load(f"{W}/rung/fig-inputs.npz")
rj = json.load(open(f"{G}/run.json")); sm = json.load(open(f"{G}/summary.json"))
case = sm["cases"][0]
SH = json.load(open(f"{W}/hpc/scp-e3770710e2f9c1ed/rung/g-shares.json"))
share = lambda r: np.mean([SH[f"seed-{s}"].get(str(r), {}).get("share", 0.0) for s in range(1, 9)])
S_AN, S_IG, S_SA = share(10) + share(11), share(2) + share(3), share(19) + share(43)

COL = {"ANOKO": "#1f5fa8", "IGOGU": "#c97d00", "SAMAK": "#6e6e6e"}
FREE = "#a9a9a9"
WP = {"VAMPI": (6.1822, 97.5856), "MEKAR": (6.5039, 96.4911), "NILAM": (6.7564, 95.9767), "ANOKO": (7.1361, 94.4161),
      "IGOGU": (7.5169, 94.4167), "SAMAK": (7.9783, 94.4167), "BULVA": (4.5667, 94.0), "ISBIX": (0.3667, 93.6751)}

def land(ax, box):
    for f in json.load(open(f"{ENG}/report/ne_110m_land.geojson"))["features"]:
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for p in polys:
            a = np.array(p[0])
            if a[:, 0].max() < box[0] or a[:, 0].min() > box[1] or a[:, 1].max() < box[2] or a[:, 1].min() > box[3]: continue
            ax.add_patch(Polygon(a, closed=True, fc="#ececec", ec="#bdbdbd", lw=0.4, zorder=0))

def build(out_png, out_pdf):
    apply_figure_style(sizes=(8, 7, 6))
    fig = plt.figure(figsize=(7.2, 7.9))
    from matplotlib.backends.backend_agg import FigureCanvasAgg; FigureCanvasAgg(fig)
    axa = fig.add_axes([0.075, 0.43, 0.40, 0.50]); axb = fig.add_axes([0.575, 0.43, 0.40, 0.50])
    R = d["g_routes"].reshape(-1, 38, 2); tf = d["g_turnfix"]; grp = np.where(np.char.startswith(tf.astype(str), "SAMAK"), "SAMAK", tf)
    rng = np.random.default_rng(1)
    # (a) early flight
    boxa = (92.6, 100.0, -0.8, 9.0); land(axa, boxa)
    for g, n in (("ANOKO", 250), ("IGOGU", 120), ("SAMAK", 14)):
        idx = np.flatnonzero(grp == g); idx = rng.choice(idx, min(n, len(idx)), replace=False)
        for i in idx: axa.plot(R[i, :12, 1], R[i, :12, 0], color=COL[g], lw=0.35, alpha=0.25 if g == "ANOKO" else 0.45, zorder=2)
    for k, (la, lo) in WP.items():
        axa.plot(lo, la, marker="^", ms=4, mfc="white", mec="black", mew=0.7, zorder=5)
        dx, dy, ha = {"VAMPI": (0, -0.35, "center"), "MEKAR": (0, 0.25, "center"), "NILAM": (0, 0.25, "center"), "ANOKO": (-0.3, -0.05, "right"),
                      "IGOGU": (-0.3, 0.08, "right"), "SAMAK": (-0.3, 0.2, "right"), "BULVA": (-0.15, 0, "right"), "ISBIX": (-0.15, 0, "right")}[k]
        axa.text(lo + dx, la + dy, k, fontsize=6, ha=ha, va="center", zorder=6)
    axa.set_xlim(boxa[:2]); axa.set_ylim(boxa[2:]); axa.set_aspect(1 / np.cos(np.radians(4)))
    axa.set_xlabel("Longitude (°E)"); axa.set_ylabel("Latitude (°N)")
    axa.set_title("Nine in ten paths turn south at ANOKO", loc="left")
    hs = [mpl.lines.Line2D([], [], color=COL[g], lw=1.5) for g in COL]
    axa.legend(hs, [f"Turn south at ANOKO ({S_AN:.0%})", f"Turn south at IGOGU ({S_IG:.0%})", f"Turn at SAMAK ({S_SA:.1%})"],
               loc="lower right", frameon=False, fontsize=7)
    panel_letter(axa, "a")
    # (b) arc crossings
    boxb = (85.0, 100.5, -39.5, -26.0); land(axb, boxb)
    arcs = {a["epoch"]: np.array(a["lat_lon"]) for a in rj["reference_arcs"]}
    for e, lab in (("m0011", "00:11 arc"), ("m0019a", "00:19 arc")):
        a = arcs[e]; m = (a[:, 0] > boxb[2]) & (a[:, 0] < boxb[3]); axb.plot(a[m, 1], a[m, 0], color="#444444", lw=0.8, ls="--", zorder=1)
        la_, dx_, ha_ = (-27.6, -0.4, "right") if e == "m0011" else (-30.5, 0.4, "left")
        j = np.argmin(abs(a[:, 0] - la_)); axb.text(a[j, 1] + dx_, a[j, 0], lab, fontsize=6, color="#444444", va="center", ha=ha_)
    fl = d["free_on_line"]; f11 = fl[fl[:, 2] == 11]
    axb.scatter(f11[:, 1], f11[:, 0], s=3, facecolors="none", edgecolors=FREE, lw=0.4, zorder=2)
    for g, n in (("ANOKO", 1500), ("IGOGU", 600), ("SAMAK", 14)):
        idx = np.flatnonzero(grp == g); idx = rng.choice(idx, min(n, len(idx)), replace=False)
        axb.scatter(d["g_lon11"][idx], d["g_lat11"][idx], s=2.5, color=COL[g], alpha=0.5, lw=0, zorder=3)
    # 00:19 density (all six routes, pooled over seeds) -> 50 % and 95 % highest-density regions
    gm = sm["map"]; la0, lo0, st = gm["lat"][0], gm["lon"][0], gm["step"]
    nla = int(round((gm["lat"][1] - la0) / st)) + 1; nlo = int(round((gm["lon"][1] - lo0) / st)) + 1
    H = np.zeros((nla, nlo))
    for i, j, v in case["map"]: H[int(i), int(j)] += v
    hs_ = np.sort(H.ravel())[::-1]; cs = np.cumsum(hs_) / hs_.sum(); lev = [hs_[np.searchsorted(cs, q)] for q in (0.95, 0.5)]
    LA = la0 + st * (np.arange(nla) + 0.5); LO = lo0 + st * (np.arange(nlo) + 0.5)
    axb.contour(LO, LA, H, levels=lev, colors="black", linewidths=[0.6, 1.0], zorder=4)
    axb.set_xlim(boxb[:2]); axb.set_ylim(boxb[2:]); axb.set_aspect(1 / np.cos(np.radians(33)))
    axb.set_xlabel("Longitude (°E)"); axb.set_ylabel("Latitude (°N)")
    axb.set_title("Crossings near 35.7°S at 00:11 and 36.7°S at 00:19", loc="left")
    hb = [mpl.lines.Line2D([], [], ls="", marker="o", ms=3, color=COL["ANOKO"]), mpl.lines.Line2D([], [], ls="", marker="o", ms=3, color=COL["IGOGU"]),
          mpl.lines.Line2D([], [], ls="", marker="o", ms=3, mfc="none", mec=FREE), mpl.lines.Line2D([], [], color="black", lw=1.0)]
    axb.legend(hb, ["00:11, turn at ANOKO", "00:11, turn at IGOGU", "00:11, free flight on the\nNILAM–ANOKO line (other run)", "00:19, 50 % and 95 % regions"],
               loc="upper left", frameon=False, fontsize=7)
    panel_letter(axb, "b")
    sh = verdict([np.array(r["density"]) for r in case["replicates"]], 0.05)["mean"]
    plain = ("Plain note (ASD-STE100): This chart shows the paths of the aircraft when it must fly along one of six routes that "
             "the author chose before the analysis. Each route goes through named airway points and then turns south. The "
             "satellite data are applied in the same way as in run C. The data at 00:19 are only the two time values, as Davey "
             "used them. This run does not give a cause for the 00:19 log-on. The physics of the flight on one engine is "
             f"provisional. The result is converged (split-half {sh:.3f}). Panel a shows a sample of the paths. Panel b shows "
             "where the paths cross the 00:11 arc, and the area of the 00:19 position. The lines in panel a join the positions at "
             "10-minute intervals. Thus they cut the corners of the turns.")
    tech = ("Technical note: run G (server-g-routes.toml), binary " + rj["code_revision"] + "; stack davey2016-inmarsat + "
            "no-exhaustion-prior + s1-s6 fuel + reference-snapshots + radar-full + s7-single-engine + s8-hold-taper (PROVISIONAL) + "
            "inop-flow-fix (internal-v1, inop_flow_scale 0.5) + waypoints routes family with turn_backs (overshoot rule); routes "
            "10, 11, 3, 2, 19, 43 at equal prior 1/6; prior 18:01:49 5.6248N 99.0482E, track 289.7 ± 1.0° (Davey Fig. 4.2); "
            "8 seeds × 3M particles, 16 equal tempering stages (run C sampler); 00:19 data = m0019a and m0019b BTO, no 00:19 "
            f"BFO; log-on cause not modelled; family ln Z −129.55 (seed sd 0.03); split-half {sh:.3f}, mean over 35 balanced "
            "partitions, 8-seed floor 0.924. Panel a: 384 of 16,000 posterior route samples (2,000 per seed), "
            "18:01:49 to 19:51:49, grouped by turn fix by nearest-polyline fit; legend shares are from the route identifier "
            "in final.npy (geometric grouping gives ANOKO 0.909, IGOGU 0.090). Panel b: 00:11 points are the route samples "
            "interpolated to 00:10:59; grey open circles are run D free-flight samples within 4 NM of the NILAM–ANOKO line "
            "to 19:11:49 (n = 1,081); 00:19 contours are 50 %/95 % highest-density regions of the pooled 0.25° map. Lines in panel a join 600 s route vertices (chords cut the turn corners). Arcs at "
            "35,000 ft, for orientation. Land: Natural Earth 1:110m.")
    y = 0.335
    for t in (plain, tech):
        txt = fig.text(0.075, y, textwrap.fill(t, 150), fontsize=6, va="top", ha="left", linespacing=1.35)
        bb = txt.get_window_extent(fig._get_renderer()).transformed(fig.transFigure.inverted())
        y = bb.y0 - 0.018
    fig.savefig(out_png, dpi=300); fig.savefig(out_pdf)
    return fig
