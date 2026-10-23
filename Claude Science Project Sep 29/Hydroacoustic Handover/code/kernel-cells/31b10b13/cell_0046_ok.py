
nblk=int((T.caveats.astype(str).str.contains("blocked path")).sum()); print("triples blocked",nblk, "finite",int(np.isfinite(T.lnLR).sum()))
top=ss.head(15).copy(); h1=ss[(ss.rx=="H01W")&(ss.time_utc.isin(["00:52:04","00:54:29"]))]
S15=pd.concat([top,h1])
def kad(s): return "" if s=="unlabelled" else s
rows=[]
for r in S15.itertuples():
    rows.append({"Rank by ln LR":r.rank_lnLR,"ln LR":f"{r.lnLR:.2f}","Rank by p":r.rank_p,"Recorder":nm(r.rx),"Time (UTC)":r.time_utc,
        "Data":"digitised plot" if str(r.source).startswith("digitised") else "recording",
        "Detector and band":dets_txt(r.det,r.band),"p (block-permutation p)":f"{r.p:.2g}"+(f" ({r.p_B:.2g})" if np.isfinite(r.p_B) else ""),
        "ln time density / ln detection and level / ln noise rate":f"{r.ln_ftime:.1f} / {r.ln_f_amp_given_time:.1f} / {r.lnB:.1f}",
        "Coupling to match the level at the median impact (× reference crash, provisional)":fmt_eta(r.eta_needed),
        "Most likely source and impact time given the signal":f"{r.implied_source}; {str(r.implied_impact_utc)[:8]}",
        "Kadri label":kad(r.kadri_label),"Sound direction against Kadri":bear_short2(r.bearing_consistency),"Searches label":r.label_searches})
cols=list(rows[0]); widths=[6,5,5,16,8,9,18,11,15,18,18,18,18,8]
F1s=("(i) Each row is one possible signal at one recorder. The rank uses an approximate likelihood ratio: how likely the signal is if it comes from the aircraft, compared with how often noise gives such a signal. "
     "ln LR below 0 means noise explains it better; all 184 signals have ln LR below 0. The two shaded rows are the Cape Leeuwin signals at Kadri's two times (text time 00:52:03, caption time 00:54:30). "
     "The coupling is the share of impact energy that must become sound; above 1 is not possible. Estimates only, no detection.")
F2s=("(ii) EXPLORATORY ranking, pre-registered at module commit 9f47cf7; not part of the frozen searches. Source posterior run J geometry sample, 00:19 Held Out (D0'), p = 0.5. ln LR = ln f_time + ln f_amp|time - ln(p/55 s): "
     "f_time = sum_i w_i K_t (Gaussian timing kernel, block 11); f_amp|time = mean over eta log-uniform [1e-6, 1e-2] of P_D(snr; alpha = p) x level consistency (sigma 10 dB) x Kadri Table 1 bearing term (within 30 s; t3, 3.3 deg) given the time match. "
     "Coupling = level match at the reference impact (37.1 S on the arc, 1.13 GJ, tau90 3.3 s): IMOS from the 5-40 Hz excess with the corrected RAM-grid TL (the searches' column used pass-A TL, about 20 dB more loss, so its IMOS values are about 100x higher; G-S5); "
     "panels from the searches' eta_needed. Reference F-35A eta 2.1e-4 (provisional - from Brown 2026's quote of Metz 2023; re-derivation from Metz pending). Scott Reef 3250: blocked path, ln LR -inf. "
     "H08S raw-panel rows are airgun-dominated (G-S9); 3315 and 3275 use the paired logger's null (G-S4); 2-5 Hz IMOS rows are below the 8 Hz hardware corner. Without the bearing term the 00:52:04 row has ln LR -2.75 (rank 9 equivalent) and the 00:54:29 row -3.40. "
     "Full table ranked_singles.csv. PREDICTIVE, NOT CALIBRATED; C1, C2.")
plt.close("all"); fig=render(rows,cols,widths,"One-recorder candidate signals, top 15 in order of approximate likelihood ratio (none favoured over noise)",F1s,F2s,"ranked_singles_top15",highlight=[len(rows)-2,len(rows)-1])
print(ss[ss.lnLR>-2.76].shape[0])
