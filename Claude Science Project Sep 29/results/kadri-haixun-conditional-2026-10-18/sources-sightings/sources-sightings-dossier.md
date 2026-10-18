# Kadri–Haixun conditional test, leg "Sources and sightings": graded source dossier

Prepared 18 Oct 2026 for the pre-registered conditional test (`../preregistration.md`, commit 207b332).
This leg collects evidence. It computes no likelihood and uses no posterior. Every number below is copied
from the named source or from a catalogue query run on 18 Oct 2026 (`catalogue_queries_2026-10-18.json`).
It builds on, and does not repeat, `results/evidence-sweep-2026-10-17/research-beacons-tpl-simulator-barnacles.md`,
`research-satellite-imagery-2014.md` and `research-surface-search-pod.md`.

**Grades.** A = primary source read here, with page (or, for web releases, release number and archive snapshot).
B = official source cited but not read in full here. C = press, online or community source.
"NOT FOUND" means no public source was found by this leg; it is not evidence of absence.

**Geometry used** (from `kadri_geom.py`, re-run here; `contact_geometry.json`): 7th arc at sea level, BTO 18,400 µs,
00:19 option m0019a (R600), 1-sigma ±63 µs. Arc crossing of the 306.18° H01W bearing: 25.732 S 101.369 E.

## Short answers

1. **Haixun 01.** The only published coordinate is the first contact, **25.975 S 101.461 E** (ATSB 2017 p.38, A).
   No coordinate of the second contact is published. Its offset is given three ways: "3 km west" (ATSB 2017 p.38; ATSB 2014/2015 p.11, A),
   "within just two kilometres" (JACC press conference 6 Apr 2014, A) and "about 1 nautical mile" (CCTV via Sina, C).
   The first contact lasted **15 min** (ATSB 2017 p.38) but was "just a quick acoustic detection" per JACC (6 Apr) and ">10 min" per CCTV. These disagree.
   The second contact lasted **90 s** (all sources), at about **15:47 AWST = 07:47 UTC on 5 Apr** (JACC 6 Apr, Houston: "I think it was 15:47")
   or **15:57 Beijing time = 07:57 UTC** (Chinese press, C). The hour of the first contact is not in any official source.
   Equipment: a Benthos pinger detector (ATSB 2014/2015 p.11) on a pole from a rescue boat, practical range about 2,000 m by the maker (ATSB 2017 pp.37, 39).
   No recording was made (Liberation Daily via PTI, C; Ulich 2018, C).
   Follow-up: HMS Echo tried to reacquire on 6 and 8 Apr and failed; it judged the contacts unlikely to be from MH370 "due to the water depth, surface noise
   and the hydrophone equipment" (ATSB 2017 p.39, A). A submarine (named HMS Tireless by the UK MoD, B) found nothing. On 14 Apr the JACC said the Haixun
   detection "has been analysed and has been discounted as a credible transmission" (JACC transcript 14 Apr, A).
2. **White objects.** Seen on **5 Apr 2014 from 11:05 local (UTC+8, so 03:05 UTC) for about 20 min** by the crew of a **PLA Air Force search aircraft** (type not stated in the 5 Apr reports)
   with an Australian pilot aboard, who reported to the JACC (Xinhua via People's Daily / 12371.cn, C). The JACC put them "about 90 kilometres from the
   detection area" (JACC release 5/6 Apr, A). **Count, sizes and position: NOT FOUND.** On 7 Apr Houston said "Apparently they've been checked out
   and they had no relationship to MH370" (JACC transcript 7 Apr, A). Who checked them, and whether any were recovered: NOT FOUND.
   One Chinese report puts the aircraft's task area at "more than 2,700 km" from Perth; the first contact is 1,550 km from Perth (great circle). This conflict is unresolved.
3. **Satellite coverage of 25–26.5 S, 100–102.5 E.** The official record shows imaging was requested from France, Italy, Germany, Thailand, China and
   the USA from about 15 Mar (ATSB 2017 pp.116–117, A), and that from 3 to 28 Apr a "satellite search (multiple nations) of areas drifted from the 7th arc"
   was coordinated by the Australian Geospatial-Intelligence Organisation (ATSB 2017 p.29, Table 15, A). No footprint, date or result for this locality is published.
   In public catalogues (18 Oct 2026) the locality has **only coarse daily imagery**: Terra MODIS 65, Aqua MODIS 64 and Suomi NPP VIIRS 160 granules
   (8 Mar–30 Apr 2014). There are **no** Landsat 7/8 scenes (not in 2014, nor in any year 2013–2026), **no** Maxar scenes in the NASA CSDA subset,
   and **no** public Sentinel-1A product (launched 3 Apr 2014; first public products 15 Jun 2014 at ASF, 3 Oct 2014 at Copernicus; first over the locality 29 May 2015).
   The nearest archived very-high-resolution strips (WorldView-1/2, 29 Mar–10 Apr 2014) are **537–599 km** from the first contact.
   Imagery therefore **cannot** supply a non-detection term for the locality: "not assessed – no listed data", not "searched and empty".

## Figures

- `fig-locality-sources-map.png`: (a) archived very-high-resolution strips, the Chinese ships' area from 4 Apr and the study area against the 7th arc;
  (b) the first contact, the arc crossing, the 306.18° ±1° bearing and the 90 km ring.
- `fig-locality-imagery-timeline.png`: listed imagery over the study area by date, with the contacts, ship checks, sonobuoys, the drifted-area air search and the beacon battery limits.

Each figure carries the two footnotes (plain ASD-STE100 and technical).

## 1. Haixun 01 contact

### 1.1 Event table (conflicts kept)

| Item | Official, read (A) | Press / community (C) | Note |
|---|---|---|---|
| Vessel | "Chinese Maritime Safety Administration vessel, MV Haixun 01" (ATSB 2014/2015 p.11; ICAO ATM/SG/2-WP30 §2.23) | "China's Maritime Safety Administration patrol ship"; captain Jiang Long (Global Times 8 Apr) | |
| Team | "crew … operating the hydrophone from one of the ship's rescue boats" (ATSB 2017 p.38) | Shanghai Maritime Surveying and Mapping Centre survey team (Xinmin Evening News 5 Apr); 5 staff on a fast rescue boat (Sina/CCTV 6 Apr); 3 people heard it (Liberation Daily via PTI) | |
| First contact date | 4 Apr 2014 (ATSB 2017 p.38; ATSB 2014/2015 p.11) | 4 Apr afternoon (Xinmin; CCTV "after 15:00") | Houston on 6 Apr: "about 36 hours ago … the night before" (JACC tr006) |
| First contact hour | NOT FOUND | "after 15:00" Beijing time (CCTV via Sina); "about 16:34 local" (forum user quoting a Chinese paper, C–) | Hour unresolved |
| First contact position | **25.975 S, 101.461 E**, "southern end of the green zone", depth about 4,500 m (ATSB 2017 p.38) | "around 25 S, 101 E" (Xinhua 5 Apr) | Only published coordinate |
| First contact signal | 37.5 kHz, once per second, **15 min** (ATSB 2017 p.38) | ">10 min" (CCTV via Sina) | JACC 6 Apr: "just a quick acoustic detection and then nothing" – conflict |
| Second contact date/time | "the next day" (ATSB 2017 p.38); "yesterday afternoon, Perth time … I think it was 15:47" (JACC tr006, 6 Apr) | 15:57 Beijing time, 5 Apr, after 5 h of fruitless sweeps that morning (Sina/CCTV) | 07:47 or 07:57 UTC 5 Apr |
| Second contact offset | "3 km west of the first detection" (ATSB 2017 p.38; ATSB 2014/2015 p.11) | "about 1 nautical mile" (CCTV via Sina); "2 km" (Xinhua, Global Times) | JACC 6 Apr: "within just two kilometres"/"less than two kilometres" – conflict |
| Second contact signal | 90 s, "much weaker" (ATSB 2017 p.38) | "boom, boom, boom" each second for 1.5 min (Sina) | |
| Equipment | "Benthos pinger detector equipment from a rescue boat" (ATSB 2014/2015 p.11); "hand held hydrophone (underwater microphone) system" (ATSB 2017 p.36); pole-mounted, operator listens while rotating (p.37); practical range "about 2,000 m according to the manufacturer" (p.39) | 2 m pole, transducer < 30 cm (Xinmin); Teledyne executive identified it as a DPL-275 diver pinger locator (NYT via blog, C); CCTV footage "a device shaped like a large soup can attached to a pole … padded suitcase" (AP) | Benthos is a Teledyne company; DPL-275 identification is C only |
| Recording | — | "not recorded as they came suddenly" (Liberation Daily via PTI); "no recordings were made" (Ulich 2018) | No data exist to re-analyse |
| Comparison with sample | — | technicians judged it "similar to the sample pulse signal provided by Boeing" (deputy skipper Wei Liang, Xinmin) | |
| China Maritime Search and Rescue Centre | — | the pulse "has not been confirmed as related" to MH370 (Xinhua 5 Apr, 22:40) | Only CMSRC statement found |

Computed here (geodesic, WGS84): first contact 28.46 km from the arc crossing, azimuth 305.68° and range 1,566.3 km from H01W, sea-level BTO 18,512.4 µs
(+112 µs, 1.8 sigma outside the arc). A second contact 3 km due west would be 27.63 km from the crossing, azimuth 305.60°, BTO 18,499.0 µs.
Great-circle distance Perth–first contact 1,550 km (Chinese press: "about 1,650 km"; JACC map 8 Apr: 1,645 km to the sonobuoy box).
Days after 00:19 UTC 8 Mar: about 27.3 (4 Apr) and 28.3 (5 Apr, 07:47 UTC).

### 1.2 Follow-up and conclusions

| Date (2014) | Action | Outcome | Source | Grade |
|---|---|---|---|---|
| 5/6 Apr (night) | JACC: sounds "consistent with the aircraft black box"; RCC Australia asks RCC China for more data; RAAF deployment considered | Not verified | JACC release mr010 (snapshot 20140405191319) | A |
| 6 Apr | RAAF assets deployed to the contact area; HMS Echo (about 14 h away) and Ocean Shield directed to join Haixun 01 | — | JACC press conference 6 Apr (tr006) | A |
| 6 Apr | Houston: "the area is in the high probability area"; southern part now higher priority after the eclipse/BFO advice | — | JACC tr006; ATSB 2017 pp.30–31 | A |
| 6 and 8 Apr | HMS Echo attempts to reacquire | "unsuccessful … unlikely to be MH370's ULBs due to the water depth, surface noise and the hydrophone equipment" | ATSB 2017 p.39; ATSB 2014/2015 p.13; ICAO ATM/SG/2-WP30 §2.24 | A |
| 6–17 Apr | A submarine "tasked to investigate the area" | "unable to identify any ULB transmissions" | ATSB 2017 p.39 | A |
| — | UK MoD: HMS Tireless "working alongside the survey ship HMS Echo"; stood down 24 Apr | "no prospect of further acoustic detections" | UK MoD news 14 and 24 Apr 2014 | B |
| 8 Apr | Haixun 01, Donghaijiu 101, PLAN ship 999 and HMS Echo scan an expanded 432 km² near 25 S 101 E | — | Global Times 8 Apr | C |
| 8 Apr | Planned sonobuoy search box of 250 km² at the contact site | — | JACC map mr_013-5 (8 Apr) | A |
| 6–17 Apr | AP-3C sonobuoys at the Haixun 01 and Ocean Shield areas and on the H01 bearing | "No acoustic detections considered to be related to ULB transmissions" | ATSB 2017 p.41 | A |
| 8–10 Apr | "Haixun 01 and HMS Echo at the southern end" of the underwater search area | — | JACC mr013–mr015 | A |
| 9 Apr | "no further detections in the area where … Haixun 01 assisted by HMS Echo" | Analysis not yet complete | JACC tr008 | A |
| 13–17 Apr | Air and sea search of the drifted "Haixun 01 ULB hearing report – green box D", 10 NM radius; 57,466 / 47,706 / 49,715 / 33,199 / 41,579 km²; track spacing 5 NM | No MH370 debris (p.33) | ATSB 2017 p.29 Table 15, p.32 Table 17, p.33 | A |
| 14 Apr | "That has been analysed and has been discounted as a credible transmission" | Closed | JACC tr009 | A |

The agency that analysed the Haixun data is not named. No official analysis report of the Haixun contact is public: NOT FOUND.
Houston (7 Apr): Haixun 01 "was on the southern extremity of the search area when it first detected a pulse signal" (JACC tr007).
JACC map mr_012-1 (7 Apr) plots the 5 Apr Haixun 01 signal on the 7th arc and 600 km from the 6 Apr Ocean Shield signal (A, map only).

### 1.3 Recorder beacons (type, batteries)

| Item | Value | Source | Grade |
|---|---|---|---|
| Type | Dukane DK-100 / DK-120; 37.5 ± 1 kHz; 10 ms pulse; ≥ 0.9 pulse/s; operating depth to 6,096 m | MOT 2015 Factual Information p.59; SIR 2018 p.136 | A |
| Source level | 160.5 dB re 1 µPa at 1 m initial; 157.0 dB after 30 days | MOT 2015 p.59; SIR p.136 | A |
| Life | 30 days minimum; maker's predicted maximum 40 days | MOT 2015 p.59; ATSB 2017 p.36 fn 20 | A |
| FDR beacon | S/N SC26210, battery expired December 2012, no evidence of replacement | MOT 2015 p.60; SIR pp.137, 364–365 | A |
| CVR beacon | S/N not recorded, battery replaced on schedule, next expiry June 2014 | MOT 2015 p.60; SIR p.137 | A |
| Past expiry | "may operate, for a reduced time period"; frequency and power not assured in specification | MOT 2015 p.60; SIR pp.364–365 | A |

Interpretation limits (for Q5): the contacts fall on days 27–28, inside the 30-day minimum for the in-date CVR beacon.
The ATSB 2014 report "MH370 – Definition of Underwater Search Areas" was read in its 30 Jul 2015 update (printed = PDF − 5); the 26 Jun and 18 Aug 2014 issues were not read.

## 2. White objects reported about 90 km from the contact

| Item | Value | Source | Grade |
|---|---|---|---|
| Statement | "A number of white objects were also sighted on the surface about 90 kilometres from the detection area" | JACC release mr010 (last updated 6 Apr) and tr006 | A |
| Observer | One PLA Air Force aircraft; type not stated in the 5 Apr reports (the PLAAF aircraft flying from Perth in March were Il-76s); Australian pilot aboard reported to JACC | Xinhua via People's Daily 6 Apr; 12371.cn 6 Apr; PTI via Deccan Herald | C |
| Flight | Departed Perth 06:04 local as the first multinational aircraft of the day; cloud base about 200 m, waves 1–2 m, wind force 4–5 | 12371.cn (Xinhua/PLA Daily) 6 Apr | C |
| Time | From 11:05 local, over 20 min (03:05–03:25 UTC if local = AWST) | same; PTI | C |
| Count, size | "multiple" / "a number of"; sizes NOT FOUND | — | — |
| Position | NOT FOUND (only "about 90 km" from the detection area; direction not given) | — | — |
| Photographs | Taken; one published by People's Daily ("photo taken 5 April") | People's Daily 6 Apr | C |
| Follow-up | 6 Apr: "Ships are going to have a look at the white objects that were found in the sea yesterday" | JACC tr006 | A |
| Outcome | 7 Apr: "Apparently they've been checked out and they had no relationship to MH370" | JACC tr007 | A |
| Recovery | NOT FOUND (which ship, whether recovered) | — | — |
| Context | Over thirty items were recovered by surface vessels during the surface search; "All of these items were considered unlikely to be associated with MH370" | ATSB 2017 p.33 | A |
| Conflict | Aircraft task area "more than 2,700 km" from Perth vs first contact 1,550 km from Perth | 12371.cn vs computed | open |

Not the same event: the Il-76 sightings of 24 Mar at 42.5453 S 95.1113 E and of 29 Mar at 28.15 S 94.44 E (Xinhua, C), and the 9 Apr
"multiple floating objects" near 20 S 98 E in the Ocean Shield area (Xinhua 9 Apr, C).

Consequence for Q7 (forward drift to the sighting): with no published position, the sighting can only be used as "within about 90 km of
25.975 S 101.461 E at about 03:05–03:25 UTC on 5 Apr, checked, not related". It cannot be scored as a located find.

## 3. Satellite coverage of the locality (25–26.5 S, 100–102.5 E), 8 Mar–mid Apr 2014

### 3.1 What was tasked (official record)

- About 15 Mar: AMSA with the Australian Geospatial-Intelligence Organisation asked France, Italy, Germany, Thailand, China and the USA to image the search region in radar, optical and infrared (ATSB 2017 pp.116–117, A).
- 3–28 Apr: "Satellite search (multiple nations) of areas drifted from the 7th arc coordinated by Australian Geospatial-Intelligence Organisation with areas advised by AMSA/ATSB" (ATSB 2017 p.29, Table 15, A). The same table lists the drifted Haixun 01 report area (13–17 Apr).
- Footprints, acquisition dates or results for this locality: NOT FOUND in ATSB 2014/2015, ATSB 2017, the JACC releases 1–17 Apr, the MOT 2015 Factual Information or the SIR 2018.
- The southern-ocean sightings of 16–26 Mar and the French Pléiades scenes of 23 Mar lie more than 1,000 km away (see `research-satellite-imagery-2014.md`).

### 3.2 Public catalogue queries (run 18 Oct 2026; A as data)

| Catalogue / collection | Hits over the locality | Control | Comment |
|---|---|---|---|
| NASA CMR MOD02QKM v6.1 (Terra MODIS 250 m) | 65 (8 Mar–30 Apr) | — | daily, about 03:00–03:20 UTC |
| NASA CMR MYD02QKM v6.1 (Aqua MODIS 250 m) | 64 | — | daily, about 06:30–07:40 UTC |
| NASA CMR VNP02IMG (Suomi NPP VIIRS 375 m) | 160 | — | day and night passes |
| USGS Landsat STAC `landsat-c2l1` (L7, L8) | 0; also 0 for 2013–2026 and 0 for 95–108 E, 20–32 S in Mar–Apr 2014 | Perth: 50 | Landsat did not image this open ocean |
| NASA CSDA Maxar L1B (WV-1, WV-2, GeoEye-1, QuickBird-2, IKONOS) | 0 | Perth WV-2 pan: 225 | Subset of the Maxar archive: it does not hold the 16 Mar 2014 WV-2 sighting scene (positive control 0), so 0 here is not proof of no Maxar imagery |
| NASA CSDA, SE Indian Ocean 85–110 E, 18–47 S | 124 records: WV-2 29 Mar and 1 Apr near 28 S 96 E; WV-2 5, 9, 10 Apr and WV-1 10 Apr near 19–22 S 97–98 E | — | Nearest strip 537–599 km from the first contact |
| ASF Sentinel-1A (GRD, SLC, OCN, RAW) via CMR | 0 | Earliest public GRD/SLC worldwide 15 Jun 2014 | Commissioning data not public |
| Copernicus Data Space SENTINEL-1 | 0 to 2015-05-28; first over the locality 29 May 2015 (WV OCN) | Earliest 2014 product worldwide 3 Oct 2014 | — |
| NASA CMR ASTER L1T, EO-1 ALI, EO-1 Hyperion | 0 | — | — |
| Copernicus Data Space LANDSAT-7/8, SENTINEL-2/3, ENVISAT | 0 | — | European mirror only; not authoritative for Landsat |
| Maxar Discover, Airbus OneAtlas (Pléiades, SPOT 5/6), e-GEOS (COSMO-SkyMed), DLR EOWEB (TerraSAR-X/TanDEM-X), MDA/EODMS (RADARSAT-2), CRESDA (Gaofen-1), GISTDA (THEOS), KARI (KOMPSAT-2/3/5), ISRO (RISAT-1) | not tested | — | Registration needed; ESA FedEO lists only collection-level "full archive and tasking" records |

### 3.3 Which satellites could have imaged it

In orbit on 8 Mar–15 Apr 2014 (CelesTrak SATCAT launch/decay dates, read 18 Oct 2026; operating state and tasking not verified):
WorldView-1 (2007), WorldView-2 (2009), GeoEye-1 (2008), QuickBird-2 (2001, decayed Jan 2015), IKONOS-2 (1999), Pléiades 1A (2011) and 1B (2012),
SPOT 5 (2002) and SPOT 6 (2012), THEOS (2008), Gaofen-1 (Apr 2013), KOMPSAT-2/3/5, DEIMOS-1 and UK-DMC 2 (2009), Landsat 7/8, Terra, Aqua, Suomi NPP;
radar: TerraSAR-X (2007), TanDEM-X (2010), COSMO-SkyMed 1–4 (2007–2010), RADARSAT-2 (2007), RISAT-1 (2012), Sentinel-1A (launched 3 Apr 2014, commissioning).
Not yet launched: SPOT 7 (30 Jun 2014), ALOS-2 (24 May 2014), WorldView-3 (13 Aug 2014), Gaofen-2 (19 Aug 2014).

### 3.4 Coverage statement

The locality was imaged daily only by sensors of 250–375 m resolution, which cannot resolve metre-scale debris. No listed public scene of
≤ 30 m resolution exists for 8 Mar–30 Apr 2014. Restricted government or commercial imagery may exist (tasking 3–28 Apr is on record) but is not listed.
For the composed test, satellite imagery over L is **not assessed** (no data), and must not enter as a non-detection.

## 4. Inputs handed to the other legs

- Q5 (beacon physics): contact data above, with the three offset values (3 km W, < 2 km, about 1.85 km) and the two first-contact durations (15 min vs "quick") carried as alternatives; depth about 4,500 m; detector practical range 2,000 m; no recording; reacquisition failures 6 and 8 Apr; submarine nil; sonobuoys nil 6–17 Apr.
- Q6 (searched areas): drifted Haixun area searched 13–17 Apr (ATSB 2017 Table 17); 8 Apr sonobuoy box 250 km²; 432 km² Chinese/Echo acoustic box (C).
- Q7 (drift): white objects, no position; checked, unrelated.

## 5. Open issues

1. ATSB 2017 Table 17 "SLDMB drop" and "Sightings" columns for 13–17 Apr are garbled in the text extraction; read the PDF table (the Drive copy is over the 10 MB connector limit; atsb.gov.au did not respond to the sandbox).
2. Hour of the first contact; reconcile 15 min (ATSB) with "quick" (JACC) and "> 10 min" (CCTV). A Chinese MSA or CMSRC primary report was not found.
3. Second-contact offset: 3 km W (ATSB) vs < 2 km (JACC) vs about 1 nmi (CCTV).
4. White-object position, count and the ship that checked them: not public. Resolve the "2,700 km" task-area conflict.
5. AGO satellite tasking footprints 3–28 Apr: not public; request from ATSB / Defence.
6. Commercial archives (Maxar Discover, Airbus OneAtlas, e-GEOS, DLR, MDA, CRESDA, GISTDA) need registration; not tested.
7. UK MoD statements (HMS Echo 14 Apr, Tireless 24 Apr) read only as search extracts (B).

## Sources (BibTeX keys in `sources-sightings-references.bib`)

A: atsb2017operational (pp.29–41, 116–119; printed = PDF − 9); atsb2015searchareas (pp.11–13; printed = PDF − 5); mot2015factual (pp.59–60);
mot2018mh370 (pp.136–137, 364–365); icao2014wp30 (§2.22–2.26); jacc2014mr010, jacc2014mr011–mr015, jacc2014tr006, jacc2014tr007, jacc2014tr008, jacc2014tr009,
jacc2014map012, jacc2014map013; data: nasacmr2026, usgsstac2026, nasacsda2026, cdse2026, celestrak2026.
B: ukmod2014echo, ukmod2014tireless. C: xinhua2014pulse, sina2014haixun, xinmin2014haixun, people2014floating, cn12371_2014, globaltimes2014expanded,
pti2014deccan, ap2014handheld, ulich2018north25.
