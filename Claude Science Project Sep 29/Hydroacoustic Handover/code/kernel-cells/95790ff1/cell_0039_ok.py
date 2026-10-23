evrows=[]
def add(tbl,src_type,r,charge,eid,label_corr="",flag="",notes=""):
    y,jd,t,stn,la,lo,dep=r
    d=jd2date(y,jd)
    evrows.append(dict(year=int(y),jd=int(jd),date_utc=d,time_utc_as_printed=t,iso_utc=f"{d}T{t}Z",
        site_label_as_printed=stn,site_label_corrected=label_corr or stn,appendixB_event_id=eid,source_type=src_type,
        charge_or_source_size=charge,source_depth_m_as_printed=dep,
        lat_as_printed=la,lon_as_printed=lo,lat_dd=round(-dm(la),7),lon_dd=round(dm(lo),7),
        table=tbl,source_page_pdf=26,source_page_printed=24,quality_flag=flag,notes=notes))
for r in T2: add("Table 2","imploding_cylinder_MPL_SIO",r,"20-litre cylinder (pdf p5,p12)","")
for r in T3: add("Table 3","glass_sphere_single",r,"22-litre glass sphere (pdf p5)",(r[3]+"sph1") if r[0]=="2003" else "")
for r in T4: add("Table 4","glass_sphere_five_cluster",r,"five 22-litre spheres (cluster; size per sphere from pdf p5/p6)",(r[3]+"sph5") if r[0]=="2003" else "")
sus_ids={"13:55:09.15":"A1sus3","14:04:59.23":"A1sus2","13:35:02":"A2sus3","13:39:47.39":"A2sus2","10:54:57.77":"A4sus3","10:59:49.04":"A4sus2",
 "06:48:38":"A5sus3","06:52:38":"A5sus2","04:20:21.90":"A6sus3","04:25:51.21":"A6sus2","11:52:11.75":"A7sus3","11:59:15.81":"A7sus2",
 "09:13:59.37":"A8sus2","09:19:59.23":"A8sus2b","10:48:48.10":"A9sus3","03:55:21.68":"A10sus3","00:37:33.83":"A11sus"}
for r in T5:
    t=r[2]; charge="1.8 lb SUS" if r[3]!="A11" else "SUS, charge size not given (table header '1.8 lb except A11')"
    corr,flag,notes="","",""
    if t=="10:54:57.77":
        corr="A4"; flag="label_typo_in_original"
        notes="Printed 'A3' in the original page image (not an extraction artefact). Coordinates, timing and Appendix B Fig B4 show this is the A4 915 m SUS (A4sus3). See jd144_check.txt."
    if t=="09:19:59.23":
        flag="depth_conflict"; notes="Table 5 prints 610 m for both A8 SUS; Fig B8 caption gives the second A8 SUS (panel A8sus2b) as 915 m while the panel label 'sus2' denotes 2000 ft (610 m). Unresolved."
    if t=="03:55:21.68":
        flag="timing_anomaly"; notes="Appendix B observed arrivals are ~60 s later than predicted at both detecting stations (H01 1842 vs 1782 s; H08S 1604 vs 1541 s): either the tabulated origin time or the prediction is about one minute off. Unresolved; provisional."
    if t=="11:59:15.81":
        flag="prediction_offset_in_appendixB"; notes="Observed sus2-minus-sus3 arrival differences (424/425/424 s at H01/H08S/H08N) match this table's origin-time difference (424.06 s); Appendix B predicted differences are 364 s, so the Appendix B prediction for A7sus2 used an origin time ~60 s early. Table value supported."
    add("Table 5","SUS_explosive",r,charge,sus_ids[t],corr,flag,notes)
# Appendix B partial charges not in Appendix A
for site,eid,dep,txtnote,pg in [("A9","A9suspuf","< 610 (as printed)","only the trigger charge ignited, not the full charge (Fig B9 caption)",32),
                                ("A10","A10suspuf","610 (as printed)","charge did not fully fire (Fig B10 caption)",33)]:
    evrows.append(dict(year=2003,jd="",date_utc="",time_utc_as_printed="",iso_utc="",site_label_as_printed=site,site_label_corrected=site,
        appendixB_event_id=eid,source_type="SUS_explosive_partial_fire",charge_or_source_size="1.8 lb SUS (partial fire)",source_depth_m_as_printed=dep,
        lat_as_printed="",lon_as_printed="",lat_dd="",lon_dd="",table="not in Appendix A; Appendix B only",source_page_pdf=pg,source_page_printed=pg-2,
        quality_flag="time_and_position_not_printed",notes=txtnote+". Origin time and position are not printed anywhere in the report; recorded as missing."))
ev=pd.DataFrame(evrows)
ev2003=ev[ev.year==2003].copy(); ev2001=ev[ev.year==2001].copy()
ev2003.to_csv("out/blackman_2003_events.csv",index=False); ev2001.to_csv("out/blackman_2001_nonairgun_events.csv",index=False)
print(len(ev2003),len(ev2001)); print(ev2003[["date_utc","time_utc_as_printed","site_label_as_printed","site_label_corrected","appendixB_event_id","source_depth_m_as_printed","quality_flag"]].to_string())