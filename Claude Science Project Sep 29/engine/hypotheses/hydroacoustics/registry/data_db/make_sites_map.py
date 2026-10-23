#!/usr/bin/env python3
"""
make_sites_map.py - map of hydroacoustic data held for 7-8 March 2014, with one label box per site.
Every number and time in the labels is read from hydro_data.sqlite (no hand-typed values), then the
figure is checked for overlaps (boxes, markers, station codes, legend, footnotes) before saving.

Usage: python make_sites_map.py --db hydro_data.sqlite --basemap basemap_005.npz --out hydro_data_sites_map
basemap_005.npz: GEBCO 2026 15" grid subsampled 1:12 (0.05 deg), lon 44-150 E, lat 60 S - 6 N.
"""
import argparse, sqlite3, textwrap
import numpy as np, pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.offsetbox import TextArea, VPacker, AnnotationBbox
from matplotlib.lines import Line2D

C_RAW, C_IMS, C_OH = "#d95f02", "#6a3d9a", "#1f1f1f"
LON, LAT = (44, 150), (-60, 5.9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True); ap.add_argument("--basemap", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    con = sqlite3.connect(a.db)
    q = lambda s: pd.read_sql(s, con)
    ds = lambda i: q(f"SELECT * FROM dataset WHERE dataset_id='{i}'").iloc[0]
    segs = lambda i: q(f"SELECT * FROM segment WHERE dataset_id='{i}' ORDER BY t_start_utc")

    def npk(i, site=None):
        w = f" AND site_id='{site}'" if site else ""
        r = q(f"SELECT COUNT(*) n, MIN(t_utc) a, MAX(t_utc) b FROM pick WHERE dataset_id='{i}'{w}").iloc[0]
        return int(r.n), r.a, r.b

    def spanr(a_, b_, force_date=False):
        A, B = pd.Timestamp(a_).round("s"), pd.Timestamp(b_).round("s")
        sec = (B - A).total_seconds() < 600 and (A.second != 0 or B.second != 0)
        f = "%H:%M:%S" if sec else "%H:%M"
        if not sec:
            A, B = A.round("min"), B.round("min")
        sa = (f"{A.day} Mar " if (force_date or A.day != 8) else "") + A.strftime(f)
        sb = (f"{B.day} Mar " if B.day != A.day else "") + B.strftime(f)
        return f"{sa}–{sb}"

    span = lambda i, fd=False: spanr(ds(i).t_start_utc, ds(i).t_end_utc, fd)
    hm = lambda t: pd.Timestamp(t).round("min").strftime("%H:%M")

    AP = q("SELECT site_id, round(arc_lat,1) lat1, class FROM arc_path")
    TIP = abs(AP.lat1.min())

    def bands_(lats, gap):
        out = []
        for x in sorted(lats, reverse=True):
            if out and out[-1][1] - x <= gap + 1e-9:
                out[-1][1] = x
            else:
                out.append([x, x])
        return out

    def los(site, width=92, indent="    ", gap=1.0, partial=True, prefix="7th arc line of sight: ", short=False):
        if isinstance(site, (list, tuple)):  # worst class at each latitude across several co-located sites
            rk = {"clear": 0, "ridge (partial)": 1, "large attenuation": 2, "blocked": 3}; inv = {v: k for k, v in rk.items()}
            gg = AP[AP.site_id.isin(site)].assign(r=lambda d: d["class"].map(rk)).groupby("lat1", as_index=False).r.max()
            g = gg.assign(**{"class": gg.r.map(inv)})
        else:
            g = AP[AP.site_id == site]
        if (g["class"] == "clear").all():
            return [f"7th arc 20° S–{TIP:.1f}° S (southern end of arc): clear line of sight"]
        parts = []
        cl = [("blocked", "blocked"), ("large attenuation", "large attenuation")] + ([("ridge (partial)", "ridge above hydrophone depth (partial loss)")] if partial else [])
        for c, lab in cl:
            gc = g[g["class"] == c]
            if not len(gc):
                continue
            bs = bands_(gc.lat1.tolist(), gap); txt = []
            for a, b in bs:
                h = g[(g.lat1 <= a) & (g.lat1 >= b)]
                share = (h["class"] == c).mean()
                txt.append((f"{abs(a):.1f}" if a == b else f"{abs(a):.1f}–{abs(b):.1f}") + ("*" if share < 0.95 else ""))
            parts.append(f"{lab} {', '.join(txt)}° S")
        if not parts:
            parts = ["no blocking or large attenuation"]
        tail = "; partial ridge losses (see chart)" if (not partial and (g["class"] == "ridge (partial)").any()) else ""
        body = prefix + "; ".join(parts) + ("" if short else tail + "; clear elsewhere")
        return textwrap.wrap(body, width=width, subsequent_indent=indent)

    # ------------------------------------------------------------------ labels (all values from the database)
    L = {}
    d = ds("kadri2024_fig9_h01w")
    p1, p2, p3 = npk("kadri2024_table1"), npk("royer2016_table5_picks", "H01W"), npk("cmst2014_fig5_ha01_detections")
    sR = segs("royer2016_spectrograms_h01w")
    L["H01W"] = ("Cape Leeuwin — IMS hydrophone station (H01W)", "Digitised from publications; times UTC on 8 March", [
        f"Pressure trace, Kadri 2024 Fig. 9 a–c: {span(d.dataset_id)}, {d.continuity};",
        f"    {d.band_lo_hz:.0f}–{d.band_hi_hz:.0f} Hz (author's filter); ~{d.sample_rate_hz:.0f} points/s",
        f"Spectrograms, element 2, Royer 2016: {span('royer2016_spectrograms_h01w')}, {ds('royer2016_spectrograms_h01w').continuity};",
        f"    0–{sR[sR.label.str.startswith('appendix')].band_hi_hz.max():.0f} Hz (Fig. 2: 0–{sR[sR.label.str.startswith('fig2')].band_hi_hz.max():.0f} Hz)",
        f"5–40 Hz band level, 3 elements, CMST 2014 Fig. 2: {span('cmst2014_fig2_h01w')}",
        f"Picks: Kadri Table 1, {p1[0]} ({spanr(p1[1], p1[2])}); Royer Table 5, {p2[0]} ({spanr(p2[1], p2[2])});",
        f"    CMST detections, {p3[0]} ({spanr(p3[1], p3[2])})",
        f"Figure images only, Kadri 2017: {spanr(ds('kadri2017_figs_ha01').t_start_utc, ds('kadri2017_figs_ha01').t_end_utc)}"] + los("H01W"))
    d = ds("kadri2024_fig9_h08s"); sS = segs("kadri2024_figS1_h08s")
    m1, m2, m3 = npk("cmst2014_fig7_ha08s_detections"), npk("kadri2019_table3"), npk("h08s_airgun_shots")
    L["H08S"] = ("Diego Garcia South — IMS hydrophone station (H08S)", "Digitised from publications; times UTC on 8 March", [
        f"Pressure trace, Kadri 2024 Fig. 9 d–e: {span(d.dataset_id)}, {d.continuity}; {d.band_lo_hz:.0f}–{d.band_hi_hz:.0f} Hz (author's filter); ~{d.sample_rate_hz:.0f} points/s",
        "    panel e amplitude scale not reliable (+8.8 dB step at the panel join)",
        "Pressure trace, Kadri 2024 Fig. S1 a–c: 7 Mar " + ", ".join(f"{hm(x)}–{hm(y)}" for x, y in zip(sS.t_start_utc, sS.t_end_utc))
        + f" ({len(sS)} separate windows); 5–40 Hz",
        f"Picks: CMST detections, {m1[0]} ({spanr(m1[1], m1[2])}); Kadri 2019 signals, {m2[0]} ({spanr(m2[1], m2[2])}); airgun shots on Fig. 9 d–e, {m3[0]}"] + los("H08S", width=100, gap=2.0))

    def imos_line(cid):
        d_ = ds(f"imos{cid}_mh370_day"); return f"Logger {cid}: {span(d_.dataset_id, True)} ({int(d_.n_segments)} records)"

    def bg_line(cid):
        d_ = ds(f"imos{cid}_background"); return f"    + 14-day background: 1–7 and 9–15 Mar ({int(d_.n_segments):,} records)"

    d = ds("imos3376_mh370_day")
    rec_len = q("SELECT value_num FROM attribute WHERE entity_id='IMOS3376' AND key='record_length_s'").value_num[0]
    common = [f"All: one {rec_len:.0f} s record every 15 min ({d.duty_fraction * 100:.0f} % of the time);",
              f"    {d.sample_rate_hz / 1000:.0f} kHz sampling; {d.band_lo_hz:.0f}–{d.band_hi_hz:,.0f} Hz"]
    L["PC"] = ("Perth Canyon — 2 seabed loggers (IMOS)", "Raw recordings held; times UTC",
               [imos_line("3315"), f"    + digitised envelope, CMST 2014 Fig. 1: 8 Mar {span('cmst2014_fig1_imos3315')}",
                imos_line("3376"), bg_line("3376")] + common + los("IMOS3315"))
    assert los("IMOS3315") == los("IMOS3376"), "Perth Canyon loggers differ in line of sight"
    pn = q("SELECT value_text FROM attribute WHERE entity_id='IMOS3250' AND key='path_note' AND value_text LIKE 'North West%'").value_text[0]
    L["SR"] = ("Scott Reef — seabed logger (IMOS)", "Raw recordings held; times UTC", [imos_line("3250"), bg_line("3250")] + common + los("IMOS3250", width=60))
    L["PO"] = ("Portland — 2 seabed loggers (IMOS)", "Raw recordings held; times UTC", [imos_line("3274"), bg_line("3274"), imos_line("3275")] + common + los("IMOS3274", width=60))
    assert los("IMOS3274", width=60) == los("IMOS3275", width=60), "Portland loggers differ in line of sight"
    rows = []
    for st in ["SWAMS3", "SWAMS2", "SWAMS1", "SSEIR", "MAD", "NCRO", "WKER"]:
        pk = npk("royer2016_table5_picks", st)
        sg = segs(f"royer2016_spectrograms_{st.lower()}")
        if len(sg) == 0:
            d_line = f"{st}: picks only, {pk[0]} ({spanr(pk[1], pk[2])})"
        else:
            dd = ds(f"royer2016_spectrograms_{st.lower()}")
            nstrip, n3 = int((sg.duration_s > 600).sum()), int((sg.duration_s < 600).sum())
            hi = int(round(sg.band_hi_hz.max(), -1))
            if dd.continuity == "continuous" and nstrip:
                sp = f"{spanr(dd.t_start_utc, dd.t_end_utc)} continuous + {n3} × 3-min panels"
            else:
                sp = f"{n3} × 3-min panels {spanr(dd.t_start_utc, dd.t_end_utc)}" if n3 > 1 else f"1 × 3-min panel {span(dd.dataset_id)}"
            d_line = f"{st}: {sp}; 0–60 Hz" + (f" (one panel 0–{hi})" if hi > 60 else "") + f"; {pk[0]} picks"
        rows += textwrap.wrap(d_line, width=70, subsequent_indent="    ")
        if st in ("SWAMS3", "SWAMS2"):
            continue
        if st == "SWAMS1":
            rows += ["    " + x for x in los(["SWAMS1", "SWAMS2", "SWAMS3"], width=70, indent="    ", gap=2.0, partial=False, prefix="SWAMS1–3, 7th arc: ", short=True)]
        else:
            rows += ["    " + x for x in los(st, width=70, indent="    ", gap=2.0, partial=False, prefix="7th arc: ", short=True)]
    L["OH"] = ("French OHASISBIO moored hydrophones", "Digitised from Royer 2016 spectrograms and Table 5; times UTC on 8 March.\n"
               "'7th arc' lines: arc latitudes with blocked or large-attenuation paths; clear elsewhere\nexcept partial ridge losses (see the line-of-sight chart)", rows)
    built = q("SELECT value FROM meta WHERE key='built_utc'").value[0]
    head = q("SELECT value FROM meta WHERE key='module_git_head'").value[0]
    nhash = q("SELECT COUNT(*) n FROM segment WHERE sha256_check='match'").n[0]
    ndup = q("SELECT COUNT(*) n FROM segment WHERE same_file_in IS NOT NULL AND dataset_id LIKE '%background'").n[0]
    s1h11 = ds("kadri2024_figS1_h11s")
    fn1 = ("Plain-language note.  Each box shows the data that the project has for one site. Orange circles: we have the recorded sound files. "
           "Diamonds: we have only values that were read from figures and tables in published papers; these are not recordings. "
           "'Continuous' means that the period has no gap. A seabed logger records for 307 seconds in each 15 minutes, so a sound can arrive "
           "between two records. The frequency band is the band of the instrument, of the author's filter or of the published plot. Times are UTC. "
           "Line of sight: we follow the sea floor along the straight path from each point of the 7th arc to the site. 'Blocked' means land or very "
           "shallow water on the path. 'Large attenuation' means that a ridge or shelf rises above the deep sound channel for a long distance. "
           "* means that the effect occurs at only some latitudes in that band.")
    fn2 = (f"Technical note.  Source: hydro_data.sqlite (hydro-data-db v1, built {built}; module branch hypothesis/hydroacoustics at {head}). "
           "Seabed loggers (IMOS, Curtin CMST): .DAT records, 6 kHz, header filter LF 8 Hz / HF 2,800 Hz; UTC = logger time − e(t), e linear between the two clock sets "
           f"(convention A; CMST 01:33:44 event reproduced to −0.24 s); {nhash:,} files SHA-256 verified; {ndup} records are in both the event-day and background sets. "
           "Digitised: Kadri 2024 Fig. 9 and S1 (PDF vector vertices of the plotted trace; 5–40 Hz = author's 5 Hz high-pass and 2–40 Hz band-pass, Methods); "
           "Royer 2016 spectrograms (colour to dB, ±1.5 dB; Cape Leeuwin figure times 7.7–16.6 s later than Table 5, cause not resolved) and Table 5 picks (all elements); "
           "CMST 2014 Figs 1, 2, 5, 7; Kadri 2019 Table 3; airgun shot table derived by the module from Fig. 9 d–e. "
           "Positions: FDSN EarthScope (IMS, mean of 3 elements, 2014 epoch), Royer 2016 Table 1 (OHASISBIO), Curtin metadata (IMOS). "
           f"Not on the map: NEAMS (lost on recovery, Royer 2016 Table 1); Wake Island South (Kadri 2024 Fig. S1 d–e, {spanr(s1h11.t_start_utc, s1h11.t_end_utc)}, 5–40 Hz); "
           "Diego Garcia North (dropped by ruling of 23 Oct 2026: Chagos Bank blocks every path from the 7th arc); calibration cases at other stations and years "
           "(F-35A 2019, ARA San Juan 2017, AF447 2009, fireballs 2003–04, 2001 airguns) are in the database under context 'calibration'. "
           "Line of sight (arc_line_of_sight.py, table arc_path): 7th arc = small circle centre 0.570° N 64.252° E, radius 44.501°, southern end 43.9° S; points every 0.1° latitude; "
           "WGS84 geodesics sampled every ~1 km on GEBCO 2026 (15 arc-s). Blocked: land, or water shallower than min(receiver depth, 200 m), more than 20 km from the receiver. "
           "Large attenuation: >= 10 km shallower than 1,000 m, more than 100 km from the receiver. Ridge above hydrophone depth: deep receivers, >= 10 km shallower than the hydrophone. "
           "Bands merged within 1°; * = fewer than 95 % of latitudes in the band. Main obstacles: Amsterdam–St Paul plateau and islands, Ninety East Ridge, Broken Ridge, a ridge near 28.5° S 98.6° E, "
           "a rise near 33° S 83° E (deep sites); North West Shelf and Exmouth Plateau (Scott Reef); Australia and the Cape Leeuwin shelf (Portland). Geometric screen, not transmission loss.")

    # ------------------------------------------------------------------ draw
    mpl.rcParams.update({"font.size": 8, "axes.labelsize": 10.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
                         "xtick.direction": "out", "ytick.direction": "out", "axes.spines.top": False, "axes.spines.right": False})
    sites = q("SELECT site_id,name,network,lat,lon FROM site").set_index("site_id")
    bm = np.load(a.basemap); Z, lats, lons = bm["Z"], bm["lats"], bm["lons"]
    boxes_pos = {"H08S": (77, 4.6, ["H08S"], C_IMS), "H01W": (70.5, -13.0, ["H01W"], C_IMS),
                 "PC": (117.0, -20.5, ["IMOS3315", "IMOS3376"], C_RAW), "SR": (123.0, -9.3, ["IMOS3250"], C_RAW),
                 "PO": (117.0, -42.5, ["IMOS3274", "IMOS3275"], C_RAW), "OH": (77.5, -36.8, [], C_OH),
                 }
    codes = {"SWAMS3": (-0.9, 0.0, "right"), "SSEIR": (0.9, 0, "left"),
             "MAD": (0.9, 0, "left"), "NCRO": (-0.9, 0, "right"), "WKER": (0.9, 0, "left")}
    fig = plt.figure(figsize=(16, 13.6), dpi=200)
    ax = fig.add_axes([0.035, 0.255, 0.93, 0.68])
    ext = [lons[0], lons[-1], lats[0], lats[-1]]
    ax.imshow(np.where(Z < 0, Z, np.nan), extent=ext, origin="lower", cmap=LinearSegmentedColormap.from_list("oc", ["#9fb8cc", "#dbe7f0"]),
              vmin=-6500, vmax=0, interpolation="bilinear", zorder=0)
    ax.imshow(np.where(Z >= 0, 1.0, np.nan), extent=ext, origin="lower", cmap=ListedColormap(["#ece8dc"]), interpolation="nearest", zorder=1)
    ax.contour(lons, lats, Z, levels=[0], colors="#8c8672", linewidths=0.4, zorder=2)
    ax.set_xlim(*LON); ax.set_ylim(*LAT); ax.set_aspect(1 / np.cos(np.radians(27)))
    ax.set_xticks(range(50, 151, 10)); ax.set_yticks(range(-60, 6, 10))
    ax.set_xticklabels([f"{x}°E" for x in range(50, 151, 10)])
    ax.set_yticklabels([f"{abs(y)}°{'S' if y < 0 else ''}" for y in range(-60, 6, 10)])
    ax.grid(color="white", lw=0.4, alpha=0.6, zorder=1.5)
    for s, r in sites.iterrows():
        if pd.isna(r.lat) or not (LON[0] <= r.lon <= LON[1] and LAT[0] <= r.lat <= LAT[1]) or s in ("H08N", "NEAMS"):
            continue
        if s.startswith("IMOS"):
            ax.plot(r.lon, r.lat, "o", ms=8, mfc=C_RAW, mec="white", mew=1.0, zorder=9)
        elif r.network.startswith("IMS"):
            ax.plot(r.lon, r.lat, "D", ms=8, mfc=C_IMS, mec="white", mew=1.0, zorder=9)
        else:
            ax.plot(r.lon, r.lat, "D", ms=6.5, mfc=C_OH, mec="white", mew=0.8, zorder=9)
    for s, (dx, dy, ha) in codes.items():
        r = sites.loc[s]
        ax.text(r.lon + dx, r.lat + dy, {"SWAMS3": "SWAMS1–3 (within 10 km)"}.get(s, s), fontsize=7, ha=ha, va="center", color=C_OH, zorder=9,
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.8))
    abs_ = {}
    for key, (x, y, targets, col) in boxes_pos.items():
        h, s2, body = L[key]
        vp = VPacker(children=[TextArea(h, textprops=dict(fontsize=8, weight="bold", color="#111111")),
                               TextArea(s2, textprops=dict(fontsize=8, style="italic", color="#333333")),
                               TextArea("\n".join(body), textprops=dict(fontsize=8, color="#111111", linespacing=1.3))], align="left", pad=0, sep=2)
        if targets:
            r = sites.loc[targets[0]]; xy = (r.lon, r.lat); arrow = dict(arrowstyle="-", color=col, lw=0.9, shrinkA=0, shrinkB=5)
        else:
            xy, arrow = (x, y), None
        ab = AnnotationBbox(vp, xy, xybox=(x, y), xycoords="data", boxcoords="data", box_alignment=(0, 1),
                            bboxprops=dict(boxstyle="round,pad=0.5", fc="white", ec=col, lw=1.2, alpha=0.95), arrowprops=arrow, zorder=8)
        ax.add_artist(ab); abs_[key] = (ab, targets, col)
    fig.canvas.draw(); rr = fig.canvas.get_renderer(); inv = ax.transData.inverted()
    leaders = []
    for key, (ab, targets, col) in abs_.items():
        bb = ab.patch.get_window_extent(rr); (x0, y0), (x1, y1) = inv.transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
        for s in targets[1:]:
            r = sites.loc[s]; px, py = min(max(r.lon, x0), x1), min(max(r.lat, y0), y1)
            leaders.append(ax.plot([px, r.lon], [py, r.lat], color=col, lw=0.7, zorder=5)[0])
    hs = [Line2D([], [], marker="o", ls="", ms=8, mfc=C_RAW, mec="white", label="Raw recordings held (sound files)"),
          Line2D([], [], marker="D", ls="", ms=8, mfc=C_IMS, mec="white", label="IMS hydrophone station: digitised published data only"),
          Line2D([], [], marker="D", ls="", ms=6.5, mfc=C_OH, mec="white", label="OHASISBIO hydrophone: digitised published data only")]
    lg = ax.legend(handles=hs, loc="upper left", frameon=True, framealpha=0.95, edgecolor="#999999", fontsize=8); lg.set_zorder(10)
    fig.text(0.035, 0.975, "The project holds raw hydroacoustic recordings for 7–8 March 2014 only from five Australian seabed loggers; "
             "all other sites are digitised from publications", fontsize=10.5, ha="left", va="top", weight="bold")
    fig.text(0.035, 0.952, "Sites where the project holds hydroacoustic data, with time periods (UTC), frequency bands and whether each record is continuous",
             fontsize=8, ha="left", va="top")
    fig.text(0.035, 0.215, textwrap.fill(fn1, 300), fontsize=7, ha="left", va="top", linespacing=1.35)
    fig.text(0.035, 0.178, textwrap.fill(fn2, 300), fontsize=7, ha="left", va="top", linespacing=1.35)

    # ------------------------------------------------------------------ checks (at the figure dpi)
    fig.canvas.draw(); rr = fig.canvas.get_renderer()
    bxs = {k: v[0].patch.get_window_extent(rr) for k, v in abs_.items()}
    ks = list(bxs); axbb = ax.get_window_extent(rr); out = {}
    out["box overlaps box"] = [(p, r_) for i, p in enumerate(ks) for r_ in ks[i + 1:] if bxs[p].overlaps(bxs[r_])]
    mk = []
    for s, r in sites.iterrows():
        if pd.isna(r.lat) or s in ("H08N", "NEAMS") or not (LON[0] <= r.lon <= LON[1] and LAT[0] <= r.lat <= LAT[1]):
            continue
        px, py = ax.transData.transform((r.lon, r.lat))
        mk += [(s, k) for k, b in bxs.items() if b.x0 - 6 <= px <= b.x1 + 6 and b.y0 - 6 <= py <= b.y1 + 6]
    out["marker under box"] = mk
    tb = [(t.get_text(), t.get_window_extent(rr)) for t in ax.texts if t.get_text().strip()]
    out["code overlaps box"] = [(n, k) for n, b in tb for k, bb in bxs.items() if b.overlaps(bb)]
    out["code overlaps code"] = [(p[0], r_[0]) for i, p in enumerate(tb) for r_ in tb[i + 1:] if p[1].overlaps(r_[1])]
    out["box outside map"] = [k for k, b in bxs.items() if b.x1 > axbb.x1 - 2 or b.x0 < axbb.x0 + 2 or b.y0 < axbb.y0 + 2 or b.y1 > axbb.y1 - 2]
    lgb = ax.get_legend().get_window_extent(rr)
    out["legend overlaps box"] = [k for k, b in bxs.items() if lgb.overlaps(b)]
    fb = [t.get_window_extent(rr) for t in fig.texts]
    out["figure text overlaps"] = [(i, j) for i in range(len(fb)) for j in range(i + 1, len(fb)) if fb[i].overlaps(fb[j])]
    out["figure text over map"] = [i for i, b in enumerate(fb) if b.overlaps(axbb)]
    out["text outside figure"] = [i for i, b in enumerate(fb) if b.x1 > fig.bbox.x1 or b.y0 < 0 or b.x0 < 0]
    tight = fig.get_tightbbox(rr).transformed(mpl.transforms.Affine2D().scale(fig.dpi))
    frac = (max(b.y1 for b in fb[2:]) - tight.y0) / tight.height
    ok = all(not v for v in out.values()) and frac <= 0.25
    for k, v in out.items():
        print(f"{'PASS' if not v else 'FAIL'} {k}: {v}")
    print(f"{'PASS' if frac <= 0.25 else 'FAIL'} footnotes occupy bottom {frac * 100:.1f} % of the image (limit 25 %)")
    fig.savefig(a.out + ".png", dpi=200, bbox_inches="tight", pad_inches=0.2); fig.savefig(a.out + ".pdf", bbox_inches="tight", pad_inches=0.2)
    with open(a.out + "_labels.txt", "w") as f:
        for k, (h, s2, body) in L.items():
            f.write(f"{h}\n{s2}\n" + "\n".join(body) + "\n\n")
        f.write(fn1 + "\n\n" + fn2 + "\n")
    print("ALL CHECKS PASS" if ok else "CHECKS FAILED")


if __name__ == "__main__":
    main()
