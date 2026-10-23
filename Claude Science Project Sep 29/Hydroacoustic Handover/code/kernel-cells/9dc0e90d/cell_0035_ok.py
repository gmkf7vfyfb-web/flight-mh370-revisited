import datetime
T = "2026-10-17 22:50Z"
R = "results/evidence-sweep-2026-10-17/"
HDR = lambda to, title: f"\n\n## {T} — evidence sweep (Pete's request, general session) -> {to} (cc architecture, composer, Pete): NEW SCOPE — {title}\n\n"
COMMON = (f"Source: the evidence register and four research notes in `{R}` (evidence-register.md; research-surface-search-pod.md; "
 "research-satellite-imagery-2014.md; research-radar-infrasound-ohasisbio.md; research-beacons-tpl-simulator-barnacles.md). "
 "Read the relevant note before you start; every value below is quoted from it, with its page or URL there. "
 "**Pete's rule for this list: no order is imposed. Only the dependencies stated below are binding.** "
 "Add these items to your existing scope; they do not replace any current work order. Each item returns a log-likelihood on the shared impact samples "
 "(or a labelled sensitivity, or an explicit 'carries no information' row), in the normal module format.\n")

E = {}
E["OCEAN_DRIFT.md"] = HDR("ocean drift","2014 surface search, ships, barnacles, expanded find set, other coasts") + COMMON + """
1. **2014 aerial and ship surface search: non-detection (register A1).** Deferred earlier; now in scope.
   - Data: 387 daily search-box polygons, 18 Mar to 28 Apr 2014 (GA/AMSA ArcGIS service `Search_And_Rescue_Search_Area2014`; © AMSA, no licence text: cite as a data source and ask AMSA for permission before you publish maps). Daily area, track spacing and asset counts are in ATSB 2017 Tables 10-18 (CC BY 3.0 AU). AMSA's daily POD values were never published (request from AMSA JRCC if wanted).
   - CSIRO did NOT assume 100 %. It applied AMSA's box POD ("low (10 or 20%)" on poor days or track spacing >20 NM; "often 100%" otherwise) to every particle in the box (Part IV pp. 1-2), and itself calls this an over-estimate for single items.
   - Build P(no sighting | impact) as alternatives, not one value: (a) CSIRO/AMSA box POD; (b) a sweep-width model: W = W_u x weather factor (NATSAR 2026 tables; 4-person raft at 1,000 ft, visibility >40 km: 2.3 NM), coverage C = W/S, POD = 1 - exp(-C) per item per pass; at the decisive 12-16 NM spacing C is about 0.14-0.19; field-level P(no detection) = product over items and days; (c) the AF447 cap of Stone et al. 2014, 1 - p_d = 0.7 + 0.3q.
   - Days lost to weather: 25 Mar, 27 Mar and 27 Apr; 22-23 Apr partly.
   - Dependencies: (i) number and size classes of floating items from settling; (ii) wind, sea state, visibility and daylight per search day from shared ocean transport (new item there); (iii) ONE surface observation model shared with the Pléiades/sightings module, because the aircraft cued by the satellite sightings searched the same areas on the same days (see the PLEIADES entry). Do not let both modules score the same day and box.
2. **Ships as opportunistic observers (register E2; Pete approved).** Low-POD surface non-detection. ATSB 2017 p. 126: two merchant ships transited the 34-35.5 S radar/optical detection area and reported nothing. Free AIS for fishing vessels: Global Fishing Watch (needs a free account token); merchant satellite AIS for 2014: commercial (Spire, exactEarth, ORBCOMM). No public list of vessels near the 7th arc on the morning of 8 Mar was found. Labelled sensitivity unless a POD can be justified.
3. **Barnacle geochemistry as a two-sided likelihood, and barnacle age and species (register A4, A5).** The data are public, more than the brief assumed:
   - SIR Appendix 2.6B (Blamart & Bassinot, LSCE, 2016): delta-18O profiles, Tableaux 6-9 (pp. 40-45). Terminal growth 25.4 +/- 1 C; EARLY growth of the largest valves 28.5 +/- 1 C. Tableau 8 gives distance in um on p. 43 and in mm on p. 44: resolve this before use.
   - Al-Qattan et al. 2023 data on Mendeley (doi:10.17632/nr4vt4h8gt): Isotope_day2.csv (dated SST series), DTW scores and their 50,000 simulated trajectories.
   - Poupin 2015 (SIR App. 2.6A): Lepas anatifera striata only; capitulum up to 36 mm; floated ventral side up.
   - Age is disputed: Poupin's extrapolation gives 476 days; Mesaglio et al. 2021 gives 1.05 mm/day mean and 1.45 mm/day maximum; Goehlich et al. 2024 shows about twice the growth in summer as in winter. Carry the age as a latent variable with these as alternatives.
   - Likelihood: modelled SST along each drift path (ocean-model temperature from shared transport) against the dated isotope temperatures, with calibration and +/-1 C error, marginalised over attachment time and growth rate.
   - Species: no Lepas australis is recorded on any MH370 item in the official documents read. This is a weak term against long cold-water exposure; state it as weak.
   - Not yet read: ATSB 2017 Appendices F (De Deckker, Mg/Ca) and G (organisms on other debris). Read the full ATSB PDF in a browser or from Drive. The largest flaperon barnacles are held by the French judiciary and are not available.
4. **Expanded find set (register E4; Pete approved).** Score items beyond the stringent nine as provenance-weighted observations, L = P(MH370) x L_drift + (1 - P(MH370)) x L_background, with interval-censored find dates. About 60 items have been collected and more than 30 examined; some were never collected. 'NO STEP 2' (Evatra, SE Madagascar, about 25 S 47 E, find date unknown) was reported in Dec 2025.
5. **Non-recovery on other coasts (register B4; Pete: "can also be looked at").** Indonesia (Sumatra, Java), Sri Lanka, Maldives and India, with reporting-probability tiers as for Western Australia, relative to the find coasts.
6. Refloat and biofouling (register B5) stay in the deferred list unless item 3 needs them.
"""

E["PLEIADES.md"] = HDR("Pléiades / sightings","other 2014 satellite sightings, imaged ocean with no objects, aerial photographed contacts") + COMMON + """
1. **Other satellite sightings (register A2).** Use the same machinery as Pléiades: transport from impact to image time, plus a false-alarm model. The published positions are:
   - DigitalGlobe, 16 Mar 2014, **04:16 UTC** (DIGO sheets): 43°58'34"S 090°57'37"E (about 24 m) and 44°03'02"S 091°13'27"E (about 5 m).
   - Gaofen-1, 18 Mar: 44°57'S 90°13'E, 22.5 x 13 m. Time not published; a sun-synchronous model gives about 04:00 UTC (inferred).
   - Airbus to MRSA, 23 Mar: 122 objects in about 400 km^2; 11 tabulated near 44.66-44.70 S, 90.43-90.62 E (two pairs are near-duplicates).
   - THEOS, 24 Mar, **03:07:56 UTC**, incidence 26.98 deg: zones near 46.47-46.52 S, 89.35-89.63 E. These positions are PROVISIONAL (read from thumbnail graticules).
   - Japan IGS, 26 Mar, 00-06 UTC: about 10 objects within 10 km of 44°17'S 90°56'E.
   - All of these are about 1,000 km south of the four GA Pléiades scenes. The 43-45 S area was searched by aircraft 20-27 Mar with no MH370 debris found (ATSB 2017 p. 126). The sighting and that aerial non-detection must therefore sit in ONE joint surface observation model with drift's surface-search term (dependency on the OCEAN_DRIFT entry of the same time).
   - The false-alarm rate is the deciding parameter. GA (Minchin et al. 2017) recommended calibrating it on comparable images where no debris is expected.
2. **Imaged ocean with no objects (register A3).** No agency has published image footprints. The total imaged area is NOT FOUND. Declare this "not assessed: footprints not available" unless ATSB/AGO release them. Pass times can be computed from Space-Track 2014 TLEs (free account needed; method in the imagery note, Q2.2). A nominal sun-synchronous model already reproduces the two published times.
3. **RNZAF P-3 photographs, 29 Mar 2014, 07:44-09:20 UTC (register B1).** Independent source only (Iannello 2017, grade C; images on Dropbox; no official comment). Positions: debris fields at 28.3927 S 97.7750 E (image 5832) and 29.19333 S 95.1250 E (image 5853); a suitcase-like object near 28.3176 S 97.8234 E; a panel-like object near 28.8867 S 96.0844 E (the spreadsheet gives 28.87167 S 96.13 E: check); a box-like object near 29.1936 S 95.1094 E. Score them as positive sightings with a false-alarm model, as alternatives (contacts used / not used).
"""

E["OCEAN_TRANSPORT.md"] = HDR("shared ocean transport","detection covariates and SST along paths") + COMMON + """
1. **Detection covariates (register E3).** Every surface-detection term (drift's surface search, ships, Pléiades and the other sightings) needs these at search and image times along the drifted debris field: 10 m wind and significant wave height (ERA5 single levels and ERA5 waves), total and low cloud cover (ERA5; MODIS cloud mask where a granule exists), sun elevation, and a visibility proxy. Period: 16 Mar to 28 Apr 2014; domain about 20-48 S, 80-110 E. Expose them through the same batch interface as transport, so that drift and Pléiades use identical values.
2. **SST along trajectories** for drift's barnacle term: ocean-model near-surface temperature sampled along each particle path, with the model name carried as the same alternative as the currents.
Consumers: ocean drift and Pléiades. Neither depends on the other for this item.
"""

E["OCEAN_SETTLING.md"] = HDR("settling","shipwreck positive controls; floating-item counts for the surface search") + COMMON + """
1. **Shipwrecks as positive controls for sonar detection (register E1; Pete: send to settling).** ATSB Phase 2 found two 19th-century merchant sailing ships carrying coal, at 3,700-3,900 m depth and about 36 km apart. They were found by Fugro Equator and Havilah Harmony in May and Dec 2015 (WA Museum, Anderson 2018; already in the settling references). They are known targets found by the same sensors and processing. Use them to check the wreckage-field detectability that settling emits (the field extent and piece sizes against sonar resolution), and pass the result to searched areas as an empirical check on the detection ratings q and on rho (rho has no published value today). A wooden hull fully degraded and an iron hull with coal and fittings are not an aircraft field: state that limit.
2. **Dependency owed to drift:** the expected number of floating items by size and windage class per impact family. Drift's surface-search term needs it.
"""

E["SEARCHED_AREAS.md"] = HDR("searched areas","passive acoustic (pinger) search; shipwreck controls; Ocean Infinity remaining area") + COMMON + """
1. **Passive acoustic search for the recorder beacons, 2-17 Apr 2014 (register B3).**
   - The FDR beacon battery had expired in Dec 2012; the CVR beacon was valid to Jun 2014 (SIR p. 137). Beacon life is 30 days minimum, 40 days predicted.
   - Coverage exists only as maps: ATSB Jun 2014 Fig. 12 (TPL tracks 4-14 Apr; 2,400 m swath; 3 km maximum effective range) and ATSB 2017 Fig. 23. Digitise both. RAAF sonobuoys covered about 3,000 km^2 per sortie, 6-17 Apr; their drop positions are not published.
   - Haixun 01 contacts were at 25.975 S 101.461 E (4 Apr) and about 3 km west (5 Apr), and were not reacquired. The Ocean Shield contacts were at about 20.95-21.2 S, 104.0-104.2 E and were later attributed to the TPL itself.
   - Term: P(no detection | seabed point) = 1 - P(CVR beacon working) x P(det | inside coverage). It is small in area but cheap. Coordinate with the existing Bluefin-21 entry so the area is not counted twice.
2. **Shipwreck controls (cc from the settling entry):** take the q and rho check from settling when it is ready. This is a dependency on settling.
3. **Ocean Infinity:** about 7,571 km^2 searched in Mar 2025 and 31 Dec 2025 to 23 Jan 2026. About 7,428 km^2 remain under contract to 30 Jun 2027; work is not expected before Nov 2026. Keep the campaign provenance, and add the new area when the polygons are published.
"""

E["HYDROACOUSTICS.md"] = HDR("hydroacoustics","OHASISBIO report now public; infrasound row") + COMMON + """
1. **OHASISBIO (register A9).** Royer, LDO-201608, 22 Dec 2016, 18 pp. It is now PUBLIC (Google Drive link in Wise's July 2026 Substack) and has been read.
   - 2014 network: 6 sites with 8 hydrophones (NCRO, WKER, the SWAMS triad, NEAMS, SSEIR, MAD), moored in the SOFAR axis at 970-1,260 m, recording at 240 Hz.
   - **NEAMS (31°34'S 083°11'E), the site nearest the arc, was lost on recovery: no data.**
   - Royer finds 5 events (6 solutions). D2 at 27.856 S 93.460 E, 01:06:05 UTC, is favoured and lies "in the vicinity of the presumed impact area" but in a seismically active area. B at 35.224 S 99.922 E, 00:21:30, is "very tentative". C1/C2 and D1/D2 are mutually exclusive alternatives. Event A is an iceberg. His time stamps were corrected from GPS to UTC (16 s).
   - Add the report to the prior-work critique (item 7). Test B and D1/D2 against your prediction, power and coverage outputs. Request the raw 2014 data from the author (address printed in the report); no DOI was found.
2. **Infrasound (register A8): expected to carry no information; run it as a declared row.**
   - The CTBTO IDC search used KLIA at 16:41 UTC as the source, +/-900 s, all stations within 50 deg; it did NOT search the southern ocean.
   - IS06 Cocos (I06AU) was operating, but March 2014 IMS infrasound is not public (EarthScope data begin 3 Apr 2014).
   - Impact kinetic energy is 0.2-1.5 t TNT equivalent, against network thresholds of 50 t to 1 kt: a factor of 33-2,500 below, before any air coupling. The only case that could matter is a close Cocos flyby, which is a route question for core.
   - Blackman et al. 2004 used no Cocos receivers.
   - II.COCO seismic data for 8 Mar are public. The LLNL CASIS 2014 poster (Kane, Lehman, Candy) could not be read.
"""

E["END_OF_FLIGHT.md"] = HDR("end of flight","debris configuration and emergency beacon, as documented alternatives") + COMMON + """
1. **Debris configuration (register A6).** Pete's ruling: sample across both readings, which the descent families already do. No new likelihood is required. Record the sources in the family-prior documentation: the ATSB found flaps "most likely" retracted and the flaperon near neutral; Vance 2018 argues extended flaps (a ditching); Kenyon 2020-21 argues flutter and in-air separation. A debris-configuration weighting of families may be run only as a labelled sensitivity.
2. **Emergency beacon non-detection (register B2), as a labelled sensitivity.**
   - 9M-MRO had four ELTs: a fixed ELTA 406 unit (g-switch; above the aft ceiling at STA 1880; blade antenna on the fuselage top), a portable unit (normally OFF), and two raft units (121.5/243 MHz only, need raft deployment) (SIR pp. 53-54).
   - The cockpit panel is guarded ARMED or ON with no OFF position; OFF exists only on the beacon itself, so in-flight silencing needs cabin-ceiling access. No official document discusses deliberate disabling.
   - Activation rates in accidents are low: 15-34 % in the SIR's ADREP figures, about 40-60 % in ATSB AR-2012-128.
   - Express P(no 406 alert | family) with these rates and a "deliberately disabled" alternative. Expect a small likelihood ratio between families.
"""

E["CORE_STAGES.md"] = HDR("core and composer","radar non-detections, received power, simulator conditional, contrails, WSPR gate") + COMMON + """
1. **Radar non-detections after 18:22 (register A7, E6, B7): labelled sensitivity only.**
   - Indonesia: officials said Lhokseumawe (Radar Unit 231, about 240 NM) and Sabang did not detect MH370. TNI-AU said its radars run 24 h. That the radars were off at night is claimed only by analysts, without a primary source. No record of other N571 traffic seen by Indonesian radar is public.
   - India: the Andaman and Nicobar Command said radars run "as required" and may have been off.
   - Geometry (`radar-site-ranges-nm.csv`; horizon at FL350 about 230 NM with the antenna at sea level): INS Baaz, Campbell Bay, is 30-146 NM from the 18:22 point, NILAM, ANOKO and IGOGU; Car Nicobar is 137-260 NM (inside the horizon only near IGOGU and ANOKO); Port Blair and Diglipur are 267-473 NM (out of range unless the route goes north). Sabang and Lhokseumawe are 25-212 NM from these points.
   - Term: P(no report | route) = 1 - P(operating) x P(detect | in coverage), with P(operating) carried as alternatives (for example 0, 0.5, 0.9). With P(operating) unknown, the result is conditional: never a headline.
2. **Received power (register D2).** First step: decompose the existing 4.4-nat along-arc received-power span by epoch along the sampled paths. Integrate as a per-epoch likelihood only if one or more epochs are selective.
3. **Captain's simulator (register C1): conditional route hypothesis only, never a likelihood.**
   - The IG transcription of the RMP data is PROVISIONAL: check it against the RMP pages on Pete's Drive. It gives KLIA, then the Malacca Strait at 3.42 N 100.89 E and 5.11 N 98.59 E, then 10.18 N 90.22 E at 40,003 ft heading 255.5, then 45.0852 S 104.1455 E (37,651 ft, fuel 0) and 45.1277 S 104.1408 E (4,000 ft input).
   - The SIR says 7 waypoints in a 3 Feb file; the ATSB says a 2 Feb session. The ATSB says the track was "not consistent" with the satcom tracks.
3b. **Contrails (register E5): low priority; Pete recalls these were cloud features, and the official record agrees.** NASA (Minnis) examined polar-orbiter imagery 19:00-05:00 UTC for the ATSB. Its one candidate, Terra MODIS 04:45 UTC at 45.5 S 84 E, was "probably a shadow ... or a cloud edge". The Ulich/Prostyakov 31-38 S line was judged a natural gap in the cloud deck (Metabunk). There are no polar-orbiter granules over the southern leg between 20:54 and 02:55 UTC, so only Meteosat-7 IODC (2.5-5 km; EUMETSAT EO:EUM:DAT:0881) and Electro-L (no public archive) could see it. Suggested cheap first step: predict contrail formation along candidate paths (Schmidt-Appleman criterion with ERA5 temperature and humidity). If no segment would form a persistent contrail, record "carries no information" and stop.
4. **WSPR (register D1).** Enters only through Pete's pre-registered gate (`~/Downloads/resolution/agents/alternative_redteam/wspr_validation_protocol.md`). His own control test placed the true path at the 43.6th percentile, and selecting on WSPR raised path RMSE from 150.8 to 291.2 km.
5. **Co-pilot's phone registration (register B6):** a consistency check before 18:01 only.
Composer: one surface observation model across drift and Pléiades (see those entries), and the radar and simulator items only as labelled sensitivities.
"""

E["architecture.md"] = HDR("architecture","evidence sweep posted to eight inboxes") + COMMON + """
Posted at the same time to OCEAN_DRIFT, PLEIADES, OCEAN_TRANSPORT, OCEAN_SETTLING, SEARCHED_AREAS, HYDROACOUSTICS, END_OF_FLIGHT and CORE_STAGES.

Binding dependencies (there is no order beyond these):
- drift surface search <- settling floating-item counts;
- drift surface search and Pléiades sightings <- shared-transport detection covariates;
- drift surface search <-> Pléiades sightings: ONE joint surface observation model;
- drift barnacle term <- shared-transport SST along paths;
- searched-areas q/rho check <- settling shipwreck controls.

Pete's rulings this session:
- the shipwreck controls go to settling;
- the expanded find set goes to drift;
- the debris-configuration evidence is sampled across both readings in end of flight (no new likelihood);
- non-recovery on other coasts is in scope.

Not assessable now: imagery-footprint non-detection (no footprints published); IMS infrasound for March 2014 (not public); Indian and Indonesian radar records (not public).
"""
for fn,txt in E.items():
    p = f"repo/r/Claude Science Project Sep 29/coordination/{fn}"
    assert os.path.exists(p), p
print({k:len(v.split()) for k,v in E.items()})