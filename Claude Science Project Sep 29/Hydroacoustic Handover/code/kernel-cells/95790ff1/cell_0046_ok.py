SC=[
dict(source_class="airgun_array",campaign_year="2001",configuration="R/V Ewing array of 20 airguns, total volume 8465 cubic inches (0.139 m3)",
 source_level_as_printed="peak level 230-240 dB re 1 µPa (adjusted to 1 meter range)",band_as_printed="5~60 Hz (as printed, '5~60')",
 pulse_duration_as_printed="about 12 ms",source_depth_as_printed="9-12 m (Fig 22 model uses 12 m)",timing_accuracy_as_printed="shot trigger times generally accurate to a millisecond",
 position_accuracy_as_printed="about 10 m; ~50 m during last shooting period (loss of P-code GPS); GPS-to-array-centre offset corrected in Table I",
 received_character_as_printed="high SNR in 5-15 Hz for some near-source seafloor/along-path conditions; otherwise high SNR only in 30-60 Hz (pdf p6); stacking ineffective above 30 Hz (pdf p10)",
 detection_summary_as_printed="recorded at ranges up to and exceeding 4000 km (pdf p4)",source_page_pdf="9; 4; 6; 10",notes="shot intervals 57, 97, 127, 173 s (Table I)"),
dict(source_class="glass_sphere_single",campaign_year="2001, 2003",configuration="LLNL triggered implosion of a single 22-litre glass sphere (rupture-disk/piston/ram smashing system)",
 source_level_as_printed="maximum levels of 250-270 dB re 1 µPa, corrected back to 1 meter, in the 300-500 Hz range; level at other frequencies much reduced",band_as_printed="300-500 Hz (maximum)",
 pulse_duration_as_printed="about 6 ms at the source; received signal almost 400 ms longer than near-source pulse",source_depth_as_printed="~700 m nominal; 670-725 m in Tables 3 (sph2 at 320 m)",
 timing_accuracy_as_printed="not given",position_accuracy_as_printed="not given",received_character_as_printed="rises above noise for frequencies greater than about 40 Hz; recorded with good SNR above 40 Hz",
 detection_summary_as_printed="detection at ranges up to ~1000 km; 2001 single-sphere ranges 800-1200 km; 320 m shot sph2 not detected",source_page_pdf="5; 6; 11; 17",
 notes="bulk of acoustic energy out of the 2-100 Hz monitoring band at 700 m (pdf p17); modelled internal air pressure 1/6 atm matches peak pressure (pdf p7, p20)"),
dict(source_class="glass_sphere_five_cluster",campaign_year="2001, 2003",configuration="five 22-litre spheres held in a cluster; one sphere smashed, others fail sympathetically",
 source_level_as_printed="not given numerically",band_as_printed="bandwidth similar to single-sphere recordings",pulse_duration_as_printed="received envelope about 1 second; peak in front of envelope centre",
 source_depth_as_printed="680-731 m (Table 4)",timing_accuracy_as_printed="not given",position_accuracy_as_printed="not given",received_character_as_printed="poor repeatability (not axially symmetric); frame degradation after first few uses",
 detection_summary_as_printed="signals detected at full-basin ranges up to 4400 km",source_page_pdf="5; 7; 11",notes=""),
dict(source_class="imploding_cylinder_MPL_SIO",campaign_year="2001",configuration="MPL/SIO 20-litre cylinder opened mechanically by hydrostatic pressure on electrical command; lowered on .322 CTD cable",
 source_level_as_printed="arrival 3 amplitude consistently about 1 x 10^6 Pa re 1 m; level in 100-200 Hz band 5-10 dB lower than single glass sphere",band_as_printed="100-200 Hz (comparison band)",
 pulse_duration_as_printed="three arrivals; high-frequency signal precedes arrival 3 by 6 ms",source_depth_as_printed="1000-1315 m (Table 2)",timing_accuracy_as_printed="not given",position_accuracy_as_printed="not given",
 received_character_as_printed="too small to be detected above background at ranges of a few hundred km",detection_summary_as_printed="no imploder shot detected in IMS data; deployed at 7 stations, fired successfully at 5",source_page_pdf="5; 12",notes=""),
dict(source_class="SUS_explosive",campaign_year="2003",configuration="1.8 lb SUS (Signals Underwater Sound) charges; A11 charge size not given ('1.8 lb except A11')",
 source_level_as_printed="not given",band_as_printed="generally high SNR in 30-100 Hz at IMS; only A11 shot contained lower-frequency energy as well",pulse_duration_as_printed="not given (A11 at H04N arrival ~8 s)",
 source_depth_as_printed="610 m and 915 m (sus2 = 2000 ft, sus3 = 3000 ft, Fig 1 legend)",timing_accuracy_as_printed="origin time from near-source hydrophone (overwhelmed; only origin time obtained)",
 position_accuracy_as_printed="not given; source depth uncertainty 'documented by prior US Navy tests' (no number)",received_character_as_printed="SNR differences 610 vs 915 m not consistent; bubble-pulse frequency not consistently reflected",
 detection_summary_as_printed="almost all SUS shots that fired were detected at an IMS station; two did not trigger; two that fired (site A1) not detected",source_page_pdf="5; 6; 12; 8",notes="detection rule (SIO): SNR > 5 dB over a band spanning at least 15 Hz within 5-100 Hz (pdf p12-13)"),
dict(source_class="electro_acoustic_HX554",campaign_year="2003 (failed); 2004 test",configuration="Alliant-Tech HX-554 ATOC source s/n 002",
 source_level_as_printed="800 m: 75 Hz m-sequence and 65 Hz CW at 260 W (195 dB re 1 µPa at 1 m), PFM at 191.8 dB re 1 µPa at 1 m; 300 m: m-sequence 188 dB, CW 195 dB",band_as_printed="40-100 Hz (ATOC system)",
 pulse_duration_as_printed="not applicable",source_depth_as_printed="800 m and 300 m (May 2004 test)",timing_accuracy_as_printed="not given",position_accuracy_as_printed="not given",
 received_character_as_printed="not used at IMS: pressurisation failure during 2003 experiment",detection_summary_as_printed="no IMS data from this source",source_page_pdf="5; 14; 15",notes="included for completeness; not a calibration source for this module"),
]
pd.DataFrame(SC).to_csv("out/blackman_source_classes.csv",index=False)
# ---- transmission loss ----
TL=[]
def T(site,rcv,band,value,kind,where,page,printed,method,notes=""):
    TL.append(dict(source_site=site,receiver=rcv,band_hz=band,tl_value_or_range_db=value,value_type=kind,evidence_location=where,source_page_pdf=page,source_page_printed=printed,extraction_method=method,notes=notes))
FR="figure-read by eye from 600-dpi render of embedded raster (351x458 px); uncertainty about ±2 dB, ±2 Hz; curve identity from grayscale legend"
PX="pixel trace of darkest curve in embedded raster (threshold gray<120; axis calibrated from frame lines and tick-label centres); partial column coverage"
T("air9","H01 (CL)","13-94 (curve extent)","about 115-139","observed TL, median over shots; figure-read",  "Fig 23 CL panel",23,21,FR,"curve shows only frequencies where signal exceeded noise by 3 dB")
T("air9","H01 (CL)","10-60","about 116-134","observed TL; figure-read",  "Fig 23 CL panel",23,21,FR,"curve starts ~13 Hz; ~116 dB dip near 19 Hz; ~123-134 dB over 22-60 Hz")
T("air9","H01 (CL)","13.5-55.6 (pixel coverage)","116.0-133.2","observed TL; pixel-traced",  "Fig 23 CL panel",23,21,PX,"55-60 Hz not captured by tracer (curve rises to ~134 there by eye)")
T("air7","H01 (CL)","22-100 (curve extent)","about 123-140","observed TL; figure-read","Fig 23 CL panel",23,21,FR,"light-gray curve")
T("air9","H08S (DGS)","5-90 (curve extent)","about 120-140","observed TL; figure-read","Fig 23 DGS panel",23,21,FR,"")
T("air9","H08S (DGS)","5-60","about 120-136","observed TL; figure-read","Fig 23 DGS panel",23,21,FR,"")
T("air9","H08S (DGS)","5.6-51.4 (pixel coverage)","120.4-134.2","observed TL; pixel-traced","Fig 23 DGS panel",23,21,PX,"dark-pixel trace may include the dark dotted air8 curve; 51-60 Hz not captured")
T("air8","H08S (DGS)","5-78 (curve extent)","about 119-142","observed TL; figure-read","Fig 23 DGS panel",23,21,FR,"dotted curve")
T("air7","H08S (DGS)","5-80 (curve extent)","about 121-144","observed TL; figure-read","Fig 23 DGS panel",23,21,FR,"light-gray thick curve")
T("air1","H08N (DGN)","5-100 (curve extent)","about 125-142","observed TL; figure-read","Fig 23 DGN panel",23,21,FR,"black thin curve")
T("air5","H08N (DGN)","5-100 (curve extent)","about 119-147","observed TL; figure-read","Fig 23 DGN panel",23,21,FR,"lightest curve; ~120-130 dB below ~20 Hz")
T("air2; air3; air4","H08N (DGN)","about 5-17","about 125-140","observed TL; figure-read","Fig 23 DGN panel",23,21,FR,"air2-air4 curves present only at low frequency; individual curves not separable reliably at this resolution")
T("air4 vs air1-air3","H08N","5-8","'very similar'","qualitative statement","Fig 23 caption",23,21,"transcribed from text","")
T("air5 vs air2","H08N","not stated","'significantly lower for air5 shots than for air2 shots'","qualitative statement","Sec 4.7 text",23,21,"transcribed from text","both had good SNR")
T("air7 vs air9","not stated (DGS and CL both show air7 and air9)","20-90","'similar'","qualitative statement","Sec 4.7 text",23,21,"transcribed from text","when signal more than 3 dB above background")
T("air6-air9","H08N","8 (model)","'significant' estimated loss","modelled (elastic PE, 8 Hz)","Sec 4.7 text",23,21,"transcribed from text","")
T("air1-air3","H08S","8 (model)","'quite high' estimated loss (topographic blockage)","modelled (elastic PE, 8 Hz)","Sec 4.7 text",23,21,"transcribed from text","")
T("air1, air2","H08N","5-10 observed vs 8 model","relative modelled loss 'similar to what was observed'","model-vs-observation comparison","Sec 4.7 text",23,21,"transcribed from text","")
T("air3-air5","H08N","8","model 'several decibels greater' than observed","model-vs-observation comparison","Sec 4.7 text",23,21,"transcribed from text","attributed to rough seafloor along Central Indian Ridge not in bathymetry model")
T("all airgun sites (map)","H08N01","8 (model)","colour scale 100-250 dB re µPa/Hz (as printed)","modelled TL map; no per-site values printed","Fig 22",23,21,"not extracted","values per site are not printed; map not digitised")
T("brief §3 claim","H01","10-60","120-133 (brief)","CHECK","brief vs Fig 23",23,21,"comparison","Not printed in the report text. Figure-read air9 at CL gives ~116-134 dB over the plotted 13-60 Hz (no curve below ~13 Hz): consistent within ~±2 dB above ~22 Hz, but the ~116 dB dip near 19 Hz falls outside the brief's range. Cite as a figure-read approximation, not a reported value.")
T("brief §3 claim","H08S","5-60","122-135 (brief)","CHECK","brief vs Fig 23",23,21,"comparison","Not printed in the report text. Figure-read air9 at DGS gives ~120-136 dB over 5-60 Hz; consistent with the brief to within the ~±2 dB reading uncertainty. Cite as a figure-read approximation.")
pd.DataFrame(TL).to_csv("out/blackman_transmission_loss.csv",index=False); print(len(TL))