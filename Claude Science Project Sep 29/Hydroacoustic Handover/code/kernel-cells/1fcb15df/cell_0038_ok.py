
def verdict(c, d):
    rx = d["rx"]
    if not d["held"]: return "not held", "could not have seen: no recording held"
    own = rx in c["rx"] and d["kind"] in ("imos","kadri")
    pr = d.get("p")
    if d["kind"] == "royer":
        inwin = [p for p in d["picks"] if d["w0"] <= p[0] <= d["w1"]]
        if inwin: return "pick", "Royer picked an arrival in the window (level not modelled)"
        return "nm_nothing", "level not modelled; no Royer pick in the window"
    if own and pr is not None and pr <= 0.3: return "present", "candidate present (defining signal)"
    if pr is not None and pr <= 0.05: return "present", f"signal present in window (p {pr:.2g})"
    snr = c.get("snr", {}).get(rx, np.nan); pdv = c.get("pd", {}).get(rx, np.nan)
    if not np.isfinite(snr) or rx == "3250": return "nm_nothing", "no expected level (path blocked)" + ("; nothing at p <= 0.05" if pr is not None else "")
    if pdv >= 0.5: return "should", f"should have seen (detection probability {pdv:.2f}): nothing (p {pr:.2g})"
    return "could_not", f"could not have seen (detection probability {pdv:.2f}): nothing (p {pr:.2g})"
plot_code = open("track_plot.py").read()
plot_code = plot_code.replace('gs = fig.add_gridspec(n, 4, left=0.13, right=0.985, top=top, bottom=bot, hspace=0.42, wspace=0.22, width_ratios=[1.15, 1.0, 1.0, 1.0])',
  'gs = fig.add_gridspec(n, 4, left=0.13, right=0.985, top=top, bottom=bot, hspace=0.55, wspace=0.22, width_ratios=[1.15, 1.0, 1.0, 1.0], height_ratios=[1.0 if d["held"] else 0.38 for d in rows])')
plot_code = plot_code.replace('n = len(rows); H = 1.08 * n + 2.6', 'n = len(rows); H = sum(1.15 if d["held"] else 0.45 for d in rows) + 3.0')
plot_code = plot_code.replace('show = (i == last_held) or (i == n - 1)', 'show = True')
plot_code = plot_code.replace('"1 s level above background median (dB) and expected level"', '"Level above background median (dB) and expected level"')
plot_code = plot_code.replace('''ax.text(-0.012, 0.5, label, transform=ax.transAxes, ha="right", va="center", fontsize=7.5)''',
  '''ax.text(-0.012, 0.5, label.replace("\\n", ", "), transform=ax.transAxes, ha="right", va="center", fontsize=7.5)''')
plot_code = plot_code.replace('''axs[0].text(-0.2, 0.5, label, transform=axs[0].transAxes, ha="right", va="center", fontsize=7.5)''',
  '''axs[0].text(-0.2, 0.62, label, transform=axs[0].transAxes, ha="right", va="center", fontsize=7.5)
        axs[0].text(-0.2, 0.12, "\\n".join(textwrap.wrap(verdict(c, d)[1], 34)), transform=axs[0].transAxes, ha="right", va="center", fontsize=6.5, color=VCOL[verdict(c, d)[0]])''')
plot_code = plot_code.replace('''"Purple line: expected level of the candidate if it were the impact; dotted purple: level for detection probability 0.5. "
             "Grey dashed lines''', '''"Purple line: expected level of the candidate if it were the impact; dotted purple: level for detection probability 0.5.\\n"
             "Grey dashed lines''')
plot_code = plot_code.replace('fig.text(0.01, bot - 0.78 / H', 'fig.text(0.01, bot - 0.80 / H').replace('fig.text(0.01, bot - 1.20 / H', 'fig.text(0.01, bot - 1.25 / H')
VCOL = {"not held":"#777777","present":"#b2182b","should":"#5e3c99","could_not":"#2166ac","nm_nothing":"#555555","pick":"#1b7f7a"}
open("track_plot.py","w").write(plot_code); exec(plot_code)
def wrap(s, w=230): return "\n".join(textwrap.wrap(s, w))
_tf = texts_for
def texts_for2(c, rows):
    a,b,f1,f2 = _tf(c, rows); return a, b, wrap(f1.replace("\n"," "), 230), wrap(f2.replace("\n"," "), 250)
c = cands[0]; draw_candidate(c, rows0, f"{OUT}/cand01_pair1", *texts_for2(c, rows0))
for d in rows0: print(d["rx"], d["kind"], verdict(c,d))
