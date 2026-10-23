cat > research-beacons-tpl-simulator-barnacles.md <<'EOF'
# Beacons, towed-pinger search, home flight simulator and flaperon barnacles: source review

Prepared 17 Oct 2026 for the MH370 Bayesian re-analysis (Journal of Navigation paper).

**Source tiers:** [O] official report or appendix; [P] peer-reviewed paper; [M] manufacturer document (read from a third-party mirror where stated); [N] news report; [I] independent analyst. Use [I] and [N] only for context.

**Page conventions.** In the Malaysian Safety Investigation Report (SIR, MH370/01/2018, issued 02 July 2018), "p." is the printed page. On the Drive copy and on the court-filed copy, PDF page = printed page + 46. In the ATSB *Operational Search for MH370* (AE-2014-054, 3 Oct 2017), PDF page = printed page + 9.

**Declared scope limits (deviations).**
1. The ATSB *Operational Search* was read only as the Drive text extraction of printed pp. 1–160. Its Appendix F (De Deckker, barnacle chemistry) and Appendix G (Geoscience Australia, organisms on debris) were cut off, so I did **not** read them. The ATSB website does not answer automated clients.
2. The Royal Malaysia Police (RMP) simulator report is on Pete's Drive ("RMP_Folder1 Pilot_Nihonmama.pdf", 40 MB; "RMP v good info Folder Appendix (1).pdf", 46 MB; "MH370 FLIGHT PLAN from RMP REPORT.pdf"). I did **not** read it, and I did not read the FBI document directly. The simulator coordinate table below comes from the Independent Group's transcription of the RMP data, so treat it as **provisional** until it is checked against the RMP pages.
3. The Al-Qattan et al. (2023) article page on Wiley refused automated access (Cloudflare HTTP 403). I identified the Supporting Information contents from the authors' Mendeley Data deposit, which carries the same SI document, and from the article's Data Availability Statement as quoted in search results.
4. SIR Appendix 2.6B is a scanned French document. I read the relevant pages as images (pp. 1, 3, 5, 6, 41–45, 47, 49, 50). I did not transcribe every table.
5. I read the Ocean Shield detection positions and the coverage geometry off ATSB figures (map grid), not from tabulated values, so they are approximate.

---

## Q1. Emergency locator transmitters (ELTs) on 9M-MRO

**Short answer.** 9M-MRO carried **four ELTs**. They were:
- one **fixed** ELTA 406-series unit (P/N 01N65900) above the aft cabin ceiling at STA 1880, with a triple-frequency blade antenna forward of the fin at STA 1881;
- one **portable** ELTA 406 unit (P/N 01N65910) in the forward right-hand coat closet;
- two **slide-raft** DME units (P/N P3-03-0029-10) at doors 1L and 4R. These transmit on 121.5/243 MHz only, are not satellite-enabled, and activate by water contact once the raft is deployed. [O: SIR pp. 53–54]

The fixed unit activates on sudden deceleration (g-switch). It transmits 406 MHz (identifier and registration) plus 121.5/243 MHz homing; the report puts VHF range at about 20 km line of sight. The cockpit aft overhead panel has a switch "guarded in the ARMED position", which the crew can move to ON. The SIR describes no OFF position on that panel. The battery expiry dates were Nov 2014 for the fixed and portable units, Aug 2016 for the 1L raft unit and May 2017 for the 4R raft unit. [O: SIR pp. 53–54] The report states that "no relevant ELT beacon signals" were reported by SAR agencies or other aircraft. [O: SIR p. 54, p. 365; finding 10 on p. 433]

**Official explanations for no signal:**
- ELTs do not transmit from deep water.
- Impact can damage the unit, or the antenna and its cable can disconnect or break ("very commonly in the case of fixed ELTs").
- Debris can shield the antenna.
- Cospas-Sarsat coverage is incomplete, and satellites no longer monitor 121.5 MHz.
- The SIR cites AF447 as a case where the ELT did not activate or was submerged. [O: SIR pp. 54–56, pp. 365–366]

**Activation statistics.** The SIR quotes ICAO ADREP data inconsistently:
- 39 effective activations out of 114 accidents with known ELT status (about 34%) [O: SIR p. 55];
- 39 out of 173 accidents [O: SIR p. 366];
- in Appendix 1.6D, 39 out of 257 accident records (aircraft above 5,700 kg, 1983 to June 2014), stated as 15%. The other categories in that appendix are: not activated 22, battery failed 14, damaged 11, internal failure 5, submerged 1, not carried 84, unknown 59. [O: SIR App. 1.6D, pp. 1–2]

The ATSB research report AR-2012-128 (2013) found that ELTs functioned as intended in about **40–60%** of accidents where activation was expected. [O: AR-2012-128, p. iii "Safety summary"] BEA's post-AF447 work concluded that automatic fixed ELTs (ELT-AF) triggered after survivable accidents but were destroyed in high-energy accidents. [O: BEA summary document] On AF447, the BEA's first interim report says that the one recovered ELT (a manually triggered type) had not been actuated and its switch was found in OFF. [O: BEA Interim Report 1, 2009]

**Could a deliberate actor disable it?** No official MH370 document discusses deliberate disabling of the ELTs. What the sources do say:
- The manufacturer handbook for the ELTA ADT406 AF/AP (P/N 01N65900) describes the cockpit remote unit as a guarded ON/ARMED switch (the cover forces ARMED) plus a RESET/TEST push-button. [M: ELTA handbook, read from third-party mirrors]
- The **OFF** position exists only on the toggle switch on the beacon itself. If that switch is not in ARMED, the remote panel is unpowered.
- RESET stops a transmission already in progress and returns the unit to ARMED.
- So, from the documents read, the crew cannot select OFF from the flight deck. Silencing the fixed unit would need access to the beacon above the aft cabin ceiling (switch, connector or antenna lead).
- The portable unit is normally OFF and needs manual activation (SIR p. 54). The raft units only work if a raft is deployed.

Any argument about a "deliberate actor" therefore rests on inference, not on official statements. **NOT FOUND:** any official statement on the ELT circuit breaker, or on in-flight access to the fixed ELT.

| Unit | Model / P/N | Location | Activation | Frequencies | Battery expiry | Source |
|---|---|---|---|---|---|---|
| Fixed ELT | ELTA 406 series, 01N65900 | Aft cabin ceiling, STA 1880; blade antenna STA 1881 | g-switch; cockpit guarded ARMED→ON | 406 + 121.5/243 MHz | Nov 2014 | SIR pp. 53–54 |
| Portable ELT | ELTA 406 series, 01N65910 | Fwd RH coat closet door | Manual switch (normally OFF); own foldable antenna | 406 + 121.5/243 MHz | Nov 2014 | SIR pp. 53–54 |
| Slide-raft ELT ×2 | DME, P3-03-0029-10 | Packed in slide-rafts at doors 1L and 4R | Armed on raft deployment; water sensor | 121.5/243 MHz only | 1L Aug 2016; 4R May 2017 | SIR p. 54 |

**What is obtainable and how.**
- SIR main report and Appendix 1.6D: public download from the Malaysian MOT website, and on project Drive (main report fileId 1eXn_nXdxnIL2xDNEJIMJaQRmLc02iId5; App 1.6D fileId 18nqWqo4W9ePq1dNOz9IS_akZ1JN7xtT7).
- AR-2012-128: public download.
- ELTA handbook: on public mirrors (a manufacturer copy should be requested from Safran/ELTA before citing).
- The 9M-MRO ELT installation wiring and circuit-breaker data are in Boeing/MAS maintenance documents. These are not public; request them from Malaysia Airlines or Boeing via the investigation.

---

## Q2. Underwater locator beacons (ULBs) on the flight recorders

**Short answer.** Both crash-protected recorders, the SSFDR (Honeywell 4700) and the SSCVR (Honeywell 6022), are in the E7 rack above the aft cabin ceiling. [O: SIR pp. 133–135] Each carried a **Dukane ULB**. The SIR gives the model as "DK-100 / DK-120"; ATSB gives DK100. The SIR specification is:
- 37.5 ± 1 kHz;
- 10 ms pulse, at least 0.9 pulse/s;
- operating depth to 6,096 m;
- **30 days minimum** operating life;
- 6-year battery life in the beacon;
- initial output 160.5 dB re 1 µPa at 1 m, falling to 157.0 dB after 30 days;
- activated by fresh or salt water. [O: SIR pp. 136–137]

The manufacturer predicted a maximum battery life of 40 days after activation. [O: ATSB 2017 p. 36 fn 20; ATSB June 2014 p. 11 fn 9]

**The SSFDR ULB battery had expired in December 2012** (ULB S/N SC26210), with no evidence that it was replaced. The SSCVR ULB battery was replaced on schedule and next expired in June 2014. [O: SIR p. 137; findings p. 364] The cause was a maintenance-tracking error: when the SSFDR was replaced on 29 Feb 2008, the new unit was not recorded as "installed" in the Engineering Maintenance System, so no battery-replacement call-out was raised. [O: SIR pp. 364–365]

Note an internal inconsistency: the SIR also gives the SSFDR "date last installed on aircraft" as 26 August 2012 (p. 134).

On performance past expiry, the SIR says a ULB "may operate, for a reduced time period", but meeting the 30-day minimum or staying within specification is not guaranteed. [O: SIR pp. 364–365]

**Explanations for no ULB detection** given in the sources:
- Detection range is limited: nominally 2–3 km, up to about 4.5 km in favourable conditions, and about 1 km is used for a robust search. [O: ATSB June 2014 p. 11]
- Environmental factors: thermoclines, ambient noise, marine life.
- Impact damage, burial in sediment, or shielding by debris.
- Ship noise. [O: ATSB 2017 p. 37]
- The search ended on 17 April 2014 because the batteries were then considered exhausted. [O: ATSB 2017 p. 36]
- The wreck was not where the 2014 acoustic search was conducted; the later seafloor search placed the 7th-arc area far to the south-west. [O: ATSB 2017; ATSB June 2014]

**Deliberate disabling.** No source read discusses it. ULBs are self-contained, battery-powered and water-activated (ATSB 2017 p. 36), with no aircraft power or cockpit control. Disabling one would need physical access to the recorders in the aft E7 rack above the ceiling. **NOT FOUND:** any official discussion of deliberate ULB disabling.

| Recorder | Model / P/N | ULB | ULB S/N | ULB battery expiry | Source |
|---|---|---|---|---|---|
| SSFDR | Honeywell 4700, 980-4700-042, S/N SSFDR-08636 | Dukane DK-100/DK-120 | SC26210 | **Dec 2012 (expired)** | SIR pp. 134, 137 |
| SSCVR | Honeywell 6022, 980-6022-001, S/N 2677 | Dukane DK-100/DK-120 | Not recorded | June 2014 | SIR pp. 136–137 |

**What is obtainable and how.**
- SIR and ATSB reports: public download, and on Drive.
- MAS hard-time component records and the EMS log: not public; request from Malaysia Airlines via the Malaysian investigation team (MH370SafetyInvestigation@mot.gov.my, as printed on the SIR cover).
- Dukane DK100 datasheet: public from the manufacturer (not fetched here).

---

## Q3. Passive acoustic (ULB) search, April 2014

**Short answer.** The acoustic search ran from **2 April to 17 April 2014**; 17 April was the last sonobuoy drop. [O: ATSB 2017 p. 36] The assets were:
- *Ocean Shield*, with US Navy Phoenix International TPL systems 01D and 03S (the "TPL-25" in media and Bremner 2015) and an Artemis (Bluefin-21) AUV;
- *Haixun 01*, with a Benthos hand-held hydrophone (5–80 kHz, practical range about 2,000 m) used from a rescue boat;
- *HMS Echo*, with a hull-mounted transponder system retuned to 37.5 kHz;
- an unnamed submarine (UK MoD and news identify it as HMS *Tireless*, in the area from about 1 April and stood down by 24 April);
- RAAF AP-3C sonobuoys. [O: ATSB 2017 pp. 36–39; ATSB June 2014 pp. 11–13; N: UK MoD 24 Apr 2014; naval-technology.com 1 Apr 2014]

The detections:
- **HMS Echo, 2 April:** discounted on 3 April as an artefact of the ship's own sonar.
- **Haixun 01:**
  - 4 April at **25.975°S, 101.461°E**, a 37.5 kHz pulse at 1/s for 15 minutes, in about 4,500 m depth;
  - a weaker second detection the next day, about 3 km west, lasting 90 seconds.
  - HMS Echo (6 and 8 April) and the submarine could not reacquire either. They judged them unlikely to be from MH370 because of the depth, surface noise and the equipment's range. [O: ATSB 2017 pp. 38–39]
- ***Ocean Shield* (TPL 03S):**
  - 5 April: about **33 kHz** for about 2 h 20 min while the TPL descended;
  - one further detection on 5 April and two on 8 April, each showing about 33 kHz and about 42 kHz components;
  - a fifth on 10 April (broadband 32–35 kHz, suspected TPL malfunction; not reported at the time);
  - none could be repeated on reverse tracks. [O: ATSB 2017 p. 39]

On Figure 12 of the June 2014 report, the four detections lie at approximately 20.95–21.2°S, 104.0–104.2°E (northern Zenith Plateau). I read these positions off the map grid; they are approximate. [O: ATSB June 2014 p. 13, Fig. 12]

Phoenix International's later bench test showed that a faulty high-resistance "self-test" cable could activate the TPL's own test ULB and shift it from 37.5 to 33 kHz with broadband noise. Independent reviewers (DST Group, AAIB, NTSB, Curtin, AJAAC, Dukane) found the signals inconsistent with a DK100. [O: ATSB 2017 pp. 40–41]

**Detection-range assumptions:**
- nominal ULB detection range 2,000–3,000 m (up to about 4,500 m), with about 1 km used for a robust search [O: June 2014 p. 11];
- the Figure 12 legend gives "Max. Effective TPL Detection Range (3 km)", "Max. Transmission of Pinger (10 km)" and a **2,400 m swath width** [O: June 2014 Fig. 12];
- the AP-3C sonobuoys (hydrophone at 300 m) could detect a ULB at up to 4,000 m, and one sortie covered about **3,000 km²** [O: ATSB 2017 p. 41; June 2014 p. 13].

Sonobuoys were dropped on 6–16/17 April near the Ocean Shield and Haixun 01 areas and along the CTBTO H01 (Cape Leeuwin) hydroacoustic bearing; none detected a ULB. [O: same] Figure 14 of the June 2014 report notes a sonobuoy detection "of different frequency" at its western edge. [O: June 2014 p. 15]

**Coverage map and area.** The coverage is published only as maps:
- June 2014 Fig. 12, "Ocean Shield TPL search coverage 04-14 April" (Phoenix International);
- ATSB 2017 Fig. 23, "TPL detections ... and TPL coverage polygons".

**NOT FOUND:** a stated total TPL area in km², or an area for the sonobuoy fields. A secondary account gives about 4.8 × 4.8 km per day for the TPL. [P: Bremner 2015, p. 16] Wikipedia's figure of about 130 km² per day is unsourced, so do not use it. The follow-up AUV side-scan search (14 April to 28 May 2014, 30 missions) covered **860 km²**: a 10 km radius around detection 2 and 3 km radii around detections 1, 3 and 4, with no debris found. [O: ATSB 2017 p. 42; June 2014 p. 14]

Independent analysts' views: Ulich (2018) measured a 33 kHz pulse period of 1.108 s on one recording and attributes the detections to drifting equipment beacons. [I] Thomson (2014 blog) gives a similar ping-interval analysis. [I]

| Asset | Equipment | Date(s) 2014 | Position | Signal | Outcome | Source |
|---|---|---|---|---|---|---|
| HMS Echo | Hull-mounted transponder system retuned to 37.5 kHz | 2 Apr | Near 7th arc, S4/S5 boundary | "possible ULB" | Discounted 3 Apr (own-sonar artefact) | ATSB 2017 p. 38 |
| Haixun 01 | Benthos hand-held hydrophone from rescue boat | 4 Apr | 25.975°S, 101.461°E | 37.5 kHz, 1/s, 15 min | Not reacquired | ATSB 2017 pp. 38–39 |
| Haixun 01 | same | 5 Apr | about 3 km W of above | 37.5 kHz, 90 s, weaker | Not reacquired | ATSB 2017 p. 38 |
| Ocean Shield | TPL 03S | 5 Apr (×2), 8 Apr (×2) | about 20.95–21.2°S, 104.0–104.2°E (read from Fig. 12) | about 33 kHz (+ about 42 kHz) | Not repeatable; AUV 860 km², nil | ATSB 2017 pp. 39–42; June 2014 Fig. 12 |
| Ocean Shield | TPL 03S | 10 Apr | same area | 32–35 kHz broadband | Suspected TPL fault | ATSB 2017 p. 39 |
| RAAF AP-3C | Sonobuoys, 300 m hydrophone | 6–17 Apr | OS/Haixun areas; H01 bearing × 7th arc | none ULB-related | about 3,000 km² per sortie | ATSB 2017 p. 41 |

**What is obtainable and how.**
- ATSB June 2014 report (updated 30 Jul 2015): public download, and on Drive (fileId 1lDHdjQhdoyiqRIck6Gkmdyur7g1ua_Lw).
- ATSB 2017: public, and on Drive as text only.
- TPL track logs, the coverage polygons as vector data, sonobuoy drop positions, and the acoustic recordings: not published. Request them from ATSB (coverage, Phoenix data) and from the Australian Defence Force/RAAF (sonobuoys).
- Ocean Shield audio: only the Defence video clips are public.

---

## Q4. Captain's home flight simulator data

**Short answer.** Official account (SIR):
- RMP seized the simulator on 15 March 2014, and the RMP Forensic Report is dated 19 May 2014.
- The report found more than 2,700 coordinates, mostly default game data, plus **seven "manually programmed" waypoint coordinates**. Connected, these make a path from KLIA through the Andaman Sea to the southern Indian Ocean.
- The coordinates were stored in a Volume Shadow Information file dated **03 February 2014**, so the RMP could not tell whether they came from one file or several.
- The RMP found no route resembling MH370 and "no unusual activities other than game-related flight simulations".
- The SIR prints a map only (Figure 1.5A, p. 28) and no coordinate values. [O: SIR pp. 27–28]

The ATSB (2017) gives a different account:
- data received on 19 April 2014 from the AFP;
- a partial reconstruction of a session on **2 February 2014**: four complete and two partial data captures for a B777-200LR;
- point 1 at KL airport; point 2 with no usable location; points 3–4 north-west up the Malacca Strait; point 4 at 40,000 ft in a 20° left bank, 4° nose down, heading 255°;
- points 5–6 about **820 NM south-west of Cape Leeuwin**, with fuel exhausted. Point 5 was at 37,651 ft, in an 11° right bank, heading 178°. Point 6 was 2.5 NM further on, 3° right bank, 5° nose down, heading 193°, with a user altitude input of 4,000 ft.

The ATSB says the simulated track was about 4,200 NM long, "further than was possible" with MH370's fuel, and **"not consistent with the aircraft tracks modelled using the MH370 satellite communications metadata."** It also notes that the first three points match the KL–Jeddah route the captain was rostered to fly on 4 February 2014. [O: ATSB 2017 pp. 98–99, Fig. 74]

The magazine and independent reporting:
- *New York* magazine (Jeff Wise, 22 July 2016) quoted a leaked RMP document. According to the document, the FBI recovered six deleted data points from the captain's 5 HDDs. [N]
- The Independent Group (IG; Iannello et al., 14 Aug 2016) tabulated parameters for six points from FSX `.FLT` fragments in a shadow-copy set, last modified 3 Feb 2014, ending near **45°S 104°E**. [I]
- Iannello & Guillaume (29 Nov 2016) argue that the points came from one simulated flight with manual repositioning, and that the aircraft model was an FS2004 add-on. [I]
- Wise later argued that the single-flight reading "unravels" (31 Aug 2016). [I/N]

The point counts and dates differ between sources: SIR seven waypoints on 3 Feb; ATSB six captures on 2 Feb; IG six points plus two parked at KLIA, last modified 3 Feb.

**Coordinates (provisional: IG transcription of RMP data, not checked against the RMP pages).** All ground speeds and fuel are as derived by the IG. Bank and pitch are from ATSB 2017 pp. 98–99.

| IG pt | Lat (°) | Lon (°) | Alt (ft) | Hdg (°) | GS (kt) | Total fuel (lb) | Fuel (%) | ATSB description | Source |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2.7480 | 101.7223 | 70 | 326.2 | 0.0 | 165,446 | 51.56 | At KL airport (runway 32R per Iannello & Guillaume) | IG 2016 Table 1 p. 2 |
| 2 | 3.4151 | 100.8856 | 23,247 | 305.3 | 403.1 | 157,850 | 49.20 | Malacca Strait, tracking NW | IG 2016 Table 1 |
| 3 | 5.1116 | 98.5879 | 32,246 | 314.8 | 433.6 | 156,263 | 48.70 | Malacca Strait, tracking NW | IG 2016 Table 1 |
| 4 | 10.1831 | 90.2245 | 40,003 | 255.5 | 469.5 | 152,253 | 47.45 | 40,000 ft, 20° left bank, 4° nose down, hdg 255° | IG Table 1; ATSB p. 98 |
| 5 | −45.0852 | 104.1455 | 37,651 | 178.2 | 363.8 | 0 | 0.00 | 37,651 ft, 11° right bank, hdg 178°, fuel exhausted | IG Table 1; ATSB p. 98 |
| 6 | −45.1277 | 104.1408 | 4,000 | 193.0 | 195.1 | 0 | 0.00 | 2.5 NM on; 3° right bank, 5° nose down, hdg 193°; user input 4,000 ft | IG Table 1; ATSB p. 98 |

Notes on the table:
- The IG lists vertical speeds (3,507 / 1,456 / 3,570 / 663 / 2,029 fpm) without sign. Tank capacities in the files are 182,840 lb (centre) and 69,010 lb (each wing).
- Iannello & Guillaume report two further KLIA-parked data sets ("Coordinate 6-2" at 100% all tanks; "Coordinate 7" at 80.3% side tanks, 0% centre) and exclude them.
- ATSB's "second data point" with no location has no IG equivalent, and ATSB gives no coordinates.

**What is obtainable and how.**
- SIR and ATSB accounts: public.
- RMP Forensic Report (19 May 2014) and the RMP folder: never officially released. Leaked copies are on Pete's Drive and should be read and checked against the IG table before the paper cites any value.
- FBI forensic report: not public; FOIA to the FBI is possible, though law-enforcement exemptions are likely.
- IG papers: public (Dropbox links in their references) and on Drive.

---

## Q5. Flaperon barnacles

**Short answer.**

**Custody.** The flaperon and its barnacles went to the DGA facility in Toulouse under the French judicial investigation (Tribunal de Grande Instance de Paris, juge d'instruction Carole Ramet). Poupin sampled them there on 9 Aug 2015. The remaining large colonies were collected and kept dry in heat-sealed bags. [O: SIR App. 2.6A pp. 1–5; App. 2.6B p. 1] The French judiciary still holds them.

The French side later gave "some samples of the largest barnacles" to Geoscience Australia, which passed them to Patrick De Deckker (ANU). His result was "inconclusive" (ATSB 2017 Appendix F, not read here). [O: ATSB 2017 p. 107] The University of South Florida (Herbert) group says the "largest and oldest barnacles have not yet been made available for research". [N: AeroTime/Gulf News, Aug 2023] It also says its approaches to the French and Malaysian authorities failed. [N: Yale Scientific 2024] **NOT FOUND:** any official statement giving the reason the samples were withheld.

**Reports.**
1. **Poupin (12 Aug 2015)**, SIR App. 2.6A.
   - Species *Lepas (Anatifa) anatifera striata* only; no other organisms on the flaperon.
   - Capitulum lengths from about 1 to **36 mm**, in at least four size classes.
   - Using a logarithmic fit to Evans (1958) data for *L. anserifera* (CL = 6.7041 ln(days) − 5.333), he extrapolated the 36 mm specimen to **476 days**, which puts settlement at about 10 Apr 2014. He called this "very approximate".
   - Lepas colonies indicate the flaperon floated ventral side up. [O: App. 2.6A pp. 1, 7–9]
2. **Blamart & Bassinot (LSCE; received by the court 23 June 2016)**, SIR App. 2.6B, in French, 50 pp. It is **published as an SIR appendix and includes data tables**, not unpublished as the brief assumed.
   - 252 mass-spectrometry analyses: 34 for calibration on Western Australian Museum specimens, 198 on 5 adult valves, 20 on juveniles.
   - Precision ±1 °C.
   - The terminal fringe and juvenile shell gave 25.4 ± 1 °C (Réunion-like water). The early growth of the largest valves gave **28.5 ± 1 °C**, suggesting drift E–NE of Réunion.
   - Growth duration could not be fixed; the largest scuta (20–25 mm) "could have formed in a few months". [O: App. 2.6B pp. 5–6; SIR §2.6.4 pp. 396]
   - The δ¹⁸O vs distance-from-umbo tables are on pp. 40–45: Tableau 6 (A2-G3), 7 (A2-G4), 8 (A2-G1), 9 (A2-G2). The Tableau 8 header gives distance in µm on p. 43 but "mm" on p. 44.
3. **Mg/Ca.** The only official item is De Deckker's ATSB Appendix F, which I did not read. An arXiv preprint (Kristensen 2018) [I] describes a Ca/Mg temperature history from that work.

**Al-Qattan et al. 2023 (AGU Advances 4(4), e2023AV000915, CC BY 4.0).**
- Calibrates δ¹⁸O against temperature in laboratory-reared *L. anatifera*.
- Reuses Blamart & Bassinot's **A2-G1** profile (their SI Table S7 reproduces Tableau 8). It is dated with Poupin's growth curve at 154 days, so drift starts 25 Feb 2015.
- Matches it by dynamic time-warping against 50,000 ICHTHYOP/HYCOM drifters released E of Réunion. The data statement as quoted reads: "Isotope data are included in Supporting Information S1".
- The SI, "Lepas supplemental Commons.docx", contains Text S1, Figs S1–S4, Eqs S1–S10, Tables S1–S7 and Movie S1:
  - Tables S1–S2: experiment shell measurements and growth;
  - Table S3: published δ¹⁸O–temperature equations;
  - Table S4: water δ¹⁸O;
  - Table S5: temperature reconstructions;
  - Table S6: B&B Table 4, with one water temperature changed to 21.4 °C;
  - Table S7: the B&B A2-G1 profile recomputed.
- The Mendeley Data deposit (doi:10.17632/nr4vt4h8gt; v4 is CC BY-NC 3.0) holds:
  - *Isotope temperature*: `Isotope_day2.csv` (dated SST series), `Isotope_day_interpolate.csv`;
  - *Dynamic time-warping results*: `DTWscore_fromApr5/Feb25/Jan17.csv` (about 0.93 MB each);
  - *Simulated_Trajectories*: `All_Drifters_Simulated_Trajectories_from{Apr5,Feb25,Jan17}.csv` (1.37 / 1.83 / 2.29 GB);
  - *Supplemental files*: the SI .docx and `Feb25_animation.mp4`;
  - four ReadMe .docx files.
- The 115- and 193-day start dates test ±25% age error.

**Growth-rate literature and the age dispute.**
- Poupin's 476 days rests on extrapolating three Evans (1958) points.
- Blamart & Bassinot, citing Evans (1958) and Inatsuchi et al. (2010), think "a few months".
- **Mesaglio et al. 2021** (*Marine Biology* 168:21, UNSW, Suthers group): mean *L. anserifera* growth 1.05 mm/day and maximum **1.45 mm/day**. The UNSW release says the 36 mm flaperon Lepas were "much younger than previously realised" and probably settled "at least halfway across the Indian Ocean".
- **Goehlich et al. 2024** (*Marine Biology* 171:36): *L. anatifera* grows about twice as fast in summer as in winter, so age estimates need regional and seasonal rates.
- Stelfox et al. (2020, Maldives): reported as about 35 mm in 105 days. I saw this only through secondary reporting.

**Other debris.** ATSB Debris Examination Update 2 (2016) records that one item (photographed 23 Dec 2015, Mossel Bay) was "significantly colonised by barnacles". Geoscience Australia removed and preserved marine organisms from all debris sent to Canberra (ATSB 2017 p. 107; details in Appendix G, not read). **NOT FOUND in any official document read:** species names for barnacles on items other than the flaperon, and **any record of *Lepas australis* on any MH370 debris.** *L. australis* appears in Poupin's list of the eight Lepas species only as a candidate he excluded, and in media and independent speculation (370location.org [I]).

**What is obtainable and how.**
- SIR App. 2.6A and 2.6B: public download (MOT), and on Drive (2.6A fileId 18qGq9srq4OBNB-bnHHT-wa3mWWt_78M9; 2.6B fileId 1GsCmFa5Af6X9idD9WurJ4pQM-uWnQ298). Tableaux 6–9 can be transcribed from the scans.
- Al-Qattan SI and model data: public download from Mendeley Data (verified 17 Oct 2026). The Wiley article page blocks automated clients; use a browser.
- ATSB 2017 Appendices F and G: public in the full ATSB PDF; download by browser, since the Drive text copy is truncated.
- The largest barnacle shells and the raw LSCE data: not available. Request through the French judicial authorities (TGI Paris instruction), the BEA, or Malaysia's Annex 13 team.
- GA organism identifications for other debris: request from Geoscience Australia/ATSB if they are not in Appendix G.

---

## Source list

**Official [O]**
- Malaysian ICAO Annex 13 Safety Investigation Team, *Safety Investigation Report MH370 (9M-MRO)*, MH370/01/2018, 02 Jul 2018. Read from Drive fileId 1eXn_nXdxnIL2xDNEJIMJaQRmLc02iId5, plus the court-filed copy text (Case 1:16-mc-01184-KBJ Doc 102-1; Drive "sir.txt", fileId 1ZnLkEA271aezeLAjS-4IDLJ5jVRdaP9X). Pages used: 27–28, 52–56, 133–137, 364–366, 396, 433.
- SIR Appendix 1.6D, *ELT Activation Summary* (29 Jul 2014). Drive fileId 18nqWqo4W9ePq1dNOz9IS_akZ1JN7xtT7.
- SIR Appendix 2.6A, Poupin, *Expert report on the barnacles...*, 12 Aug 2015. Drive fileId 18qGq9srq4OBNB-bnHHT-wa3mWWt_78M9.
- SIR Appendix 2.6B, Blamart & Bassinot, *Estimation des températures de croissance des valves de cirripèdes...*, LSCE, 2016. https://www.mot.gov.my/my/Laporan%20Siasatan%20Mh370/02-Appendices/Appendices%20Set%207%20-%203%20Appendices%202.6A%20to%202.6C/Appendix2.6B-MarineBiologistReport2.pdf (URL as cited by Al-Qattan et al.; I read it from Drive fileId 1GsCmFa5Af6X9idD9WurJ4pQM-uWnQ298).
- ATSB, *The Operational Search for MH370*, AE-2014-054, 3 Oct 2017. Drive fileId 1zwSCCwXcsryJdi4kHb4WE13_9-WIb4J4 (text pp. 1–160). Pages used: 36–43, 98–99, 107.
- ATSB, *MH370 – Definition of Underwater Search Areas*, 26 Jun 2014 (updated 30 Jul 2015). https://www.atsb.gov.au/sites/default/files/media/5668327/ae2014054_mh370__search_areas_30jul2015.pdf (pp. 11–15, Figs 12, 14).
- ATSB, *Debris examination update 2*, 2016. https://www.atsb.gov.au/sites/default/files/media/5773386/debris-examination-update-2_amended.pdf (seen in search result only).
- ATSB, AR-2012-128, *A review of the effectiveness of emergency locator transmitters in aviation accidents*, 2013. https://skybrary.aero/sites/default/files/bookshelf/3688.pdf (p. iii).
- BEA, *Improving the location of transoceanic flights which have disappeared at sea – summary of work carried out*. https://bea.aero/fileadmin/documents/enquetes/vol.af.447/Improving_the_location_of_transoceanic_flights_which_have_disappeared_at_sea_-_summary_of_work_carried_out.pdf
- BEA, AF447 *Interim Report* (2 Jul 2009). https://bea.aero/fileadmin/documents/docspa/2009/f-cp090601e1.en/pdf/f-cp090601e1.en.pdf
- BEA, *Triggered Transmission of Flight Data Working Group Report*. https://bea.aero/uploads/tx_elyextendttnews/triggered.transmission.of.flight.data.pdf
- RTCA SC-229 / NASA, *ELT Survivability and Reliability (ELTSAR)*. https://www.sarsat.noaa.gov/wp-content/uploads/2021/08/SC-229_ELT-Survivability.pdf
- UK MoD, "HMS Tireless stands down...", 24 Apr 2014. https://www.globalsecurity.org/wmd/library/news/uk/2014/uk-140424-ukmod01.htm

**Peer-reviewed [P]**
- Al-Qattan N. et al. (2023) AGU Advances 4(4), doi:10.1029/2023AV000915. Dataset: Herbert G. (2023) doi:10.17632/nr4vt4h8gt (Mendeley Data, file list read via public API, v4).
- Mesaglio T.P. et al. (2021) Marine Biology 168:21, doi:10.1007/s00227-021-03822-1. UNSW release: https://www.unsw.edu.au/newsroom/news/2021/02/could-a-common-barnacle-help-find-missing-persons-lost-at-sea-
- Goehlich H. et al. (2024) Marine Biology 171:36, doi:10.1007/s00227-023-04336-8.
- Bremner L. (2015) J. Indian Ocean Region 11(1):8–29, doi:10.1080/19480881.2014.985899 (p. 16).

**Manufacturer [M]**
- ELTA, *ADT406 AF/AP User's Handbook*, P/N 01N65900, doc 02E62356 (third-party mirrors: https://silo.tips/download/user-s-handbook-including-installation-manual-and-log-book ; https://usermanual.wiki/ELTA/ADT406.ADT-406-AF-AP-users-handbook/html).

**News [N]**
- Wise J., *New York* / jeffwise.net, 22 Jul 2016: http://www.jeffwise.net/2016/07/22/new-york-mh370-pilot-flew-a-suicide-route-on-his-home-simulator-closely-matching-final-flight/
- CNN, 22 Jul 2016: https://www.cnn.com/2016/07/22/asia/mh370-pilot-simulation/index.html
- CNN, 28 Jul 2016 (JACC confirmation): https://www.cnn.com/2016/07/28/asia/mh370-pilot-flight-simulator/
- naval-technology.com, 1 Apr 2014: https://www.naval-technology.com/news/newshms-tireless-tasked-to-support-missing-aircraft-search-mission-4207634/
- AeroTime, Aug 2023: https://www.aerotime.aero/articles/barnacles-could-provide-clues-to-mh370-location-scientist-says
- Yale Scientific, Jan 2024: https://www.yalescientific.org/2024/01/barnacle-breadcrumbs/
- National Geographic: https://www.nationalgeographic.com/environment/article/barnacles-missing-malaysian-airlines-flight-drift-path

**Independent analysts [I]**
- Iannello V. et al. (IG), *Captain Zaharie Shah's Recovered Flight Simulator Information: Preliminary Assessment*, 14 Aug 2016 (Drive fileId 1EQ7s5z_vvUUXtY4nH-03KGKglKKGbPf0).
- Iannello V. & Godfrey R., *Possible Flight Path of MH370 towards McMurdo Station*, 25 Aug 2016 (Drive fileId 1ihPpZdTJ2qrcHPexog1akKZGi4Ek6bhB).
- Iannello V. & Guillaume Y., *Further Analysis of Simulator Data Related to MH370*, 29 Nov 2016 (Drive fileId 1npHNdf_750XDQ6IohblEHuBeNnOWMjag).
- Wise J., "MH370 Flight Simulator Claim Unravels Under Inspection", 31 Aug 2016: http://www.jeffwise.net/2016/08/31/mh370-flight-simulator-claim-unravels-under-inspection/
- Ulich B., *Search for MH370 north of 25S* (2018) (Drive fileId 1yRDZNpqGJonOWS4ZFBwcB1jbmKzw-Sai).
- Kristensen (2018) arXiv:1811.09315.
- 370location.org (2024): https://370location.org/2024/03/barnacle-growth-on-mh370-debris-is-consistent-with-a-7th-arc-crash-site-in-tropical-waters/
EOF
wc -w research-beacons-tpl-simulator-barnacles.md