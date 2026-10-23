
def ptxt(ps,pbs):
    ps=ps.split(";"); pbs=(pbs if isinstance(pbs,str) else "").split(";")+[""]*3
    return "; ".join(f"{float(a):.2g}"+(f" ({float(b):.2g})" if b.strip() else "") for a,b in zip(ps,pbs))
def dets_txt(d,b): 
    out=[]
    for x,y in zip(d.split(";"),b.split(";")):
        out.append("residual envelope" if y=="residual env" else f"{DETN.get(x,x)} {y.replace(' (plot)','')} Hz")
    return "; ".join(out)
def bear_short2(s):
    v=bear_short(s); return "n/a (no Cape Leeuwin signal)" if v=="no H01W" else v
rows=[]
for r in T15.itertuples():
    rows.append({"Rank by ln LR":r.rank_lnLR,"ln LR":f"{r.lnLR:.2f}","Rank by largest p":r.rank_p,"Recorders":rxs_names(r.receivers),"Arrival times (UTC)":r.times.replace(";","; "),
        "Detector and band":dets_txt(r.detectors,r.bands),"p-values (block-permutation p, panels)":ptxt(r.p_values,r.p_B),
        "Time differences, s: observed [predicted 99 % range]":r.lags.replace(" s in","").replace("; ","\n") if r.n_sites==3 else r.lags.replace(" s in",""),
        "Arc point from the time difference; impact time (UTC)":(f"{-r.locus_lat:.1f}°S {r.locus_lon:.1f}°E; {str(r.implied_impact_utc)[:8]}" if np.isfinite(r.locus_lat) else "no arc point fits all three"),
        "Coupling for detection at all recorders with probability 0.5 (× reference crash, provisional)":fmt_eta(r.eta_pd50_all_a005),
        "Sound direction at Cape Leeuwin against Kadri":bear_short2(r.bearing_consistency),"Searches label":r.label_searches})
cols=list(rows[0]); widths=[6,5,6,22,14,20,15,22,19,17,18,8]
F1=F1.replace("The last row (shaded) is the pair with the smallest p-values in the searches;","The last row (shaded) is the pair the searches named as the strongest two-recorder pair;")+" Rank by largest p is over all 15,652 sets."
plt.close("all"); fig=render(rows,cols,widths,"Two- and three-recorder candidate signals, top 15 in order of approximate likelihood ratio (none favoured over noise)",F1,F2,"ranked_multisite_top15",highlight=[len(rows)-1])
