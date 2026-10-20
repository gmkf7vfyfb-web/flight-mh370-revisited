"""Map: 2001 airgun calibration site air9 against the MH370 BTO arcs, IMS hydrophones and nearby airways.

Sources: air9 positions, Blackman et al. SIO/LLNL report UCRL-TR-207323 Table 1 (19 Oct 2001), which states
air9 was recorded at both H01 (Cape Leeuwin) and H08S (Diego Garcia); arcs from runs/davey2016/run.json
(reference arcs at 35,000 ft, the core's BTO model); coastline Natural Earth 1:50m; waypoints from the core
thread's sequence_1825.py / archived N571 config; IMOS logger positions from the IMOS MH370 metadata file.
"""
import json, math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUT = Path(__file__).resolve().parent
LAND = Path("/jackbox/home/MH370/.archive/.sources/pleiades-bran2016-forward-inversion/data/natural-earth-v5.1.2-50m-land.geojson")
RUN = Path("/jackbox/home/MH370/runs/davey2016/run.json")

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#dcdad4"
LANDFILL, COAST = "#e8e6e0", "#a3a19a"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"   # reference categorical slots 1-3

def dm(d, m): return d + m / 60.0
AIR9 = (-(dm(27, 33.2) + dm(27, 33.7) + dm(27, 33.8)) / 3, (dm(98, 51.6) + dm(98, 53.0) + dm(98, 53.2)) / 3)
H01W = (-34.892, 114.141)   # IMS HA01 Cape Leeuwin, H01W triad (approximate centre)
H08S = (-7.639, 72.484)     # IMS HA08 Diego Garcia, H08S triad (approximate centre)
IMOS = {"IMOS Perth Canyon (2 loggers)": (-dm(31, 51.3), dm(115, 0.45)), "IMOS Scott Reef": (-dm(15, 29.002), dm(121, 15.060))}
WPT = {"VAMPI": (6.182222, 97.585556), "MEKAR": (6.503889, 96.491111), "NILAM": (6.756389, 95.976389),
       "IGOGU": (7.516944, 94.416667), "BEDAX": (5.364328, 93.787575)}
AIRWAYS = {"N571": ["VAMPI", "MEKAR", "NILAM", "IGOGU"], "P627": ["NILAM", "BEDAX"]}
ARC_NUMBER = {"m1825": 1, "m1941": 2, "m2041": 3, "m2141": 4, "m2241": 5, "m0011": 6, "m0019a": 7}
EXTENT = (68, 124, -42, 12)

def great_circle(a, b, n=200):
    (la1, lo1), (la2, lo2) = [(math.radians(x), math.radians(y)) for x, y in (a, b)]
    p1 = [math.cos(la1) * math.cos(lo1), math.cos(la1) * math.sin(lo1), math.sin(la1)]
    p2 = [math.cos(la2) * math.cos(lo2), math.cos(la2) * math.sin(lo2), math.sin(la2)]
    w = math.acos(sum(x * y for x, y in zip(p1, p2)))
    pts = []
    for i in range(n + 1):
        t = i / n
        s1, s2 = math.sin((1 - t) * w) / math.sin(w), math.sin(t * w) / math.sin(w)
        x, y, z = (s1 * u + s2 * v for u, v in zip(p1, p2))
        pts.append((math.degrees(math.atan2(z, math.hypot(x, y))), math.degrees(math.atan2(y, x))))
    return pts, 6371.0088 * w

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.linewidth": 0.6, "xtick.color": MUTED, "ytick.color": MUTED})
fig, ax = plt.subplots(figsize=(10.5, 10.2), dpi=180)
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)

for feat in json.loads(LAND.read_text())["features"]:
    g = feat["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        ring = poly[0]
        xs, ys = [p[0] for p in ring], [p[1] for p in ring]
        if max(xs) < EXTENT[0] - 5 or min(xs) > EXTENT[1] + 5 or max(ys) < EXTENT[2] - 5 or min(ys) > EXTENT[3] + 5:
            continue
        ax.fill(xs, ys, facecolor=LANDFILL, edgecolor=COAST, linewidth=0.4, zorder=1)

for lon in range(70, 125, 10): ax.axvline(lon, color=GRID, lw=0.5, zorder=0)
for lat in range(-40, 15, 10): ax.axhline(lat, color=GRID, lw=0.5, zorder=0)

arcs = {a["epoch"]: a["lat_lon"] for a in json.loads(RUN.read_text())["reference_arcs"]}
for epoch, number in ARC_NUMBER.items():
    pts = [(la, lo) for la, lo in arcs[epoch] if EXTENT[2] <= la <= EXTENT[3] and EXTENT[0] <= lo <= EXTENT[1]]
    seventh = number == 7
    ax.plot([p[1] for p in pts], [p[0] for p in pts], color=BLUE if seventh else "#9c9a93",
            lw=2.0 if seventh else 0.8, zorder=3 if seventh else 2)
    la, lo = min(pts, key=lambda p: abs(p[0] - 10.8))  # label along the top edge, where the arcs are spread out
    ax.annotate(f"{number}", (lo, la), xytext=(0, 3), textcoords="offset points", fontsize=8, ha="center",
                color=BLUE if seventh else MUTED, fontweight="bold" if seventh else "normal",
                bbox=dict(boxstyle="round,pad=0.12", fc=SURFACE, ec="none"), zorder=8)

for name, route in AIRWAYS.items():
    ax.plot([WPT[w][1] for w in route], [WPT[w][0] for w in route], color=INK, lw=1.0, zorder=4)
for w, (la, lo) in WPT.items():
    ax.plot(lo, la, "o", ms=2.5, color=INK, zorder=5)
    off = {"VAMPI": (6, -3), "MEKAR": (-10, -11), "NILAM": (3, 7), "IGOGU": (-31, 0), "BEDAX": (-14, -10)}[w]
    ax.annotate(w, (lo, la), xytext=off, textcoords="offset points", fontsize=6.5, color=MUTED)
ax.annotate("N571", (95.2, 7.14), xytext=(-12, 9), textcoords="offset points", fontsize=7, color=INK, fontweight="bold")
ax.annotate("P627", (94.88, 6.06), xytext=(-28, -3), textcoords="offset points", fontsize=7, color=INK, fontweight="bold")

for station, label, off in [(H01W, "HA01 Cape Leeuwin (H01W)", (8, -16)), (H08S, "HA08 Diego Garcia (H08S)", (8, -14))]:
    path, km = great_circle(AIR9, station)
    ax.plot([p[1] for p in path], [p[0] for p in path], color=ORANGE, lw=1.2, ls=(0, (4, 3)), zorder=4)
    ax.plot(station[1], station[0], "^", ms=10, color=AQUA, mec=INK, mew=0.6, zorder=6)
    ax.annotate(f"{label}\nrecorded air9 · {km:,.0f} km", station[::-1], xytext=off, textcoords="offset points",
                fontsize=8, color=INK)
for label, (la, lo) in IMOS.items():
    ax.plot(lo, la, "o", ms=6, mfc=SURFACE, mec=AQUA, mew=1.6, zorder=6)
    ax.annotate(label + "\n8 Mar 2014 records public", (lo, la), xytext=(-8, 8) if "Scott" in label else (6, 6),
                textcoords="offset points", fontsize=7, color=MUTED, ha="right" if "Scott" in label else "left")

ax.plot(AIR9[1], AIR9[0], "*", ms=17, color=ORANGE, mec=INK, mew=0.6, zorder=7)
ax.annotate("air9 airgun array\n19 Oct 2001, 02:10–02:46 UTC\n27°33.6′S 98°52.6′E",
            AIR9[::-1], xytext=(-150, 6), textcoords="offset points", fontsize=8, color=INK)
for text, (lo, la) in {"Sumatra": (100.5, -0.6), "Western\nAustralia": (118.5, -26), "Java": (109.5, -8.5)}.items():
    ax.text(lo, la, text, fontsize=8, color=MUTED, ha="center", style="italic")

ax.set_xlim(EXTENT[0], EXTENT[1]); ax.set_ylim(EXTENT[2], EXTENT[3])
ax.set_aspect(1 / math.cos(math.radians(15)))
ax.set_xticks(range(70, 125, 10)); ax.set_xticklabels([f"{x}°E" for x in range(70, 125, 10)])
ax.set_yticks(range(-40, 15, 10)); ax.set_yticklabels([f"{-y}°S" if y < 0 else (f"{y}°N" if y else "0°") for y in range(-40, 15, 10)])
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(length=0)

legend = [Line2D([], [], color="#9c9a93", lw=0.8, label="BTO arcs 1–6 (35,000 ft)"),
          Line2D([], [], color=BLUE, lw=2.0, label="7th arc (00:19 UTC)"),
          Line2D([], [], marker="*", ls="", ms=12, color=ORANGE, mec=INK, mew=0.6, label="2001 airgun site air9"),
          Line2D([], [], color=ORANGE, lw=1.2, ls=(0, (4, 3)), label="Great-circle path to recording station"),
          Line2D([], [], marker="^", ls="", ms=9, color=AQUA, mec=INK, mew=0.6, label="IMS hydrophone station"),
          Line2D([], [], marker="o", ls="", ms=6, mfc=SURFACE, mec=AQUA, mew=1.6, label="IMOS recorder (public data)"),
          Line2D([], [], color=INK, lw=1.0, label="Airways N571, P627")]
ax.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, -0.045), ncol=4, frameon=False, fontsize=8,
          handlelength=2.2, columnspacing=1.6)
ax.set_title("2001 airgun calibration site air9, recorded at both HA01 and HA08, relative to the MH370 arcs",
             fontsize=11, color=INK, loc="left", pad=10)
fig.text(0.07, 0.005, "Sources: Blackman et al., SIO/LLNL report UCRL-TR-207323, Table 1 and Fig. 4 (air9 recorded at H01 and H08S). "
         "Arcs: core BTO model at 35,000 ft. Coastline: Natural Earth 1:50m.\nStation positions are approximate triad centres; "
         "distances are great-circle. The report quotes 1,665 km to H01; its ~4,825 km figure for H08S does not match the geodesic.",
         fontsize=6.8, color=MUTED)
fig.savefig(OUT / "airgun-2001-air9.png", facecolor=SURFACE, bbox_inches="tight")
print("air9", AIR9, "->", OUT / "airgun-2001-air9.png")
