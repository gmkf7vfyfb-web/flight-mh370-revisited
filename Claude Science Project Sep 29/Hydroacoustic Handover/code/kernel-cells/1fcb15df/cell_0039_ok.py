
for lab, la, lo, ot in [("A",-57.3,88.965,"00:16:29.4"),("idx2",-64.51,127.048,"00:13:09.3")]:
    d_ = dist_km(la,lo,"H01W")[0]; print(lab, round(d_), hms(hms2u(ot)+d_/C), hms(hms2u(ot)+d_/1.467), hms(hms2u(ot)+d_/1.518))
    rl,ro = RX["H01W"]; az,_,_ = G.inv(ro, rl, lo, la); print("  bearing from H01W", round(az%360,1))
print(rarr[rarr["index"].isin([3])][["station","arrival_utc","implied_speed_km_s"]].to_string())
mk = pd.read_csv(RD_+"/royer_figure_marks.csv"); print(mk.columns.tolist()); print(mk[mk.iloc[:,0].astype(str).str.contains("eventA|h01w", case=False)].head(12).to_string())
