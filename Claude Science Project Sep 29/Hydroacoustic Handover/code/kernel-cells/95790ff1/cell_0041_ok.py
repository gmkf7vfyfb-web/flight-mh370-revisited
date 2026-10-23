STN={"CL":"H01","DGS":"H08S","DGN":"H08N"}
# (event, page_pdf, printed, figure, {stn:(pred, obs, nd_marker, arrows)})
B=[("A1sph1",27,25,"Fig B1",{"CL":("2404","ND","yes","no"),"DGS":"TRUNC","DGN":"TRUNC"}),
("A1sus2",27,25,"Fig B1",{"CL":("4719","ND","yes","no"),"DGS":"TRUNC","DGN":"TRUNC"}),
("A1sus3",27,25,"Fig B1",{"CL":("4129","ND","yes","no"),"DGS":"TRUNC","DGN":"TRUNC"}),
("A2sus2",28,26,"Fig B2",{"CL":("2827","2846?","yes","no"),"DGS":("1330","ND","yes","no"),"DGN":("1342","1332","no","yes")}),
("A2sus3",28,26,"Fig B2",{"CL":("2542","2553?","yes","no"),"DGS":("1045","ND","yes","no"),"DGN":("1057","1047","no","yes")}),
("A3sph1",28,26,"Fig B3",{"CL":("3031","ND","yes","no"),"DGS":("1521","ND","yes","no"),"DGN":("1544","ND","yes","no")}),
("A4sus2",29,27,"Fig B4",{"CL":("7176","7190?","yes","no"),"DGS":("5656","5650?","yes","no"),"DGN":("5689","ND","yes","no")}),
("A4sus3",29,27,"Fig B4",{"CL":("6885","ND","yes","no"),"DGS":("5365","5362?","no","yes"),"DGN":("5398","ND","yes","no")}),
("A4sph5",29,27,"Fig B4",{"CL":("4979","ND","yes","no"),"DGS":("3459","ND","yes","no"),"DGN":("3492","ND","yes","no")}),
("A5sus2",30,28,"Fig B5",{"CL":("6376","ND","yes","no"),"DGS":("4856","ND","yes","no"),"DGN":"DUP"}),
("A5sus3",30,28,"Fig B5",{"CL":("6136","ND","yes","no"),"DGS":("4616","4622?","no","yes"),"DGN":"DUP"}),
("A5sph5",30,28,"Fig B5",{"CL":("4931","4934?","yes","no"),"DGS":("2813","ND","yes","no"),"DGN":"DUP"}),
("A6sus2",30,28,"Fig B6",{"CL":("4408","4416?","yes","no"),"DGS":("2629","2624","no","yes"),"DGN":("2734","ND","yes","no")}),
("A6sus3",30,28,"Fig B6",{"CL":("4078","4089","no","yes"),"DGS":("2300","2295","no","yes"),"DGN":("2405","ND","yes","no")}),
("A7sus2",31,29,"Fig B7",{"CL":("2412","2478","no","yes"),"DGS":("908","966","no","yes"),"DGN":("1052","1108","no","yes")}),
("A7sus3",31,29,"Fig B7",{"CL":("2048","2054","no","yes"),"DGS":("544","541","no","yes"),"DGN":("688","684","no","yes")}),
("A7sph5",31,29,"Fig B7",{"CL":("135","140","no","yes"),"DGS":("5830","5828","no","yes"),"DGN":("5974","ND","yes","no")}),
("A8sph1",32,30,"Fig B8",{"CL":("5224","5254?","yes","no"),"DGS":("3887","3890?","no","yes"),"DGN":("4034","ND","yes","no")}),
("A8sus2",32,30,"Fig B8",{"CL":("6858","6862","no","yes"),"DGS":("5521","5519","no","yes"),"DGN":("5668","5668?","yes","no")}),
("A8sus2b",32,30,"Fig B8",{"CL":("17","22","no","yes"),"DGS":("5881","5879","no","yes"),"DGN":("6028","6028?","yes","no")}),
("A9sus3",32,30,"Fig B9",{"CL":("5128","5125","no","yes"),"DGS":("4402","4410","no","yes"),"DGN":("4539","ND","yes","no")}),
("A9suspuf",32,30,"Fig B9",{"CL":("5556","ND","yes","no"),"DGS":("4830","ND","yes","no"),"DGN":("4966","ND","no","no")}),
("A10sus3",33,31,"Fig B10",{"CL":("1782","1842","no","yes"),"DGS":("1541","1604","no","yes"),"DGN":("1671","ND","yes","no")}),
("A10suspuf",33,31,"Fig B10",{"CL":("2191","ND","yes","no"),"DGS":("1950","ND","yes","no"),"DGN":("2080","ND","yes","no")}),
("A11sus",33,31,"Fig B11",{"CL":("3994","3992","no","yes"),"DGS":("4653","4657","no","yes"),"DGN":("4782","ND","yes","no")}),
("A11sph5",33,31,"Fig B11",{"CL":("5920","5918","no","yes"),"DGS":("6707","ND","yes","no"),"DGN":("6836","ND","yes","no")}),]
stype=lambda e: "glass_sphere_single" if "sph1" in e else "glass_sphere_five_cluster" if "sph5" in e else "SUS_explosive_partial_fire" if "puf" in e else "SUS_explosive"
for eid,pg,pp,fig,d in B:
    for k in ["CL","DGS","DGN"]:
        v=d[k]; rc=STN[k]
        if v=="TRUNC":
            O(2003,eid,stype(eid),rc,"LLNL (Appendix B)","not_assessed_data_truncated",pg,pp,f"{fig} panel","waveform truncated at 550 secs, before predicted arrival time")
        elif v=="DUP":
            O(2003,eid,stype(eid),rc,"LLNL (Appendix B)","not_reported",pg,pp,f"{fig} H08N column",
              "",notes="Fig B5 H08N column reproduces the A4 panels (labels A4sus2/A4sus3/A4sph5, predicted 5689/5398/3492 s, identical to Fig B4); no A5 result at H08N is printed")
        else:
            p,o,nd,ar=v
            if o=="ND": st="not_detected"
            elif o.endswith("?"): st="not_detected_with_tentative_pick" if nd=="yes" else "detected_questionable_pick"
            else: st="detected" if nd=="no" else "ambiguous_as_printed"
            note=""
            if eid=="A9suspuf" and k=="DGN": note="no ND marker drawn on this panel but observed printed as ND"
            if eid in("A7sph5","A8sus2b") and k=="CL": note="predicted/observed counted from a different time reference from the other A7/A8 panels at H01"
            if eid=="A7sus2": note="observed-minus-predicted 56-66 s at all three stations; consistent with ~60 s origin-time offset in the Appendix B prediction (see events file)"
            if eid=="A10sus3" and k!="DGN": note="observed-minus-predicted ~60 s; origin time or prediction ~1 min off (unresolved)"
            O(2003,eid,stype(eid),rc,"LLNL (Appendix B)",st,pg,pp,f"{fig} panel",f"arrival time predicted = {p} sec.; arrival time observed = {o}",p,o,nd,ar,notes=note)
# ---- 2003 SIO / report-text statements ----
O(2003,"A1sus3; A1sus2","SUS_explosive","any IMS station (text; Crozet H04 nearest)","SIO (report text)","not_detected",12,10,"Sec 4.4 text","two that did fire but were not detected were closest to Crozet (site A1, Table 5) but those hydrophones were experiencing very high noise conditions",notes="identification of the two shots as the A1 SUS is the plain reading of the sentence")
O(2003,"A4sus3; A4sus2","SUS_explosive","H08N","SIO (report text)","detected",13,11,"Sec 4.4 text","The two SUS charges at site A4 were detected at Diego Garcia, North, in the SIO analysis but not picked up using the LLNL method",notes="SIO/LLNL disagreement; LLNL rows show ND at H08N")
O(2003,"A11sph5","glass_sphere_five_cluster","station not specified (SIO)","SIO (report text)","not_detected",13,11,"Sec 4.4 text","indicated as detected in the LLNL analysis where as SIO ... did not detect the signal",notes="LLNL App B shows detection at H01 only")
O(2003,"A11sph5","glass_sphere_five_cluster","H01","Australian colleagues monitoring Cape Leeuwin (per report text)","not_detected",13,11,"Sec 4.4 text","Australian colleagues monitoring the Cape Leeuwin data during the experiment did not detect the signal")
for rc,band in [("H08S","sonogram S1-S3; time series highpass 5 Hz"),("H01","sonogram W1-W3; bandpass 50-100 Hz time series"),("H04N","sonogram N2-N3")]:
    O(2003,"A6sus3","SUS_explosive",rc,"SIO (report figures)","detected",13,11,"Fig 9a,b + Sec 4.4 text","Figures 9-11 illustrate the character of the signal recorded at the IMS hydrophones",band=band)
for rc in ["H08S","H01"]:
    O(2003,"A6sus2","SUS_explosive",rc,"SIO (report figures)","detected",13,11,"Fig 9c + Sec 4.4 text","Figures 9-11 illustrate the character of the signal recorded at the IMS hydrophones",band="de-meaned sonogram",notes="H01: conflicts with LLNL App B (ND marker, tentative 4416?)" if rc=="H01" else "")
for rc in ["H04N","H04S"]:
    O(2003,"A8sus2 or A8sus2b (not specified)","SUS_explosive",rc,"SIO (report figures)","detected",14,12,"Fig 10 left caption + arrows","Sonograms of SUS at site A8, 610 m depth, for Crozet",notes="Table 5 has two 610 m A8 SUS; figure does not say which")
O(2003,"A11sus","SUS_explosive","H08S","report figure","detected",14,12,"Fig 10 right","arrival time predicted = 4653 sec. arrival time observed = 4657 sec.",pred="4653",obsv="4657",rng="3577")
for rc,rg,bd in [("H04N","6140","duration ~8 s, energy 40-100 Hz"),("H08S","3577","most energy 60-100 Hz, reduced down to 30 Hz"),("H01","2595","significant energy 10-120 Hz")]:
    O(2003,"A11sus","SUS_explosive",rc,"SIO (report figures)","detected",14,12,"Fig 11 caption","All three IMS hydrophone stations recorded this shot",rng=rg,band=bd)
ro=pd.DataFrame(obs); ro.insert(0,"obs_id",[f"BLK{i+1:03d}" for i in range(len(ro))])
ro.to_csv("out/blackman_receiver_observations.csv",index=False)
print(len(ro)); print(ro.status.value_counts().to_string())