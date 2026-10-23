mkdir -p royer_figs
cp royer_pages/royer2016_p03.png royer_figs/royer2016-p03-fig1-network-map-table1.png
cp royer_pages/royer2016_p04.png royer_figs/royer2016-p04-fig2-H01W2-spectrogram-S1-S2.png
cp royer_pages/royer2016_p05.png royer_figs/royer2016-p05-fig3-candidate-locations-table2.png
cp royer_pages/royer2016_p08.png royer_figs/royer2016-p08-fig4-eventA-spectrograms-map.png
cp royer_pages/royer2016_p09.png royer_figs/royer2016-p09-fig5-eventB-spectrograms-map.png
cp royer_pages/royer2016_p10.png royer_figs/royer2016-p10-fig6-eventC1-spectrograms-map.png
cp royer_pages/royer2016_p11.png royer_figs/royer2016-p11-fig7-eventC2-spectrograms-map.png
cp royer_pages/royer2016_p12.png royer_figs/royer2016-p12-fig8-eventD2-spectrograms-map.png
cp royer_pages/royer2016_p13.png royer_figs/royer2016-p13-fig9-all-events-map-table3.png
cp royer_pages/royer2016_p16.png royer_figs/royer2016-p16-SWAMS3-spectrogram-0000-0200.png
cp royer_pages/royer2016_p17.png royer_figs/royer2016-p17-SSEIR-spectrogram-0000-0200.png
cp royer_pages/royer2016_p18.png royer_figs/royer2016-p18-H01W2-spectrogram-0000-0200.png
ls royer_figs | wc -l
cat > q5.md <<'EOF'
## Q5 follow-up: OHASISBIO network, the Royer (2016) figures, all located events, and Royer's location method

Sources for this section:
- **[Royer]** J.-Y. Royer, *Search for the flight MH370 impact site in the Indian Ocean from hydroacoustic data, March 8, 2014*, report LDO-201608, 22 Dec 2016, 18 pp. Saved as the artifact royer-2016-LDO-201608.pdf. Page numbers below are the printed numbers, which equal the PDF page numbers.
- **[MD197]** Royer (2014), OHASISBIO mission report MD197/VT135, doi 10.13155/114374, https://archimer.ifremer.fr/doc/01032/114374/. Printed page = PDF page − 2.
- **[SEANOE]** data-set descriptions 10.17882/46124 and 10.17882/51007.
- **[Archimer MD240]** final recovery report, doi 10.13155/114384.

I read the report figures from page renders at 150 dpi. Times read from figure labels are given to the second, as printed.

### Q5(a) What the OHASISBIO network is

**Short answer.** OHASISBIO (Observatoire HydroAcoustique de la SISmicité et de la BIOdiversité) is a multi-year passive-acoustic observatory in the southern Indian Ocean. It has two aims [MD197 p. 4]:
1. Record the low-magnitude seismic and volcanic activity of the three Indian Ocean spreading ridges (and intraplate deformation) that land networks miss. MD197 says land networks detect only magnitude > 4.0–4.5 in mid-ocean, while the hydrophones can locate magnitude > 2.5 events to 2–3 km over about 1,500 × 1,500 km.
2. Monitor large baleen whales acoustically: fin whale, Antarctic blue whale, and Madagascar, Australian and Sri Lankan pygmy blue whales.

The network followed a 2006–2007 test with three hydrophones (DEFLOHYDRO, Nov 2006–Jan 2008 [SEANOE]). It was installed in December 2009–January 2010 and redeployed every year from RV *Marion Dufresne* during the French Southern Territories supply voyages [MD197 pp. 4–5]. The final recovery was mission MD240 in Jan–Feb 2023 [Archimer MD240].

Each mooring, from top to bottom [MD197 p. 7]:
1. A syntactic-foam buoy (200 kg buoyancy, 250 kg in air) with flag and flasher. The instrument sits inside it: a titanium cylinder about 1.20 m long, 60 kg, with the sensor fixed to the buoy's steel cage.
2. About 1,000 m of Vectran line, then polyethylene (Pentex) sections. Their length is set so that the hydrophone sits in the SOFAR axis (500–1,200 m depth depending on site).
3. A galvanised chain, a swivel and an acoustic release, above a 400 kg anchor on the seafloor.

The instrument [MD197 p. 7]:
- Built by the laboratory itself.
- Samples at 240 Hz (useful band 0–120 Hz), 24-bit.
- Uses a Persistor CF2 controller and a GPS-synchronised clock with drift of about 10⁻⁷ s/s.
- Buffers 512 MB in RAM, written to a 160 GB disk every ~6.5 h (~22.7 GB per year).
- Runs on lithium batteries (7.2 V) for about 18 months. The acoustic release lasts 4–5 years.
- Records internally. Nothing is telemetered: data are recovered only when the mooring is released and hauled aboard, normally once a year.

In 2014 there were 8 hydrophones at 6 sites, with SWAMS as a triangle about 10 km on a side [Royer p. 2]. MD197 p. 4 describes triplets in general as "30 km" apart, which differs from the 10 km Royer gives for SWAMS in 2014. Hydrophone sensors are HTI units at −164 dB re 1 µPa/V [Royer p. 13]. Funding: cruises VT135 and VT141 by the French Polar Institute (IPEV), extra support from INSU-CNRS, and equipment from Région Bretagne (CPER ODO) and INSU-CNRS [Royer p. 7]. The operator was the Laboratoire Domaines Océaniques (CNRS / Université de Bretagne Occidentale, IUEM, Plouzané) [Royer p. 1], now UMR 6538 Geo-Ocean.

**Obtainable and how.**
- Mission reports for every year: **public download** (Archimer DOIs 10.13155/114372–114385).
- Instrument description (D'Eu, Royer & Perrot 2012, IEEE Oceans, Yeosu): **publisher** (IEEE Xplore).

### Q5(b) Figures in the Royer report

**Short answer.** Yes, the report contains raw-data plots, all of them spectrograms; there are **no waveform (time-series) plots**. It has 9 numbered figures and 3 unnumbered full-page spectrograms (pp. 16–18).
- Spectrogram parameters: Hann window 256 samples, 80% overlap, FFT length 256, at 240 Hz (OHASISBIO) or 250 Hz (H01W).
- Colour scale: 70–100 dB re 1 µPa²/Hz.
- Every event figure (Figs 4–8) pairs four spectrogram panels with a map. The map shows ray paths and the arrival-time label at each station used.
- **No H08S (Diego Garcia) spectrogram appears anywhere, and Table 5 has no H08S column.** H08S was examined but not used in any inversion: p. 6 says C1 is "indistinguishable from the seismic shots in the H08S data".

| Figure | Page | What it shows | Saved image |
|---|---|---|---|
| Fig. 1 | 3 | Bathymetric map of the 2014 OHASISBIO sites (open circles), IMS H08N/H08S/H01W (triangles), and the presumed MH370 impact polygon "after ATSB, 2014"; Table 1 below it | royer2016-p03-fig1-network-map-table1.png |
| Fig. 2 | 4 | H01W-2 spectrograms 00:15–01:00 and 01:00–01:45, 8 Mar 2014 (0–125 Hz); arrows mark S1 (Stead/LANL, ~00:52) and S2 (Curtin, ~01:34) | royer2016-p04-fig2-H01W2-spectrogram-S1-S2.png |
| Fig. 3 | 5 | Map of candidate solutions A, B, C1, C2, D2 with origin times (D1 not plotted); Table 2 below it | royer2016-p05-fig3-candidate-locations-table2.png |
| Fig. 4 | 8 | Event A (00:16:29): spectrograms MAD 01:03–01:06, H01W-2 00:51–00:54, WKER 00:41–00:44, SWAMS-3 00:36–00:39 (0–60 Hz), plus ray map; "Seismic shots are clearly visible on SWAMS-3" | royer2016-p08-fig4-eventA-spectrograms-map.png |
| Fig. 5 | 9 | Event B (00:21:30): MAD, SWAMS-2, SWAMS-3 picks marked "?" (uncertain); H01W-2 00:34–00:37 shows a ~30 s low-frequency (10–15 Hz) arrival; ray map | royer2016-p09-fig5-eventB-spectrograms-map.png |
| Fig. 6 | 10 | Event C1 (00:33:44, north of Diego Garcia): MAD, SSEIR, NCRO, H01W-2 01:33–01:36; SSEIR and NCRO dominated by periodic airgun shots; ray map | royer2016-p10-fig6-eventC1-spectrograms-map.png |
| Fig. 7 | 11 | Event C2 (00:57:32, west of the 90°E Ridge): H01W-2 01:33–01:36, SSEIR, SWAMS-3, NCRO (airgun shots dominate the last three); ray map | royer2016-p11-fig7-eventC2-spectrograms-map.png |
| Fig. 8 | 12 | Event D2 (01:06:05, east of the 90°E Ridge): H01W-2 01:29–01:32 (0–125 Hz), SSEIR, SWAMS-3, MAD; ray map to MAD, SSEIR, NCRO, H01W | royer2016-p12-fig8-eventD2-spectrograms-map.png |
| Fig. 9 | 13 | Map of all 20 located events 23:45–02:05; earthquakes (16, 20) brown, cryogenic (1, 3, 10, 17, 18, 19) blue; dashed lines join mutually exclusive solutions; Table 3 (sensitivities) above it | royer2016-p13-fig9-all-events-map-table3.png |
| (unnumbered) | 16 | SWAMS-3 full spectrogram 00:00–02:00, 8 Mar 2014, four 30-min rows, picked events arrowed | royer2016-p16-SWAMS3-spectrogram-0000-0200.png |
| (unnumbered) | 17 | SSEIR full spectrogram 00:00–02:00, arrows at the picks | royer2016-p17-SSEIR-spectrogram-0000-0200.png |
| (unnumbered) | 18 | H01W-2 full spectrogram 00:00–02:00 (250 Hz), arrows at the picks | royer2016-p18-H01W2-spectrogram-0000-0200.png |

Internal inconsistencies found while reading the figures (my observations, not stated by Royer):
1. **H01W times differ between the figure maps and Table 5.** In Figs 4–8 the H01W arrival labels are **14–19 s later** than the mean of the H01W1–3 picks in Table 5: +16.7 s (A), +18.8 s (B), +15.8 s (C1), +15.8 s (C2), +14.3 s (D2). The OHASISBIO labels agree with Table 5 within about 1 s at MAD, NCRO, WKER and SSEIR, and within about 5 s at SWAMS. The offset is close to the 16 s GPS–UTC difference that Royer applied to the OHASISBIO clocks (p. 2). Either the map labels or the H01W table entries may carry an extra 16 s shift. The report does not say which, so this is **unresolved**. As an illustration, 16 s at a SOFAR sound speed of about 1.48 km/s (my assumed typical value, not from the report) is about 24 km of range on the H01W path. That is larger than the formal standard errors (D2 σ_lat 0.047° ≈ 5 km).
2. **D2 (Fig. 8) does not match its table rows.** The map labels NCRO 01:49:48, but Table 5 row 15 gives 01:50:28.57 (−40.6 s). Fig. 8's spectrogram panels show SWAMS-3 (01:32–01:35), which is used in D1 and not in D2, and they omit NCRO, which D2 does use. The MAD panel's axis reads "01:45 … 01:58" while its ticks run 01:46–01:47, which looks like a typo for 01:48.
3. **Event 4 has two labels.** Fig. 9 labels it "4-E", but Tables 2, 4 and 5 call it "B".
4. **Royer's own 5 versus 6 count.** Royer's text says "5 acoustic events" and "These five solutions are summarized in Table 3" (p. 5). The solutions are actually in Table 2, which lists 6 rows (C1/C2 and D1/D2 are alternatives); Table 3 is the sensitivity table.

**Obtainable and how.**
- The report PDF and the page images listed above: **saved as artifacts** in this session; the original is a **public download** via Wise's Google Drive link.

### Q5(c) All located events in the report (Table 4, p. 14; arrival sets in Table 5, p. 15)

Notes on the columns:
- Errors are standard errors as printed.
- "Hydrophones" is Royer's count. "Sites" is my count of distinct sites, computed from Table 5, with the SWAMS and H01W triplets each counted as one site.
- Class is Royer's label: Table 4 type plus the Fig. 9 colour key. "Unexplained" means "Uncertain", "Unc." or (for B) untyped.
- Royer locates **no airgun event**. The airgun shots (a survey in the Bay of Bengal off Myanmar, shots 10 s apart, p. 4) are treated only as noise.
- Mutually exclusive sets (Table 5 note): {2, 8, 9}, {5, 6, 12, 13}, {14, 15}, {7, 11, 12, 13}.
- Royer shades events 2, 5, 8, 10, 13 and 19 for high origin-time error, which "question the reliability of the solution".

| # | Royer label | Class (per Royer) | Origin time UTC | Lat | Lon | σ lat (°) | σ lon (°) | σ time (s) | Hydrophones | Sites | Sites used |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Icequake | cryogenic | 23:47:46.2 (7 Mar) | −55.400 | 88.173 | 0.219 | 0.036 | 11.348 | 7 | 3 | MAD, SWAMS, H01W |
| 2 | Uncertain | unexplained; high σt | 00:13:09.3 | −64.510 | 127.048 | 1.619 | 4.504 | 99.999 | 6 | 2 | SWAMS, H01W |
| 3 | A icequake | cryogenic (iceberg) | 00:16:29.4 | −57.300 | 88.965 | 0.060 | 0.025 | 3.221 | 8 | 4 | MAD, WKER, SWAMS, H01W |
| 4 | B | unexplained ("very tentative") | 00:21:30.6 | −35.224 | 99.922 | 0.076 | 0.022 | 1.533 | 7 | 3 | MAD, SWAMS, H01W |
| 5 | Uncertain | unexplained; high σt | 00:28:51.5 | −49.755 | 133.114 | 0.213 | 1.354 | 61.139 | 7 | 3 | MAD, SWAMS, H01W |
| 6 | Uncertain | unexplained | 00:32:49.2 | −66.090 | 127.043 | 0.018 | 0.041 | 0.334 | 6 | 2 | SWAMS, H01W |
| 7 | C1 Unc. | unexplained (= Curtin solution) | 00:33:43.5 | −3.445 | 74.087 | 0.117 | 0.025 | 7.447 | 6 | 4 | MAD, NCRO, SSEIR, H01W |
| 8 | Uncertain | unexplained; high σt | 00:36:21.8 | −60.844 | 78.097 | 0.216 | 0.202 | 15.099 | 7 | 3 | SSEIR, SWAMS, H01W |
| 9 | Uncertain | unexplained | 00:37:52.4 | −48.671 | 97.477 | 0.045 | 0.023 | 1.583 | 8 | 4 | MAD, WKER, SWAMS, H01W |
| 10 | Icequake | cryogenic; high σt | 00:56:45.5 | −57.967 | 92.050 | 0.394 | 0.035 | 21.666 | 7 | 3 | MAD, SWAMS, H01W |
| 11 | C2 Unc. | unexplained (favoured over C1) | 00:57:32.4 | −26.469 | 80.952 | 0.038 | 0.015 | 2.075 | 8 | 4 | NCRO, SSEIR, SWAMS, H01W |
| 12 | C3 Unc. | unexplained | 00:57:33.5 | −26.539 | 80.979 | 0.127 | 0.050 | 6.929 | 8 | 4 | NCRO, SSEIR, SWAMS, H01W |
| 13 | C4 Unc. | unexplained; high σt (discarded, p. 6) | 00:59:55.3 | −55.719 | 87.615 | 0.866 | 0.195 | 46.771 | 7 | 3 | SSEIR, SWAMS, H01W |
| 14 | D1 Unc. | unexplained | 01:04:39.1 | −25.404 | 93.567 | 0.071 | 0.014 | 3.448 | 7 | 3 | SSEIR, SWAMS, H01W |
| 15 | D2 Unc. | unexplained (favoured over D1) | 01:06:05.4 | −27.856 | 93.460 | 0.047 | 0.007 | 1.439 | 6 | 4 | MAD, NCRO, SSEIR, H01W |
| 16 | Earthquake | earthquake | 01:15:48.0 | −8.052 | 107.622 | 0.067 | 0.024 | 4.706 | 9 | 5 | MAD, NCRO, SSEIR, SWAMS, H01W |
| 17 | Icequake | cryogenic | 01:37:39.5 | −57.950 | 95.354 | 0.062 | 0.028 | 3.468 | 8 | 4 | NCRO, SSEIR, SWAMS, H01W |
| 18 | Icequake | cryogenic | 01:49:33.0 | −52.635 | 80.389 | 0.193 | 0.121 | 10.832 | 8 | 4 | MAD, SSEIR, SWAMS, H01W |
| 19 | Icequake | cryogenic; high σt | 01:58:14.2 | −51.322 | 117.339 | 0.381 | 0.713 | 33.969 | 7 | 3 | MAD, SWAMS, H01W |
| 20 | Earthquake | earthquake | 02:02:31.7 | −27.149 | 67.307 | 0.062 | 0.050 | 3.426 | 6 | 4 | MAD, NCRO, SSEIR, SWAMS |

Further notes:
- WKER is used only for events 3 and 9. H08S is used for none.
- **Events 2 and 6 use only 2 distinct sites** (the SWAMS and H01W triplets). With 4 unknowns (lat, lon, origin time, plus the effective sound speed fixed by the model), these solutions rest on within-triplet time differences. They are effectively bearing-limited, which is consistent with the very large errors of event 2.
- The per-hydrophone arrival times for all 20 events are in Table 5 (p. 15). They are kept as the machine-readable file royer_table5.json in the work folder.

**Obtainable and how.**
- Event list and arrival times: **in the public report** (Tables 4–5).
- Waveforms behind them: **request from the author** (OHASISBIO) and from the **CTBTO** (H01W).

### Q5(d) How Royer locates events

**Short answer.**
- **Method.** Royer picks event arrival times by hand on spectrograms at each hydrophone. He associates arrivals across sites by signal resemblance, starting from events seen on H01W (Stead's S1 at ~00:52, Curtin's S2 at ~01:34, and others at 00:36 and 01:30). He then "inverts (i.e. triangulates)" the arrival times with the PMEL "Seas" software (Fox et al. 2001) [Royer p. 4].
- **Cross-correlation not used.** The inter-site distances (hundreds to thousands of km) make the cross-correlation used on IMS triplets "inapplicable" [p. 4].
- **Solver.** The report does not describe the solver. In the literature the PMEL/Seas method is an iterative non-linear least-squares fit (Marquardt), solving for latitude, longitude and origin time from arrival times of peak energy, with travel times from the GDEM sound-speed climatology (Fox et al. 2001 as described in secondary sources). This is [secondary; not stated in the report].
- **Sound speed.** The sound-speed model and its value are **NOT stated in the report: NOT FOUND**.
- **Errors.** The output gives formal standard errors in latitude, longitude and origin time (Tables 2 and 4). No picking-error value, no a-priori sound-speed error and no Monte Carlo error estimate are given: **NOT FOUND**.
- **Clock corrections** [p. 2]:
  - Each OHASISBIO instrument is GPS-synchronised a few hours before deployment and after recovery.
  - The drift (about 10⁻⁷) is interpolated linearly to each file's time stamp.
  - Time stamps are converted from GPS time to UTC by subtracting 16 s (GPS − UTC in 2014).
  - Drift could not be determined for MAD and SWAMS-1 because their batteries failed before recovery. Their time stamps are therefore uncorrected for drift, an unquantified error.
  - Files were converted to CSS format in UTC.
- **Minimum stations.** No minimum is stated. In practice every located event uses 6–9 hydrophones but only 2–5 distinct sites (computed above). Royer notes that the SWAMS (10 km) and H01W (2 km) triplets "give confidence in the picked events but will not add much constraint" [p. 4, Table 2 note].
- **Limitations Royer states:**
  1. Event association is non-unique, giving mutually exclusive solutions (C1–C4, D1/D2) [pp. 2, 5–6, 15].
  2. Picks are "very faint and often hardly distinguishable from the background acoustic noise" [p. 2].
  3. Records west of 90°E are obscured by airgun shots from a Bay of Bengal survey; H01W is shielded from them [p. 4].
  4. NEAMS, the hydrophone closest to the presumed impact area, was lost [pp. 2, 6].
  5. The triplets add little constraint [p. 4].
  6. Some paths may be acoustically shaded: Chagos Bank for H08S and C1; Broken Ridge for SSEIR/WKER and D2 [p. 6].
  7. Signal shapes differ between stations for D2 [p. 6].
  8. C2 lies off the H01W triplet's measured azimuth [p. 6].
  9. Solutions with large origin-time errors are unreliable [p. 14].
  10. C2 and D2 lie in seismically active areas [p. 6].
  11. "even if correct, we cannot tell whether these acoustic events are related to the disappearance of flight MH370" [pp. 2, 6].

**Obtainable and how.**
- Fox, Matsumoto & Lau (2001), *J. Geophys. Res.* 106, 4183–4206 (method reference): **publisher** (AGU/Wiley).
- The Seas software and the sound-speed grid Royer used: **request from the author** or NOAA-PMEL.
EOF
python - <<'EOF'
p='research-radar-infrasound-ohasisbio.md'; md=open(p).read(); q5=open('q5.md').read()
anchor='\n---\n\n## Sources'
assert md.count(anchor)==1
md=md.replace(anchor,'\n---\n\n'+q5+anchor)
add='''- **Royer 2016 report PDF and page images (Q5):** saved as artifacts in this project (royer-2016-LDO-201608.pdf and twelve royer2016-pNN-*.png figure pages).
- **Seas location software / sound-speed grid used by Royer:** request from the author or NOAA-PMEL.
'''
md=md.rstrip('\n')+'\n'+add
md=md.replace('- The Q3 energy comparison','- Q5: Royer figures were read from 150 dpi renders. The H01W timing inconsistency between the figure maps and Table 5 is my observation and is unresolved. The sound-speed model is not stated in the report.\n- The Q3 energy comparison')
open(p,'w').write(md); print(len(md.split()))
EOF
grep -n "^## \|^### Q5" research-radar-infrasound-ohasisbio.md