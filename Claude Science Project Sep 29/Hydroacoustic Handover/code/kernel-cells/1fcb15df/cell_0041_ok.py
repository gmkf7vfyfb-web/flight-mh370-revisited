
EVCLASS = {str(r.label) if isinstance(r.label,str) else f"event {r['index']}": r.event_class for _, r in ev.iterrows()}
def verdict(c, d):
    rx = d["rx"]
    if not d["held"]: return "not held", "could not have seen: no recording held"
    inm = sorted({m[2] for m in d.get("marks", []) if d["w0"]-10 <= m[0] <= d["w1"]+10} |
                 {(p[2] if p[2] else "unlabelled") for p in d["picks"] if d["w0"] <= p[0] <= d["w1"]})
    roy = ("; Royer marks an arrival in the window: " + ", ".join(f"{x} ({EVCLASS.get(x,'-')})" for x in inm)) if inm else ""
    if d["kind"] == "royer":
        if inm: return "pick", "Royer arrival in the window: " + ", ".join(f"{x} ({EVCLASS.get(x,'-')})" for x in inm) + "; level not modelled"
        return "nm_nothing", "no Royer arrival in the window; level not modelled"
    pr = d.get("p"); own = rx in c["rx"]
    ps = f"p {pr:.2g}" if pr is not None else "no statistic sample in the window"
    if own and pr is not None and pr <= 0.3: return "present", "candidate present (defining signal)" + roy
    if pr is not None and pr <= 0.05: return "present", f"signal present in the window ({ps})" + roy
    snr = c.get("snr", {}).get(rx, np.nan); pdv = c.get("pd", {}).get(rx, np.nan)
    if rx == "3250" or not np.isfinite(snr): return "nm_nothing", f"no expected level (sound path blocked); nothing ({ps})" + roy
    if pdv >= 0.5: return "should", f"should have seen (detection probability {pdv:.2f}): nothing ({ps})" + roy
    return "could_not", f"could not have seen (detection probability {pdv:.2f}): nothing ({ps})" + roy
plot_code = open("track_plot.py").read()
plot_code = plot_code.replace('top = 1 - 1.15 / H', 'top = 1 - 1.45 / H')
plot_code = plot_code.replace('''axs[2].plot(tm[mm2] - T0, o["m1b"][mm2], color=COL_TR, lw=0.6, label="raw plot")''',
                              '''axs[2].plot(tm[mm2] - T0, o["m1b"][mm2], color=COL_TR, lw=0.6, label="raw plot" if o is d["segs"][0] else None)''')
plot_code = plot_code.replace('''ls=(0,(3,1)), label="airgun shots removed")''', '''ls=(0,(3,1)), label="airgun shots removed" if o is d["segs"][0] else None)''')
open("track_plot.py","w").write(plot_code); exec(plot_code)
import glob as _g
for f in _g.glob(f"{OUT}/*"): os.remove(f)
for k_, c in enumerate(cands, 1):
    nm = c["name"].split(":")[0].lower().replace(" (strongest)", "-strongest").replace(" ", "")
    c["slug"] = f"cand{k_:02d}_{nm}"
    rows_ = [row_data(rx, kind, c["win"][rx][0], c["win"][rx][2]) for rx, kind in ROWS]; ALLROWS[c["slug"]] = rows_
    draw_candidate(c, rows_, f"{OUT}/{c['slug']}", *texts_for2(c, rows_))
    print(c["slug"], [verdict(c,d)[0] for d in rows_])
