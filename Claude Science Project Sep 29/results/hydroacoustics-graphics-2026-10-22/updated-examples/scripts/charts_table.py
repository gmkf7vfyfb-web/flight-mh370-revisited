"""Chart 7: hypothesis table A-G (A-F from the 21 Oct table, recomputed on tonight's arc and searches; G = tonight's
strongest two-station pair), as a table figure and a CSV."""
exec(open(str(WS_ROOT) + "/gfx/common.py").read())
from pyproj import Geod
import run_j_windows as R
G_ = Geod(ellps="WGS84"); RX = R.receivers()
TP = json.load(open(RD / "tl_grid_run_j" / "table_points.json")); PTS = sorted([(v["lat"], v["lon"]) for v in TP.values() if v["offset_nm"] == 0])
LA = np.array([p_[0] for p_ in PTS]); LO = np.array([p_[1] for p_ in PTS])
WIN = pd.read_csv(SR / "panels/panel_windows.csv"); WIN["ws"] = WIN.window_start_utc.map(unix)
T1 = pd.read_csv(SR / "named/table1_verdicts.csv")
C_LO, C_MID, C_HI = 1.470, 1.482, 1.494     # +/- 2 sd of N(1.482, 0.006) km/s


def dk(st, lat, lon): return float(G_.inv(lon, lat, RX[st][1], RX[st][0])[2] / 1000.0)
def az(st, lat, lon): return float(G_.inv(RX[st][1], RX[st][0], lon, lat)[0] % 360)


def tband(t_arr, d_km):
    return hms(t_arr - d_km / C_MID), hms(t_arr - d_km / C_LO), hms(t_arr - d_km / C_HI)


def pair_locus(tA, tB):
    dA = np.array([dk("H01W", a, b) for a, b in zip(LA, LO)]); dB = np.array([dk("H08S", a, b) for a, b in zip(LA, LO)])
    L = (dB - dA) / C_MID; lag = tB - tA; cr = np.where(np.diff(np.sign(L - lag)) != 0)[0]; out = []
    for i in cr:
        lat = float(np.interp(lag, [L[i], L[i + 1]], [LA[i], LA[i + 1]])); lon = float(np.interp(lat, LA, LO)); out.append((lat, lon))
    return lag, out


def win(rxn, t):
    tt = unix(t); m = WIN[(WIN.receiver == rxn) & (WIN.ws <= tt) & (WIN.ws + 55 > tt)]
    return {r.detector: r for r in m.itertuples()}


def build_rows():
    rows = []
    def t1(tm, brg): return T1[(T1.time_utc == tm) & np.isclose(T1.bearing_deg, brg)].iloc[0]
    # A, B: Table 1 catalogue entries
    for lab, tm, brg, old in (("A", "00:49:58", 260.41, "35.88 S 91.79 E; 00:26:22–00:28:29"), ("B", "00:53:31", 257.58, "36.74 S 90.52 E; 00:28:38–00:30:52")):
        r = t1(tm, brg); w = win("H01W", tm); tm_, lo_, hi_ = tband(unix(tm), r.range_km)
        rows.append(dict(row=lab, hypothesis=f"Catalogue entry {tm} ({brg:.2f}°)", source="Kadri (2024) Table 1, p. 14",
                         implied_position=f"{-r.arc_crossing_lat:.2f}°S {r.arc_crossing_lon:.2f}°E (bearing line meets the arc {r.line_to_arc_km:.1f} km off)",
                         implied_impact_utc=f"{tm_} ({lo_}–{hi_})", arrivals_utc=f"H01W {tm}; no Diego Garcia counterpart identified",
                         trace_assessment=(f"No candidate within 10 s. Window {w['M1b'].window_start_utc}: matched filter p {w['M1b'].p_A:.2f}, STA/LTA {w['D1'].p_A:.2f}, "
                                           f"band 2–5 Hz {w['BE'].p_A:.2f}. Impact time inside the 50 % band (00:19 data not used)."),
                         eta_needed="— (no signal)",
                         bearing=f"Bearing points into the run J impact region: log10 Bayes factor {r.log10_BF_demonstrated_t3_3p3:+.2f} ({r.bearing_verdict}).",
                         p_H01W=round(float(w["M1b"].p_A), 3), p_H08S=np.nan, old_21oct=old))
    # C: H01W 00:52 cluster (text time)
    w = win("H01W", "00:52:04.35"); ec = float(w["M1b"].eta_needed)
    rows.append(dict(row="C", hypothesis="Cape Leeuwin 00:52 cluster (text time 00:52:03)", source="Kadri (2024) Fig. 9(c) rectangle 1, p. 9; Table 1 caption, p. 14",
                     implied_position="No crossing of the southern arc for the 57° bearing of the text (it points north-east); for 306.18° see D",
                     implied_impact_utc="Unresolved (no mapped source position)", arrivals_utc="H01W 00:52:03 (Kadri); our peak 00:52:04.35",
                     trace_assessment=(f"Matched filter p {w['M1b'].p_A:.3f} at 00:52:04 (the only Cape Leeuwin value below 0.05: 1 of 120 tests, 6 expected by chance); "
                                       f"STA/LTA {w['D1'].p_A:.2f}; band 2–5 Hz {w['BE'].p_A:.2f}. Inside every option's 99 % arrival window."),
                     eta_needed=f"{ec:.3f} for the median impact ({ec / ETA_F35A:.0f} x the provisional F-35A value)",
                     bearing="57° (text) gives no arc crossing; 306.18° (Table 1 caption) gives row D.", p_H01W=round(float(w["M1b"].p_A), 3), p_H08S=np.nan,
                     old_21oct="no southern-arc intersection; unresolved"))
    # D: preferred candidate 00:54:30 / 306.18
    r = t1("00:54:30", 306.18); rt = T1[T1.event_id == "event_005430_text"].iloc[0]; w = win("H01W", "00:54:29"); ed = float(w["M1b"].eta_needed)
    tm_, lo_, hi_ = tband(unix("00:54:30"), r.range_km); tmt, lot, hit = tband(unix("00:52:03"), r.range_km)
    rows.append(dict(row="D", hypothesis="Preferred candidate 00:54:30 / 306.18°", source="Kadri (2024) Fig. 9(c) rectangle 2, p. 9; Table 1, p. 14",
                     implied_position=f"{-r.arc_crossing_lat:.2f}°S {r.arc_crossing_lon:.2f}°E (bearing line meets the arc {r.line_to_arc_km:.1f} km off)",
                     implied_impact_utc=f"{tm_} ({lo_}–{hi_}) at the caption time; {tmt} at the text time", arrivals_utc="H01W 00:54:30 (caption) or 00:52:03 (text); no Diego Garcia counterpart identified",
                     trace_assessment=(f"Matched filter p {w['M1b'].p_A:.3f} at 00:54:29 (screen level); STA/LTA {w['D1'].p_A:.2f}; band 5–9 Hz {w['BE'].p_A:.2f}. "
                                       f"Likelihood with the IMOS loggers: ln Bayes factor −0.004 (uninformative; only Perth Canyon 3376 recorded at the predicted time)."),
                     eta_needed=f"{ed:.3f} for the median impact ({ed / ETA_F35A:.0f} x the provisional F-35A value)",
                     bearing=f"Bearing test log10 Bayes factor {r.log10_BF_demonstrated_t3_3p3:+.2f} ({r.bearing_verdict}).", p_H01W=round(float(w["M1b"].p_A), 3), p_H08S=np.nan,
                     old_21oct="25.79 S 101.38 E; 00:36:01–00:37:40"))
    # E, F, G: two-station timing pairs
    for lab, ta, tb, hyp, src, old in (
            ("E", "00:52:04.35", "01:10:00.5", "Timing pair H01W 00:52:04.350 x H08S 01:10:00.500", "Kadri (2024) Fig. 9(c, e), p. 9; project analysis, not a source identification in the paper", "34.92 S 92.05 E; 00:28:38–00:30:44"),
            ("F", "00:54:26.95", "01:12:49.3", "Timing pair H01W 00:54:26.950 x H08S 01:12:49.300", "Kadri (2024) Fig. 9(c, e), p. 9; project analysis, not a source identification in the paper", "35.21 S 92.10 E; 00:31:07–00:33:12"),
            ("G", "00:52:04", "01:12:49", "Tonight's strongest two-station pair H01W 00:52:04 x H08S 01:12:49", "Digitised Kadri (2024) Fig. 9(c, e); searches and composition notes, 22 Oct 2026", "new row")):
        lag, loci = pair_locus(unix(ta), unix(tb)); lat, lon = loci[0]; d1 = dk("H01W", lat, lon); tm_, lo_, hi_ = tband(unix(ta), d1)
        a1, a2 = az("H01W", lat, lon), az("H08S", lat, lon)
        wa = win("H01W", ta); wb = win("H08S", tb)
        pa = float(wa["M1b"].p_A); pb = float(wb["M1b"].p_A) if wb else np.nan
        pos = f"{-lat:.2f}°S {lon:.2f}°E (lag {lag:,.0f} s; predicted lag range 809–1,536 s)"
        if len(loci) > 1: pos += f"; second crossing at {-loci[1][0]:.1f}°S, grid edge, prior mass < 0.1 %"
        if lab == "E":
            ta_txt = (f"H01W as row C (p {pa:.3f}). H08S 01:10:00.5 lies in the gap between the scored windows of panels d and e (panel edge, cropped segment): "
                      f"not scored, so not in tonight's pair list.")
            eta = f"H01W {float(wa['M1b'].eta_needed):.3f}; H08S not scored"
        elif lab == "F":
            ta_txt = (f"Pair found tonight (matched filter rows 00:54:29, p {pa:.3f} x 01:12:49, p {pb:.3f}; lag 1,100 s, inside the predicted range). The airgun-suppressed "
                      f"Diego Garcia residual does not keep the 01:12:49 row (p_B 0.30).")
            eta = f"H01W {float(wa['M1b'].eta_needed):.3f}; H08S {float(wb['M1b'].eta_needed):.1f}"
        else:
            ta_txt = (f"Matched filter p {pa:.3f} x p {pb:.3f}; the airgun-suppressed residual does not keep the H08S row (p_B 0.30). 19 lag-consistent pairs against 8.8 expected, "
                      f"permutation p 0.019; over 36 receiver-pair tests the smallest p is at or below 0.019 by chance with probability 0.51.")
            eta = f"Both stations P_D = 0.5: 0.069 (330 x the provisional F-35A value); single rows H01W 0.026, H08S 1.5"
        brg = (f"Locus at {a1:.1f}° from H01W and {a2:.1f}° from H08S." if lab != "G" else
               "Locus at 268.9° from H01W and 144.8° from H08S. Kadri gives 57° (text) or 306.18° (Table 1 caption) for the 00:52 signal: neither is within 37°. "
               "Nearest Table 1 bearing: 00:52:50 at 274.84°, 46 s later (its window: matched filter p 0.51).")
        if lab == "E": brg += f" Kadri's 306.18° is {306.18 - a1:.0f}° away."
        if lab == "F": brg += f" Kadri's 306.18° for 00:54:30 is {306.18 - a1:.0f}° away."
        rows.append(dict(row=lab, hypothesis=hyp, source=src, implied_position=pos, implied_impact_utc=f"{tm_} ({lo_}–{hi_})",
                         arrivals_utc=f"H01W {ta}; H08S {tb}", trace_assessment=ta_txt, eta_needed=eta, bearing=brg, p_H01W=round(pa, 3),
                         p_H08S=round(pb, 3) if np.isfinite(pb) else np.nan, old_21oct=old, az_H01W_recomputed=round(a1, 2), az_H08S_recomputed=round(a2, 2),
                         locus_lat=round(lat, 3), locus_lon=round(lon, 3), lag_s=round(lag, 1)))
    return pd.DataFrame(rows)


def chart7(fname, csvname):
    df = build_rows(); df.to_csv(OUT / csvname, index=False)
    cols = [("hypothesis", "Hypothesis and source", 0.16, 0), ("implied_position", "Implied position", 0.125, 0), ("implied_impact_utc", "Implied impact, UTC", 0.10, 0),
            ("arrivals_utc", "Arrival(s), UTC", 0.105, 0), ("trace_assessment", "Our trace assessment (22 Oct searches)", 0.235, 0),
            ("eta_needed", "Coupling needed", 0.105, 0), ("bearing", "Bearing consistency", 0.165, 0)]
    FS = 7.3; cols = [(k, h, w_, int(w_ * 16 / (FS * 0.585 / 72)) - 1) for k, h, w_, _ in cols]
    fig = plt.figure(figsize=(16, 7.9))
    plain = ("Each row is one idea about where and when the aircraft hit the water, from Kadri's paper or from our own timing analysis. The columns give "
             "the place and time that the idea needs, the times of the signals, what our detectors found in the published traces, how much of the impact "
             "energy would have to become sound, and whether the direction from Cape Leeuwin agrees. A p-value near 0.05 among many tests is expected by "
             "chance. Row G is the strongest pair of signals found tonight, but its direction does not agree with any direction that Kadri gives.")
    tech = ("Rows A–F carry the hypotheses of the 21 Oct table; every number is recomputed tonight: positions on the offset-0 arc of the block-2 TL grid "
            "(table_points.json); implied impact = H01W arrival − WGS84 geodesic / c, c = 1.482 km/s (range for c = 1.470–1.494, +/- 2 sd); bearing-line loci "
            "and Bayes factors from named/table1_verdicts.csv (Student-t(3), sd 3.3 deg, demonstrated error model). The 21 Oct values (column old_21oct of the CSV) "
            "differ by up to 1.2 deg in latitude for E and F because the earlier table used another arc and speed. p = per-window p_A of the block-5 panel search "
            "on the DIGITISED Fig. 9 traces (panels/panel_windows.csv), matched filter = M1b envelope; H08S p_B = airgun-suppressed residual null. Pair statistics: "
            "coincidence/coincidence_summary.csv (H01W x H08S, primary matched-filter family). Coupling needed: eta at which the run J D0′ median impact (1.13 GJ, "
            "tau90 3.3 s) gives the observed excess at the station (searches note), and for G the eta at which P_D(H01W) x P_D(H08S) = 0.5 at the pair locus "
            "(composition note, alpha 0.05, +4.8 dB triad gain). Bearings measured clockwise from north at the station; recomputed from the triad centroid: G "
            "269.0 deg / 144.8 deg (268.9 deg in the parent check). Kadri bearing: text p. 9 says 57 deg, Table 1 caption 306.18 deg; they disagree. " + CAV)
    b = need_bottom(fig, plain, tech)
    top = 0.935; x0 = 0.012
    xs = [x0]; [xs.append(xs[-1] + c[2]) for c in cols]
    y = top
    for (k, h, w_, n), x in zip(cols, xs): fig.text(x + 0.003, y, h, fontsize=7.5, weight="bold", va="top", ha="left")
    y -= 0.022; fig.add_artist(matplotlib.lines.Line2D([x0, xs[-1]], [y, y], color="#333333", lw=0.8))
    avail = y - (b + 0.01)
    wrapped = []
    for _, r in df.iterrows():
        cells = []
        for k, h, w_, n in cols:
            txt = (f"{r.row} · {r.hypothesis}\n" + textwrap.fill(r.source, n)) if k == "hypothesis" else str(r[k])
            if k == "hypothesis": txt = "\n".join(textwrap.fill(s_, n) for s_ in txt.split("\n"))
            else: txt = textwrap.fill(txt, n)
            cells.append(txt)
        wrapped.append(cells)
    nl = [max(c.count("\n") + 1 for c in cells) for cells in wrapped]; lh = FS * 1.18 / 72 / fig.get_size_inches()[1]
    for (_, r), cells, n_ in zip(df.iterrows(), wrapped, nl):
        y -= 0.45 * lh
        if r.row == "G": fig.add_artist(matplotlib.patches.Rectangle((x0, y - n_ * lh - 0.3 * lh), xs[-1] - x0, n_ * lh + 0.55 * lh, color="#fff3dc", zorder=0))
        for cell, x, (k, h, w_, n) in zip(cells, xs, cols):
            fig.text(x + 0.003, y, cell, fontsize=FS, va="top", ha="left", linespacing=1.18, weight="bold" if False else "normal")
        y -= n_ * lh + 0.45 * lh
        fig.add_artist(matplotlib.lines.Line2D([x0, xs[-1]], [y, y], color="#cccccc", lw=0.5))
    fig.text(0.01, 0.985, "Where and when each candidate idea puts the impact, and what tonight's searches of the published traces say about it", fontsize=10, ha="left", va="top")
    footnotes(fig, plain, tech)
    return save(fig, fname, check=False), df
