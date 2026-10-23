cat > leg/fig_map.py <<'EOF'
import sys, json; sys.path.insert(0, "leg"); import numpy as np, pandas as pd, matplotlib as mpl; mpl.use("Agg"); import matplotlib.pyplot as plt
import gebco as GB; from geometry_windows import ST, pos, AZ, R7, HX, H01W
from geographiclib.geodesic import Geodesic
M = GB.M; st = 24; i0 = int((-50 - M["lat0"]) / M["step_deg"]); i1 = int((2 - M["lat0"]) / M["step_deg"]); j0 = int((48 - M["lon0"]) / M["step_deg"]); j1 = int((120 - M["lon0"]) / M["step_deg"])
Zs = np.asarray(GB.Z[i0:i1:st, j0:j1:st], float); la = M["lat0"] + M["step_deg"] * np.arange(i0, i1, st); lo = M["lon0"] + M["step_deg"] * np.arange(j0, j1, st)
B = pd.read_csv("leg/out/path_blockage.csv"); E = pd.read_csv("leg/out/royer_events_vs_L.csv"); RC = json.load(open("leg/out/royer_recombination.json"))
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.6), gridspec_kw=dict(width_ratios=[1.55, 1], wspace=0.18))
for ax, (x0, x1, y0, y1) in zip(axs, ((48, 120, -50, 2), (98.5, 103.5, -27.5, -23.5))):
    ax.contourf(lo, la, -Zs, levels=[-1e4, 0, 1000, 2000, 3000, 4000, 5000, 9000], colors=["#d9d9d9", "#f7f7f7", "#eef1f6", "#e1e7f0", "#d3dcea", "#c5d1e3", "#b7c6dd"])
    ax.contour(lo, la, Zs, levels=[0], colors="#555555", linewidths=0.4)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect(1 / np.cos(np.radians((y0 + y1) / 2)))
    ax.set_xlabel("Longitude, deg E"); 
axs[0].set_ylabel("Latitude, deg (negative = south)")
COL = {"OPEN": "#1f3b73", "PARTIAL": "#c26a00", "BLOCKED": "#9a9a9a"}; LS = {"OPEN": "-", "PARTIAL": "--", "BLOCKED": ":"}
src = pos(AZ, R7["bto"]); g = Geodesic.WGS84
for stn, (sla, slo, *_ ) in list(ST.items()) + [("H01W", (-34.8903, 114.1426))]:
    if stn == "H01W": sla, slo = -34.8903, 114.1426
    v = B[(B.source == "crossing") & (B.station == stn)].verdict.iloc[0]
    l = g.InverseLine(src[0], src[1], sla, slo); ss = np.linspace(0, l.s13, 200); P = [l.Position(x) for x in ss]
    axs[0].plot([p["lon2"] for p in P], [p["lat2"] for p in P], color=COL[v], ls=LS[v], lw=0.7, zorder=2)
    axs[0].plot(slo, sla, marker="^", ms=3.5, color="black" if "NEAMS" not in stn else "white", mec="black", mew=0.5, zorder=4)
for ax in axs:
    l = g.Line(H01W[0], H01W[1], AZ); ss = np.linspace((R7["bto"] - 60) * 1e3, (R7["bto"] + 250) * 1e3, 50)
    for da in (-1, 0, 1):
        l = g.Line(H01W[0], H01W[1], AZ + da); P = [l.Position(x) for x in ss]
        ax.plot([p["lon2"] for p in P], [p["lat2"] for p in P], color="black", lw=1.2 if da == 0 else 0.5, ls="-" if da == 0 else "--", zorder=5)
    ax.plot(src[1], src[0], "o", ms=4.5, color="#1f3b73", mec="white", zorder=7); ax.plot(HX[1], HX[0], "s", ms=3.5, color="none", mec="#c26a00", mew=1.0, zorder=7)
    ev = E[E.event.isin([3, 4, 7, 9, 11, 14, 15])]; ax.plot(ev.lon, ev.lat, "*", ms=4.5, color="#555555", zorder=6)
r = RC["inversions"][list(RC["inversions"])[0]]
axs[1].add_patch(mpl.patches.Rectangle((r["region_95_lon"][0], r["region_95_lat"][0]), r["region_95_lon"][1] - r["region_95_lon"][0], r["region_95_lat"][1] - r["region_95_lat"][0], fc="none", ec="#7a3e9d", lw=0.9, ls="-", zorder=6))
axs[1].plot(r["best_lon"], r["best_lat"], "x", color="#7a3e9d", ms=4, zorder=8)
axs[0].set_title("Paths from the bearing-arc crossing to each station", loc="left"); axs[1].set_title("The locality on the 7th arc", loc="left")
from matplotlib.lines import Line2D
h = [Line2D([], [], color=COL["OPEN"], ls="-"), Line2D([], [], color=COL["PARTIAL"], ls="--"), Line2D([], [], color=COL["BLOCKED"], ls=":"), Line2D([], [], color="black", lw=1.2),
     Line2D([], [], marker="o", ls="none", color="#1f3b73"), Line2D([], [], marker="s", ls="none", mfc="none", mec="#c26a00"), Line2D([], [], marker="*", ls="none", color="#555555"),
     Line2D([], [], color="#7a3e9d"), Line2D([], [], marker="^", ls="none", color="black")]
fig.legend(h, ["path open (GEBCO)", "path meets a ridge shallower than 1,500 m", "path blocked (land or shelf)", "Kadri bearing 306.18 deg; dashed +/-1 deg (strip -60 to +250 km)",
               "bearing-arc crossing 25.732 S 101.369 E", "Haixun 01 contact (sensitivity only)", "Royer (2016) located events", "exploratory 3-station fit, 95 % box (caption time)", "receiver"],
           loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.12))
import textwrap
f1 = "(i) The chart shows where the sound would start and the path to each station. A blue line is a clear path. An orange line goes over an undersea ridge. A grey line is stopped by land or a shelf. The purple box is a test that we did after we saw the data."
f2 = ("(ii) Geometry only, no posterior. Sea-level 7th arc R600 BTO 18,400 us, m0019a. GEBCO_2026 15 arc-s along WGS84 geodesics, last 50 km before each receiver excluded; rule: land or >10 km above 200 m or >100 km above 1,000 m = blocked; "
      "minimum depth <1,500 m = partial (loss not computed). Physics: no TL. Royer events from LDO-201608 Table 4. Purple box: exploratory free fit of H01W 00:54:30 + bearing + S-SEIR + MAD picks (not pre-registered). Excluded: NE-AMS (lost).")
fig.text(0.01, -0.02, "\n".join(textwrap.wrap(f1, 190)), fontsize=5.6, ha="left", va="top"); fig.text(0.01, -0.09, "\n".join(textwrap.wrap(f2, 190)), fontsize=5.6, ha="left", va="top", color="#444444")
fig.savefig("leg/fig/locality-paths-map.png", dpi=300, bbox_inches="tight"); fig.savefig("leg/fig/locality-paths-map.pdf", bbox_inches="tight")
EOF
echo