
print("ranked exists:", os.path.exists(RANK))
d_ = dist_km(-57.3,88.965,"H08S")[0]; print("event A at H08S", round(d_), hms(hms2u("00:16:29.4")+d_/C))
MARK_ST = {"H01W":["H01W-2"],"SWAMS":["SWAMS-2","SWAMS-3"],"SSEIR":["SSEIR"],"MAD":["MAD"],"WKER":["WKER"],"NCRO":["NCRO"]}
_row_data0 = row_data
def row_data(rx, kind, w0, w1, pad=120.0):
    d = _row_data0(rx, kind, w0, w1, pad)
    d["marks"] = []
    if rx in MARK_ST and kind in ("royer","kadri"):
        mm = mk[mk.station.isin(MARK_ST[rx])]
        d["marks"] = [(T0+float(r.t_utc_s), r.kind, r.nearest_table5_label if isinstance(r.nearest_table5_label,str) else f"event {r.nearest_table5_index}", r.mark_minus_table5_s)
                      for _, r in mm.iterrows() if d["s0"] <= T0+float(r.t_utc_s) <= d["s1"]]
    return d
_verdict0 = verdict
def verdict(c, d):
    k, s = _verdict0(c, d)
    inm = [m for m in d.get("marks", []) if d["w0"]-10 <= m[0] <= d["w1"]+10]
    if inm:
        labs = sorted({m[2] for m in inm}); s += f"; Royer marks an arrival here (Royer event {', '.join(labs)})"
        if k == "nm_nothing": k = "pick"
    return k, s
plot_code = open("track_plot.py").read()
plot_code = plot_code.replace('''def pick_marks(ax, d):
    for t, s, l, e in d["picks"]:''', '''def pick_marks(ax, d):
    for t, kd, l, off in d.get("marks", []):
        ax.plot([t - T0], [0.0], marker="^", color=COL_PICK, ms=4.5, mfc="white", transform=ax.get_xaxis_transform(), clip_on=False, zorder=6)
    for t, s, l, e in d["picks"]:''')
plot_code = plot_code.replace('if d["picks"]:\n                for ax in (axs[0], axs[3]): pick_marks(ax, d)', 'if d["picks"] or d.get("marks"):\n                for ax in (axs[0], axs[3]): pick_marks(ax, d)')
plot_code = plot_code.replace('"Grey dashed lines: matched-filter thresholds for p = 0.3, 0.1, 0.05 (light to dark). Teal: Royer\'s picked arrivals."',
   '"Grey dashed lines: matched-filter thresholds for p = 0.3, 0.1, 0.05 (light to dark). Teal: Royer\'s picked arrivals (filled triangle and dotted line: his Table 5; open triangle: the arrival marks on his figures)."')
plot_code = plot_code.replace('fig.text(0.01, 1 - 0.58 / H, subtitle,', 'fig.text(0.01, 1 - 0.58 / H, "\\n".join(textwrap.fill(s_, 250) for s_ in subtitle.split("\\n")),')
open("track_plot.py","w").write(plot_code); exec(plot_code)
def texts_for2(c, rows):
    a,b,f1,f2 = _tf(c, rows); return a, b, wrap(f1.replace("\n"," "), 330), wrap(f2.replace("\n"," "), 360)
ALLROWS = {}
for k_, c in enumerate(cands, 1):
    c["slug"] = f"cand{k_:02d}_" + ("pair" if c["kind"]=="pair" else "single") + c["name"].split(":")[0].split()[-1].replace("(strongest)","").strip()
    rows_ = [row_data(rx, kind, c["win"][rx][0], c["win"][rx][2]) for rx, kind in ROWS]; ALLROWS[c["slug"]] = rows_
    draw_candidate(c, rows_, f"{OUT}/{c['slug']}", *texts_for2(c, rows_))
    print(c["slug"], [verdict(c,d)[0] for d in rows_])
