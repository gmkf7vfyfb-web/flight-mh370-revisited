evt={r["appendixB_event_id"]:tsec(r["time_utc_as_printed"]) for _,r in ev2003.iterrows() if r["time_utc_as_printed"]}
day={r["appendixB_event_id"]:r["jd"] for _,r in ev2003.iterrows() if r["time_utc_as_printed"]}
Bd={e:d for e,_,_,_,d in B}
chk=[]
pairs=[("A1sus3","A1sph1"),("A1sus2","A1sus3"),("A2sus2","A2sus3"),("A4sus3","A4sph5"),("A4sus2","A4sus3"),("A5sus3","A5sph5"),("A5sus2","A5sus3"),
("A6sus2","A6sus3"),("A7sus3","A7sph5"),("A7sus2","A7sus3"),("A8sus2","A8sph1"),("A8sus2b","A8sus2"),("A11sph5","A11sus")]
for a,b in pairs:
    dt_tab=evt[a]-evt[b] if day[a]==day[b] else None
    for k in ["CL","DGS","DGN"]:
        va,vb=Bd[a][k],Bd[b][k]
        if isinstance(va,str) or isinstance(vb,str): continue
        dp=int(va[0])-int(vb[0])
        do=(float(va[1].rstrip("?"))-float(vb[1].rstrip("?"))) if (va[1]!="ND" and vb[1]!="ND") else None
        chk.append(dict(later_event=a,earlier_event=b,station=STN[k],table_origin_diff_s=round(dt_tab,2),appB_predicted_diff_s=dp,appB_observed_diff_s=do,
                        predicted_minus_table_s=round(dp-dt_tab,2),consistent_within_2s=abs(dp-dt_tab)<=2))
ck=pd.DataFrame(chk); ck.to_csv("out/appendixB_timing_consistency.csv",index=False); print(ck.to_string())