"""Chart 4: our companion to Kadri's SnT 2025 poster - his six boxes on the digitised Fig. 9 Cape Leeuwin panels with our
detector statistics and p-values (tonight's panel search). The poster itself is Kadri's and is not reproduced."""
exec(open(str(WS_ROOT) + "/gfx/common.py").read())
TRD = WS / "hydro/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/figure9-vector-traces"
PS = np.load(SR / "panels/panel_series.npz")
PB = pd.read_csv(SR / "named/poster_boxes.csv")
BOXLAB = {"poster (a) box 1": "a1", "poster (a) box 2": "a2", "poster (a) box 3": "a3", "poster (a) box 4": "a4",
          "text time 00:52:03": "c1", "caption time 00:54:30": "c2"}
PANEL0 = {"a": "00:27:00", "b": "00:37:00", "c": "00:47:00"}
BCOL = "#e08a00"


def chart4(fname):
    fig = plt.figure(figsize=(14.5, 9.4))
    plain = ("This chart is our check of the six boxes that Kadri drew on his 2025 poster. The grey lines are the Cape Leeuwin pressure traces "
             "of his 2024 paper, read from the published figure. The orange boxes are his boxes. Under each trace is the output of our "
             "envelope matched filter. The table gives, for each box, the lowest p-value that each of our four detectors found in the box, "
             "and the part of the predicted arrival that falls in the box. A small p-value means that the noise alone seldom gives so strong "
             "a value. Only box c1 (Kadri's text time) reaches p below 0.05, and one value of 0.043 among many tests is expected by chance. "
             "The boxes in panel a are too early for an impact on the arc after 00:19:29.")
    tech = ("Traces: Kadri (2024) Fig. 9 panels a–c (H01W), vector-digitised (~19 samples/s, 8,706–8,721 vertices per 600 s), 'figure9-vector-traces'. "
            "Boxes: SnT 2025 poster P1.4-254 panels (a) and (c), positions read from the poster image (named/poster_boxes.csv). Detectors (block-5 panel search, "
            "pre-registered, searches_run_j): M1b = envelope matched filter against the KRAKEN dispersed template; D1 = STA/LTA; BE = band energy 2–5 and 5–9 Hz "
            "(the plot band is 1–9 Hz; 10–40 Hz is not recoverable from the figure). p = per-window p_A against an IMOS 3376 plot emulation (6,720 null windows); "
            "box p = minimum over the 55 s windows overlapping the box (panels/box_minima.csv). No multiplicity correction: 30 H01W windows x 4 detectors = 120 tests were "
            "scored; 6 report-level (p <= 0.05) rows are expected by chance and 1 was found (searches note, Table 2). Arrival share = run J D0′ (p 0.5) mass of the predicted H01W "
            "deep-channel arrival inside the box. Timing: the panel (a) boxes end 0–7.2 min before the earliest arc arrival, so their source is before 00:19:29 or "
            "off the arc (prior 0 under the 00:19 log-on). Kadri times: text time 00:52:03 (p. 9), caption time 00:54:30 (Table 1). DIGITISED DATA: amplitude "
            "+/- chart reading. " + CAV)
    b = need_bottom(fig, plain, tech)
    top = 0.93; H = top - b - 0.06; rowh = H / 3
    left, wdt = 0.05, 0.56
    for k, pn in enumerate(["a", "b", "c"]):
        y0 = top - (k + 1) * rowh + 0.035
        ax = fig.add_axes([left, y0 + 0.36 * (rowh - 0.05), wdt, 0.6 * (rowh - 0.05)])
        axs = fig.add_axes([left, y0, wdt, 0.33 * (rowh - 0.05)], sharex=ax)
        tr = pd.read_csv(TRD / f"kadri-2024-figure9-panel-{pn}-H01W.csv")
        t0 = unix(PANEL0[pn])
        ax.plot(t0 + tr.plotted_time_s, tr.pressure_pa, color="#6b6b6b", lw=0.35, rasterized=True)
        st = PS[f"{pn}_M1b_s"]; tt = t0 + PS[f"{pn}_M1b_t"]
        axs.plot(tt, st, color="#1f4e9c", lw=0.7)
        for _, r in PB.iterrows():
            a_, b_ = unix(r.start), unix(r.end); lab = BOXLAB[r.box]
            if lab[0] != pn: continue
            for a in (ax, axs): a.axvspan(a_, b_, color=BCOL, alpha=0.22, lw=0)
            ax.add_patch(matplotlib.patches.Rectangle((a_, -1.15), b_ - a_, 2.3, fill=False, ec=BCOL, lw=1.2))
            ax.text(0.5 * (a_ + b_), 1.22, f"{lab}: p = {r.min_p_M1b:.3f}", ha="center", va="bottom", fontsize=6.5, color="#8a5300")
        if pn == "c":
            tpk = unix("00:52:04.35"); axs.plot(tpk, np.interp(tpk, tt, st), "v", color="#111111", ms=5)
            axs.annotate("00:52:04, strongest value in the Cape Leeuwin panels", (tpk, np.interp(tpk, tt, st)), xytext=(8, -2), textcoords="offset points", fontsize=6)
            for tk, ls in ((unix("00:52:03"), "--"), (unix("00:54:30"), ":")): ax.axvline(tk, color="#b4232c", lw=0.8, ls=ls)
        ax.set_ylim(-1.3, 1.55); ax.set_ylabel("Pressure (Pa)"); axs.set_ylabel("Matched-\nfilter output", fontsize=7)
        axs.set_ylim(-0.25, 0.85); ax.set_xlim(t0, t0 + 600)
        plt.setp(ax.get_xticklabels(), visible=False)
        axs.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(60))
        axs.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _=None: hms(x)[:8] if False else f"{tfmt(x)}"))
        ax.set_title(f"{pn}  Cape Leeuwin, from {PANEL0[pn][:5]} UTC (Kadri 2024 Fig. 9{pn}, digitised)" + ("  —  no box drawn by Kadri" if pn == "b" else ""), fontsize=8)
    axs.set_xlabel("Time, UTC, 8 March 2014")
    # table
    axt = fig.add_axes([0.645, b + 0.06, 0.345, H]); axt.axis("off")
    cols = ["box", "span, UTC", "matched\nfilter", "STA/LTA", "band\n2–5 Hz", "band\n5–9 Hz", "arrival\nin box", "timing"]
    order = ["poster (a) box 1", "poster (a) box 2", "poster (a) box 3", "poster (a) box 4", "text time 00:52:03", "caption time 00:54:30"]
    cells = []
    for bx in order:
        r = PB[PB.box == bx].iloc[0]
        tim = "too early¹" if r.verdict_timing.startswith("source before") else ("at the edge²" if r.verdict_timing == "marginal" else "possible")
        cells.append([BOXLAB[bx] + (" (text time)" if bx.startswith("text") else " (caption time)" if bx.startswith("caption") else ""),
                      f"{r.start[:8]}–{r.end[3:8]}", f"{r.min_p_M1b:.3f}", f"{r.min_p_D1:.2f}", f"{r['min_p_BE_2-5']:.2f}", f"{r['min_p_BE_5-9']:.2f}",
                      (pct(r.H01W_arrival_mass_D0, 1) if r.H01W_arrival_mass_D0 >= 1e-3 or r.H01W_arrival_mass_D0 == 0 else pct(r.H01W_arrival_mass_D0, 3)), tim])
    tab = axt.table(cellText=cells, colLabels=cols, loc="upper center", cellLoc="center", colLoc="center",
                    colWidths=[0.2, 0.17, 0.09, 0.09, 0.09, 0.09, 0.1, 0.13])
    tab.auto_set_font_size(False); tab.set_fontsize(6.6); tab.scale(1, 2.3)
    for (i, j), c in tab.get_celld().items():
        c.set_edgecolor("#cccccc"); c.set_linewidth(0.5)
        if i == 0: c.set_facecolor("#f0f0f0"); c.set_text_props(weight="bold")
        if i > 0 and j == 2 and float(cells[i - 1][2]) <= 0.05: c.set_facecolor("#fde3b8")
    axt.set_title("Lowest p-value in each of Kadri's six boxes, per detector", fontsize=8, loc="left")
    axt.text(0.0, 0.52, "¹ ends 2.9–7.2 min before the earliest predicted arrival for an impact on\n   the arc after 00:19:29: the source would be earlier or off the arc.\n"
             "² ends at the earliest predicted arrival (share of arrival < 0.001 %).\n"
             "p-values are per window, without correction for the 120 tests\n(30 windows x 4 detectors) at Cape Leeuwin; 6 values below 0.05\nare expected by chance, 1 was found.\n"
             "Arrival in box: share of the predicted arrival (00:19 data not used)\nthat falls inside the box.", transform=axt.transAxes, fontsize=6.4, va="top")
    from matplotlib.lines import Line2D
    fig.legend([Line2D([], [], color="#6b6b6b", lw=0.8), matplotlib.patches.Patch(fc=BCOL, alpha=0.3, ec=BCOL), Line2D([], [], color="#1f4e9c", lw=0.8),
                Line2D([], [], color="#b4232c", ls="--"), Line2D([], [], color="#b4232c", ls=":")],
               ["pressure trace (digitised)", "Kadri 2025 poster box", "our matched-filter output", "Kadri text time 00:52:03", "Kadri caption time 00:54:30"],
               loc="upper left", bbox_to_anchor=(0.645, b + 0.06 + 0.22 * H), ncol=1, frameon=False, fontsize=6.5)
    fig.text(0.01, 0.985, "Kadri's six poster boxes on the published Cape Leeuwin traces, tested with our detectors", fontsize=10, ha="left", va="top")
    footnotes(fig, plain, tech)
    return save(fig, fname)
