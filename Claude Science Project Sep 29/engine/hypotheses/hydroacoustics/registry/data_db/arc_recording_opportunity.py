#!/usr/bin/env python3
"""
arc_recording_opportunity.py - observation opportunity for a 7th-arc impact on 8 March 2014: bathymetric line of sight
(table arc_path) combined with what each instrument was recording at the time the sound would arrive.

Chart 1 (<out>_by_latitude): per 0.1 deg of arc latitude, each station location's state over the whole reception window
          [t_start + d/c, t_end + d/c].  Red = blocked, or not recording (data lost).  Purple = recording only part of
          the time (IMOS loggers, 307 s every 15 min; Perth Canyon and Portland have two staggered loggers each).
Chart 2 (<out>_by_impact_time): for impacts at 25, 30, 35 and 40 S on the arc, impact time on the x-axis; each
          location is coloured at its own reception time t + d/c: line-of-sight class if recording, red if blocked
          or not recording.

Recording status (from hydro_data.sqlite):
  IMOS 3315/3376/3250/3274/3275 - the actual record windows in table segment (UTC, clock-corrected), event-day and
          background sets joined.
  OHASISBIO - Royer 2016: "The data are sampled continuously at 240Hz"; all recovered instruments recorded on 8 Mar 2014;
          NEAMS "was lost during recovery" (no data).
  IMS H01W, H08S - continuous 250 Hz; 8 Mar 2014 data used by Kadri 2024, Royer 2016, CMST 2014.
  IMS H08N - continuous 250 Hz assumed (FDSN epoch 2002-); no published use of its 8 Mar 2014 data found.

Usage: python arc_recording_opportunity.py --db hydro_data.sqlite --out arc_recording_opportunity
         [--c-kms 1.482] [--t-start 00:19:00] [--t-end 00:52:00] [--glide-end 00:42:29] [--impacts sample.npz]
"""
import argparse, sqlite3, textwrap, json
from datetime import datetime, timezone
import numpy as np, pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch

BUILD_UTC = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
T0 = pd.Timestamp("2014-03-08T00:00:00Z")
# instrument -> recording mode on 8 Mar 2014 and source
MODE = {
    "H01W": ("continuous", "IMS 250 Hz; 8 Mar 2014 data used by Kadri 2024, Royer 2016, CMST 2014"),
    "H08S": ("continuous", "IMS 250 Hz; 8 Mar 2014 data used by Kadri 2024, Kadri 2019, CMST 2014"),
    "H08N": ("continuous (assumed)", "IMS 250 Hz, FDSN epoch 2002-; no published use of 8 Mar 2014 data found"),
    "IMOS3315": ("windows", "segment table"), "IMOS3376": ("windows", "segment table"),
    "IMOS3250": ("windows", "segment table"), "IMOS3274": ("windows", "segment table"),
    "IMOS3275": ("windows", "segment table"),
    **{s: ("continuous", "Royer 2016: sampled continuously at 240 Hz; recorded 8 Mar 2014")
       for s in ["SWAMS1", "SWAMS2", "SWAMS3", "SSEIR", "MAD", "NCRO", "WKER"]},
    "NEAMS": ("no data", "Royer 2016: lost during recovery"),
}
RANK = {"blocked": 0, "large attenuation": 1, "ridge (partial)": 2, "clear": 3}
# plotted state codes
S_RED, S_ATT, S_RIDGE, S_CLEAR, S_INT_ATT, S_INT_CLEAR = 0, 1, 2, 3, 4, 5
COLS = ["#b2182b", "#f4a582", "#d9d9d9", "#4393c3", "#d8c3e3", "#7b3294"]
CMAP = ListedColormap(COLS); NORM = BoundaryNorm(np.arange(-0.5, 6.5), 6)
LAT_PANELS = [-25.0, -30.0, -35.0, -40.0]


def hms(s):
    s = int(round(s)); return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def parse_hms(x):
    h, m_, s = (int(v) for v in x.split(":")); return h * 3600 + m_ * 60 + s


def union(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1] + 0.01: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out


def covered(u, a, b):
    return sum(max(0.0, min(y, b) - max(x, a)) for x, y in u)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--c-kms", type=float, default=1.482, help="registry constant c_sofar (1.482 +/- 0.006 km/s)")
    ap.add_argument("--c-sd", type=float, default=0.006)
    ap.add_argument("--t-start", default="00:19:00"); ap.add_argument("--t-end", default="00:52:00")
    ap.add_argument("--glide-end", default="00:42:29", help="longest Boeing-simulator glide: 23 min after 00:19:29")
    ap.add_argument("--impacts", default=None, help="run J sample.npz, for the impact-time quantiles in the note")
    a = ap.parse_args()
    ts, te, tg = parse_hms(a.t_start), parse_hms(a.t_end), parse_hms(a.glide_end)
    con = sqlite3.connect(a.db)
    AP = pd.read_sql("SELECT site_id, round(arc_lat,3) arc_lat, arc_lon, dist_km, class FROM arc_path", con)
    loc_of = dict(con.execute("SELECT entity_id, value_text FROM attribute WHERE key='station_location'").fetchall())
    held_of = dict(con.execute("SELECT entity_id, value_text FROM attribute WHERE key='data_held'").fetchall())
    assert set(AP.site_id) == set(MODE), set(AP.site_id) ^ set(MODE)
    seg = pd.read_sql("""SELECT d.site_id, s.t_start_utc, s.t_end_utc FROM segment s JOIN dataset d USING(dataset_id)
                         WHERE d.site_id LIKE 'IMOS%' AND d.data_form = 'raw_waveform'""", con)
    for c in ["t_start_utc", "t_end_utc"]:
        seg[c] = (pd.to_datetime(seg[c], utc=True, format="ISO8601") - T0).dt.total_seconds()
    seg = seg[(seg.t_end_utc > -3600) & (seg.t_start_utc < 6 * 3600)]
    WIN = {s: union(list(zip(g.t_start_utc, g.t_end_utc))) for s, g in seg.groupby("site_id")}
    for s in [k for k, v in MODE.items() if v[0] == "windows"]:
        w = WIN[s]; st = np.array([x for x, _ in w])
        assert len(w) >= 20 and np.diff(st).max() < 960, (s, len(w), np.diff(st).max())   # no missing record in 00:00-05:00
    WIN_ROWS = [(s, i, hms(x), hms(y), round(y - x, 3)) for s, w in WIN.items() for i, (x, y) in enumerate(w)]

    def recording(site, t):            # t: array of UTC seconds after 00:00 8 Mar
        mode = MODE[site][0]
        if mode.startswith("continuous"): return np.ones_like(t, dtype=bool)
        if mode == "no data": return np.zeros_like(t, dtype=bool)
        r = np.zeros_like(t, dtype=bool)
        for x, y in WIN[site]: r |= (t >= x) & (t < y)
        return r

    LOCS = list(dict.fromkeys(loc_of[s] for s in MODE))
    inst = {L: [s for s in MODE if loc_of[s] == L] for L in LOCS}
    lats = np.sort(AP.arc_lat.unique())[::-1]

    # ---------------- chart 1 table: by latitude over the reception window
    rows = []
    for lat in lats:
        g = AP[AP.arc_lat == lat].set_index("site_id")
        for L in LOCS:
            best_cont, best_int, frac = -1, -1, 0.0
            uni = []
            for s in inst[L]:
                cls = RANK[g.loc[s, "class"]]; tt = g.loc[s, "dist_km"] / a.c_kms
                mode = MODE[s][0]
                if cls == 0 or mode == "no data": continue
                if mode.startswith("continuous"): best_cont = max(best_cont, cls)
                else:
                    best_int = max(best_int, cls)
                    uni += [[x - tt, y - tt] for x, y in WIN[s]]      # windows mapped back to impact time
            if uni: frac = covered(union(uni), ts, te) / (te - ts)
            if best_cont >= 0: state = best_cont
            elif best_int >= 0 and frac > 0: state = S_INT_CLEAR if best_int == 3 else S_INT_ATT
            else: state = S_RED
            rows.append({"arc_lat": lat, "location": L, "state": state,
                         "best_class_recording": {-1: "none", 0: "blocked", 1: "large attenuation", 2: "ridge (partial)", 3: "clear"}[max(best_cont, best_int)],
                         "continuous": best_cont >= 0, "share_of_window_recorded": round(1.0 if best_cont >= 0 else frac, 3)})
    B = pd.DataFrame(rows)
    B["arc_lon"] = B.arc_lat.map(AP.groupby("arc_lat").arc_lon.first())
    B.to_csv(a.out + "_by_latitude.csv", index=False)
    cnt = B.groupby("arc_lat").apply(lambda g: pd.Series({
        "n_clear_continuous": int((g.state == S_CLEAR).sum()),
        "n_clear_any": int(g.state.isin([S_CLEAR, S_INT_CLEAR]).sum()),
        "n_clear_or_ridge_any": int(g.state.isin([S_CLEAR, S_RIDGE, S_INT_CLEAR]).sum()),
        "n_red": int((g.state == S_RED).sum())}), include_groups=False).reset_index().sort_values("arc_lat", ascending=False)
    cnt.to_csv(a.out + "_by_latitude_counts.csv", index=False)

    # ---------------- chart 2 table: by impact time at four latitudes
    tgrid = np.arange(ts, te + 1, 1.0)
    P = {}; trows = []
    for lat in LAT_PANELS:
        g = AP[AP.arc_lat == lat].set_index("site_id"); assert len(g) == len(MODE), lat
        M = np.full((len(LOCS), tgrid.size), S_RED, dtype=int); notes = []
        for i, L in enumerate(LOCS):
            tts = []
            for s in inst[L]:
                cls = RANK[g.loc[s, "class"]]; tt = g.loc[s, "dist_km"] / a.c_kms; tts.append(tt)
                if cls == 0: continue
                rec = recording(s, tgrid + tt)
                M[i] = np.where(rec & (cls > M[i]), cls, M[i])
            classes = [g.loc[s, "class"] for s in inst[L]]; modes = [MODE[s][0] for s in inst[L]]
            reason = ("data lost" if all(m_ == "no data" for m_ in modes) else
                      "blocked" if all(c == "blocked" for c in classes) else f"{min(tts) / 60:.1f} min")
            notes.append(reason)
            trows.append({"arc_lat": lat, "arc_lon": round(g.arc_lon.iloc[0], 3), "location": L,
                          "travel_min": round(min(tts) / 60, 2), "travel_sd_s": round(min(tts) * a.c_sd / a.c_kms, 1),
                          "reception_first_utc": hms(ts + min(tts)), "reception_last_utc": hms(te + max(tts)),
                          "share_of_impact_times_with_opportunity": round(float((M[i] != S_RED).mean()), 3),
                          "share_clear_and_recording": round(float((M[i] == S_CLEAR).mean()), 3),
                          "row_note": reason})
        P[lat] = (M, notes)
    TT = pd.DataFrame(trows); TT.to_csv(a.out + "_by_impact_time.csv", index=False)
    pd.DataFrame(WIN_ROWS, columns=["site_id", "seq", "start_utc", "end_utc", "duration_s"]).to_csv(a.out + "_imos_windows.csv", index=False)

    q_note = ""
    if a.impacts:
        z = np.load(a.impacts); mm = (z["t_unix"] - 1394236800) / 60.0; la = z["lat"]; qs = {}
        for lat in LAT_PANELS:
            k = (np.abs(la - lat) < 0.5) & (mm >= ts / 60)
            for wk in ["w_D0", "w_D2"]:
                ww = z[wk][k]; o = np.argsort(mm[k]); cw = np.cumsum(ww[o]) / ww.sum()
                qs[(lat, wk)] = float(mm[k][o][np.searchsorted(cw, 0.999)])
        json.dump({f"{abs(l):.0f}S_{w}": hms(v * 60) for (l, w), v in qs.items()}, open(a.out + "_impact_q999.json", "w"), indent=1)
        q_note = ("Run J impacts after 00:19 within 0.5° of each panel latitude, 99.9 % weighted quantile: "
                  + "; ".join(f"{abs(l):.0f}° S {hms(qs[(l, 'w_D2')] * 60)} (00:19 range and frequency used), {hms(qs[(l, 'w_D0')] * 60)} (00:19 data not used)"
                              for l in LAT_PANELS) + ". ")
    con.close()

    # ---------------- shared labels
    def label(L):
        ss = inst[L]; held = held_of[ss[0]]; mode = MODE[ss[0]][0]
        rec = {"continuous": "continuous", "continuous (assumed)": "continuous, assumed", "windows": "307 s every 15 min" + (", 2 loggers" if len(ss) > 1 else ""),
               "no data": "data lost on recovery"}[mode]
        return f"{L}  [{rec}; {({'raw': 'raw data held', 'digitised': 'digitised only', 'none': 'no data held'})[held]}]"
    ylabels = [label(L) for L in LOCS]
    net_of = lambda L: L.split('(')[-1].split()[0]
    mpl.rcParams.update({"font.size": 8, "axes.labelsize": 9, "axes.titlesize": 9, "xtick.labelsize": 7, "ytick.labelsize": 7,
                         "axes.spines.top": False, "axes.spines.right": False, "xtick.direction": "out", "ytick.direction": "out"})
    legend_handles = [Patch(color=COLS[S_CLEAR], label="clear, recording"), Patch(color=COLS[S_RIDGE], label="ridge above hydrophone depth (partial loss), recording"),
                      Patch(color=COLS[S_ATT], label="large attenuation, recording"), Patch(color=COLS[S_RED], label="blocked, or not recording")]
    c_txt = f"{a.c_kms:.3f} ± {a.c_sd:.3f} km/s"
    common_tech = ("Line of sight: hydro_data.sqlite table arc_path (arc_line_of_sight.py; WGS84 geodesics on GEBCO 2026, 15 arc-s). Blocked: land or water shallower than "
                   "min(receiver depth, 200 m) more than 20 km from the receiver. Large attenuation: >= 10 km shallower than 1,000 m more than 100 km from the receiver. "
                   "Ridge: >= 10 km shallower than the hydrophone (deep receivers). These thresholds are agent choices, not ruled. Recording: IMOS record windows from table "
                   "segment (UTC, clock-corrected, event-day and background sets joined; no record missing 00:00-05:00 UTC); OHASISBIO continuous at 240 Hz (Royer 2016), "
                   "NEAMS lost during recovery; IMS H01W/H08S continuous 250 Hz (8 Mar 2014 data used in Kadri 2024, CMST 2014); H08N continuous assumed (no published use "
                   "of its 8 Mar 2014 data found). A location takes its most favourable instrument that is recording. Travel time = geodesic distance / c, "
                   f"c = {c_txt} (registry constant c_sofar); 1-sigma timing error 4-16 s. Not included: HA04 Crozet (installed Dec 2016), IMOS deployments with no 8 Mar 2014 files, "
                   "island seismometers. Geometric screen, not transmission loss; noise (for example the seismic survey shots Royer reports) is not included.")

    def check_overlaps(fig, name):
        fig.canvas.draw(); rr = fig.canvas.get_renderer()
        texts = [t for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
        bbs = [(t.get_text()[:30], t.get_window_extent(rr)) for t in texts]
        ov = [(p, q_) for i, (p, b) in enumerate(bbs) for q_, c in bbs[i + 1:] if b.overlaps(c)]
        print(name, "text overlaps:", ov[:10])
        return ov

    # ---------------- chart 1
    fig = plt.figure(figsize=(12, 9.6), dpi=200)
    ax1 = fig.add_axes([0.27, 0.655, 0.68, 0.235]); ax2 = fig.add_axes([0.27, 0.25, 0.68, 0.36], sharex=ax1)
    x = -cnt.arc_lat
    ax1.step(x, cnt.n_clear_or_ridge_any, where="mid", color="#7f7f7f", lw=1.0, label="clear or ridge (partial loss), recording all or part of the time")
    ax1.step(x, cnt.n_clear_any, where="mid", color=COLS[S_INT_CLEAR], lw=1.2, ls="--", label="clear, recording all or part of the time")
    ax1.step(x, cnt.n_clear_continuous, where="mid", color="#1b6ca8", lw=1.6, label="clear, recording all the time")
    whole = cnt[np.isclose(cnt.arc_lat, cnt.arc_lat.round()) | (cnt.arc_lat == cnt.arc_lat.min())]
    ax1.plot(-whole.arc_lat, whole.n_clear_continuous, "o", ms=3.2, color="#1b6ca8", zorder=5)
    nL = len(LOCS)
    for _, r in whole.iterrows():
        ax1.text(-r.arc_lat, nL + 0.9, f"{int(r.n_clear_continuous)}", ha="center", va="bottom", fontsize=6.5, color="#1b6ca8")
    ax1.text(19.75, nL + 0.9, "clear, recording all the time, at each whole degree:", ha="right", va="bottom", fontsize=6.5, color="#1b6ca8")
    ax1.set_ylim(0, nL + 0.5); ax1.set_yticks(range(0, nL + 1, 2))
    ax1.set_ylabel(f"Station locations\n(of {nL} deployed)")
    ax1.legend(loc="lower left", frameon=False, fontsize=7)
    plt.setp(ax1.get_xticklabels(), visible=False)
    Mx = B.pivot(index="location", columns="arc_lat", values="state").reindex(LOCS); Mx = Mx[sorted(Mx.columns, reverse=True)]
    tip = lats.min()
    ax2.imshow(Mx.values, aspect="auto", cmap=CMAP, norm=NORM, interpolation="nearest",
               extent=[-Mx.columns.max() - 0.05, -Mx.columns.min() + 0.05, nL - 0.5, -0.5])
    ax2.set_yticks(range(nL)); ax2.set_yticklabels(ylabels, fontsize=6.8)
    ax2.set_xticks(range(20, 45, 2)); ax2.set_xticklabels([f"{t}° S" for t in range(20, 45, 2)]); ax2.set_xlim(19.8, -tip + 0.15)
    ax2.set_xlabel("7th-arc latitude (arc points every 0.1°; southern end of the arc at 43.9° S)")
    for yy in [2.5, 5.5]: ax2.axhline(yy, color="white", lw=1.5)
    # share recorded, per intermittent location
    for i, L in enumerate(LOCS):
        g = B[(B.location == L) & B.state.isin([S_INT_CLEAR, S_INT_ATT])]
        if len(g):
            lo, hi = g.share_of_window_recorded.min(), g.share_of_window_recorded.max()
            ax2.text(-tip + 0.3, i, f"{lo * 100:.0f}–{hi * 100:.0f} %" if round(lo, 2) != round(hi, 2) else f"{lo * 100:.0f} %",
                     va="center", ha="left", fontsize=6.5, color=COLS[S_INT_CLEAR], clip_on=False)
    ax2.text(-tip + 0.3, -0.85, "time\nrecorded", va="bottom", ha="left", fontsize=6.2, color=COLS[S_INT_CLEAR], clip_on=False)
    ax2.legend(handles=legend_handles[:3] + [Patch(color=COLS[S_INT_CLEAR], label="clear, recording part of the time"),
                                             Patch(color=COLS[S_INT_ATT], label="large attenuation, recording part of the time"), legend_handles[3]],
               loc="upper left", bbox_to_anchor=(-0.36, -0.12), ncol=3, frameon=False, fontsize=7)
    S_ = cnt[cnt.arc_lat <= -33]; N_ = cnt[cnt.arc_lat > -33]
    xtra = (cnt.n_clear_any - cnt.n_clear_continuous); words = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four"}
    xtra_txt = words[xtra.min()] if xtra.min() == xtra.max() else f"{words[xtra.min()]} to {words[xtra.max()]}"
    print("extra intermittent clear locations:", xtra.min(), xtra.max())
    title1 = (f"Observation opportunity for a sound from the 7th arc on 8 March 2014: line of sight and recording together.\n"
              f"Recording all the time with clear line of sight: {S_.n_clear_continuous.min()}–{S_.n_clear_continuous.max()} station locations south of 33° S, "
              f"{N_.n_clear_continuous.min()}–{N_.n_clear_continuous.max()} north of 33° S; {xtra_txt} more record part of the time")
    fig.text(0.02, 0.985, title1, fontsize=9.5, weight="bold", va="top", ha="left")
    fn1 = ("Plain-language note.  For each point on the 7th arc we follow the sea floor to each station, and we look at what the station recorded when the sound "
           f"would arrive (impact from {a.t_start} to {a.t_end} UTC, plus the travel time). Red: the path is blocked, or the station did not record (NEAMS was "
           "recording, but its data was lost when it was recovered). Purple: the Australian seabed loggers record 307 s in each 15 min, so they record only part "
           "of the time; the number at the right is the part of the time recorded. This shows where a sound can be received; it does not show that the sound "
           "was loud enough to detect. That is the next step.")
    fn2 = ("Technical note.  " + common_tech + f" Reception window per arc point: impact {a.t_start}-{a.t_end} UTC + d/c; 'time recorded' = share of that window "
           "covered by the union of the location's unblocked loggers.")
    fig.text(0.02, 0.125, textwrap.fill(fn1, 210), fontsize=6.4, va="top", linespacing=1.35)
    fig.text(0.02, 0.072, textwrap.fill(fn2, 210), fontsize=6.4, va="top", linespacing=1.35)
    ov1 = check_overlaps(fig, "chart1")
    fig.savefig(a.out + "_by_latitude.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    fig.savefig(a.out + "_by_latitude.pdf", bbox_inches="tight", pad_inches=0.15); plt.close(fig)

    # ---------------- chart 2 (rows with no opportunity at any impact time are left out, per panel)
    tminutes = tgrid / 60.0
    keep = {lat: [i for i in range(nL) if (P[lat][0][i] != S_RED).any()] for lat in LAT_PANELS}
    dropped = {lat: [(LOCS[i], P[lat][1][i]) for i in range(nL) if i not in keep[lat]] for lat in LAT_PANELS}
    row_h = 0.0118; cnt_h = 0.04; gap = 0.062; top = 0.935
    fig = plt.figure(figsize=(12, 16.5), dpi=200)
    y = top
    for k, lat in enumerate(LAT_PANELS):
        M, notes = P[lat]; kk = keep[lat]; Mk = M[kk]; n = len(kk)
        sh = n * row_h
        axc = fig.add_axes([0.27, y - cnt_h, 0.62, cnt_h]); axs = fig.add_axes([0.27, y - cnt_h - 0.006 - sh, 0.62, sh], sharex=axc)
        ncl = (Mk == S_CLEAR).sum(0); nany = (Mk != S_RED).sum(0)
        axc.step(tminutes, nany, where="post", color="#7f7f7f", lw=0.9, label="any opportunity (clear, ridge or large attenuation)")
        axc.step(tminutes, ncl, where="post", color="#1b6ca8", lw=1.4, label="clear, recording")
        axc.set_ylim(0, n + 0.5); axc.set_yticks(range(0, n + 1, 3)); axc.tick_params(labelsize=6.5)
        axc.set_ylabel("locations", fontsize=7)
        plt.setp(axc.get_xticklabels(), visible=False)
        lon = TT[TT.arc_lat == lat].arc_lon.iloc[0]
        axc.set_title(f"Impact on the 7th arc at {abs(lat):.0f}° S, {lon:.2f}° E:  clear and recording {ncl.min()}–{ncl.max()} station locations "
                      f"(median {np.median(ncl):.0f}); any opportunity {nany.min()}–{nany.max()}", fontsize=8.5, loc="left", weight="bold", pad=14)
        axc.text(0.0, 1.04, "Not shown, no opportunity at any impact time: " + "; ".join(f"{l} ({r})" for l, r in dropped[lat]),
                 transform=axc.transAxes, fontsize=6.5, va="bottom", ha="left", color="#b2182b")
        if k == 0: cnt_handles = axc.get_legend_handles_labels()
        axs.imshow(Mk, aspect="auto", cmap=CMAP, norm=NORM, interpolation="nearest",
                   extent=[tminutes[0], tminutes[-1] + 1 / 60, n - 0.5, -0.5])
        axs.set_yticks(range(n)); axs.set_yticklabels([ylabels[i] for i in kk], fontsize=6.3)
        for yy in range(n - 1):
            if net_of(LOCS[kk[yy]]) != net_of(LOCS[kk[yy + 1]]): axs.axhline(yy + 0.5, color="white", lw=1.2)
        for ax_ in (axc, axs): ax_.axvline(tg / 60, color="k", lw=0.8, ls=":")
        axc.text(tg / 60, 0.4, " longest simulator glide", fontsize=6, va="bottom", ha="left")
        for j, i in enumerate(kk):
            axs.text(tminutes[-1] + 0.35, j, notes[i], va="center", ha="left", fontsize=6.2, color="#333333", clip_on=False)
        axs.text(tminutes[-1] + 0.35, -0.75, "travel time", va="bottom", ha="left", fontsize=6.2, clip_on=False)
        xt = np.arange(np.ceil(ts / 60), te / 60 + 0.01, 3)
        axs.set_xticks(xt); axs.set_xticklabels([hms(v * 60)[:5] for v in xt])
        axs.set_xlim(tminutes[0], tminutes[-1] + 1 / 60)
        if k == 3: axs.set_xlabel("Impact time on the 7th arc, UTC, 8 March 2014 (each station is coloured at the time the sound would arrive there)")
        y = y - cnt_h - 0.006 - sh - gap
    ybot = y + gap
    fig.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(0.27, ybot - 0.03), ncol=4, frameon=False, fontsize=7)
    fig.legend(handles=cnt_handles[0], labels=["count strip: " + l for l in cnt_handles[1]], loc="upper left",
               bbox_to_anchor=(0.27, ybot - 0.044), ncol=2, frameon=False, fontsize=7)
    fig.text(0.02, 0.985, "Recording opportunity by impact time: which stations had line of sight and were recording when the sound would arrive,\n"
             "for an impact on the 7th arc at 25° S, 30° S, 35° S and 40° S", fontsize=10, weight="bold", va="top", ha="left")
    fn1 = ("Plain-language note.  Read across from an impact time. For each station, the colour shows the state at the time the sound would arrive there "
           "(impact time plus travel time; the travel time is at the right). Red: the path is blocked, or the station was not recording at that time. "
           "Stations that have no opportunity at any impact time are not shown; they are named in red under each panel title. The Australian seabed "
           "loggers record 307 s in each 15 min, so their rows have gaps; Perth Canyon and Portland have two loggers that start 5 min apart. This shows where "
           "a sound can be received; it does not show that it was loud enough to detect. That is the next step.")
    fn2 = ("Technical note.  " + common_tech + f" Impact time axis {a.t_start}-{a.t_end} UTC at 1 s steps (agent choice: covers the run J 99.9 % impact-time quantile "
           f"after 00:19 at all four latitudes for the 00:19 range-and-frequency option); dotted line {a.glide_end} = longest Boeing-simulator glide (23 min after "
           "00:19:29). " + q_note + "Later impacts are not shown. Arrival treated as an instant; a sound that lasts some tens of seconds can still be partly recorded when it starts just "
           "before a record window.")
    yb = ybot - 0.068
    fig.text(0.02, yb, textwrap.fill(fn1, 210), fontsize=6.4, va="top", linespacing=1.35)
    fig.text(0.02, yb - 0.036, textwrap.fill(fn2, 210), fontsize=6.4, va="top", linespacing=1.35)
    ov2 = check_overlaps(fig, "chart2")
    fig.savefig(a.out + "_by_impact_time.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    fig.savefig(a.out + "_by_impact_time.pdf", bbox_inches="tight", pad_inches=0.15); plt.close(fig)

    # ---------------- chart 3: count of locations clear and recording, one line per impact latitude
    C = pd.DataFrame({"impact_utc": [hms(v) for v in tgrid]})
    varying = {}
    for lat in LAT_PANELS:
        M = P[lat][0]; C[f"n_clear_recording_{abs(lat):.0f}S"] = (M == S_CLEAR).sum(0)
        varying[lat] = [LOCS[i] for i in range(nL) if 0 < (M[i] == S_CLEAR).mean() < 1]
        varying[lat] = (varying[lat], [LOCS[i] for i in range(nL) if (M[i] == S_CLEAR).all()])
    C.to_csv(a.out + "_clear_count_by_impact_time.csv", index=False)
    lat_cols = {-25.0: "#1b9e77", -30.0: "#d95f02", -35.0: "#7570b3", -40.0: "#e7298a"}
    offs = {-25.0: 0.09, -30.0: 0.03, -35.0: -0.03, -40.0: -0.09}
    fig, ax = plt.subplots(figsize=(11, 6.4), dpi=200)
    fig.subplots_adjust(left=0.08, right=0.86, top=0.85, bottom=0.42)
    allv = np.concatenate([C[f"n_clear_recording_{abs(l):.0f}S"].values for l in LAT_PANELS])
    ends = []
    for lat in LAT_PANELS:
        v = C[f"n_clear_recording_{abs(lat):.0f}S"].values
        ax.step(tminutes, v + offs[lat], where="post", color=lat_cols[lat], lw=1.6)
        ends.append([v[-1] + offs[lat], lat, v])
    ends.sort(key=lambda e: -e[0])
    for j in range(1, len(ends)):                      # spread end labels at least 0.55 apart
        ends[j][0] = min(ends[j][0], ends[j - 1][0] - 0.55)
    for yv, lat, v in ends:
        ax.text(tminutes[-1] + 0.4, yv, f"{abs(lat):.0f}° S  ({v.min()}–{v.max()})", color=lat_cols[lat],
                fontsize=8, va="center", ha="left", clip_on=False)
    ax.axvline(tg / 60, color="k", lw=0.8, ls=":"); ax.text(tg / 60, 0.3, " longest simulator glide", fontsize=7, va="bottom")
    ax.set_ylim(0, nL); ax.set_yticks(range(0, nL + 1, 2))
    ax.set_xlim(tminutes[0], tminutes[-1] + 1 / 60)
    ax.set_xticks(xt); ax.set_xticklabels([hms(v * 60)[:5] for v in xt])
    ax.set_xlabel("Impact time on the 7th arc, UTC, 8 March 2014")
    ax.set_ylabel(f"Station locations clear and recording\n(of {nL} deployed)")
    ax.text(tminutes[-1] + 0.4, nL - 0.3, "impact latitude\n(range of count)", fontsize=7.5, va="top", ha="left", clip_on=False)
    ax.grid(axis="y", color="#e5e5e5", lw=0.6); ax.set_axisbelow(True)
    fig.text(0.02, 0.975, f"For an impact on the 7th arc at 25° S, 30° S, 35° S or 40° S between {a.t_start[:5]} and {a.t_end[:5]} UTC, "
             f"{allv.min()} to {allv.max()} station locations had clear line of sight\nand were recording when the sound would arrive",
             fontsize=10, weight="bold", va="top", ha="left")
    vary_txt = " ".join(f"{abs(l):.0f}° S: counted throughout {', '.join(s.split(' (')[0] for s in varying[l][1])}; part of the time "
                        f"{', '.join(s.split(' (')[0] for s in varying[l][0]) or 'none'}." for l in LAT_PANELS)
    fn1 = ("Plain-language note.  Each line counts the stations that have a clear path from the impact point and were recording at the time the sound "
           "would arrive there. Stations at one place are counted once. The steps come from the Australian seabed loggers, which record 307 s in each 15 min. "
           "Lines are moved up or down by less than 0.1 so that equal counts stay visible; read the count from the nearest whole number. " + vary_txt +
           " This does not show that the sound was loud enough to detect; that is the next step.")
    fn2 = ("Technical note.  Count of locations in state 'clear, recording' in the impact-time chart (arc_recording_opportunity.py; series in "
           "arc_recording_opportunity_clear_count_by_impact_time.csv). Ridge (partial loss) and large-attenuation paths are not counted. " + common_tech +
           f" Impact time axis {a.t_start}-{a.t_end} UTC at 1 s steps (agent choice, run J 99.9 % impact-time quantile after 00:19); dotted line {a.glide_end} = "
           "longest Boeing-simulator glide. Arrival treated as an instant.")
    fig.text(0.02, 0.31, textwrap.fill(fn1, 190) + "\n\n" + textwrap.fill(fn2, 190), fontsize=6.4, va="top", linespacing=1.35)
    check_overlaps(fig, "chart3")
    fig.savefig(a.out + "_clear_count_by_impact_time.png", dpi=200, bbox_inches="tight", pad_inches=0.15)
    fig.savefig(a.out + "_clear_count_by_impact_time.pdf", bbox_inches="tight", pad_inches=0.15); plt.close(fig)
    for l in LAT_PANELS: print(abs(l), "dropped:", dropped[l], "| varying:", varying[l][0])
    print("TITLE1:", title1.replace("\n", " "))
    print(cnt[np.isclose(cnt.arc_lat, cnt.arc_lat.round())].to_string(index=False))
    print(TT.to_string(index=False))


if __name__ == "__main__":
    main()
