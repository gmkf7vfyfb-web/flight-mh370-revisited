cat >> research-beacons-tpl-simulator-barnacles.md <<'EOF'

---

## Q6 follow-up (added 17 Oct 2026)

**Grades used in this section:**
- **A**: official investigation or agency document.
- **B**: peer-reviewed paper, investigation-commissioned technical report, or manufacturer document.
- **C**: named aviation journalist or specialist outlet.
- **D**: blog, forum or anonymous comment.

**Additional scope limits:**
1. **ATSB 2017 Figure 23 was not obtained.** The project Drive copy of the ATSB 2017 report is 41.7 MB, above the connector's 10 MB download limit; only its text is readable. The ATSB website does not answer automated clients. Pete can download it in a browser; Fig. 23 is on printed p. 40.
2. **Books not read.** I did not read the full texts of Vance (2018), de Changy (2016/2021), Higgins (2019) or Hardy (2015). Where I say a claim was not found, it means "not found in what was reachable", not "the author never says it".

### (a) Would a 406 MHz ELT transmission from the surface have been received?

**Short answer: yes, almost certainly, by geostationary satellite within about a minute of the first burst, but with no position.**

- **Geostationary detection.** Cospas-Sarsat geostationary payloads give "almost immediate alerting" across 70°N–70°S (Cospas-Sarsat system description [A]). In March–April 2014 the Indian Ocean was covered by INSAT-3A at 93.5°E (operational since 2003) and Electro-L N1 at 76°E. The Cospas-Sarsat System Data and Secretariat briefings list both [A]. A Cospas-Sarsat official told CNN in April 2014 that a 406 MHz transmission "almost certainly would have been picked up by one of the geostationary satellites", naming those two [C: CNN 25 Apr 2014].
  - INSAT-3D (83.5°E, listed as "projected" in 2010): its operational status in March 2014 is NOT FOUND.
  - MSG (EUMETSAT, near 0–10°E) is about 90° of longitude from 100°E. That puts it at or beyond the edge of its useful footprint; this is my geometric inference, not a sourced statement.
- **No position from geostationary satellites.** A geostationary satellite sees no Doppler shift, so it cannot locate a beacon unless the beacon encodes a GNSS position in its message (Cospas-Sarsat; NOAA [A]).
  - Neither the SIR nor the ATSB says that 9M-MRO's ELTA 406 unit had a navigation input. The SIR lists the transmitted content only as identifier, nationality and registration (SIR p. 53).
  - So a geostationary alert would have identified 9M-MRO but carried no position. That is my inference from the SIR description: no navigation interface is mentioned.
- **Low-orbit detection and position.** Polar-orbiting satellites locate a beacon by Doppler.
  - Typical waiting time is under one hour at mid-latitudes with the four-satellite design constellation [A: Cospas-Sarsat].
  - NOAA gives an average **46-minute** time advantage of geostationary over low-orbit first detection [A: NOAA FAQ]. Training material gives about 45 minutes on average, longer near the equator [D: eGMDSS course].
  - Doppler accuracy is about 5–10 km for one pass and about 2 km for 406 MHz beacons [D/A: eGMDSS; eoPortal].
- **Burst timing.** On activation the ELTA unit starts 121.5/243 MHz homing straight away. The first 406 MHz burst comes about **50 s** later, then one burst roughly every 50 s for 24 h [B: ELTA/Kannad 406 AF manual]. The C/S T.001 specification sets a mean repetition period of 50 s [A].
  - If the antenna is underwater before about 50 s, no 406 MHz burst is radiated [D: radiantphysics comment; consistent with the manual].
- **Statements that no alert was received:**
  - **SIR:** no relevant ELT signals were reported by SAR agencies or other aircraft (pp. 54, 365; finding p. 433) [A].
  - **ATSB 2017:** "no distress transmissions were received by SAR authorities at any time during the flight". The ATSB concludes that the ELTs "did not transmit an emergency signal either by automatic or manual activation or by water immersion" (p. 145) [A].
  - **ATSB June 2014:** "No Emergency Locator Transmissions were received" (p. 3) [A].
  - **Australia's ICAO paper WP30 (2015):** "No ELT transmissions received" and "No distress beacon detections (ELT or others carried on board)" (p. 2) [A].
  - **Cospas-Sarsat-related article:** Inside GNSS (Airbus/Cospas-Sarsat authors) says that for AF447 and MH370 "no alert messages transmitted by the ELT were received" [B/C].
  - **AMSA:** NOT FOUND as a stand-alone AMSA statement. AMSA runs the Australian MCC (SIR p. 52).
- **ELT failure rate.** ATSB 2017 p. 145 adds that studies put ELT failure rates "in the region of 25–75 per cent" (citing ATSB 2013, DRDC 2009, Stimson 2015) [A].

### (b) Unofficial and independent accounts: why the ELT did not activate, or how it could be prevented

| Claim | Who | Grade | Source |
|---|---|---|---|
| The fixed ELT is "accessible via a ceiling panel at station 1880 above the aft passenger cabin close to the aft galley". A step ladder would be needed. Once accessed it "can theoretically be disabled" by switching its front-panel switch to OFF or disconnecting the antenna. From the cockpit it can only be switched ARMED/ON. | AirlineRatings Q&A (Geoffrey Thomas's site), c. 2024 | C | airlineratings.com "10 most asked questions on MH370" |
| The 777 ELT location (aft fuselage crown) is shown on the Boeing ARFF chart. The chart gives no access procedure. | Boeing | B | Boeing 777 ARFF document |
| The airframe ELT cannot be disabled by hijackers or pilots: battery powered and "inaccessible to the crew". | CNN (Brian Todd segment, 25 Apr 2014) | C | CNN 25 Apr 2014 |
| A likelier cause is that impact activated the beacon but the aircraft sank in under 50 s, before the first burst. | Experts quoted by CNN | C | same |
| The 50 s first-burst delay means no 406 MHz signal if the antenna is submerged first. The portable ELT (P/N 01N65910, "ADT 406 AP with float") could float free and transmit, but needs impact or manual activation. | Commenters on Iannello's blog | D | radiantphysics.com, 4 Jun 2017 thread |
| A controlled ditching sank the aircraft largely intact (Vance: powered, flaps extended; Hardy: unpowered glide then ditching; Bailey: glide and ditching "to leave as little wreckage as possible"). | Vance (2018 book; CBC); Hardy (2015); Bailey (Sky News 2020) | C/D | CBC 2018; radiantphysics 16 May 2018; Malay Mail 20 Feb 2020 |
| None of these three, in what I could read, explains the ELT mechanism; the ELT link is inferred by commentators. | — | — | NOT FOUND in sources read |
| Former MAS chief pilot: the ELT needs a threshold impact, and AF447's "was not triggered" at low impact speed. This is inconsistent with BEA findings: AF447 hit the water at high vertical speed. | Nik Huzlan (Bernama, 2014) | C | Malay Mail 17 May 2014 |
| Pilots cannot reach the E/E bay controls or switch off the 777 FDR/CVR from the cockpit; access is through a floor hatch in the cabin. | Leeham News, 24 Mar 2014 | C | leehamnews.com |
| A forum commenter wonders why cabin crew did not manually activate the portable ELT. | Metabunk user "TWCobra" | D | metabunk.org thread |

**Assessment.**
- **In-flight access to the fixed ELT:** no official source states it. The only explicit public claim is the grade-C AirlineRatings Q&A: a ceiling panel at STA 1880 near the aft galley, needing a ladder. It agrees with the SIR location (above the aft cabin ceiling at STA 1880) and with the manufacturer's design (OFF switch on the beacon only, coax antenna connector on the unit).
- **Door 4/5 access panel:** NOT FOUND.
- **A circuit breaker that disables the beacon:** NOT FOUND. On the ELTA design the remote panel is unpowered if the beacon switch is not in ARMED. One forum post says the circuit breaker only cuts the charging/remote circuit; it is grade D and uncorroborated.
- **Named authors:** I found no grade-A/B source in which Vance, Wise, Iannello/IG, Godfrey, Higgins or de Changy gives a specific ELT-disabling procedure. Wise appeared in CNN's April 2014 ELT segment, but no written claim of his was found.

### (c) ULB reliability in real ocean accidents

- **AF447 (2009, about 3,900 m).**
  - The 31-day passive search (10 Jun–10 Jul 2009) did not detect either ULB, although on 22–23 June the hydrophones passed close to the debris field.
  - BEA found that "the CVR's ULB ... was damaged on impact"; "the other ULB was separated from the FDR and never found"; and the recovered beacon "could not transmit with a new battery". [B: BEA/Phoenix/WHOI ISASI 2011 paper, p. 3; A: GAO-15-443]
  - Metron's survival model used P(single ULB survives) = 0.8, detection 0.9 within 1,730 m, combined P_D = 0.77. [B: Metron report to BEA, 20 Jan 2011, p. 20; Stone et al. 2014, *Statistical Science* 29(1)]
- **BEA dataset of 27 at-sea crashes (Metron Appendix B, Table 4, p. 39).** I read the table from an image ([metron_appB_table4_p39.png]({{artifact:8069288e-3f0c-4a73-aa46-dbe092ed3ddb}})).
  - **52 ULBs, of which 5 failed to function (>90% survival)** and **14 detached** from their recorders. This counts detachment, not failure.
  - The 5 failures include SAA295, attributed to the in-flight fire. Metron therefore calls 90% possibly low for a non-fire crash. [B]
  - Rows read from the table:
    - **SAA295 Helderberg** (28 Nov 1987, 4,400 m): 2 ULBs inoperative; CVR recovered after 840 days; FDR never found. The 30-day ULB search heard nothing [C: Admiral Cloudberg; A: FAA transcript note "FDR was not recovered"].
    - **Adam Air 574** (1 Jan 2007, 1,800 m): 0 detached, 0 inoperative; recorders recovered after 240 days. The USNS Mary Sears TPL detected the pingers [C: Al Jazeera, US Embassy statement, Jan 2007].
    - **Yemenia 626** (30 Jun 2009, 1,200 m): "Both ULBs detached", 0 inoperative; recovered after 60 days. BEA confirmed signals from both recorders on 5 Jul 2009 [C: ABC News].
    - **Ethiopian 409** (25 Jan 2010, off Beirut, 45 m; listed as "Ethiopian Airlines #4062"): 1 detached, 1 inoperative; CVR's ULB detached; recovered after 20/13 days.
    - **AirAsia 8501** (Dec 2014): after the table's date. Pings were detected in about 30 m of water and both recorders recovered by divers in Jan 2015 [C: NBC/Inquirer/Gulf News].
- **Implication for P(CVR ULB transmitting).**
  - The pooled per-beacon survival from the BEA table is about 0.90 (47/52), with an independent-failure assumption. Metron's conservative planning value was 0.8.
  - **9M-MRO specifics:** the CVR ULB battery was in date (expiry June 2014). The FDR ULB battery was 15 months past expiry (Dec 2012), so per the SIR its 30-day performance is "not guaranteed".
  - So a defensible prior is P(CVR ULB activated and transmitting in spec) ≈ 0.8–0.9, and a lower, poorly bounded value for the FDR ULB. P(at least one transmitting) is close to the CVR value if their failures are strongly dependent; Metron weighted the dependent case 0.75.
  - These are my derivations from grade-B data and should be labelled provisional.
- **Statistics from NTSB or ICAO:** a specific ULB failure statistic is NOT FOUND. ATSB 2017 p. 146 cites ICAO (2016): ULB search rate about **100 km²/day**, with a maximum of about **2,300 km²** searchable within the 30-day battery life [A].
- **Unofficial discussion of preventing ULB operation** (removal, damage, burial): NOT FOUND in any named source. Official texts give damage, detachment, burial, shielding and battery state as causes of non-detection (ATSB 2017 p. 37; SIR pp. 364–365) [A]. Neither the SIR nor the ATSB discusses deliberate removal. The recorders sit in rack E7 above the aft cabin ceiling (SIR p. 133). Whether that rack is reachable in flight is NOT FOUND.

### (d) Sonobuoy fields, 6–17 April 2014

- **What is published:**
  - Sonobuoy drops ran 6–16 April (ATSB June 2014 p. 13) or 6–17 April (ATSB 2017 p. 41) [A].
  - They were laid near the 7th arc where depths were favourable, at the Ocean Shield and Haixun 01 detection areas, and along the Curtin/CTBTO H01 hydroacoustic bearing [A].
  - One sortie covered about 3,000 km², with hydrophones at 300 m and detection to 4,000 m [A].
  - On 9 April "dozens" of sonobuoys were dropped around the Ocean Shield detection zone [C: ABC 10 Apr 2014]. Reports say an AP-3C carried up to 84 sonobuoys [C: Time; Malay Mail 10 Apr 2014].
  - On 10 April an AP-3C sonobuoy near Ocean Shield picked up a "possible signal". On 11 April the Australian Joint Acoustic Analysis Centre judged it unlikely to be from the recorders [C: ABC; Time, quoting Houston/JACC].
  - ATSB June 2014 Fig. 14 marks the western detection as "a sonobuoy detection of different frequency", inside the AUV coverage chart [A].
- **What is not published:** sonobuoy drop positions or a sonobuoy-pattern map: **NOT FOUND** in ATSB, JACC (as reported) or Defence sources reached. These would have to be requested from the Department of Defence/RAAF 92 Wing or ATSB.
- **Rendered figures (from the project Drive copy of the ATSB June 2014 report, fileId 1lDHdjQhdoyiqRIck6Gkmdyur7g1ua_Lw):**
  - [atsb2014_fig12_page18.png]({{artifact:d3a5c183-9d7c-446f-befa-121af7d8ade4}}) — Fig. 12, Ocean Shield TPL coverage 4–14 April, printed p. 13 (legend: 3 km effective range, 10 km pinger transmission, 2,400 m swath).
  - [atsb2014_fig14_page20.png]({{artifact:54902127-5d6e-42e9-b165-5a8d85e7f4de}}) — Fig. 14, AUV coverage 14 April–28 May with the four TPL detections and the western sonobuoy detection, printed p. 15.
  - ATSB 2017 Fig. 23 (TPL coverage polygons): **not obtained** (see the scope limits above).

### Q6 sources

**[A] Official**
- Cospas-Sarsat system overview: https://www.cospas-sarsat.int/en/system-overview/cospas-sarsat-system ; detailed description: https://www.cospas-sarsat.int/en/system-overview/detailed-cospas-sarsat-system-description
- NOAA SARSAT FAQ: https://www.sarsat.noaa.gov/faqs/
- Cospas-Sarsat System Data No. 36 (Dec 2010): https://www.gcaa.gov.ae/en/epublication/EPublications/Forms%20Download/GCAA%20Events/Gulf%20Satellite%20Aided%20SAR%20Seminar%20March%202011/Gulf%20SAR%20-%20Presentations%20and%20Materials/Cospas-Sarsat%20Materials/Cospas-Sarsat%20System%20Data%20-%20December%202010.pdf
- Cospas-Sarsat Secretariat briefings 2010/2011: https://www.sarsat.noaa.gov/wp-content/uploads/2021/08/BMW_CS_updates_Secretariat2011.pdf
- C/S T.001 specification (Thai MCC copy): https://sar.mot.go.th/document/THMCC/T001-MAR-26-2021%20SPECIFICATION%20FOR%20COSPAS-SARSAT%20406%20MHz%20DISTRESS%20BEACONS.pdf
- ATSB 2017 pp. 145–146 (Drive text); ATSB June 2014 p. 3, Figs 12 and 14; Australia ICAO WP30 (2015) p. 2 (Drive fileId 1DJG-kkcV5JiofBZQFA0YCVnajIrwcIWJ)
- GAO-15-443: https://www.gao.gov/assets/gao-15-443.pdf
- FAA SAA295 transcript note: https://www.faa.gov/sites/faa.gov/files/2022-11/Transcript_CVR_MRU.pdf

**[B] Peer-reviewed / commissioned / manufacturer**
- Stone, Keller, Kratzke, Strumpfer, *Search Analysis for the Location of the AF447 Underwater Wreckage*, Metron report to BEA, 20 Jan 2011 (Drive fileId 1_FpHT5nsRBMo9L2808j281wvBRKzQH9l; BEA copy https://bea.aero/fileadmin/uploads/tx_elyextendttnews/metron.search.analysis.pdf), p. 20 and App. B p. 39.
- Stone et al. (2014) *Statistical Science* 29(1):69–80, doi:10.1214/13-STS420.
- BEA/Phoenix/WHOI, ISASI 2011 paper on the AF447 sea search (Drive fileId 1XyxPBjlQ4vjVsd7Xl9W46I1xIdmQBvhJ), p. 3.
- Kannad/ELTA 406 AF manual (Aircraft Spruce copy): https://www.aircraftspruce.com/catalog/pdf/406af_rev17.pdf
- Boeing 777 ARFF chart: https://www.boeing.com/content/dam/boeing/boeingdotcom/commercial/airports/arff/arff777.pdf
- Inside GNSS, "The Cospas-Sarsat MEOSAR System Solution to Support ICAO GADSS": https://insidegnss.com/the-cospas-sarsat-meosar-system/

**[C] Journalism**
- CNN, 25 Apr 2014: https://www.cnn.com/2014/04/25/world/asia/malaysia-airlines-flight-370-beacons/index.html
- AirlineRatings: https://www.airlineratings.com/articles/the-10-most-asked-questions-on-mh370-answered
- CBC (Vance), 2018: https://www.cbc.ca/news/mh370-flight-malaysian-airlines-crash-1.4665938
- Malay Mail (Bailey), 20 Feb 2020: https://www.malaymail.com/news/malaysia/2020/02/20/aussie-pilot-claims-he-knows-exactly-where-mh370-wreckage-is/1839139
- Malay Mail (Nik Huzlan), 17 May 2014: https://www.malaymail.com/news/malaysia/2014/05/17/mh370-after-71-days-the-silence-gets-louder/670709
- Leeham News, 24 Mar 2014: https://leehamnews.com/2014/03/24/caution-on-recovering-data-from-mh370-fdr-cvr/
- ABC, 10 Apr 2014: https://www.abc.net.au/news/2014-04-10/mh370-another-possible-signal-detected/5382246
- Time: https://time.com/59062/mh370-black-box-may-be-found/
- Malay Mail, 10 Apr 2014: https://www.malaymail.com/news/malaysia/2014/04/10/australia-finds-possible-signal-in-mh370-search/650427
- ABC (Yemenia), 5 Jul 2009: https://www.abc.net.au/news/2009-07-05/yemenia-black-box-signal-detected/1342364
- Al Jazeera (Adam Air), 25 Jan 2007: https://www.aljazeera.com/news/2007/1/25/missing-jets-black-box-detected
- NBC (AirAsia 8501): https://www.nbcnews.com/storyline/airasia-plane-crash/divers-find-both-black-boxes-airasia-flight-8501-n284216
- Admiral Cloudberg (SAA295): https://admiralcloudberg.medium.com/fall-of-the-helderberg-the-crash-of-south-african-airways-flight-295-ef6261a01b46

**[D] Blogs / forums**
- radiantphysics.com threads (4 Jun 2017; 16 May 2018)
- metabunk.org "Jeff Wise's new MH370 theory"
- eGMDSS course pages
EOF
grep -c "" research-beacons-tpl-simulator-barnacles.md