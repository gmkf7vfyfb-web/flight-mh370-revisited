
code = open("track_rowdata.py").read().replace('out["reason"] = NOT_HELD_REASON[rx]; return out', 'out["reason"] = NOT_HELD_REASON[rx]; out["cover_frac"] = 0.0; return out')
open("track_rowdata.py","w").write(code); exec(code)
for rx, kind in ROWS:
    w0, _, w1 = c["win"][rx]; d = row_data(rx, kind, w0, w1)
    print(rx, kind, d["held"], round(d["cover_frac"],2), round(d.get("stat",np.nan),3), None if d.get("p") is None else round(d["p"],3), hms(d["stat_t"]) if "stat_t" in d else "",
          [(hms(t),s,l,e) for t,s,l,e in d["picks"] if w0<=t<=w1], d.get("reason",""))
ev = pd.read_csv(RD_+"/royer_events.csv"); print(ev[ev.label.notna()][["label","origin_time_utc","lat_deg","lon_deg","event_class"]].to_string())
print(rarr[rarr.station.str.startswith("H01W") & (rarr.arrival_s_after_T0.between(3000,3300))][["index","label","event_class","station","arrival_utc"]].to_string())
