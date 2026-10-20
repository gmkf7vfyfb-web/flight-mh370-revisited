import sys, json; sys.path.insert(0, "leg"); import numpy as np, pandas as pd, matplotlib as mpl; mpl.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
exec(open(sys.argv[1]).read()) if len(sys.argv) > 1 else None   # figure-style kernel helpers when run standalone
W = pd.read_csv("leg/out/arrival_windows.csv"); O = pd.read_csv("leg/out/arrival_windows_superseded_26p2S.csv"); T5 = json.load(open("leg/out/royer_table5.json"))
s = lambda x: sum(float(a) * m for a, m in zip(x.split(":"), (3600, 60, 1)))
ROWS = [("PerthCanyon_3376", "Perth Canyon logger 3376", None), ("H08S", "Diego Garcia South (IMS)", None), ("OHAS_SSEIR", "OHASISBIO S-SEIR", "SSEIR"),
        ("OHAS_SWAMS3", "OHASISBIO SW-AMS 3", "SWAMS3"), ("OHAS_MAD", "OHASISBIO MAD", "MAD"), ("OHAS_WKER", "OHASISBIO W-KER", "WKER"), ("OHAS_NCRO", "OHASISBIO N-CRO", "NCRO")]
TESTED = {("T", "H08S"): [("01:16:19", "01:17:33")], ("C", "H08S"): [("01:18:46", "01:20:00")],
          ("T", "PerthCanyon_3376"): [("00:50:44", "00:51:10")], ("C", "PerthCanyon_3376"): [("00:53:11", "00:53:37")]}
FOC, STRIP, HXC, OLD, PICK = "#1f3b73", "#b9c6dd", "#c26a00", "#9a9a9a", "#000000"
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.9), sharey=True, gridspec_kw=dict(wspace=0.06))
for ax, br, ttl in ((axs[0], "T", "Reception at Cape Leeuwin 00:52:03 (text time)"), (axs[1], "C", "Reception at Cape Leeuwin 00:54:30 (caption time)")):
    for i, (stn, lab, rk) in enumerate(ROWS):
        y = len(ROWS) - 1 - i; g = W[(W.branch == br) & (W.station == stn)].set_index("source_set")
        r = g.loc["locality_strip_wide"]; ax.add_patch(Rectangle((r.window_start_s / 60, y - 0.32), (r.window_end_s - r.window_start_s) / 60, 0.64, fc=STRIP, ec="none", zorder=1))
        r = g.loc["crossing_core"]; ax.add_patch(Rectangle((r.window_start_s / 60, y - 0.22), (r.window_end_s - r.window_start_s) / 60, 0.44, fc=FOC, ec="none", zorder=3))
        r = g.loc["haixun"]; ax.add_patch(Rectangle((r.window_start_s / 60, y - 0.30), (r.window_end_s - r.window_start_s) / 60, 0.60, fc="none", ec=HXC, lw=1.0, zorder=4))
        for a, b in TESTED.get((br, stn), []):
            ax.add_patch(Rectangle((s(a) / 60, y - 0.36), (s(b) - s(a)) / 60, 0.72, fc="none", ec=OLD, lw=0.9, hatch="////", zorder=2))
        if rk:
            for k, d in T5.items():
                if d.get(rk, "X") != "X": ax.plot(s(d[rk]) / 60, y, marker="v", ms=3.6, color=PICK, mec="white", mew=0.4, zorder=6, clip_on=True)
    ax.set_title(ttl, loc="left"); ax.set_xlim(49.5, 92); ax.set_ylim(-0.7, len(ROWS) - 0.2)
    tk = np.arange(50, 93, 10); ax.set_xticks(tk); ax.set_xticklabels([f"{int(t//60):02d}:{int(t%60):02d}" for t in tk]); ax.set_xlabel("Predicted arrival time, UTC, 8 March 2014")
axs[0].set_yticks(range(len(ROWS))); axs[0].set_yticklabels([r[1] for r in ROWS][::-1])
from matplotlib.lines import Line2D
h = [Rectangle((0, 0), 1, 1, fc=FOC), Rectangle((0, 0), 1, 1, fc=STRIP), Rectangle((0, 0), 1, 1, fc="none", ec=HXC), Rectangle((0, 0), 1, 1, fc="none", ec=OLD, hatch="////"),
     Line2D([], [], marker="v", ls="none", color=PICK, ms=4)]
fig.legend(h, ["95 % window, source at the bearing-arc crossing", "95 % window, whole bearing strip (arc -60 to +250 km)", "95 % window, source at the Haixun 01 contact",
               "window searched on 13 Oct (superseded point 26.2 S 101.9 E)", "arrival picked by Royer (2016), any event"], loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.13))
f1 = ("(i) The chart shows when a sound from the place on the bearing would arrive at each station. The time comes from the Cape Leeuwin time and the distance. "
      "No flight data is used. Hatched boxes show what was searched before. The old search used a wrong point. Triangles are times that another author found.")
f2 = ("(ii) Source: sea-level 7th arc from R600 BTO 18,400 us (ephemeris m0019a) crossed by Kadri's 306.18 deg H01W bearing (25.732 S 101.369 E); no posterior used. "
      "t_X = t_H01W + (d_X - d_H01W)/c, c = 1.48 +/- 0.015 km/s, pick 5 s, 1.96 sigma; bearing +/-0.5 deg and BTO +/-63 us re-solved. Physics: geodesic, no TL; "
      "search case n/a; ocean model none. Royer picks: LDO-201608 Table 5 (UTC as printed). Excluded: NE-AMS (lost), H08N, Portland, Scott Reef (blocked).")
import textwrap
fig.text(0.01, -0.04, "\n".join(textwrap.wrap(f1, 190)), fontsize=5.6, ha="left", va="top"); fig.text(0.01, -0.12, "\n".join(textwrap.wrap(f2, 190)), fontsize=5.6, ha="left", va="top", color="#444444")
fig.savefig("leg/fig/arrival-windows-corrected.png", dpi=300, bbox_inches="tight"); fig.savefig("leg/fig/arrival-windows-corrected.pdf", bbox_inches="tight")
