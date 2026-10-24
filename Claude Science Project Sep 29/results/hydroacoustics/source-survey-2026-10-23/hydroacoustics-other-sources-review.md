# Non-impact underwater sound sources at H01W, H08S/H08N and the IMOS loggers, and how they differ from an impact signal

Review note, hydroacoustics module. Written 23 Oct 2026. Track: other (non-impact) sources.
Companion table: [other-source-characteristics.csv]({{artifact:46f64144-9ba1-4d9a-8f95-dab690399fae}}) (41 rows, one per source class or sub-type; each number carries its source and a primary / second-hand flag).

## Declared deviations and limits

1. **Full texts read:** Samaran et al. 2013, Leroy et al. 2021, Matsumoto et al. 2014, Royer 2016 (LDO-201608, held), Duncan et al. 2014 CMST 2014-30 (held), Brown et al. 2026 (held) and Raumer et al. 2026 (arXiv). All other values come from abstracts, publisher pages or search-engine extracts of the paper text. The table marks each of these in `read_in_primary`.
2. **Not retrieved this session (ask Pete if a copy is wanted):** the full texts of Royer et al. 2015 GJI 202:748 and Chapp et al. 2005 G-cubed (their DOI routes returned HTTP 403); Erbe et al. 2015 (CC BY, but no PDF route worked); Okal 2008; Hanson & Bowman 2005/2006; Li & Gavrilov 2006/2008 (conference papers); Talandier et al. 2002/2006; MacAyeal et al. 2008; Sousa & Harris 2015; Stafford et al. 2011; Gavrilov & McCauley 2013; McKenna et al. 2012; Hanson et al. 2001; Fauvel et al. 2026 (JASA 160:2370, IMS source catalogue).
3. **Where I looked before writing 'not retrieved':** the repo papers folder (ISO Sept 28 Status/inputs/papers/hydroacoustics), the artifact store (title and DOI-fragment searches: whale, iceberg, royer, gavrilov, okal, matsumoto, talandier, hanson, T-phase, airgun, 10.1121, 10.1029, 10.1093, soundscape, bolide, seism), Google Drive (30 title terms and 9 full-text terms) and ~/Downloads (file-name search to depth 3). Only Royer 2016, CMST 2014 and Brown 2026 are held among the sources for this track.
4. **Cut from scope:** there are no source-level values for several sub-types (Sri Lankan, Madagascan and Chagos songs, Omura's, Bryde's, sonar, drilling, surf, lightning). I found no primary value this session, so those cells say 'not retrieved this session'. I did not invent values.
5. **Provisional numbers:** the predicted T-phase arrival times for the ISC/IDC-catalogued earthquakes use a straight great-circle path at 1.48 km/s. They include no blockage, no conversion-point offset and no bearing check. Treat them as provisional (file tphase_arrivals_catalogue.csv in my workspace; not saved as an artifact).
6. **No new waveform analysis.** I did not process any recording. 'Likely present on 8 Mar 2014' calls rest on published seasonality and on the held CMST and Royer reports. They are not detections.

## 1. Main findings

1. **The 8 March 2014 arrival windows already hold documented non-impact transients.** Royer 2016 (Table 4) locates 20 events between 23:45 (7 Mar) and 02:05 UTC (8 Mar) with OHASISBIO plus H01W. Six are icequakes (51-58 S, 80-117 E), two are earthquakes, and twelve are 'uncertain'. Royer states that the association is not unique.
2. **H01W has about twelve distinct arrivals from these located events inside its window (00:25-02:20 UTC).** This is my count from Royer Table 5 (H01W1 column). Four are icequakes (00:51:43, 01:31:04, 02:10:34, 02:18:53), one is the Java earthquake (01:50:01), and the rest are 'uncertain'. That is roughly six located transients per hour, before any weaker detections. This is the realistic false-alarm background for an H01W impact search.
3. **At H01W, most automatic detections came from the Antarctic sector.** CMST 2014 (s.3.3, Fig. 5) gives 158-209 deg for most detections between 00:10 and 08:00 UTC and calls the majority 'likely to be ice cracking events'. The 01:34:50 arrival was the only northerly one; Curtin later placed it near the Chagos-Laccadive Ridge (Royer 2016 p.4). LANL (Stead 2014, via Royer) gave about N190 and an ice-related signature for the 00:52 event S1.
4. **H08S was dominated by two airgun surveys on 8 March 2014.** CMST Table 4 gives a constant 34.9-35.4 deg bearing for 0-3 h (Sri Lanka or Bay of Bengal; Royer places it off Myanmar) and 113.0-113.6 deg for 0-2.14 h (TGS Huzzas 3D, NW Australia). Shots were about 10 s apart (Royer 2016; the project H08S shot table gives 9.98 s). H01W is shadowed from the Bay of Bengal survey (Royer 2016).
5. **Catalogued earthquakes in or near the windows:** ISC mb 4.04 south of Java at 23:52:17 (predicted H01W about 00:24, H08S about 00:36; provisional); IDC mb 3.7 Mauritius-Reunion region at 23:07:54; Royer event 16 (Java, 01:15:48), which matches the CMST 'small earthquake in the Java Trench' at H08S 01:59-02:00 (my 1.48 km/s prediction: 01:59); and Royer event 20 (02:02:32, 27.15 S 67.31 E). The Banda Sea, Talaud and Halmahera events in the ISC list are probably blocked by the Indonesian archipelago (not checked).
6. **The biological sources most likely present in March are the tonal baleen whale songs.** The SE Indian Ocean (Australian) pygmy blue whale is present at Cape Leeuwin from December to June. At Perth Canyon it peaks from March to June. The Sri Lankan type is present at Diego Garcia (DGN mostly March-June). The Chagos song is in its low season at Diego Garcia but peaks in March at the IMOS Kimberley site. Bryde's whale calls dominate the 3250 records (CMST 2014). Fin whales, humpbacks and minke bio-duck are out of season at the Australian sites in early March.
7. **IMOS logger 3250 ('Scott Reef') is at 15 deg 29.0' S 121 deg 15.1' E in 216 m of water** (held metadata file). That is the same position as Leroy et al. 2021's 'Kimberley' site, where Chagos songs peaked in March 2012 and the Australian Omura's whale song was recorded in March 2013. Expect both, plus Bryde's whale calls, in the 3250 records.
8. **Early March is the seasonal maximum of iceberg-related noise.** Matsumoto et al. 2014 (p.5) find maximum daily noise levels in March at the EEP-NW hydrophone. They cite a seasonal range of about 7 dB at 8-16 Hz in the southern Indian Ocean (Hanson & Bowman 2006, second-hand). Cryogenic transients are therefore the main natural false-alarm class at H01W on 8 March.
9. **No bolide on 7-8 March 2014 is in the CNEOS fireball list.** The only March 1-15 entry is on 3 March at 29 S 94.9 W (Pacific). Brown 2026 reports no confirmed hydroacoustic fireball detection in 30 cases.
10. **New lead (open data):** EarthScope FDSN dataselect serves IMS hydrophone waveforms without login for some dates. I tested 20 s requests: H01W1 on 8 March 2015 and 2017 and H08S1 on 8 March 2015-2018 returned data (HTTP 200). All 2014 dates I tried (7, 8, 9 and 15 March) returned 'no data' (HTTP 204) at H01W1, H08S1 and H08N1. The 8 March 2014 records therefore stay request-only (CTBTO vDEC). The open March records from other years can still give a same-season background and false-alarm rate for these source classes without any request.

## 2. Station bands and local time in the arrival windows

- IMS H01W1, H08S1, H08N1: 250 Hz sampling, sensor '1 to 100 Hz' (FDSN station service, queried this session). Hydrophone elevations are -1,063 m (H01W1), -1,413 m (H08S1) and -1,248 m (H08N1).
- IMOS loggers: 6 kHz sampling and an 8 Hz analogue high-pass (project value). Sources whose energy lies mainly below 8 Hz (iceberg tremor fundamentals of 4-10 Hz, T-phase energy of 1-5 Hz) are attenuated at the IMOS loggers.
- Local mean solar time in the windows (computed from longitude): H01W 00:25-02:20 UTC is 08:01-09:56; H08S 00:45-02:50 UTC is 05:34-07:39; Perth Canyon about 08:20-08:50; 3250 about 09:00-09:30. All windows are morning. Evening fish choruses (Perth Canyon 1.8-2.5 kHz; Kimberley about 0.7 kHz) are therefore weak or absent, and they lie above 125 Hz anyway. Antarctic blue whale Z-calls are more frequent by day (Leroy 2016).

## 3. Source classes (summary; values in the table)

**Biological.** The baleen whale songs are tonal or pulsed-tonal. Their units last several seconds to tens of seconds. They repeat at fixed intervals: about 200 s for the Australian pygmy blue whale, 70-80 s for the Sri Lankan type, 90-100 s for the Madagascan type, 191 s for the Chagos song, 40-50 s for the Antarctic Z-call and 7-26 s for the fin whale 20 Hz pulse. Source levels near 189 dB re 1 uPa @ 1 m are measured for Antarctic blue and fin whales (Sirovic et al. 2007). The fin whale 1 s pulse train is the only whale sound whose period approaches the 10 s airgun period; Royer's 10 s train near 00:45-00:48 on SSEIR and SWAMS3 was matched to airguns, not to fin whales (project exploratory result). Sperm whale clicks, fish choruses and snapping shrimp put little energy below 125 Hz. They matter only for the 6 kHz IMOS records.

**Cryogenic.** Two types are known from H01 and H08: variable harmonic tremor (4-10 Hz fundamental, up to 10 harmonics, packets up to about 30 min, received up to 142 dB p-p at Cape Leeuwin; Chapp 2005) and cusped pulse tremor (25-90 s pulses). Open-sea iceberg break-up gives broadband bursts lasting tens of seconds to about 20 min (Matsumoto 2014, citing Dziak 2013). At H01 these sources lie at 158-209 deg (CMST 2014), and the six tremors in Li et al. 2008 were at 160-200 deg. Sea-ice sources are weakest in early March (sea-ice minimum).

**Geophysical.** T-phases from the SEIR, CIR, SWIR and the Sunda trench are emergent, 'cigar'-shaped trains lasting tens of seconds to minutes, with dominant energy at 1-5 Hz. Hanson & Bowman 2005 located 4,725 events with H01 plus H08 in about 276 days of 2003 (about 17 per day). Shallow volcanic or hotspot events can have impulsive onsets and short durations like explosion T-phases (Tepp et al. 2021). They are the geophysical class nearest to an impact in shape. Microseisms (below 1 Hz) and tsunami signals (mHz) lie below the band.

**Anthropogenic.** Airgun surveys are the dominant false-alarm class at H08S on 8 March 2014. Airgun source levels are 200-260 dB zero-to-peak, with most energy at 10-100 Hz. Shots come at about 10 s intervals for hours, from a constant or slowly drifting bearing, and are recorded up to about 4,000 km from the vessel (Nieukirk 2012). Shipping (177-188 dB broadband; McKenna 2012) is continuous and tonal and changes slowly. Explosions have bubble-pulse modulation, which a surface impact does not have.

**Environmental.** Wind, rain and surf set the noise floor; they are not transients in the 1-125 Hz band. Lightning is rare in the open ocean. No bolide is listed for the date.

## 4. Example libraries and annotated datasets

- IWC-SORP/SOOS Acoustic Trends Annotated Library (Miller et al. 2021, Sci Rep 11:806; AADC doi 10.26179/5e6056035c01b): Antarctic blue and fin whale annotations, WAV at 250-2,000 Hz, 2005-2017 site-years including the Indian sector. Free.
- Watkins Marine Mammal Sound Database (WHOI; Sayigh et al. 2016, POMA 27:040013): more than 60 species, about 15,000 annotated clips; few or no Indian Ocean low-frequency items (not checked).
- DCLDE 2015 low-frequency set: blue whale D-calls and fin whale 40 Hz calls (California sites).
- Australian fish chorus catalogue 2005-2023 (Front Remote Sens 2024).
- IMOS AODN passive acoustic archive: raw Perth Canyon, Portland and Kimberley records (the project holds the 2014 MH370 set).
- EarthScope FDSN (net IM): open IMS waveforms for some dates (see finding 10).
- Leroy et al. 2021 (Sci Rep, open): spectrograms and waveforms of the Chagos, Sri Lankan, Madagascan and Australian pygmy blue whale songs and of four Omura's whale song types, including DGN H08N1 and IMOS Perth Canyon and Kimberley examples.
- CMST 2014 Fig. 5 and Royer 2016 Figs 2-9 (held): annotated 8 March 2014 bearings, spectrograms and located events.
- Not found as a public annotated library: Indian Ocean iceberg tremor, T-phase and airgun examples at IMS stations. These are request-only (CTBTO vDEC; OHASISBIO via Royer).

## 5. Published discrimination methods and IDC categories

- **IDC phase categories.** The IDC automatic system classifies each hydroacoustic detection as **H** (in-water source), **T** (seismically generated, converted at the seabed) or **N** (noise) (Hanson et al. 2001, as cited in a later paper; CTBTO SnT presentation by Nielsen, Le Bras et al., year not checked). Only H phases help to define events; T phases do not. Rule changes reduced the number of T phases wrongly called H. Analysts use duration, spectral content and spectral scalloping (the bubble pulse) to tell H from T (Global Detection Capabilities of T Phases, SRL 2025). The Reviewed Event Bulletin (REB) keeps events with three or more primary stations and event weight of 4.6 or more. Screening then goes into the Standard Event Bulletin (SEB) and the Standard Screened Event Bulletin (SSEB). That screening identifies 'natural or non-nuclear man-made' events; it does not classify whales, ice or ships.
- **Cepstral / bubble-pulse detection.** IDC detection and feature extraction includes cepstral analysis for bubble pulses (LDEO SRR 2006 paper). Explosions give positive cepstral peaks from the bubble and negative peaks from the surface reflection; earthquakes have no bubble peak.
- **Duration-amplitude discriminant.** Talandier & Okal 2001: log10 eMax = 4.9 log10 tau1/3 - 4.1 separates earthquakes (D < 0) from explosions (D > 0) for T-phase stations. All 77 documented underwater explosions had D > 0; hotspot earthquakes near steep slopes can also give D > 0 (Talandier & Okal 2004 abstract).
- **Spectral fall-off and dispersion.** Earthquake T-phases have a steeper power-law spectral fall-off; explosions show dispersion at the lowest SOFAR frequencies (Talandier & Okal 2004, 2016). Iceberg signals are separated by harmonic structure, frequency gliding and southern bearings; Li & Gavrilov 2008 use frequency dispersion for single-station ranging of ice events.
- **Machine learning.** An IDC-built reference set of 778 reviewed samples supports ML signal classification (cited in a later paper; search extract only). Fauvel et al. 2026 (JASA 160:2370) build an IMS-wide source catalogue for discrimination by source type (abstract only). Raumer et al. 2026 (arXiv:2607.07733) cluster self-supervised embeddings of OHASISBIO, MAHY and CTBTO data into source classes. An earthquake ML study used H01, H08 and H11 (Sci Rep 2021, s41598-021-02483-w).
- **What this means for an impact.** An impact is an in-water source, so the IDC would class it as H, not T. It has no gas bubble pulse unless a cavity collapses later. It is a single event, not a periodic train, and its bearing points to the 7th arc. No published discriminant was built for aircraft impacts; the explosion discriminants are the nearest analogue.

## 6. Comparison matrix: impact versus each source class

The impact column states the expected form. It is not a measured value. Source duration comes from the end-of-flight module (tau90) and is not re-derived here. 'Bearing' is the behaviour seen by a triplet (H01W, H08S).

| Class | Duration | Band (1-125 Hz view) | Envelope | Repetition | Bearing |
|---|---|---|---|---|---|
| **Surface impact (expected)** | short source (about 1 s scale); arrival spread by SOFAR dispersion to tens of seconds at 1,000+ km (not quantified here) | broadband, few Hz to >100 Hz at source | impulsive onset, no harmonics | single; later implosions over minutes to tens of minutes and a seabed strike | fixed, toward the 7th arc 20-40 S |
| Baleen whale song (blue, Omura's, Bryde's) | units 3-50 s; songs 16-85 s | narrow tonal lines 17-108 Hz | emergent, tonal or pulsed-tonal | strict: 40-50, 70-80, 90-100, about 190-200 s | local (<~200 km), slow drift |
| Fin whale 20 Hz pulse | about 1 s | 15-28 Hz (+ about 99 Hz) | short downsweep | 7-26 s, hours | local or southern, slow drift |
| Odontocetes, fish, shrimp | ms clicks; hours-long choruses | mostly >125 Hz | impulsive clicks / diffuse | about 1 s clicks; nightly | local |
| Iceberg tremor (VHT/CPT) | minutes to 30 min packets; 25-90 s pulses | 4-10 Hz fundamental + harmonics | emergent, gliding harmonics | clustered, hours-days; CPT near-periodic | Antarctic sector (H01: 158-209 deg) |
| Iceberg break-up / icequake | tens of s to about 20 min | broadband, strongest <40 Hz at range | impulsive-to-emergent burst | swarms | Antarctic sector; located 51-58 S |
| Tectonic T-phase | tens of s to minutes | 1-40 Hz, peak 1-5 Hz, steep fall-off | emergent 'cigar' | Poisson, aftershock clusters | ridge or trench bearing |
| Volcanic / hotspot event | short | wider band | impulsive | swarms | fixed (St Paul/Amsterdam etc.) |
| Airgun survey | ms at source; seconds at range | 10-100 Hz | sharp onset | about 10 s for hours | constant or slowly drifting (35 and 113 deg at H08S) |
| Shipping | hours | 10-200 Hz, tonal lines | stationary, slow rise/fall | continuous | slow drift with track |
| Explosion | short | broadband | impulsive with bubble pulses | single or series | fixed |
| Bolide | short | 2-10 Hz (modelled) | impulsive | single | fixed |
| Wind, rain, surf, microseism | continuous | floor; rain >2 kHz; microseism <1 Hz | stationary | none | diffuse |

## 7. Source classes most likely to cause false alarms in the 8 March 2014 windows

1. **H01W (00:25-02:20 UTC):** (a) iceberg break-up and icequakes from the Antarctic sector. Royer located four in the window and CMST describes most detections as ice. (b) T-phases from the Sunda/Java trench (Royer event 16 at 01:50; ISC 23:52 event near the window start, provisional) and from the SEIR. (c) Royer's twelve 'uncertain' events, whose bearings and locations are not unique; some lie near the Ninety East Ridge at 25-28 S, inside the arc corridor. (d) SE Indian Ocean pygmy blue whale song (in season; tonal, so easy to reject by shape). (e) Antarctic blue whale Z-calls in low numbers.
2. **H08S (00:45-02:50 UTC):** (a) the two airgun trains at 35 deg and 113 deg. These overlap the whole window, and an impact arrival that coincides with a shot must be tested by interference or residual, not excluded (project rule). (b) Java trench T-phase at 01:59-02:00 (92.5-93.5 deg) and the Rodrigues-area earthquake (Royer event 20; predicted H08S about 02:27, provisional). (c) the unknown 168 deg arrival at 00:11-00:12 (CMST: 'possibly ice cracking noise or a small seismic event'), which is before the window. (d) Sri Lankan pygmy blue whale song, Omura's croak and low-season Chagos song.
3. **H08N:** blocked from the arc (project result), so false alarms there carry no impact information.
4. **IMOS Perth Canyon 3315/3376:** pygmy blue whale song (peak season); ships at 8-100 Hz; T-phases and ice (below and near the 8 Hz corner); the CMST/Royer 01:34 arrival (located near the Chagos-Laccadive Ridge).
5. **IMOS 3250:** Bryde's whale calls at 25-50 Hz (dominant, CMST 2014); Chagos song (peak in March at this site); Omura's whale song; possible NW Shelf airgun or industrial noise; the unexplained 8-9 s periodicity found in an earlier project check (source not identified).
6. **IMOS Portland 3274/3275:** blocked from the northern arc (project result); shipping and local biology are the main transients (not assessed here).

## 8. What the module can do with this (plain-language proposals; no compute run)

- Use Royer's 20 located events and the catalogued earthquakes as a labelled set of real arrivals for the false-alarm model at H01W and for the real-arrival test. The project has proposed this before; it needs no new data.
- Add a 'source-class veto feature' to each candidate: bearing sector (south of about 150 deg at H01W is ice), periodicity (about 10 s = airgun; 40-200 s = whale song), harmonic structure, duration and the Talandier-Okal D. Record each feature as a label, not as an exclusion.
- Measure the same-season false-alarm rate on the open IMS March records from 2015-2018 (EarthScope). This needs no request. Pete should rule on it before any compute runs.

## 9. Key references (DOIs or URLs only where seen in a retrieved record)

- Samaran F. et al. 2013, PLoS ONE 8:e71561, doi 10.1371/journal.pone.0071561 (full text read).
- Leroy E.C. et al. 2021, Sci Rep 11:8762, doi 10.1038/s41598-021-88062-5 (full text read).
- Matsumoto H. et al. 2014, G-cubed 15:3448, doi 10.1002/2014GC005454 (full text read, Ifremer archive copy).
- Royer J.-Y. 2016, LDO-201608 report (held artifact royer-2016-LDO-201608.pdf; full text read).
- Duncan A.J., Gavrilov A. & McCauley R. 2014, CMST Project 1308 Report 2014-30, 23 June 2014, for ATSB (held; full text read).
- Brown, McFadden, McCormack, Adams & Vida 2026, A search for hydroacoustic signals from bolides, Icarus 455:117106, doi 10.1016/j.icarus.2026.117106 (peer-reviewed; accepted 14 April 2026; held as the author accepted manuscript, arXiv:2604.12723; read). [Citation corrected 23 Oct 2026 by the synthesis step.]
- Chapp E. et al. 2005, G-cubed 6:Q06003, doi 10.1029/2004GC000889 (abstract).
- Hanson J.A. & Bowman J.R. 2005, GRL 32:L06301, doi 10.1029/2004GL021931 (abstract).
- Tsang-Hin-Sun E., Royer J.-Y. & Perrot J. 2016, GJI 206:1232 (extract).
- Sirovic A., Hildebrand J.A. & Wiggins S.M. 2007, JASA (PMID 17672667) (abstract).
- Miller B.S. et al. 2021, Sci Rep 11:806, doi 10.1038/s41598-020-78995-8; Miller B.S. et al. 2021, Front Mar Sci 8:792651.
- Aulich M.G. et al. 2022, Front Mar Sci 9:864153, doi 10.3389/fmars.2022.864153.
- Stafford K.M. et al. 2011, Mar Mamm Sci 27:828, doi 10.1111/j.1748-7692.2010.00437.x (abstract).
- Sousa A.G. & Harris D. 2015, JASA 138:1379, doi 10.1121/1.4928719 (abstract).
- Risch D. et al. 2014, Biol Lett 10:20140175, doi 10.1098/rsbl.2014.0175.
- Nieukirk S.L. et al. 2012, JASA 131(2):1102-1112 (abstract).
- McKenna M.F. et al. 2012, JASA 131:92, doi 10.1121/1.3664100 (abstract).
- Hanson J. et al. 2001, Pure Appl Geophys 158:425, doi 10.1007/PL00001190 (abstract).
- Talandier J. & Okal E.A. 2001, Pure Appl Geophys 158:567 (abstract); Talandier & Okal 2016, GJI 206:1784, doi 10.1093/gji/ggw249 (extract).
- Okal E.A. 2008, Adv Geophys 49:1, doi 10.1016/S0065-2687(07)49001-X (second-hand).
- Fauvel H. et al. 2026, JASA 160:2370, doi 10.1121/10.0044415 (abstract).
- Raumer P.-Y. et al. 2026, arXiv:2607.07733 (read).
- ISC bulletin and USGS FDSN event queries, 7-8 Mar 2014, 70 S-25 N, 40-140 E (run this session); NASA/JPL CNEOS fireball API (run this session); EarthScope FDSN station and dataselect services (run this session).
