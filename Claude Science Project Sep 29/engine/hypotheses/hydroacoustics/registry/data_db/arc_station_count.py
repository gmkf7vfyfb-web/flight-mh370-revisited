#!/usr/bin/env python3
"""
arc_station_count.py - for each 1 deg of 7th-arc latitude (20 S to the arc's southern end, 43.9 S), count the hydroacoustic
stations that were recording on 8 March 2014 and have bathymetric line of sight to that arc point. Uses table arc_path
(written by arc_line_of_sight.py). Writes the 8 March 2014 station inventory into the attribute table
(keys recording_8mar2014, station_location, data_held), the view v_arc_los_by_location, a CSV table and a chart.

Counting unit = station location: co-located instruments count once (Perth Canyon 3315+3376, Portland 3274+3275,
SWAMS1-3 within 10 km; IMS triads are one site each). A location takes the most favourable class of its instruments.

Usage: python arc_station_count.py --db hydro_data.sqlite --out arc_los_station_count
"""
import argparse, sqlite3, textwrap
from datetime import datetime, timezone
import numpy as np, pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

BUILD_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
# instrument -> (location label, network, recording status on 8 Mar 2014, source of status, data held by the project)
INVENTORY = {
    "H01W": ("Cape Leeuwin (IMS H01W)", "IMS", "recording", "FDSN epoch 2004-; Kadri 2024 and Royer 2016 use 8 Mar 2014 data", "digitised"),
    "H08S": ("Diego Garcia South (IMS H08S)", "IMS", "recording", "FDSN epoch 2002-; Kadri 2024, CMST 2014 use 8 Mar 2014 data", "digitised"),
    "H08N": ("Diego Garcia North (IMS H08N)", "IMS", "recording", "FDSN epoch 2002-", "none"),
    "IMOS3315": ("Perth Canyon (IMOS 3315, 3376)", "IMOS", "recording", "Curtin metadata (deployment Nov 2013 - Mar 2014); files held", "raw"),
    "IMOS3376": ("Perth Canyon (IMOS 3315, 3376)", "IMOS", "recording", "Curtin metadata; IMOS archive has 20140308", "raw"),
    "IMOS3250": ("Scott Reef (IMOS 3250)", "IMOS", "recording", "Curtin metadata; IMOS archive has 20140308", "raw"),
    "IMOS3274": ("Portland (IMOS 3274, 3275)", "IMOS", "recording", "Curtin metadata; IMOS archive has 20140308", "raw"),
    "IMOS3275": ("Portland (IMOS 3274, 3275)", "IMOS", "recording", "Curtin metadata; files held", "raw"),
    "SWAMS1": ("SWAMS1-3 (OHASISBIO)", "OHASISBIO", "recording", "Royer 2016 Table 1 'recorded'", "digitised"),
    "SWAMS2": ("SWAMS1-3 (OHASISBIO)", "OHASISBIO", "recording", "Royer 2016 Table 1 'recorded'", "digitised"),
    "SWAMS3": ("SWAMS1-3 (OHASISBIO)", "OHASISBIO", "recording", "Royer 2016 Table 1 'recorded'", "digitised"),
    "SSEIR": ("SSEIR (OHASISBIO)", "OHASISBIO", "recording", "Royer 2016 Table 1 'recorded'", "digitised"),
    "MAD": ("MAD (OHASISBIO)", "OHASISBIO", "recording", "Royer 2016 Table 1 'recorded'", "digitised"),
    "NCRO": ("NCRO (OHASISBIO)", "OHASISBIO", "recording", "Royer 2016 Table 1 'recorded'", "digitised"),
    "WKER": ("WKER (OHASISBIO)", "OHASISBIO", "recording", "Royer 2016 Table 1 'recorded'", "digitised"),
    "NEAMS": ("NEAMS (OHASISBIO)", "OHASISBIO", "deployed; data lost on recovery", "Royer 2016 Table 1 'lost on recovery, no data'", "none"),
}
NOT_RECORDING = [("HA04 Crozet (IMS)", "installed Dec 2016, certified Jun 2017 (CTBTO)"),
                 ("IMOS Kangaroo Island, Tuncurry, Pilbara deployments", "no 8 Mar 2014 files in the public IMOS archive (S3 listing, 23 Oct 2026)")]
RANK = {"blocked": 0, "large attenuation": 1, "ridge (partial)": 2, "clear": 3}
INV_RANK = {v: k for k, v in RANK.items()}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--db", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    con = sqlite3.connect(a.db)
    con.execute("DELETE FROM attribute WHERE key IN ('recording_8mar2014','station_location','data_held')")
    con.execute("DELETE FROM attribute_key WHERE key IN ('recording_8mar2014','station_location','data_held')")
    con.executemany("INSERT INTO attribute_key (key, entity_type, datatype, unit, description) VALUES (?,?,?,?,?)", [
        ("recording_8mar2014", "site", "text", None, "Whether the instrument was recording on 8 March 2014, and the source of that statement."),
        ("station_location", "site", "text", None, "Location label used to count co-located instruments once."),
        ("data_held", "site", "text", None, "Data the project holds for 8 March 2014: raw, digitised or none.")])
    for s, (loc, net, rec, src, held) in INVENTORY.items():
        for k, v, note in [("recording_8mar2014", rec, src), ("station_location", loc, None), ("data_held", held, None)]:
            con.execute("INSERT INTO attribute (entity_type, entity_id, key, value_text, evidence, note, added_utc) VALUES (?,?,?,?,?,?,?)",
                        ("site", s, k, v, "stated in source" if k == "recording_8mar2014" else "project inventory", note, BUILD_UTC))
    con.executescript("""DROP VIEW IF EXISTS v_arc_los_by_location;
      CREATE VIEW v_arc_los_by_location AS
      SELECT ap.site_id, loc.value_text AS location, rec.value_text AS recording_8mar2014, held.value_text AS data_held,
             round(ap.arc_lat, 1) AS arc_lat, ap.arc_lon, ap.class, ap.obstacle_name
      FROM arc_path ap
      JOIN attribute loc ON loc.entity_id = ap.site_id AND loc.key = 'station_location'
      JOIN attribute rec ON rec.entity_id = ap.site_id AND rec.key = 'recording_8mar2014'
      JOIN attribute held ON held.entity_id = ap.site_id AND held.key = 'data_held';""")
    con.commit()
    V = pd.read_sql("SELECT * FROM v_arc_los_by_location", con)
    V["r"] = V["class"].map(RANK)
    # location class = most favourable instrument class
    LOCS = list(dict.fromkeys(v[0] for v in INVENTORY.values()))
    Lc = V.groupby(["location", "arc_lat"], as_index=False).r.max()
    Lc["class"] = Lc.r.map(INV_RANK)
    lats = np.sort(Lc.arc_lat.unique())[::-1]
    tip = lats.min()
    deg = [x for x in lats if abs(x - round(x)) < 1e-6] + [tip]
    rows = []
    for d in deg:
        g = Lc[Lc.arc_lat == d]
        band = Lc[(Lc.arc_lat <= d + 0.5) & (Lc.arc_lat >= d - 0.5)]
        clear_band = band.groupby("location").r.min()
        row = {"arc_lat_deg": d, "arc_lon_deg": round(V[V.arc_lat == d].arc_lon.iloc[0], 2),
               "n_locations": len(g),
               "n_clear": int((g["class"] == "clear").sum()),
               "n_clear_or_partial": int(g["class"].isin(["clear", "ridge (partial)"]).sum()),
               "n_large_attenuation": int((g["class"] == "large attenuation").sum()),
               "n_blocked": int((g["class"] == "blocked").sum()),
               "n_clear_throughout_pm0p5deg": int((clear_band == RANK["clear"]).sum()),
               "clear_locations": "; ".join(sorted(g[g["class"] == "clear"].location)),
               "partial_locations": "; ".join(sorted(g[g["class"] == "ridge (partial)"].location)),
               "large_attenuation_locations": "; ".join(sorted(g[g["class"] == "large attenuation"].location)),
               "blocked_locations": "; ".join(sorted(g[g["class"] == "blocked"].location))}
        held = {loc: V[V.location == loc].data_held.iloc[0] for loc in LOCS}
        row["n_clear_with_data_held"] = int(sum(1 for l in g[g["class"] == "clear"].location if held[l] != "none"))
        row["n_clear_with_raw_data"] = int(sum(1 for l in g[g["class"] == "clear"].location if held[l] == "raw"))
        rows.append(row)
    T = pd.DataFrame(rows)
    T.to_csv(a.out + ".csv", index=False)
    # per-location class at each integer degree (wide)
    W = Lc[Lc.arc_lat.isin(deg)].pivot(index="location", columns="arc_lat", values="class").reindex(LOCS)
    W = W[sorted(W.columns, reverse=True)]
    W.columns = [f"{abs(c):.1f}S" for c in W.columns]
    W.to_csv(a.out + "_by_location.csv")

    # ------------------------------------------------------------------ chart
    mpl.rcParams.update({"font.size": 8, "axes.labelsize": 9, "axes.titlesize": 9, "xtick.labelsize": 7, "ytick.labelsize": 7,
                         "axes.spines.top": False, "axes.spines.right": False, "xtick.direction": "out", "ytick.direction": "out"})
    fig = plt.figure(figsize=(12, 9.2), dpi=200)
    ax1 = fig.add_axes([0.25, 0.63, 0.70, 0.24]); ax2 = fig.add_axes([0.25, 0.235, 0.70, 0.37], sharex=ax1)
    full = []
    for d in lats:
        g = Lc[Lc.arc_lat == d]
        full.append((d, (g["class"] == "clear").sum(), g["class"].isin(["clear", "ridge (partial)"]).sum()))
    F = pd.DataFrame(full, columns=["lat", "clear", "clear_or_partial"])
    x = -F.lat
    ax1.step(x, F.clear_or_partial, where="mid", color="#7f7f7f", lw=1.0, label="clear, or ridge above hydrophone depth only (partial loss)")
    ax1.step(x, F.clear, where="mid", color="#1b6ca8", lw=1.6, label="clear line of sight")
    ax1.plot(-T.arc_lat_deg, T.n_clear, "o", ms=3.5, color="#1b6ca8", zorder=5)
    for _, r in T.iterrows():
        ax1.text(-r.arc_lat_deg, len(LOCS) + 0.9, f"{r.n_clear}", ha="center", va="bottom", fontsize=6.5, color="#1b6ca8")
    ax1.text(19.75, len(LOCS) + 0.9, "clear at each whole degree:", ha="right", va="bottom", fontsize=6.5, color="#1b6ca8")
    ax1.set_ylim(0, len(LOCS) + 0.5); ax1.set_yticks(range(0, len(LOCS) + 1, 2)); ax1.set_clip_on(False)
    ax1.set_ylabel(f"Station locations\n(of {len(LOCS)} recording)")
    ax1.legend(loc="lower left", frameon=False, fontsize=7)
    S = F[F.lat <= -33]; N = F[F.lat > -33]
    sh = (S.clear >= 8).mean()
    title = (f"South of 33° S, {S.clear[S.clear >= 8].min()}–{S.clear.max()} of the {len(LOCS)} recording station locations have clear line of sight at "
             f"{sh * 100:.0f} % of 7th-arc points;\nnorth of 33° S, mid-ocean ridges cut this to {N.clear.min()}–{N.clear.max()}")
    print("TITLE:", title.replace(chr(10), " "))
    fig.text(0.02, 0.985, title, fontsize=9.5, weight="bold", va="top", ha="left")
    plt.setp(ax1.get_xticklabels(), visible=False)
    # strip chart
    order = LOCS
    M = Lc.pivot(index="location", columns="arc_lat", values="r").reindex(order)
    M = M[sorted(M.columns, reverse=True)]
    cmap = ListedColormap(["#b2182b", "#f4a582", "#d9d9d9", "#4393c3"]); norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], 4)
    ax2.imshow(M.values, aspect="auto", cmap=cmap, norm=norm, interpolation="nearest",
               extent=[-M.columns.max() - 0.05, -M.columns.min() + 0.05, len(order) - 0.5, -0.5])
    held = {loc: V[V.location == loc].data_held.iloc[0] for loc in LOCS}
    rec = {loc: V[V.location == loc].recording_8mar2014.iloc[0] for loc in LOCS}
    ylabels = [f"{loc}  [{ {'raw': 'raw data held', 'digitised': 'digitised only', 'none': 'no data held'}[held[loc]] }]"
               + ("  †" if rec[loc] != "recording" else "") for loc in order]
    ax2.set_yticks(range(len(order))); ax2.set_yticklabels(ylabels, fontsize=7)
    ax2.set_xticks(range(20, 45, 2)); ax2.set_xticklabels([f"{t}° S" for t in range(20, 45, 2)])
    ax2.set_xlim(19.8, -tip + 0.15)
    ax2.set_xlabel("7th-arc latitude (arc points every 0.1°; southern end of the arc at 43.9° S)")
    for yy in [2.5, 5.5]:
        ax2.axhline(yy, color="white", lw=1.5)
    from matplotlib.patches import Patch
    ax2.legend(handles=[Patch(color="#4393c3", label="clear"), Patch(color="#d9d9d9", label="ridge above hydrophone depth (partial loss)"),
                        Patch(color="#f4a582", label="large attenuation"), Patch(color="#b2182b", label="blocked")],
               loc="upper left", bbox_to_anchor=(0.0, -0.13), ncol=4, frameon=False, fontsize=7)
    fn1 = ("Plain-language note.  For each point on the 7th arc, we follow the sea floor along the straight path to each station that was recording on "
           "8 March 2014. 'Clear' means no land, no shallow water and no long ridge that rises into the deep sound channel. A station with clear line of "
           "sight can receive the sound, but it does not show that the sound was loud enough to detect; that is the next step. Stations at one place are counted once. "
           "† NEAMS was recording, but its data was lost when it was recovered.")
    fn2 = ("Technical note.  Source: hydro_data.sqlite tables arc_path and attribute (arc_line_of_sight.py, arc_station_count.py). 7th arc: small circle, centre 0.570° N "
           "64.252° E, radius 44.501°. WGS84 geodesics on GEBCO 2026 (15 arc-s), ~1 km steps. Blocked: land or water shallower than min(receiver depth, 200 m) more than 20 km "
           "from the receiver. Large attenuation: >= 10 km shallower than 1,000 m more than 100 km from the receiver. Ridge above hydrophone depth: >= 10 km shallower than "
           "the hydrophone (deep receivers). Location class = most favourable instrument (Perth Canyon 3315/3376, Portland 3274/3275, SWAMS1-3). Not recording on "
           "8 Mar 2014: " + "; ".join(f"{n} ({w})" for n, w in NOT_RECORDING) + ". Island seismometers that record T-phases are not included. "
           "Geometric screen, not transmission loss; IMOS loggers record 34 % of the time.")
    fig.text(0.02, 0.11, textwrap.fill(fn1, 205), fontsize=6.5, va="top", linespacing=1.35)
    fig.text(0.02, 0.065, textwrap.fill(fn2, 205), fontsize=6.5, va="top", linespacing=1.35)
    fig.savefig(a.out + ".png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    fig.savefig(a.out + ".pdf", bbox_inches="tight", pad_inches=0.15)
    # checks
    fig.canvas.draw(); rr = fig.canvas.get_renderer()
    texts = [t for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
    bbs = [(t.get_text()[:30], t.get_window_extent(rr)) for t in texts]
    ov = [(p, q_) for i, (p, b) in enumerate(bbs) for q_, c in bbs[i + 1:] if b.overlaps(c)]
    print("text overlaps:", ov[:10])
    print(T[["arc_lat_deg", "arc_lon_deg", "n_clear", "n_clear_or_partial", "n_large_attenuation", "n_blocked",
             "n_clear_throughout_pm0p5deg", "n_clear_with_raw_data"]].to_string(index=False))
    con.close()


if __name__ == "__main__":
    main()
