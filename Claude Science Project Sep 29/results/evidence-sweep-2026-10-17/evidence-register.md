# Evidence sweep: evidence types not yet in the estimate (17 Oct 2026)

Scope. A broad online sweep of official sources (ATSB, CSIRO, Malaysian Safety Investigation Team, CTBTO, Geoscience Australia) and unofficial sources (independent analysts, journalism, peer-reviewed independent work). Each item is compared against the repository on branch `claude-science-sep29` (ARCHITECTURE.md, module briefs, coordination inboxes, results/, and the Sep 28 archive), searched by keyword.

Status codes used in the table:
- **IN**: in the estimate now.
- **PARTIAL**: in the estimate, but in a reduced form.
- **DEFERRED**: named in a brief or inbox but not built.
- **NOT FOUND**: no mention in the repository.

## 1. What the estimate already uses (baseline for the comparison)

Satcom BTO and BFO, including the 18:25 and 00:19 log-ons and the unanswered calls. Primary radar to 18:22. Fuel and performance. End-of-flight descent families. Settling. Debris drift: finds, find timing, windage classes, the flaperon isotope screen (one-sided), and the Western Australia non-recovery term (in progress). Hydroacoustics: CTBTO H01 and H08, the IMOS loggers, and the Curtin, Kadri, Duncan and OHASISBIO prior work (the OHASISBIO report has not been obtained). Seabed searches: Bluefin-21, ATSB Phase 2, Ocean Infinity 2018 and Ocean Infinity 2025-26. Pléiades and COSMO-SkyMed imagery. WSPR and antenna gain (received power) are NOT in the estimate; see section 2D.

## 2. Candidate evidence types, ranked

### A. High value, quantifiable now

| # | Evidence | Observable and likelihood form | Informs | Status | Key sources |
|---|---|---|---|---|---|
| A1 | 2014 aerial and ship surface search (non-detection) | Cumulative probability of detection (POD) per drifted debris particle on each search day; P(no sighting \| impact) = Π(1 − POD). CSIRO found it effective north of 33° S and ineffective south of 34° S | impact latitude (strong against about 25–32° S) | DEFERRED (drift brief: 387 day-labelled polygons; licence under review) | CSIRO Drift II and IV; ATSB First Principles Review 2016 |
| A2 | Other 2014 satellite imagery of floating objects | Positions and sizes of objects, treated as Pléiades is: transport from impact to image time, with a false-alarm rate. WorldView-2 (16 Mar, AMSA), Gaofen-1 (18 Mar, 22 × 13 m), THEOS (24 Mar, about 300 objects), Japanese satellite (26 Mar, 10 objects) | impact latitude, impact time | NOT FOUND (only Pléiades and COSMO-SkyMed) | AMSA/JACC releases 2014; GISTDA; CNSA |
| A3 | Satellite imagery coverage with no objects seen | Imaged footprints in which no objects were seen; this is a surface non-detection of the same kind as A1, with a sensor-specific POD | impact latitude | NOT FOUND | Geoscience Australia (Minchin et al. 2017) tasking records; MRSA |
| A4 | Barnacle geochemistry as a two-sided likelihood | δ18O and Mg/Ca sea-surface-temperature time series against the temperature history modelled along each drift path (Al-Qattan et al. 2023 used 50,000 drifters). Today only a capped penalty is applied | impact latitude, through the drift path | PARTIAL (one-sided flaperon screen; review item E12) | Al-Qattan et al. 2023 AGU Advances doi:10.1029/2023AV000915; Blamart and Bassinot (unpublished, French judiciary) |
| A5 | Barnacle age and size, and species composition | Capitulum size with a growth law gives time since colonisation (now disputed: Mesaglio/Suthers growth rates give an age of about 4 months for 36 mm). Only *Lepas anatifera* was present, with no cold-water *L. australis* | drift timing; time spent in cold water | DEFERRED (18 °C threshold, "biofouling") | Poupin 2015 (Malaysian report, appendix 2.6a); Mesaglio et al. 2021 |
| A6 | Debris damage and configuration | The ATSB found the flaps retracted at separation and the flaperon near neutral, and cabin-interior debris shows breakup. Independent work disputes this (Vance: ditching; Kenyon: flutter, in-air separation). As a likelihood on end-of-flight family (high-energy vs piloted ditching), with the dispute carried as alternatives | distance from the 7th arc, through family weights | NOT FOUND as evidence (used only for windage class) | ATSB debris updates Nov 2016 and Aug 2017; Malaysian report 2018; Vance 2018; Kenyon 2020-21 |
| A7 | Indonesian military radar non-detection | Lhokseumawe (Radar Unit 231, about 240 NM) and Sabang reported no detection. P(no detection \| route) from radar coverage and detection probability, with an alternative "detected but not reported" | early route after 18:22 (route stratum) | NOT FOUND | Jakarta Post 14 and 19 Mar 2014; Antara |
| A8 | Infrasound (CTBTO IMS) non-detection | The IDC searched only near the take-off region. Stations IS06 (Cocos), IS04, IS07 and IS52 (Diego Garcia). Use the same prediction, power and coverage format as hydroacoustics | impact energy and time; weak on latitude | NOT FOUND (one paper in inputs) | CTBTO IDC infrasound report 2014; LLNL Cocos study |
| A9 | OHASISBIO hydrophones (Royer, CNRS) | Six moorings (Crozet, Kerguelen, Madagascar Basin, Southeast Indian Ridge), recovered Jan–Feb 2015. Royer's 2016 report surfaced through journalism in July 2026 | impact time and position; detectability | PARTIAL (registered; report and data not obtained) | Wise, Popular Mechanics, 16 Jul 2026 |

### B. Medium value, or more work for less information

| # | Evidence | Observable | Informs | Status |
|---|---|---|---|---|
| B1 | Aerial-search photographed contacts (29 Mar 2014) | Positive detections of unidentified objects, with a false-alarm model (Iannello 2017) | impact latitude (north of 33° S) | NOT FOUND |
| B2 | ELT non-detection | No 406 MHz alert. The Indian Ocean GEO relays (Insat-3A, Electro-L1) should have received one. Likelihood of ELT survival and activation by impact type | end-of-flight family; not latitude | NOT FOUND |
| B3 | Towed-pinger and sonobuoy acoustic search for the recorder beacon (Apr 2014) | Passive acoustic coverage while the CVR beacon battery lasted (FDR beacon battery reportedly expired). This is AF447 Step 2 in Stone et al. 2014 | seabed location, in a narrow area | PARTIAL (Bluefin-21 area only) |
| B4 | Non-recovery on other coasts | Indonesia (Sumatra, Java), Sri Lanka, Maldives, India, and Kerguelen and Amsterdam islands, each with a reporting-probability tier as for Western Australia | impact latitude (northern sources) | PARTIAL (WA only) |
| B5 | Refloat and beaching history | Fouling patterns across items (barnacle-free "Roy", abrasion under growth on the flaperon) | find timing, residence time ashore | DEFERRED |
| B6 | Co-pilot's phone registration (about 17:52, Penang) | Network registration time and cell | consistency check before 18:01 | NOT FOUND |
| B7 | Maldives and Indian Ocean radar non-detection | MNDF military and civil radars reported nothing | rules out western routes (already excluded by satcom) | NOT FOUND |

### C. Screened; little or no information, or not compatible with the data

| # | Item | Reason |
|---|---|---|
| C1 | Home flight-simulator waypoints (file dated 3 Feb 2014, ending far south) | Bears on intent, not on position. The ATSB stated it was not consistent with the satcom tracks. At most a labelled conditional hypothesis (route prior towards about 45° S), never a likelihood. |
| C2 | Near-surface carbon monoxide (Rolston 2026, NASA data, 23–24° S) | No physical source model links aircraft impact to a column-CO anomaly. Could be run as a negative control against same-day climatology, but not as evidence. |
| C3 | Kuda Huvadhoo (Maldives) sighting, 01:15 UTC | After the final log-on at 00:19 and off the 7th arc, so zero likelihood under every satcom model. |
| C4 | Oil-rig (McKay) and yacht sightings | Locations and times are inconsistent with radar and satcom. |
| C5 | Seabed-impact seismic candidates (370location) | No trials accounting. This is the same failure as the independent hydroacoustic candidates. |

### D. Registered but not in the estimate: WSPR and received power (antenna gain)

| # | Evidence | Observable and likelihood form | Informs | Status | Evidence so far |
|---|---|---|---|---|---|
| D1 | WSPR (amateur HF links as a passive radar) | Per link: P(anomaly \| aircraft on the link path) against P(anomaly \| no aircraft), from a receiver operating characteristic (ROC) calibrated on independent known flights. Path likelihood = product over links, with blocked (flight/day/station) dependence | whole track, including the end point | NOT IN ESTIMATE. Pete's prior control test exists; the pre-registered validation gate was proposed and not performed | Pete's control test (review manuscript §3.6, CLAIM-LEDGER): over 24,000 candidate paths the true path sat at the 43.6th weighted percentile, and choosing the top tenth by WSPR score raised mean path RMSE from 150.8 to 291.2 km. Published ROC areas under the curve are 0.59-0.67. No peer-reviewed Liverpool result found (Oct 2026) |
| D2 | Received power, C/N0 and BER per burst (SITA logs) | Per burst: rx dBm = constant + β·G(azimuth and elevation relative to the airframe; attitude) + noise. β = 0.63 ± 0.04 (Pete 2019, n = 937). The gain surface is a model alternative | mainly heading and attitude at each epoch, and through them the track; weak on 7th-arc position | NOT IN ESTIMATE (antenna-gain module parked). Used today only as a data-quality flag (the 18:25:27 burst) | The existing whole-path likelihood spans about 4.4 nat along the arc (−4.1 at 38-40° S, about −0.9 at 26-32° S), conditional on the gain surface and headings. At 00:19 alone, 37° S and 26° S differ by 0.1-0.9 dB of received power against a 0.5 dB noise floor; heading moves gain by 11.6-14.1 dB |

Assessment.
- D1 is quantifiable in principle, but no independent test has shown that it carries information, and Pete's own control test shows it does harm. It should enter only through the pre-registered gate (Downloads/resolution/agents/alternative_redteam/wspr_validation_protocol.md). Otherwise it is reported as "tested, carries no information", in the same format as a hydroacoustic null.
- D2 is real data, already held, and it is a per-epoch function of the state the core filter already samples. It belongs in core as a satcom-epoch likelihood, with gain-surface alternatives marginalised. It is not new information about position at the 7th arc. Its value is as a separate check on heading and attitude at every epoch, including the 00:19 attitude question and the no-precompensation conditional hypothesis. First step: decompose the 4.4 nat epoch by epoch along sampled paths, to find which epochs produce it before any integration.

### E. Second pass (17 Oct 2026, later): further items

| # | Evidence | Observable and likelihood form | Informs | Status | Sources |
|---|---|---|---|---|---|
| E1 | Positive controls for sonar detection: the two 19th-century shipwrecks found in ATSB Phase 2 | Known targets found by the same sensors and processing give an empirical check on the detection ratings (q) and on ρ | seabed-search q and ρ (today ρ has no published value) | NOT USED for detection (cited only in settling) | Anderson 2018, WA Museum for the ATSB |
| E2 | Merchant, fishing and transiting search vessels as opportunistic surface observers (AIS tracks, Mar-May 2014) | Low-POD surface non-detection over a large area and time, added to A1 in the same drift observation model | impact latitude | NOT FOUND | AIS archives (commercial) |
| E3 | Sea state, wind, cloud cover and daylight on each search and imaging date | NOT evidence. These are the covariates that set POD for A1, A2, A3, E2 and Pléiades. Without them, any surface term uses a constant POD | all surface terms | NOT FOUND (no sea-state or cloud fields in the repository) | ERA5 waves and wind; MODIS/Himawari/Meteosat-7 cloud |
| E4 | Expanded debris set beyond the stringent nine | About 60 items have been picked up and more than 30 examined; some were handed in but not collected or examined. "NO STEP 2" (Evatra, Madagascar, about 25° S 47° E, find date unknown) was reported in 2025. Each enters as a provenance-weighted observation, P(from MH370) × drift likelihood + (1 − P) × background, with interval-censored find dates | impact latitude; find timing on the south Madagascar coast | PARTIAL (drift scores 9) | Malaysian debris summaries 2017 and 2018; Gibson; Changing Times Dec 2025 |
| E5 | Contrails seen from satellites (Meteosat-7 IODC, MODIS long-wave IR) | Contrail formation from ERA5 temperature and humidity (Schmidt-Appleman) along each candidate path, then detection against the image. The 2014 claims are disputed (resolution, wind advection) | early turns 18:22-18:40; southern track | NOT FOUND (core has the Poll-Schumann performance model only) | Ulich and Prostyakov (claim); Vasquez/Meteosat-7 2014; Metabunk critique |
| E6 | Indian (Andaman) radar non-detection | As A7, with the alternative "not operating" | early route | NOT FOUND | press reports, Mar 2014 |

Screened on the second pass (no location information under the model):
- **US infrared early-warning satellites: no explosion.** This is a statement about the period near Malaysia, not the southern ocean at 00:19, and the data are not public. It bears only on in-flight-explosion hypotheses.
- **Fire or plume at impact (VIIRS night fires, the MODIS "plume" candidate).** After fuel exhaustion no fuel fire is expected, so absence carries no information. The candidates have no trials accounting.
- **ATSB finding that the Madagascar items were not exposed to heat.** This bears only on fire hypotheses.
- **SIGINT-satellite receptions of the satcom bursts.** Speculative and not available.

## 3. Suggested order of work

1. A1 and A3 together inside drift's observation model (the surface search belongs to drift by ruling). This is the term the ATSB and CSIRO weighted most against latitudes north of about 33° S, so it is probably the largest single gap.
2. A2 next, reusing the Pléiades machinery (same transport call, new image times and positions).
3. A4 and A5: turn the isotope screen into a two-sided likelihood, and carry the barnacle-age dispute as alternatives.
4. A6: an end-of-flight family likelihood from debris configuration, with the ATSB and independent interpretations as named alternatives.
5. A7: a route-stratum term in core.
6. A8 and A9: hydroacoustics' existing prediction, power and coverage format.
7. D2: the epoch-by-epoch decomposition of received power first (cheap), then a core likelihood if one or more epochs are selective.
8. D1: only through the pre-registered gate.

Second-pass additions to the order: E3 is a prerequisite of item 1 and must be built with it. E1 is cheap and goes to searched areas now. E4 goes to drift as an extension of the find list. E2 and E5 come last (high effort, low or disputed information).

Caveats. Source data for A1 (polygons) and A3 (footprints) are not all public. A2 object lists are partly from press releases only. The "flaps retracted" finding is contested in the literature. Nothing here has been computed; these are candidates only.
