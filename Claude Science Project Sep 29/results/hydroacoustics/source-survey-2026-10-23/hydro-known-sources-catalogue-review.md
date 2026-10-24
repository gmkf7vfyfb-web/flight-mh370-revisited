# Known non-impact sources, 6-10 March 2014: online catalogue survey for H01W, H08S and the IMOS loggers

Track: online databases and catalogues for known (non-impact) sources. Prepared 23 Oct 2026. Status: review note for the hydroacoustics module. All counts come from queries run in this session unless marked otherwise.

## Deviations and limits (read first)

1. **ISC arrivals, later weeks: not retrieved.** The ISC arrivals search gave the IDC-associated arrivals at H01W1 and H08S1 for 6-10 March only. The queries for 11 March-30 April, and for H08N1, II.DGAR and II.COCO, failed. The failures were HTTP 429, "request cannot be processed" pages and truncated responses. For the later weeks, coverage comes from the event catalogues only.
2. **Earthquake selection is a rule, not the full catalogue.** The event table holds (a) all events in the region box (70 S-10 N, 40-130 E) on 6-10 March from ISC, USGS, EMSC, GEOFON and Global CMT, and (b) global events from 7 March 12:00 to 8 March 06:00 with M >= 4.0, or located by IDC. Global events below M 4.0 outside the box are left out (about 800 ISC records, mostly small onshore events far from the receivers).
3. **The path flags are coarse.** I sampled the land, shelf and ridge flags from ETOPO1 at 0.25° (NOAA ERDDAP). The flags are only indicative. IDC observed T phases on paths that this flag marks as "ridge" or "shelf". No mode or parabolic-equation propagation was run.
4. **The arrival times use a simple rule.** The rule is great-circle (WGS84 geodesic) distance divided by 1.48 km/s, from the epicentre. The "alt" column replaces the seismic leg to the first point deeper than 1,000 m with 8.0 km/s. Station positions are the FDSN centroids of the H01W and H08S triplets.
5. **Not downloaded, by choice or by need:** the AMSA March 2014 AIS file (needs a copyright and disclaimer click-through, which I did not accept on Pete's behalf); the ISC-GEM form (needs a user identity); Global Fishing Watch (needs a free API token, not held); and the ERA5 CDS API (the stored COPERNICUS credential is an account login, not an API token). I read ERA5 from the open ARCO copy instead. The AADC Casey 2014 recordings are large and were not downloaded.
6. **Sources not reached today:** the Smithsonian weekly reports (site "temporarily unavailable", HTTP 403). The GVP eruption database (WFS) was reached.
7. **Not tested in code:** NOAA PMEL catalogues, the GA 2014 survey shapefiles, WWLLN and GLD360 (paid), MarineCadastre (US waters only), and the Copernicus Marine iceberg products. The reason for each is in the table.
8. **Altiberg dates may be off by one day.** The day index is days since 1990-01-01, and the first 2014 record is 8,767. I also dropped 4,872 records that had invalid time values.

## Database counts (45 databases tested or assessed; see [source-catalogues.csv]({{artifact:d02397a5-874c-4d63-86bc-8574a9e1e151}}))

| Group | Count | Databases |
|---|---|---|
| (i) open (or held) download and includes March 2014 | 29 | USGS ComCat (FDSN event); ISC Bulletin (FDSN event, prime hypocentres); ISC Bulletin arrivals: IDC hydroacoustic T phases at H01W1/H08S1; ISC-EHB; EMSC SeismicPortal (FDSN event); GEOFON event service; Global CMT; EarthScope FDSN dataselect: seismic stations recording T phases (II, IU, G, AU, S1); GEOFON FDSN dataselect (GE network); RESIF FDSN dataselect (G network mirror); Smithsonian GVP Volcanoes of the World (WFS eruption table); Smithsonian GVP Weekly Volcanic Activity Reports; CNEOS fireball database; BYU/NIC Antarctic Iceberg Tracking Database (consolidated v8); US National Ice Center Antarctic iceberg archive; Altiberg small-iceberg database v3.1; NSIDC Sea Ice Index (G02135) daily extent, Southern Hemisphere; OBIS occurrence API (Cetacea); GBIF occurrence API (Cetacea); IWC-SORP Annotated Library of Antarctic blue and fin whale sounds; AADC long-term underwater acoustic recordings (AAS_4102); SEANOE 10.17882/46124: OHASISBIO Antarctic blue whale Z-call detections; IMOS AODN passive acoustic observatories; NOPTA Seismic_Surveys FeatureServer (NOPIMS/NEATS); CMST 2014-30 MH370 passive acoustics report; AMSA Craft Tracking System monthly vessel traffic (March 2014); ARCO-ERA5 (Google public dataset, Zarr); IOC Sea Level Station Monitoring Facility; NOAA NDBC DART historical data |
| (ii) free registration needed | 3 | ISC-GEM; Global Fishing Watch API (AIS-derived vessel presence and fishing effort); ERA5 hourly single levels via Copernicus CDS |
| (iii) request-only or paid | 6 | EarthScope FDSN dataselect: IMS hydrophones (IM.H01W*, H08S*, H08N*); IDC REB / LEB / SEL bulletins and SLSD detections; OHASISBIO raw hydrophone data 2014; WWLLN lightning strokes; Vaisala GLD360; EarthScope IMS infrasound (IM.I04/I06/I07/I52) |
| (iv) no 2014 coverage, no coverage of the region, or retired | 4 | EarthScope (IRIS) FDSN event service; Copernicus Marine iceberg and Antarctic high-resolution sea-ice products; MarineCadastre AIS; NOAA PMEL hydroacoustic event catalogues |
| (v) coverage not determined | 3 | OBIS-SEAMAP; Geoscience Australia Marine Seismic Survey shape/KML files (2014 version); EPBC Act public portal (referrals) |

## Earthquake catalogue returns (region box)

| Catalogue | Primary window (7 Mar 18:00-8 Mar 06:00) | Extended (6-10 Mar) | March-April 2014 | Oceanic part (south of 15 S), Mar-Apr: n / min / median magnitude |
|---|---|---|---|---|
| ISC Bulletin | 16 | 146 | 1747 | 152 / 3.32 / 3.9 |
| USGS ComCat | 7 | 38 | 437 | 37 / 3.8 / 4.6 |
| EMSC | 3 | 31 | 261 | 9 / 4.6 / 4.8 |
| GEOFON | 2 | 30 | 257 | 9 / 4.56 / 4.82 |
| ISC-EHB | 1 | 17 | 133 | 9 / - / - |
| Global CMT | 0 | 6 | 42 | 7 / 4.9 / 5.0 |

The magnitude columns are empirical indicators, not formal completeness magnitudes. In the oceanic part, ISC goes about 0.7 magnitude units lower than USGS (median 3.9 against 4.6), because it holds IDC events located from T phases. After merging across catalogues (60 s and 150 km rule), the event table holds 174 earthquakes.

## Check of the 1.48 km/s rule against observed IDC arrivals

The ISC Bulletin lists the IDC-associated arrivals at H01W1 and H08S1. For 6-10 March 2014 there are 12 at H01W1 (11 T, 1 P) and 13 at H08S1 (all T). For the 24 T arrivals, observed minus predicted time has median +10 s, SD 46 s and range -111 to +71 s, over distances of 832-7862 km. The rule is therefore good to about ±2 min. The IDC-associated sources were mb/MS 3.2-5.2 events on mid-ocean ridges, Sumatra, Java and the Andaman arc, the Macquarie ridge and the South Pacific.

**No IDC-associated arrival at H01W1 or H08S1 falls inside the 8 March windows.** At H01W1 the associated arrivals nearest the window are 20:55:51 on 7 March (Western Indian-Antarctic Ridge, MS 3.6) and 08:43:09 on 8 March. At H08S1 the nearest are 14:52:39 on 7 March and 09:28:48 on 8 March. This list holds only arrivals that IDC associated with REB events. The unassociated detections (SLSD) are request-only.

## (a) Earthquakes with a predicted arrival inside, or a coda reaching into, the 8 March windows

The windows are H01W 00:25-02:20 UTC and H08S 00:45-02:50 UTC. "IN" means the predicted arrival is inside the window. "coda" means the predicted arrival is 0-15 min before the window opens, so the T-phase coda can extend into it. The angle in brackets is the back-azimuth at the receiver.

| Event | Catalogues | Origin (UTC) | Lat, Lon | Size | Place | H01W predicted | H01W path | H08S predicted | H08S path |
|---|---|---|---|---|---|---|---|---|---|
| EV076 | isc | 2014-03-07T23:08:29.39 | -3.7799, 150.5861 | mb1 4.0 | New Ireland region | 00:05:52 (55.8°) - | blocked: crosses land | 00:45:55 (92.3°) IN | blocked: crosses land |
| EV077 | isc | 2014-03-07T23:12:53.67 | 28.8563, 68.7385 | mb1 3.6 | Pakistan | 00:48:48 (320.0°) IN | inland or long seismic leg (2170 km); open deep-water path | 23:58:35 (354.5°) - | inland or long seismic leg (1116 km); crosses shelf <200 m |
| EV078 | isc | 2014-03-07T23:27:16.24 | -6.9723, 129.3775 | mbtmp 3.6 | Banda Sea | 00:06:16 (30.3°) - | blocked: crosses land | 00:37:58 (93.3°) coda | blocked: crosses land |
| EV079 | isc;usgs | 2014-03-07T23:52:17.62 | -9.5511, 108.4208 | mb 4.04 | South of Jawa | 00:24:34 (346.9°) coda | crosses ridge/plateau 200-1000 m | 00:36:53 (95.7°) coda | open deep-water path |
| EV080 | emsc;geofon;isc;usgs | 2014-03-08T00:07:36.93 | -24.4116, -67.1904 | MW 4.96 | Chile-Argentina border region | 02:38:57 (178.6°) - | inland or long seismic leg (3611 km); blocked: crosses land | 02:49:40 (229.5°) IN | inland or long seismic leg (1930 km); blocked: crosses land |
| EV081 | isc | 2014-03-08T00:22:02.80 | 4.6369, 126.9653 | mb 3.37 | Talaud Islands | 01:13:35 (19.7°) IN | blocked: crosses land | 01:31:52 (79.1°) IN | blocked: crosses land |
| EV083 | isc | 2014-03-08T00:56:53.35 | -6.6275, 129.6086 | ML 3.8 | Banda Sea | 01:36:24 (30.5°) IN | blocked: crosses land | 02:07:54 (92.9°) IN | blocked: crosses land |
| EV084 | isc;usgs | 2014-03-08T01:13:09.01 | 2.3308, 128.2278 | mb 3.93 | Halmahera | 02:02:25 (22.6°) IN | inland or long seismic leg (375 km); blocked: crosses land | 02:23:57 (82.1°) IN | blocked: crosses land |

Interpretation:
1. No catalogued earthquake has an open deep-water path and a predicted arrival inside either window.
2. **EV079 (south of Java, mb 4.04, ISC and USGS, 23:52:17 UTC on 7 March) is the main confound.** The predicted H01W arrival is 00:24:34, 26 s before the window opens, at back-azimuth 346.9°. The predicted H08S arrival is 00:36:53, about 8 min before the window, at 95.7°, on an open deep-water path. The rule's uncertainty is about ±2 min. So the T phase at H01W can fall inside the window, and the codas can reach into both windows. The source is a catalogued earthquake to the north of H01W.
3. Four events (EV076 New Ireland, EV081 Talaud, EV083 Banda Sea, EV084 Halmahera) are predicted inside a window, but the great-circle path crosses the Indonesian islands. EV080 (Chile-Argentina, intermediate depth) and EV077 (Pakistan, inland) are not credible T-phase sources at these receivers.
4. EV083 (Banda Sea, ML 3.8, ISC) has a back-azimuth at H08S of 92.9°. This matches the CMST H08S detection at 01:58:55 from 93° (Table 4, "small earthquake in the Java Trench"). But the predicted time is 02:07:54, about 9 min later than the detection, so the match is not accepted. That detection stays unresolved.

## CMST 2014-30 detections with no catalogue match

| Detection | Receiver | Time (UTC, 8 Mar) | Bearing | Result |
|---|---|---|---|---|
| Detection of interest | HA01 (H01W) | 01:34:50 | 301.6° | No event; the only catalogued events on this bearing within ±15 min are ML 0.9-2.0 onshore events in Italy, Greece, Turkey and Jordan |
| Discrete detection | HA08S | about 00:11-00:12 | 168.05° | No event |
| Discrete detection | HA08S | 01:58:55 | 93° | Only the Banda Sea ML 3.8 candidate, +9 min; unresolved |
| Clock cross-check | HA01 | 04:59:21 (high SNR) | 210.2° | No event |
| Clock cross-check | HA01 | 05:14:28 | 208.5° | No event |

The two H01W clock cross-check events are high-SNR arrivals from the Southern Ocean, and no catalogue holds either of them. This shows directly that the public catalogues miss many sources that H01W records clearly. A clean catalogue window is therefore weak evidence of a quiet source field.

## (b) Volcanic, bolide, iceberg, survey and other activity

1. **Seismic surveys (airgun arrays).** NOPTA lists 4 Australian offshore 3D acquisitions whose dates overlap 6-10 March 2014: Huzzas MC 3D Phase 1 (TGS, Geo Caspian, to 12 Mar), Centaurus 3D (Woodside, Polarcus Alima, to 12 Mar), Fortuna 3D (Woodside, Vespucci, Northern Carnarvon Basin, 6 Jan-30 May) and Nerites MC 3D Phase 1 (TGS, Polar Duchess, Bight Basin, about 34.9 S 132.1 E, 20 Jan-3 Jun). Huzzas and Centaurus are already in the ground-truth table. **Fortuna and Nerites are new candidates.** The NOPTA dates are acquisition spans, so shooting on 8 March is not confirmed. Nerites is about 1,635 km east of H01W at back-azimuth 95°. The coarse flag marks the path as crossing land near Cape Leeuwin, which needs a proper bathymetric check. CMST also reports a survey on bearing 35° from HA08S ("off Sri Lanka or in Bay of Bengal") all through 00:00-03:00. No public database identified its operator. Later in the period: Babylon 3D (from 21 Mar), WA484P 3D (from 24 Mar) and Lord 3D (from 20 Apr). No 2D survey line overlaps March-April 2014.
2. **Volcanoes.** 13 GVP eruptions in the region were active on 6-10 March. Heard (eruption from 2012-09-05) and McDonald Islands (no end date in GVP) are the only ocean-island volcanoes with open paths to H01W, at about 3,760-3,820 km and back-azimuth about 225°. The rest are on Sumatra, Java and the islands to the east, and their paths are flagged shelf or land. Slamet started on 8 March 2014 and Merapi on 9 March (GVP start dates). Neither is a submarine source.
3. **Bolides.** CNEOS lists no fireball anywhere on 6-10 March 2014. The nearest later in time in the region is on 29 March 2014 at 28.7 S 121.5 E (0.13 kt, over Western Australia).
4. **Icebergs and sea ice.** The BYU/NIC database places 16 named large icebergs in 40-130 E on 6-10 March, all at 64.8-68.2 S. Altiberg has 60 small-iceberg detections in the sector on 6-10 March; the northernmost is at 55.3 S 90.7 E (0.017 km², 8 March). The Antarctic sea-ice extent was 4.10-4.19 million km² on 7-8 March (NSIDC), near the seasonal minimum. Ice sources are therefore 15° of latitude or more south of the arc. They are still the most likely class for the many CMST H01W detections from 158-209°.
5. **Whale calls.** The SEANOE OHASISBIO Z-call file (Leroy et al. 2016) has 366 detections in the primary window and 2574 on 6-10 March at 5 SW Indian Ocean sites. 78 fall between 00:25 and 02:50 on 8 March (MAD 9, NCRO 1, SSEIR 1, SWAMS 2, WKER 65). Antarctic blue whales were calling across the basin during the window, at about 18-28 Hz. Visual records (OBIS 0 and GBIF 7 in the extended window) have no value for this.
6. **Weather and sea state (ERA5, ARCO copy).** Over 20-40 S, 88-110 E the mean 10 m wind was 8.65999984741211-8.949999809265137 m/s and the mean Hs was 3.190000057220459-3.2899999618530273 m. Near H01W the mean wind was 7.460000038146973-9.970000267028809 m/s; near H08S it was 2.0799999237060547-3.490000009536743 m/s. Hourly values are in the records bundle.
7. **Tsunami and tide gauges.** The 7 Indian Ocean DART buoys with data report only 15-minute records in the primary window, with no event-mode triggers. IOC gauges returned data at 11 of 16 stations tested.
8. **Lightning and shipping.** WWLLN and GLD360 are paid. Global Fishing Watch needs a free token. AMSA's March 2014 AIS file is the best free shipping record for the arc area; it needs one click-through.

## Receivers found as a by-product

1. Public seismic waveforms for the full primary window: II.DGAR (Diego Garcia, next to H08), II.COCO (location 10), G.AIS (Amsterdam Island), G.PAF, AU.XMIS, AU.GIRL, IU.NWAO, IU.MBWA, S1.AUALB and GE.KAAM (Maldives). They are in [returned-waveforms-12h.zip]({{artifact:fe96bfde-27f9-40c8-8a61-d211e76deccf}}). An island station can record T phases, so these are an independent and public check on H08S and H01W.
2. AADC long-term recordings (AAS_4102) list a downloadable Casey 2014 dataset. Miller et al. (2021) Table 2 gives Casey 2014 (63.8 S 111.8 E, 2013-12-25 to 2014-12-12) and S Kerguelen Plateau 2014 (62.4 S 81.8 E, from 2014-02-22). Both moorings were recording on 8 March 2014. Their duty cycle and frequency band must be confirmed before use.

## Files

- [known-events-6-10mar2014.csv]({{artifact:df0f8673-f306-41ef-9b41-11e2230e3f70}}) - 298 rows: 174 earthquakes, 13 eruptions, 16 large icebergs, 60 small-iceberg detections, 5 surveys, 25 Z-call site-day counts and 5 unmatched CMST detections, with distances, back-azimuths, path flags, predicted arrivals and window flags.
- [source-catalogues.csv]({{artifact:d02397a5-874c-4d63-86bc-8574a9e1e151}}) - 45 databases with access, coverage, test result, counts, completeness, usefulness and notes.
- [returned-records-catalogues.zip]({{artifact:a67afdbc-0eaf-42c2-9f2b-99fa59c88386}}) - raw query returns: catalogue text files, ISC/IDC arrivals, GCMT, GVP, CNEOS, BYU and Altiberg subsets, NSIDC, OBIS/GBIF, OHASISBIO Z-calls, NOPTA, IOC, DART, ERA5 summaries.
