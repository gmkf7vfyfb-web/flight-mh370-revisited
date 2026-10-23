
exec(open("table_figs.py").read())
def rxs_names(s): return " × ".join(nm(x.strip()) for x in s.split(" x "))
def dets_txt(d,b): return "; ".join(f"{DETN.get(x,x)} {y} Hz".replace(" (plot) Hz"," Hz (plot)") for x,y in zip(d.split(";"),b.split(";")))
top=MS.head(15).copy()
star=MS[(MS.n_sites==2)&(MS.receivers=="H01W x H08S")&(MS.times=="00:52:04;01:12:49")&(MS.detectors=="M1b;M1b")]
T15=pd.concat([top,star])
rows=[]
for r in T15.itertuples():
    rows.append({"Rank by ln LR":r.rank_lnLR,"ln LR":f"{r.lnLR:.2f}","Rank by p":r.rank_p,"Recorders":rxs_names(r.receivers),"Arrival times (UTC)":r.times.replace(";","; "),
        "Detector and band":dets_txt(r.detectors,r.bands),"p-values (block-permutation p for panels)":r.p_values.replace(";","; ")+(f" [{r.p_B.replace(';','; ')}]" if isinstance(r.p_B,str) and r.p_B.strip(";") else ""),
        "Time differences, s: observed in [predicted 99 % range]":r.lags.replace(" s in","").replace("; ","\n") if r.n_sites==3 else r.lags.replace(" s in",""),
        "Arc point from the time difference; impact time (UTC)":(f"{-r.locus_lat:.1f}°S {r.locus_lon:.1f}°E; {str(r.implied_impact_utc)[:8]}" if np.isfinite(r.locus_lat) else "no arc point fits all three"),
        "Coupling for detection at both (all) with probability 0.5 (× reference crash, provisional)":fmt_eta(r.eta_pd50_all_a005),
        "Sound direction at Cape Leeuwin vs Kadri":bear_short(r.bearing_consistency),"Searches label":r.label_searches})
cols=list(rows[0]); widths=[6,5,5,22,15,20,14,22,19,16,18,7]
F1=("(i) Each row is a set of possible signals at two or three recorders whose times agree with one simulated impact. The rank uses an approximate likelihood ratio: "
    "how likely the signals are if they come from the aircraft, compared with how often noise gives such signals. ln LR below 0 means noise explains the set better. "
    "All sets have ln LR below 0. The last row (shaded) is the pair with the smallest p-values in the searches; its sound direction does not agree with the directions Kadri published. "
    "The coupling is the share of impact energy that must become sound; above 1 is not possible. Estimates only, no detection.")
F2=("(ii) EXPLORATORY ranking, pre-registered at module commit 9f47cf7 (prepare/ranked_candidates/prereg.py); not part of the frozen searches. Source posterior run J geometry sample, 00:19 Held Out (D0'), p = 0.5. "
    "ln LR = ln sum_i w_i mean_eta prod_c[P_D(snr; alpha = p_c) K_t A G] - ln prod_c(p_c/55 s); eta log-uniform [1e-6, 1e-2]; P_D block 7 fits (IMS rows: IMOS-proxy noise + 4.8 dB); TL block 11 machinery with the corrected IMOS RAM-grid table; "
    "A = level consistency (sigma 10 dB); G = Kadri Table 1 bearing within 30 s, t3 scale 3.3 deg. Arc point: crossing of the observed lag on the 7th-arc grid (block 11 method; the crossing with most D0' mass within +/-1 deg). "
    "Coupling: eta for prod P_D = 0.5 at alpha 0.05 with run J median E and tau within +/-1 deg; reference F-35A eta 2.1e-4 (provisional - from Brown 2026's quote of Metz 2023; re-derivation from Metz pending). "
    "Star pair: locus bearing 268.9 deg from H01W (1,812 km), 144.8 deg from H08S (3,660 km); Kadri gives 57 or 306.18 deg for the 00:52 signal (text p. 9 vs Table 1 caption), neither within 37 deg; nearest Table 1 bearing 00:52:50 at 274.84 deg, 46 s later. "
    "H08S raw-panel rows are airgun-dominated (G-S9); Perth Canyon 3315 2-5 Hz rows are below the 8 Hz hardware corner and use the 3376 null (G-S4). Digitised Kadri (2024) Fig. 9 panels; text time 00:52:03, caption time 00:54:30. "
    "Full tables: ranked_multisite.csv (15,652 sets: 3,321 pairs + 12,331 triples; 11,130 triples and all IMOS x IMOS x IMOS sets contain blocked Scott Reef 3250, ln LR -inf). PREDICTIVE, NOT CALIBRATED; C1, C2.")
fig=render(rows,cols,widths,"Two- and three-recorder candidate signals, top 15 in order of approximate likelihood ratio (none favoured over noise)",F1,F2,"ranked_multisite_top15",highlight=[len(rows)-1])
