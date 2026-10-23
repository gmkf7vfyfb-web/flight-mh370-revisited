
import textwrap
def wrap(s, w=260): return "\n".join(textwrap.wrap(s, w))
BEARING = ("Bearing check: the source point is at 268.9 deg from Cape Leeuwin (1,812 km) and 144.8 deg from Diego Garcia South (3,660 km). Kadri gives 57 deg or 306.18 deg "
           "for the 00:52 signal (text p. 9 and Table 1 caption disagree); neither is within 37 deg of 268.9 deg. The nearest Table 1 bearing is 00:52:50 at 274.84 deg, 46 s later.")
def texts_for(c, rows):
    held = [ROW_LABEL[(d['rx'],d['kind'])].split('\n')[0] for d in rows if d['held']]
    if c["kind"]=="pair":
        src = f"{abs(c['lat']):.1f} S {c['lon']:.1f} E, impact {hms(c['t_imp'],0)} UTC"
        title = (f"If the {names[c['rx'][0]]} {hms(c['t_obs'][0],0)} and {names[c['rx'][1]]} {hms(c['t_obs'][1],0)} signals were one impact ({src}): "
                 "the data held at every receiver when its sound should arrive")
    else:
        src = (f"most probable source {abs(c['lat']):.1f} S {c['lon']:.1f} E, impact {hms(c['t_imp'],0)} UTC" if c["kind"]=="single" else "no flight-model impact can make this arrival (impact before 00:19:29)")
        title = f"If the {names[c['rx'][0]]} {hms(c['t_obs'][0],0)} signal were the impact ({src}): the data held at every receiver when its sound should arrive"
    eta = c.get("eta_need", np.nan)
    eta_s = (f"needed coupling {eta:.2g} ({eta/RC.ETA_ANCHOR:.0f} times the F-35A value 2.1e-4; {c['eta_basis']})" if np.isfinite(eta)
             else f"needed coupling {'unbounded' if eta==np.inf else 'undefined'} ({c['eta_basis']}); expected levels drawn at {c.get('eta_line_label','-')}")
    sub = f"{eta_s}."
    if c["name"].startswith("Pair 1"): sub += "\n" + BEARING
    elif c["kind"]=="single-arc-uniform": sub += "\nThe arrival time needs an impact between 00:05 and 00:16 UTC, before the last aircraft message (00:19:29); windows assume any point on the arc."
    foot1 = wrap("(i) Each row is one receiver. The orange band shows when sound from the candidate source would arrive at that receiver. A grey row means that we hold no recording "
                 "for that time. The purple line shows how loud the candidate would be if it were the impact, with the coupling that it needs. If the purple line is high and the trace "
                 "shows nothing above the dotted purple line, the receiver should have detected the sound and did not. Plots marked digitised are copies of published figures, not recordings. "
                 "These are model predictions. The sound-loss model and the coupling are not calibrated.")
    ln = (f"Source: {'lag locus on the 7th-arc grid (offset 0), Monte Carlo n = ' + str(c['n']) + ', c ~ N(1.482, 0.006) km/s, pick error sd 3.6 s (injection 3 s + clock 2 s)' if c['kind']=='pair' else 'run J search-geometry sample (waypoints stratum seeds 1-8 + northern supplement; 00:19 Held Out, p 0.5) conditioned on the observed arrival (Gaussian kernel, sd from c and 3.6 s pick error); ESS ' + str(round(c.get('ess',0)))}. "
          f"Window = 2.5-97.5 % of predicted arrival incl. c and pick errors; plots window +/- 2 min. Level: E {c.get('E_med',np.nan)/1e9:.2f} GJ, tau90 {c.get('tau_med',np.nan):.1f} s ({c.get('Etau_src','-')}); "
          "SNR = peak 1 s 5-40 Hz level re 14-day background median, TL from the arc grid (IMOS: RAM-corrected table imos_tl_ram_arc.csv; IMS: KRAKEN - RAM delta, +4.8 dB triad gain), "
          "P_D = block 7 logistic fit, M1b, alpha 0.05 (IMS: proxy noise). M1b = envelope matched filter (18-template KRAKEN bank on IMOS, station templates on panels); p = (k+1)/(n+1) against 55 s window maxima of the logger's "
          "own 1-15 March background (3315 <- 3376, 3275 <- 3274 stand-ins) or, for panels, IMOS 3376 through the plot emulator; p for the window maximum is not corrected for window length. "
          "Kadri Fig. 9 panels: digitised plots, 20 Hz, nothing above ~7 Hz trusted; Kadri times: text time 00:52:03, caption time 00:54:30. Royer (2016) spectrograms: colour->dB inversion (+/-1.5 dB), "
          "band 5-40 Hz; picks from Table 5 (H01W figure labels run 13.6-16 s later than the table, unresolved). PREDICTIVE, NOT CALIBRATED; caveats C1 (slope misfit +10.4/+7.4 dB/octave at H01W/H08S) and C2 (coupling not calibrated; F-35A anchor 2.1e-4).")
    return title, sub, foot1, wrap("(ii) " + ln, 300)
def build_rows(c):
    return [row_data(rx, kind, c["win"][rx][0], c["win"][rx][2]) for rx, kind in ROWS]
OUT = "graphics_out"; os.makedirs(OUT, exist_ok=True)
c = cands[0]; rows0 = build_rows(c); tt_ = texts_for(c, rows0)
t1=time.time(); draw_candidate(c, rows0, f"{OUT}/cand01_pair1", *tt_); print(round(time.time()-t1,1))
