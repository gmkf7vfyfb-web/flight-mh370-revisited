obs=[]
def O(year,eid,stype,rcv,analysis,status,page,printed,where,quote,pred="",obsv="",nd="",arrows="",rng="",band="",notes=""):
    obs.append(dict(campaign_year=year,event_id=eid,source_type=stype,receiver=rcv,analysis=analysis,status=status,
      predicted_arrival_as_printed_s=pred,observed_arrival_as_printed=obsv,nd_marker_present=nd,backazimuth_arrows_present=arrows,
      range_km_as_printed=rng,band_or_signal_note=band,evidence_location=where,evidence_text=quote,source_page_pdf=page,source_page_printed=printed,notes=notes))
AG="airgun_array"
# ---- 2001 airgun, report text/figures ----
O(2001,"air1",AG,"H08N","SIO (report text/figures)","detected",9,7,"Fig 3 caption","shot 3 from air1 site shown at the three hydrophones of H08N",notes="also Fig 23 DGN air1 observed-TL curve (pdf p23)")
O(2001,"air2",AG,"H08N","SIO (report text/figures)","detected",10,8,"Sec 4.1 text; Fig 4a","recordings of air2 shots have high SNR in the 5-10 Hz range",band="5-10 Hz high SNR; wavetrain after initial pulse ~2 s")
O(2001,"air3",AG,"H08N","SIO (report text/figures)","detected",23,21,"Fig 23 DGN panel + caption","At H08N, air4 loss is very similar to air1-air3 losses in the 5-8 Hz band",notes="observed TL plotted only where signal exceeded noise by 3 dB")
O(2001,"air4",AG,"H08N","SIO (report text/figures)","detected",23,21,"Fig 23 DGN panel + caption","At H08N, air4 loss is very similar to air1-air3 losses in the 5-8 Hz band",band="5-8 Hz")
O(2001,"air5",AG,"H08N","SIO (report text/figures)","detected",10,8,"Sec 4.1 text; Figs 3b, 4b","air5 shots have high SNR in the 5-40 Hz band",band="5-40 Hz high SNR; duration after main pulse >5 s in 5-10 Hz")
for a in ["air1","air2","air3","air4"]:
    O(2001,a,AG,"H08S","SIO (report text/figures)","not_detected",10,8,"Sec 4.1 text","Propagation to H08S was blocked for the first 4 airgun sites",notes="explicit statement of blockage (no reception); Sec 4.7 adds modelled loss for air1-3 at H08S 'quite high'")
O(2001,"air5",AG,"H08S","none","not_reported",10,8,"Sec 4.1","",notes="no explicit statement; not inferred from silence")
O(2001,"air6",AG,"H08S","none","not_reported",10,8,"Sec 4.1","",notes="no explicit statement")
O(2001,"air6",AG,"H08N","SIO (report text)","ambiguous_as_printed",10,8,"Sec 4.1 text","Propagation from shooting last 3 sites (air6-air9, Table 1) to H08N was also blocked",
  notes="'last 3 sites' conflicts with the range air6-air9 (four sites); air7-air9 are covered under either reading, air6 only under the range reading. Supplementary: the clipped (not printed) part of the embedded Fig 22 raster carries an earlier caption stating white + marks a site whose signal was not seen at DGN; the white + plots at the air6 position.")
for a in ["air7","air8","air9"]:
    O(2001,a,AG,"H08N","SIO (report text)","not_detected",10,8,"Sec 4.1 text","Propagation from shooting last 3 sites (air6-air9, Table 1) to H08N was also blocked",notes="covered under both readings of the air6-air9/'last 3' wording")
O(2001,"air7",AG,"H08S","SIO (report figures)","detected",23,21,"Fig 23 DGS panel legend/curve","Curves show only frequencies where signal exceeded background noise levels by 3 dB",notes="air7 observed-TL curve present at DGS (H08S), ~5-80 Hz (figure-read)")
O(2001,"air8",AG,"H08S","SIO (report figures)","detected",23,21,"Fig 23 DGS panel legend/curve","Curves show only frequencies where signal exceeded background noise levels by 3 dB",notes="air8 (dotted) observed-TL curve present at DGS (H08S), ~5-78 Hz (figure-read). Only evidence of air8 reception anywhere.")
O(2001,"air9",AG,"H08S","SIO (report text/figures)","detected",10,8,"Sec 4.1 text; Fig 4c","The signal recorded at H08S is clearly visible at a whole-basin-scale source-receiver range of about 4825 km",rng="about 4825",band="40-60 Hz exceeds noise significantly; 5-10 Hz stacked narrow peak ~3 s after onset")
O(2001,"air9",AG,"H01","SIO (report text/figures)","detected",10,8,"Sec 4.1 text; Fig 4d","These were the only shots that were clearly visible in the VLF band at Cape Leeuwin, at a range of 1665 kilometers",rng="1665",band="significant energy 30-60 Hz")
O(2001,"air8",AG,"H01","SIO (report text)","not_detected",10,8,"Sec 4.1 text","It is not clear why these shots were not observed",
  notes="NEGATIVE CONTROL. Report: blockage of air8 not known to be significant; H01 noise during air8 similar to air9. Range to H01 not printed.")
O(2001,"air7",AG,"H01","SIO (report text/figures)","detected",10,8,"Sec 4.1 text; Fig 23 CL panel","some energy did propagate the full range",
  notes="weak: noisier period, west-dipping slope of Ninety East Ridge; air7 observed-TL curve in Fig 23 CL panel (~22-100 Hz). Note the text also says air9 shots were the only ones 'clearly visible in the VLF band' at Cape Leeuwin.")
for a in ["air1","air2","air3","air4","air5","air6"]:
    O(2001,a,AG,"H01","none","not_reported",10,8,"Sec 4.1","",notes="No per-site statement. Text gives only an a-priori expectation of Ninety East Ridge blockage and says air9 shots were the only ones clearly visible in the VLF band at Cape Leeuwin; neither is an explicit non-detection.")
# ---- 2001 cylinders ----
for r in T2:
    O(2001,r[3],"imploding_cylinder_MPL_SIO","all IMS stations (not individually named)","SIO (report text)","not_detected",12,10,"Sec 4.3 text (also Sec 1.4, pdf p5)","We were not able to detect any of the imploder shots in the IMS hydrophone data",notes="report: deployed at 7 stations, firing successful at five (Table 2 lists five)")
# ---- 2001 spheres ----
O(2001,"sph1","glass_sphere_single","H08N","SIO (report text/figures)","detected",11,9,"Fig 6 caption","single-glass-sphere implosion sph 1 (Table 3) recorded at H08N",rng="798 (to H08N01)",band="rises above noise above ~40 Hz")
O(2001,"sph2","glass_sphere_single","all IMS stations (not individually named)","SIO (report text)","not_detected",11,9,"Sec 4.2 text","a 320 m deep implosion (sph2) fired at the same location as a deeper shot (sph3) was not detected")
for s in ["sph3","sph4"]:
    O(2001,s,"glass_sphere_single","IMS station(s) not specified","SIO (report text)","detected",11,9,"Sec 4.2 text","Five of the six successful imploding glass sphere shots in 2001 (Tables 3, 4) were detected at IMS hydrophone stations",rng="single-sphere ranges 800-1200 km (as printed)",notes="station not named; the five detected are those other than sph2 ('All detected shots had source depth ~680 meters')")
O(2001,"sph6","glass_sphere_five_cluster","IMS station(s) not specified","SIO (report text)","detected",11,9,"Sec 4.2 text","Five of the six successful imploding glass sphere shots in 2001 (Tables 3, 4) were detected at IMS hydrophone stations",notes="station not named")
O(2001,"sph7","glass_sphere_five_cluster","H08S","SIO (report figures)","detected",11,9,"Fig 7 caption + DGS01-03 traces","Five-sphere signal (sph7) high pass filtered, cut at 40 Hz",rng="4396 (to H08S01)")
O(2001,"sph7","glass_sphere_five_cluster","H01","SIO (report figures)","detected",11,9,"Fig 7 caption + CL01-03 traces","Five-sphere signal (sph7) high pass filtered, cut at 40 Hz",rng="1465 (to H0101)")
print(len(obs))