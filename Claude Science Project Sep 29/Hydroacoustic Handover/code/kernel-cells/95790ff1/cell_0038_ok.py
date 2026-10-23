os.makedirs("out",exist_ok=True)
def jd2date(y,jd): return (dt.date(int(y),1,1)+dt.timedelta(days=int(jd)-1)).isoformat()
# ---------- 1. shot lines ----------
rows=[]; site=None; seg=0
for i in range(0,len(T1),2):
    s,e=T1[i],T1[i+1]
    if s[6]: site=s[6]; seg=1
    else: seg+=1
    jd=s[0].rstrip(":")
    interval=s[5].replace(" sec","")
    r=dict(year=2001,site=site,segment=seg,jd=int(jd),date_utc=jd2date(2001,jd),start_utc=s[1],end_utc=e[1],
      start_lat_as_printed=s[2],start_lon_as_printed=s[3],end_lat_as_printed=e[2],end_lon_as_printed=e[3],
      start_lat_dd=round(-dm(s[2]),6),start_lon_dd=round(dm(s[3]),6),end_lat_dd=round(-dm(e[2]),6),end_lon_dd=round(dm(e[3]),6),
      seafloor_start_m=int(s[4].replace(" m","")),seafloor_end_m=int(e[4]),shot_interval_s=int(interval),shot_numbers=s[7],
      jd_time_as_printed_start=f"{s[0]} {s[1]}" if not s[0].endswith(":") else f"{s[0]}{s[1]}",
      range_H01_km="",range_H08S_km="",range_H08N_km="",range_source="not printed for this site",
      source_page_pdf=25,source_page_printed=23,
      verification="text layer (ucrl-tr-207323.txt p25) matched whitespace-stripped; every value checked against 300-dpi page render",
      notes="")
    if site=="air9":
        r.update(range_H01_km="1665",range_H08S_km="about 4825",range_source="site-level range printed in text, pdf p10 (printed p8): H08S 'about 4825 km', Cape Leeuwin '1665 kilometers'; not per segment; H08N not printed (propagation to H08N stated blocked for air6-air9)")
    if site=="air1" and seg==1: r["notes"]="interval printed '97 sec' and seafloor '2110 m' (units printed only on first row)"
    if site in("air1","air4","air7","air8","air9") and seg==2: r["notes"]="continuation segment; site column blank in table, assigned to preceding site"
    if site=="air9": r["notes"]=(r["notes"]+"; " if r["notes"] else "")+"jd/time printed with colon separator '292:02:10' in original"
    rows.append(r)
shot=pd.DataFrame(rows); shot.to_csv("out/blackman_shot_lines.csv",index=False)
print(shot[["site","segment","start_utc","end_utc","start_lat_dd","end_lon_dd","shot_interval_s","shot_numbers"]].to_string())