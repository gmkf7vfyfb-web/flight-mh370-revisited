pb="prior/Blackman_2004_extracted_data/"
ps=pd.read_csv(pb+"blackman_2001_airgun_shot_lines.csv")
m=[]
for (a,b) in zip(ps.itertuples(),shot.itertuples()):
    for f1,f2 in [("start_lat_dd","start_lat_dd"),("end_lat_dd","end_lat_dd"),("start_lon_dd","start_lon_dd"),("end_lon_dd","end_lon_dd"),("seafloor_start_m","seafloor_start_m"),("seafloor_end_m","seafloor_end_m"),("shot_interval_s","shot_interval_s")]:
        if abs(float(getattr(a,f1))-float(getattr(b,f2)))>1e-6: m.append((a.site,f1,getattr(a,f1),getattr(b,f2)))
    if a.start_utc!=b.start_utc or a.end_utc!=b.end_utc or str(a.shot_numbers)!=b.shot_numbers: m.append((a.site,"time/shots",a.start_utc,b.start_utc))
print(len(ps),len(shot),m)
pe=pd.read_csv(pb+"blackman_2003_source_events.csv"); pn=pd.read_csv(pb+"blackman_2001_nonairgun_source_events.csv")
mine=pd.concat([ev2003,ev2001]); mine=mine[mine.time_utc_as_printed!=""]
mm=[]
for df in (pe,pn):
    for r in df.itertuples():
        k=mine[(mine.jd==r.jd)&(mine.time_utc_as_printed==r.utc_time)]
        if len(k)!=1: mm.append(("nomatch",r.jd,r.utc_time)); continue
        k=k.iloc[0]
        if abs(k.lat_dd-r.latitude_dd)>1e-6 or abs(k.lon_dd-r.longitude_dd)>1e-6 or str(k.source_depth_m_as_printed)!=str(r.source_depth_m): mm.append((r.jd,r.utc_time,k.lat_dd,r.latitude_dd,k.source_depth_m_as_printed,r.source_depth_m))
print(len(pe),len(pn),len(mine),mm)
print(pe[pe.quality_flag.notna()][["jd","site","utc_time","quality_flag"]].to_string())
sc=pd.read_csv(pb+"blackman_source_class_characteristics.csv"); print(sc[["source_type","near_source_level"]].to_string())