
print("ranked exists:", os.path.exists(RANK), os.listdir(os.path.dirname(RANK)) if os.path.exists(os.path.dirname(RANK)) else None)
for c in cands:
    if c["kind"]=="pair" and c["eta_need"]==np.inf:
        c["eta_basis"] = f"the sound path from {abs(c['lat']):.1f} S to {names[c['rx'][0]]} is blocked in the sound-loss grid, so no coupling gives detection there; Scott Reef 3250 path also blocked"
    if c["kind"]=="single" and not np.isfinite(c["eta_need"]):
        c["eta_basis"] = "Scott Reef 3250: sound path from the arc blocked in the sound-loss grid"
_verdict1 = verdict
def verdict(c, d):
    k, s = _verdict1(c, d)
    if not c.get("snr"): s = s.replace("no expected level (sound path blocked)", "no expected level (no flight-model source)")
    return k, s
plot_code = open("track_plot.py").read()
plot_code = plot_code.replace('''axs[3].text(0.99, 0.95, "expected level: not modelled at this site" if rx not in ("3250",) else "expected level: none (sound path blocked)",''',
 '''axs[3].text(0.99, 0.95, ("expected level: none (no flight-model source)" if not c.get("snr") else "expected level: not modelled at this site" if rx not in ("3250",) else "expected level: none (sound path blocked)"),''')
open("track_plot.py","w").write(plot_code); exec(plot_code)
def texts_for3(c, rows):
    a,b,f1,f2 = texts_for2(c, rows)
    if not np.isfinite(c.get("eta_need", 0)):
        if c["kind"]=="single-arc-uniform":
            b = b.replace("needed coupling undefined (not computed: no run J impact can produce this arrival); expected levels drawn at -.", "needed coupling: not computed, because no flight-model impact can produce this arrival.")
        else:
            b = b.replace("needed coupling undefined (undefined: ", "needed coupling undefined (").replace("needed coupling unbounded (", "needed coupling unbounded (")
    if c["kind"]=="single-arc-uniform":
        f2 = f2.replace(f"run J search-geometry sample (waypoints stratum seeds 1-8 + northern supplement; 00:19 Held Out, p 0.5) conditioned on the observed arrival (Gaussian kernel, sd from c and 3.6 s pick error); ESS 0",
                        "no run J row reaches this receiver at this time (zero conditioned mass); source drawn uniformly on the 41-20 S arc with impact time = arrival - range/c (n 20,000)")
        f2 = wrap(f2.replace("\n"," ")[5:].replace("Level: E nan GJ, tau90 nan s (sample rows conditioned on the observed arrival); ", "No level computed; "), 355); f2 = "(ii) " + f2
    return a,b,f1,f2
for c in cands:
    rows_ = ALLROWS[c["slug"]]
    draw_candidate(c, rows_, f"{OUT}/{c['slug']}", *texts_for3(c, rows_))
print(texts_for3(cands[-1], ALLROWS[cands[-1]["slug"]])[1]); print(texts_for3(cands[2], ALLROWS[cands[2]["slug"]])[1]); print(texts_for3(cands[5], ALLROWS[cands[5]["slug"]])[1])
