mine["tn"]=mine.time_utc_as_printed.map(tsec)
mm=[]
for df in (pe,pn):
    for r in df.itertuples():
        k=mine[(mine.jd==r.jd)&((mine.tn-tsec(r.utc_time)).abs()<1e-6)]
        if len(k)!=1: mm.append(("nomatch",r.jd,r.utc_time)); continue
        k=k.iloc[0]
        if abs(k.lat_dd-r.latitude_dd)>1e-6 or abs(k.lon_dd-r.longitude_dd)>1e-6 or str(k.source_depth_m_as_printed)!=str(r.source_depth_m): mm.append((r.jd,r.utc_time,k.lat_dd,r.latitude_dd,k.lon_dd,r.longitude_dd,k.source_depth_m_as_printed,r.source_depth_m))
print(mm)