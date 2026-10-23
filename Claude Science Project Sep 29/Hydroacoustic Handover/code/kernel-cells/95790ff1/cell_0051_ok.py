jd=f"""JD144 10:54:57.77 LABEL CHECK — Blackman et al. (2004) UCRL-TR-207323, Appendix A Table 5
Checked 2026-10-08 against the rendered page image (pdf page 26 = printed page 24, 300 dpi, pypdfium2 {vers['pypdfium2']}).
Image crop: jd144_check_crop.png

WHAT IS PRINTED
  Table 5 row:  "2003 144 10:54:57.77   A3   30 52.227   56 19.046   915"
  The label "A3" is in the ORIGINAL PAGE IMAGE. It is not an error introduced by the
  text extraction (the text layer agrees with the image character for character).

VERDICT
  The correct site label is A4. "A3" is a typographical error in the printed report.
  The row is the A4 915 m SUS charge, which Appendix B calls A4sus3.

EVIDENCE (each item independent)
  1. Coordinates. The row's position (30°52.227'S 56°19.046'E) is 8 m from the A4
     five-sphere shot (Table 4: 30 52.227 / 56 19.051, JD144 10:23:11.56) and 368 km
     from the A3 single sphere (Table 3: 31 49.640 / 52 36.594, JD143 13:47:29.06).
  2. Time and kinematics. The row falls 1906.21 s (31.8 min) after the A4 five-sphere
     shot and 291.27 s before the A4 610 m SUS (10:59:49.04), all on JD144. To fire at
     A3 the ship would have needed about {spd:.0f} km/h out and back. A3 was
     occupied on JD143.
  3. Depth pairing. Every SUS site with two charges in Table 5 has one 915 m and one
     610 m shot (A1, A2, A5, A6, A7). With this row assigned to A4, A4 has the usual
     915/610 pair and A3 has no SUS at all.
  4. Appendix B, Figure B3 (pdf p28). The caption says the only A3 source was a
     single-sphere glass implosion at 690 m depth, and no A3 SUS panel exists.
  5. Appendix B, Figure B4 (pdf p29). The caption lists A4 as "a 1.8 lb SUS charge at
     610 m depth ... a 1.8 lb SUS charge at 915 m depth ... and a five-sphere glass
     implosion at 715 m depth". Panels A4sus2, A4sus3 and A4sph5 are printed.
  6. Appendix B relative timing. At each of H01, H08S and H08N the predicted arrival
     times give A4sus3 - A4sph5 = 1906 s and A4sus2 - A4sus3 = 291 s. These equal the
     Table 4/5 origin-time differences (1906.21 s, 291.27 s) to within the 1 s rounding,
     so LLNL computed A4sus3 from the A4 location. Tentative observed picks for A4sus3
     (H08S 5362? against 5365 predicted) and A4sus2 (H01 7190? against 7176; H08S 5650?
     against 5656) agree with A4-location predictions. A source at A3 would arrive about
     +195 to +205 s later. That travel-time shift is computed from approximate external
     station positions, not report values, so it is a sensitivity check only.
  7. Report text, Sec 4.4 (pdf p13): "The two SUS charges at site A4 were detected at
     Diego Garcia, North, in the SIO analysis". That implies two SUS at A4.

CAVEAT
  Item 6 shows only that LLNL treated the shot as an A4 event. The tentative "?" picks
  are weak evidence about the physical location. Items 1-5 and 7 rest on the printed
  tables, captions and text. The report says (pdf p4) that "a typographical error
  contained in the 2003 source listing in a previous paper (Blackman et al., 2003) has
  been corrected". This row shows that at least one label error is still in the 2004
  listing.

ACTION IN THE CSVs
  blackman_2003_events.csv keeps site_label_as_printed = A3. It sets
  site_label_corrected = A4, appendixB_event_id = A4sus3 and
  quality_flag = label_typo_in_original. The printed value is not overwritten.
"""
open("out/jd144_check.txt","w").write(jd)
# ---- discrepancy file vs Drive ----
dexp={
2:"agree (detected). Drive note 'All airgun sites west of DGN (air1-air5) visible' not found in UCRL-TR-207323; new row cites Fig 3 + Fig 23.",
3:"agree (Drive grade 'detected_clear' ~ report 'high SNR in the 5-10 Hz range').",
4:"agree (detected). New evidence is Fig 23 DGN curve + caption; Drive note wording not in UCRL.",
5:"agree (detected). New evidence Fig 23 caption 'air4 loss very similar to air1-air3'.",
6:"agree (Drive grade 'detected_clear' ~ 'high SNR in the 5-40 Hz band').",
7:"DISCREPANCY: Drive 'no_clear_signal' for air6 at H08N. Report wording 'last 3 sites (air6-air9)' is internally inconsistent, so new status = ambiguous_as_printed. 'Chagos Bank' is not named in UCRL (probably JASA 2004, not verified).",
8:"status agrees in substance (blocked/no signal). New status not_detected (stated 'blocked'). 'Chagos Bank' not in UCRL.",
9:"as row 8.",10:"as row 8.",
11:"agree (blocked/not detected). 'Chagos Bank' attribution not in UCRL.",12:"as row 11.",13:"as row 11.",14:"as row 11.",
15:"DISCREPANCY: Drive asserts air6 not_detected at H08S with a seafloor-coupling explanation. UCRL has no statement about air6 at H08S: new status = not_reported. Drive claim probably from JASA 2004 (closed access, not verified).",
16:"status agrees (detected). Drive grade 'detected_weak' and 'greater loss than air8-air9' are not stated in UCRL text; Fig 23 DGS shows air7 TL above air9 at most frequencies (figure-read).",
17:"agree (detected). UCRL evidence is only the air8 curve in Fig 23 DGS; Drive wording 'Reported among eastern sites with observed signals' not found in UCRL.",
18:"agree (detected, range 4825 km).",
19:"DISCREPANCY (attribution): Drive cites 'Saya de Malha Bank'; UCRL names the Ninety East Ridge for the expected H01 blockage. Both treat it as expectation, not detection status; new status = not_reported.",
20:"agree (detected weak). Drive band note '20-90 Hz' comes from a UCRL sentence that does not name the receiver.",
21:"agree (not detected; negative control).",
22:"agree (detected, 1665 km). Drive 'low-SNR stacked 5-10 Hz arrival' is an interpretation of Fig 4d, not a stated finding.",
23:"PARTIAL: UCRL names H08N for sph1 (Fig 6, 798 km); Drive leaves the subarray unspecified.",
24:"DISCREPANCY: Drive puts sph3 at Diego Garcia; UCRL says only 'detected at IMS hydrophone stations' (station unspecified).",
25:"DISCREPANCY: as row 24, for sph4.",
26:"DISCREPANCY (receiver): UCRL says sph2 'was not detected' with no station named; new receiver = all IMS stations (not individually named).",
27:"DISCREPANCY: Drive range 4168 km for sph6 at Diego Garcia is not in UCRL; UCRL names no station for sph6.",
28:"DISCREPANCY: Drive row sph6 at H01 (detected, 1960 km) has no support in UCRL. No matching new row.",
29:"DISCREPANCY: Drive range 4397 km; UCRL Fig 7 caption prints 4396 km, to H08S01 specifically.",
30:"agree (detected, 1465 km to H0101).",
31:"agree.",32:"agree.",33:"agree.",34:"agree.",35:"agree.",
36:"agree (SIO detected at H08N). New file also carries the LLNL ND rows for the same shots.",
37:"agree (which of the two 610 m A8 SUS is not specified in UCRL).",38:"as row 37.",
39:"agree (6140 km).",40:"agree (3577 km).",41:"agree (2595 km).",
42:"agree in substance; new file splits the disagreement into an LLNL detected row (App B H01 5918 s) and SIO / Australian not_detected rows."}
dd["discrepancy_assessment"]=dd.drive_row.map(dexp)
dd.to_csv("out/receiver_observations_diff_vs_drive.csv",index=False)
missing=sorted(set(ro.event_id)-set(dr.source_id.map(lambda s: srcmap.get(s,s))))
print(len(missing), missing[:40])