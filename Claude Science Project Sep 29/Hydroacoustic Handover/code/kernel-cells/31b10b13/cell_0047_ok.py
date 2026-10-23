
nnorow=int((~np.isfinite(T.lnLR)).sum())-nblk
r0524=int((ss.lnLR>-2.7513).sum())+1; r0529=int((ss.lnLR>ss[(ss.rx=="H01W")&(ss.time_utc=="00:54:29")].lnLR_no_bearing.iloc[0]).sum())+1
print(nnorow,r0524,r0529)
F2s2=F2s.replace("Without the bearing term the 00:52:04 row has ln LR -2.75 (rank 9 equivalent) and the 00:54:29 row -3.40.",
   f"Without the bearing term the 00:52:04 row has ln LR -2.75 (would rank {r0524}) and the 00:54:29 row -3.40 (would rank {r0529}); the bearing term also moves their most likely source to about 28 S 99-100 E.")
plt.close("all"); fig=render(rows,cols,widths,"One-recorder candidate signals, top 15 in order of approximate likelihood ratio (none favoured over noise)",F1s,F2s2,"ranked_singles_top15",highlight=[len(rows)-2,len(rows)-1])
F2m=F2.replace("11,130 triples and all IMOS x IMOS x IMOS sets contain blocked Scott Reef 3250, ln LR -inf",
   f"{nblk:,} triples, including every IMOS x IMOS x IMOS set, contain blocked Scott Reef 3250 and {nnorow} more have no simulated impact that fits all three times: ln LR -inf")
# rebuild multisite rows
rowsm=[]
for r in T15.itertuples():
    rowsm.append({"Rank by ln LR":r.rank_lnLR,"ln LR":f"{r.lnLR:.2f}","Rank by largest p":r.rank_p,"Recorders":rxs_names(r.receivers),"Arrival times (UTC)":r.times.replace(";","; "),
        "Detector and band":dets_txt(r.detectors,r.bands),"p-values (block-permutation p, panels)":ptxt(r.p_values,r.p_B),
        "Time differences, s: observed [predicted 99 % range]":r.lags.replace(" s in","").replace("; ","\n") if r.n_sites==3 else r.lags.replace(" s in",""),
        "Arc point from the time difference; impact time (UTC)":(f"{-r.locus_lat:.1f}°S {r.locus_lon:.1f}°E; {str(r.implied_impact_utc)[:8]}" if np.isfinite(r.locus_lat) else "no arc point fits all three"),
        "Coupling for detection at all recorders with probability 0.5 (× reference crash, provisional)":fmt_eta(r.eta_pd50_all_a005),
        "Sound direction at Cape Leeuwin against Kadri":bear_short2(r.bearing_consistency),"Searches label":r.label_searches})
plt.close("all"); fig=render(rowsm,list(rowsm[0]),[6,5,6,22,14,20,15,22,19,17,18,8],"Two- and three-recorder candidate signals, top 15 in order of approximate likelihood ratio (none favoured over noise)",F1,F2m,"ranked_multisite_top15",highlight=[len(rowsm)-1])
plt.close("all")
# energy chart: legend wording + P/S identities in technical footnote
src=open("energy_chart.py").read()
src=src.replace('label="★ strongest pair by p-value (Cape Leeuwin 00:52:04 × Diego Garcia South 01:12:49)"','label="★ pair the searches named strongest (Cape Leeuwin 00:52:04 × Diego Garcia South 01:12:49)"')
ids="; ".join([f"P{i+1} {r.rx_a} {r.t_a} x {r.rx_b} {r.t_b}" for i,r in enumerate(top5p.itertuples())]+[f"S{i+1} {r.rx} {r.time_utc} {r.det}" for i,r in enumerate(top5s.itertuples())])
src=src.replace('tau dependence of the required level ignored along each band.',f'Lines (ranked by approximate ln LR, ranked_pairs.csv / ranked_singles.csv): {ids}. tau dependence of the required level ignored along each band.')
open("energy_chart.py","w").write(src); exec(src)
