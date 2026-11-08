# Master citation ledger — MH370 paper

Owner: paper drafting and citations module (`PAPER_CITATIONS_MODULE`).
Generated 12 October 2026 by `write_citation_outputs.py` from `build_citation_library.py`.
Companion file: `paper/references.bib` (generated from the same index — never
hand-edited). Reference style follows `paper/JON-RULES.md` §6 (Harvard).

## 1. What was gathered

| Source | Result |
|---|---|
| Module bibliographies under `results/*.bib` | 10 files, 307 raw entries |
| After deduplication by DOI, else by first author, year and title | **278 entries** |
| Repository files scanned for in-text use | 1117 (`results/**/*.md`, `ARCHITECTURE.md`, `README.md`, `RUNBOOK.md`, `threads/master-prompts/`, `coordination/`, and the engine's Rust, TOML and Python) |
| Entries whose use in the project could be traced to a file | 161 of 278 |
| Local candidate copies indexed (`~/Downloads`, `mh370-exchange`) | 1085 files |

Still to be folded in, and therefore **not** represented in the counts below:
Pete's Google Drive; `deskstar`; the prose ledgers `results/*-references.md` (which carry the printed pages and the per-claim provenance); `results/davey-2016-reference.md`; `results/hydroacoustics-bibliography.csv`; `results/seabed-search-references.md`.

## 2. Counts by grade

Grades follow the module brief §1: **official** (publisher, agency, standards body), **peer-reviewed**, **grey** (reports, theses, preprints), **unofficial** (blogs, forums, independent analysts).

| Grade | Entries |
|---|---|
| official | 54 |
| peer-reviewed | 123 |
| grey | 101 |
| unofficial | 0 |
| **total** | **278** |

Every grade below is assigned by rule from the entry type and the publisher, institution or URL field, and each entry records the basis. **The grades are heuristic and need Pete's or architecture's confirmation on the `misc` entries in particular**, where the entry type carries no information.

No entry graded **unofficial** is present in the module bibliographies. That is worth noting rather than celebrating: independent analysts' work (for example 370location.org) is cited in project prose and in the hydroacoustics discussion, so either those citations are missing from the bibliographies or they are being used without being cited. See §5.

## 3. Verification status

Of **278** entries, **137** carry a DOI and **141** do not. Every DOI was looked up at CrossRef and, on a 404 there, at DataCite — 126 are registered with CrossRef and 11 with DataCite (datasets, data products and arXiv deposits are DataCite's, and 404 at CrossRef without being broken).

| Status | Entries | Meaning |
|---|---|---|
| METADATA VERIFIED | 128 | the DOI resolves and the registered title and year agree with ours |
| METADATA MISMATCH | 9 | the DOI resolves but a field disagrees — listed in §4 |
| UNVERIFIED, no DOI | 141 | the entry carries no DOI, so there was nothing to check automatically |
| UNVERIFIED, DOI not found | 0 | a DOI is recorded but neither registry knows it — these need attention, listed in §4.5 |
| **total** | **278** | |

Arithmetic check, so the table can be audited: 137 with a DOI = 128 verified + 9 mismatched + 0 not found; 128 + 9 + 0 + 141 without a DOI = 278.

**None is yet VERIFIED against the source document** in the brief's strongest sense — that requires opening the work and checking the claim it is cited for, which happens claim by claim as the draft is written, not in bulk.

Legitimate held copies located on this machine: 17 candidate matches, of which 5 are confident. Title-token matching against downloaded filenames is weak for agency reports whose filenames bear no relation to their titles, so this count is a floor, not a finding. The Drive sweep will raise it.

## 4. Entries that need a decision

### 4.1 Four year disagreements that are not errors

CrossRef's `issued` date is the earliest registered date, which for a journal article is the online-first date. In four cases our year is the **printed issue** year and is the right one for a Harvard reference list:

| Key | Our year | CrossRef print | CrossRef online | Venue |
|---|---|---|---|---|
| `durgadoo2021` | 2021 | 2021 | 2019 | Journal of Operational Oceanography |
| `ashton2015` | 2015 | 2015 | 2014 | Journal of Navigation |
| `Karney2013` | 2013 | 2013 | 2012 | Journal of Geodesy |

**No change needed.** This includes `ashton2015` — Ashton et al. in *The Journal of Navigation* — which is one of the paper's two anchor references. It is cited elsewhere in the literature as both 2014 and 2015; the printed issue is 2015 and that is what we will use. Worth stating once in the ledger so that nobody 'corrects' it later.

### 4.2 9 genuine mismatches against the registry

**Year (3).** The registered title agrees, the year does not:

- **`gdp6h`** — Lumpkin, Rick and Centurioni, Luca, *Global Drifter Program quality-controlled 6-hour interpolated data fro*. Ours: 2019; DataCite records 2010 in NOAA National Centers for Environmental Information.
- **`kaiser1990`** — Kaiser, *On a simple algorithm to calculate the 'energy' of a signal*. Ours: 1990; CrossRef records - in International Conference on Acoustics, Speech, and Signal Processing, 381-384.
- **`Taylor1921`** — Taylor, G. I., *Diffusion by continuous movements*. Ours: 1921; CrossRef records 1922 in Proceedings of the London Mathematical Society s2-20, 196-212.

  **Recommendation:** take the year from the registry record of the version we actually cite, and keep this note so the choice stays visible. Pete's call on each. Note that a dataset's registered publication year is the year the *series* was first published, which is not the year of the product version used in a run — so for data products the run's own configuration is the better authority and the reference should name the version, not just the year.

**Title (6).** The DOI resolves, but to a differently titled record — in each case a data product cited under a working name rather than its registered title:

- **`gordon1993`** — ours: *Novel approach to nonlinear/non-Gaussian Bayesian state estima*; registered as *Novel approach to nonlinear/non-Gaussian Bayesian state estimation* (Institution of Engineering and Technology (IET), 1993).
- **`gilks2001`** — ours: *Following a moving target–-Monte Carlo inference for dynamic B*; registered as *Following a Moving Target—Monte Carlo Inference for Dynamic Bayesian Mod* (Oxford University Press (OUP), 2001).
- **`delmoral2006`** — ours: *Sequential Monte Carlo samplers*; registered as *Sequential Monte Carlo Samplers* (Oxford University Press (OUP), 2006).
- **`glorys12`** — ours: *Global Ocean Physics Reanalysis (GLOBAL_MULTIYEAR_PHY_001_030)*; registered as *Global Ocean Physics Reanalysis* (Mercator Ocean International, 2018).
- **`FDSNIM`** — ours: *International Miscellaneous Stations (FDSN network IM; IMS hyd*; registered as *International Miscellaneous Stations* (International Federation of Digital Seismograph Networks, 1965).
- **`cmems_glo_wav_001_032`** — ours: *Global Ocean Waves Reanalysis (GLOBAL_MULTIYEAR_WAV_001_032), *; registered as *Global Ocean Waves Reanalysis WAVERYS* (Mercator Ocean International, 2019).

  **Recommendation:** cite the registered title, and give the working name only if the paper needs it for continuity with the figures. A referee checking the DOI must land on the thing the reference names.

### 4.3 The 141 entries with no DOI

These are mostly agency reports, where a DOI often does not exist. They are not suspect — but under JON's website/dataset format each needs a **URL and an access date**, and the access date is recorded for almost none of them. Entries missing both a DOI and a URL cannot be formatted in JON style at all:

**67 entries have neither a DOI nor a URL:**

- `CMST2014` (techreport, official) — Analysis of low frequency underwater acoustic signals possibly related to the loss of Malaysian
- `GaspinShuler1971` (techreport, official) — Source Levels of Shallow Underwater Explosions
- `Jeffreys1961` (book, official) — Theory of Probability
- `KadriAbdolaliKirby2025` (article, peer-reviewed) — Acoustic-gravity quantum tunnelling analogy
- `McDougallBarker2011` (manual, grey) — Getting started with TEOS-10 and the Gibbs Seawater (GSW) Oceanographic Toolbox
- `Porter1992` (techreport, official) — The KRAKEN Normal Mode Program
- `RHUMRUM_YV` (misc, grey) — RHUM-RUM experiment, 2011–2015 (FDSN network YV)
- `TEOS10` (manual, grey) — The International Thermodynamic Equation of Seawater – 2010: Calculation and Use of Thermodynam
- `af447seabed2011` (misc, grey) — Recovery of AF447 victims from the seabed, 2011 (secondary: Encyclopaedia Britannica; Al Jazeer
- `andersen2005` (article, peer-reviewed) — Unsteady aerodynamics of fluttering and tumbling plates
- `andersen2005b` (article, peer-reviewed) — Analysis of transitions between fluttering, tumbling and steady descent of falling cards
- `anderson2018` (techreport, official) — Report on two shipwrecks found during the MH370 search
- `atsb2014fpu` (techreport, official) — MH370 – Flight Path Analysis Update
- `atsb2016sdu` (techreport, official) — MH370 – Search and debris examination update
- `atsb2017operational` (techreport, official) — The Operational Search for MH370
- `bea2009frwg` (techreport, grey) — Flight Data Recovery Working Group Report
- `blackman2004ucrl` (misc, grey) — UCRL-TR-207323: 2001 airgun calibration shots at H01 and H08 (held as digitised source)
- `boeingeofsims2016` (misc, official) — End-of-flight engineering-simulator exports, ten cases
- `ccaa2010kenya507` (techreport, grey) — Technical Investigation into the Accident of the B737-800 Registration 5Y-KYA Operated by Kenya
- `chu2006` (article, peer-reviewed) — Prediction of falling cylinder through air-water-sediment columns
- `ciada1997austral2553` (techreport, grey) — Informe final de accidente de aviación: McDonnell Douglas DC-9-32, Austral Líneas Aéreas Cielos
- `cmst2014report` (misc, official) — CMST report 2014-30: analysis of IMOS and IMS records for MH370 (held; pdf sha256 1c19b353562ff
- `daai2016lam470` (techreport, grey) — Civil Aircraft Accident Report: Aircraft C9-EMC, Embraer 190, Bwabwata National Park, 29 Novemb
- `dnv2010` (techreport, grey) — Risk Assessment of Pipeline Protection
- `esdu-windmill` (techreport, grey) — Estimation of windmilling drag and airflow of turbo-jet and turbo-fan engines
- `esdu84004` (techreport, grey) — Estimation of spillage drag for a wide range of axisymmetric intakes at M less than 1
- `esdu84005` (techreport, grey) — Estimation of drag due to inoperative turbo-jet and turbo-fan engines using Data Item Nos 81009
- `faa2024part60` (misc, grey) — 14 CFR Part 60, Flight Simulation Training Device Initial and Continuing Qualification and Use,
- `fprg2016satcomlogs` (techreport, official) — Internal study regarding SATCOM ground-station logs
- `ga2017searchareas` (misc, grey) — MH370 search area survey geometry
- `griffa1996stochastic` (incollection, official) — Applications of stochastic particle models to oceanographic problems
- `griffin2017partii` (techreport, official) — The search for MH370 and ocean surface drift – Part II
- `griffin2017partiii` (techreport, official) — The search for MH370 and ocean surface drift – Part III
- `heffley1972cr2144` (techreport, official) — Aircraft Handling Qualities Data
- `iannello2018` (misc, grey) — End-of-flight simulations (web article; VERIFY title and URL from the archive snapshot)
- `icao2014wp30` (misc, official) — MH370 Search and Rescue Response – JRCC Australia
- `india1978airindia855` (techreport, grey) — [Report of the Court of Inquiry into the accident to Air India Boeing 747 VT-EBD 'Emperor Ashok
- `ioc2010teos10` (manual, grey) — The international thermodynamic equation of seawater – 2010: Calculation and use of thermodynam
- `iso2533` (standard, grey) — Standard Atmosphere
- `jiaac2010wca708` (techreport, grey) — Informe Final Caso West Caribbean HK4374X, vuelo WCW708, Machiques, Estado Zulia, 16 de agosto 
- `kadri2025snt` (misc, official) — CTBTO Science and Technology Conference 2025 poster on MH370 hydroacoustic signals (held as dig
- `kish1965` (book, official) — Survey Sampling
- `knkt2019lionair610` (techreport, grey) — Final KNKT.18.10.35.04 Aircraft Accident Investigation Report: PT. Lion Mentari Airlines, Boein
- `lebanon2012et409` (techreport, grey) — Investigation Report on the Accident to Ethiopian 409, Boeing 737-800, Registration ET-ANB, at 
- `margo1990` (techreport, grey) — Report of the Board of Inquiry into the Helderberg Air Disaster
- `mca2006fsh604` (techreport, grey) — Final Report of the Accident Investigation, Flash Airlines Flight 604, January 3, 2004, Boeing 
- `mearns1994` (techreport, grey) — MV Derbyshire survey report
- `mh370caption_oi_tracings` (misc, official) — Traced outlines of the Ocean Infinity 2018 and 2025–26 search areas
- `mot2015factual` (techreport, official) — Factual Information: Safety Investigation for MH370, Malaysia Airlines MH370 Boeing B777-200ER 
- `mot2017` (techreport, official) — Summary of Possible MH370 Debris Recovered (updated 30 April 2017)
- `mot2018mh370` (techreport, official) — Safety Investigation Report, Malaysia Airlines Boeing B777-200ER (9M-MRO), 08 March 2014
- `ntsb2010` (techreport, grey) — Loss of Thrust in Both Engines After Encountering a Flock of Birds and Subsequent Ditching on t
- `ntsc2000silkair185` (techreport, grey) — Aircraft Accident Report: SilkAir Flight MI 185, Boeing B737-300, 9V-TRF, Musi River, Palembang
- `ntsc2008adamair574` (techreport, grey) — Aircraft Accident Investigation Report: PT. Adam SkyConnection Airlines (AdamAir) Flight DHI 57
- `ntsc2008dki574` (techreport, grey) — Aircraft Accident Investigation Report, PK-KKW
- `pollschumann2021` (article, peer-reviewed) — An estimation method for the fuel burn and other performance characteristics of civil transport
- `rahimi2007random` (inproceedings, peer-reviewed) — Random features for large-scale kernel machines
- `romania2000tarom371` (techreport, official) — [Final report on the accident to the Airbus A310-324 YR-LCC, TAROM flight ROT 371, Balotești, 3
- `royer2016report` (misc, grey) — OHASISBIO hydroacoustic analysis for MH370, report LDO-201608 (held as project artifact royer-2
- `russia1994aeroflot593` (techreport, grey) — Report on the investigation into the crash of A310-308, registration F-OGQS, on 22 March 1994 n
- `sir2018` (techreport, official) — Safety Investigation Report: MH370 (9M-MRO)
- `sir2018app16e` (techreport, official) — Performance Analysis – Malaysian Airlines 777 9M-MRO Missing Occurrence
- `sutherland2020leeway` (article, peer-reviewed) — Evaluating the leeway coefficient of ocean drifters using operational marine environmental pred
- `tcds777` (techreport, grey) — Type Certificate Data Sheet T00001SE, Revision 48: Boeing 777-200, -200LR, -300, -300ER, 777F
- `thresher1963` (techreport, official) — Court of Inquiry into the loss of USS Thresher
- `tsb2003` (techreport, grey) — Aviation Investigation Report A98H0003: In-Flight Fire Leading to Collision with Water, Swissai
- `ulich2018north25` (misc, grey) — Search for MH370 north of 25S unlikely

Each needs a locator before submission. For agency reports the report number plus the issuing body is usually enough for a Harvard entry, and most of these have one; the gap is a retrievable URL for the reader.

### 4.4 Entries that cannot yet be formatted completely

JON requires full details "even if the list of authors is extensive" (`JON-RULES.md` §6), so an author list abbreviated in the module bibliography cannot go into the reference list as it stands.

**35 entries have a truncated author list** (`and others` / `et al.` in the stored author field):

- `abbott2016` — Abbott and Abbott and Abbott and others — Observation of Gravitational Waves from a Binary Black Hole Merger
- `anderson2001` — Anderson and Brady and Creighton and others — Excess power statistic for detection of burst sources of gravitational
- `baillard2013` — Baillard and Crawford and Ballu and others — An Automatic Kurtosis-Based P- and S-Phase Picker Designed for Local S
- `blackman2004` — Blackman and de Groot-Hedlin and Harben and others — Testing low/very low frequency acoustic sources for basin-wide propaga
- `blackman2004b` — Blackman and de Groot-Hedlin and Orcutt and others — Methods for Calibrating Basin-Wide Hydroacoustic Propagation in the In
- `blackman2004ucrl` — Blackman and others — UCRL-TR-207323: 2001 airgun calibration shots at H01 and H08 (held as 
- `brown2026` — Brown and McFadden and McCormack and others — A search for hydroacoustic signals from bolides
- `capano2017` — Capano and Dent and Hanna and others — Systematic errors in estimation of gravitational-wave candidate signif
- `chamberlain2021bran2020` — Chamberlain, Matthew A. and others — Next generation of Bluelink ocean reanalysis with multiscale data assi
- `hanson2001` — Hanson and Le Bras and Dysart and others — Operational Processing of Hydroacoustics at the Prototype Internationa
- `ishii2005` — Ishii and Shearer and Houston and others — Extent, duration and speed of the 2004 Sumatra–Andaman earthquake imag
- `kadri2017` — Kadri and Crivelli and Parsons and others — Rewinding the waves: tracking underwater signals to their source
- `knijnenburg2009` — Knijnenburg and Wessels and Reinders and others — Fewer permutations, more accurate P -values
- `lawchune2021waverys` — Law-Chune, Stéphane and others — WAVERYS: a CMEMS global wave reanalysis during the altimetry period
- `lellouche2021glorys12` — Lellouche, Jean-Michel and others — The Copernicus Global 1/12° Oceanic and Sea Ice GLORYS12 Reanalysis
- `locarnini2024woa23t` — Locarnini, Ricardo A. and others — World Ocean Atlas 2023, Volume 1: Temperature
- `nielsen2020` — Nielsen and Zampolli and Le Bras and others — CTBTO’s Data and Analysis Pertaining to the Search for the Missing Arg
- `oke2013ofam3` — Oke, Peter R. and others — Evaluation of a near-global eddy-resolving ocean model
- `oliveira2025` — Oliveira and Prior and Lin and others — Underwater explosions recorded at IMS hydroacoustic stations from well
- `prior2011` — Prior and Meless and Bittner and others — Long-Range Detection and Location of Shallow Underwater Explosions Usi
- `puri2013access` — Puri, K. and Dietachmayer, G. and Steinle, P. and Dix, M. and others — Implementation of the initial ACCESS numerical weather prediction syst
- `raumer2025` — Raumer and Bazin and Royer and others — Hydroacoustic geophony automatic detection: an open benchmark dataset 
- `reagan2024woa23s` — Reagan, James R. and others — World Ocean Atlas 2023, Volume 2: Salinity
- `royer2015` — Royer and Chateau and Dziak and others — Seafloor seismicity, Antarctic ice-sounds, cetacean vocalizations and 
- `schwardt2022` — Schwardt and Pilger and Gaebler and others — Natural and Anthropogenic Sources of Seismic, Hydroacoustic, and Infra
- `sutherland2020leeway` — Sutherland, Graig and others — Evaluating the leeway coefficient of ocean drifters using operational 
- `talandier2006` — Talandier and Hyvernaud and Reymond and others — Hydroacoustic signals generated by parked and drifting icebergs in the
- `theiler1992` — Theiler and Eubank and Longtin and others — Testing for nonlinearity in time series: the method of surrogate data
- `tolstoy2004` — Tolstoy and Diebold and Webb and others — Broadband calibration of R/V Ewing seismic sources
- `usman2016` — Usman and Nitz and Harry and others — The PyCBC search for gravitational waves from compact binary coalescen
- `vergoz2021` — Vergoz and Cansi and Cano and others — Analysis of Hydroacoustic Signals Associated to the Loss of the Argent
- `withers1998` — Withers and Aster and Young and others — A comparison of select trigger algorithms for automated global seismic
- `ws2009` — Wąs and Bizouard and Brisson and others — On the background estimation by time slides in a network of gravitatio
- `yeh2016` — Yeh and Zhu and Ulanova and others — Matrix Profile I: All Pairs Similarity Joins for Time Series: A Unifyi
- `yoon2015` — Yoon and O’Reilly and Bergen and others — Earthquake detection through computationally efficient similarity sear

**6 entries have no year**, and print as `(n.d.)`:

- `ciada1997austral2553` — Informe final de accidente de aviación: McDonnell Douglas DC-9-32, Austral Líneas Aéreas C
- `cmems_glo_wav_001_032` — Global Ocean Waves Reanalysis (GLOBAL_MULTIYEAR_WAV_001_032), dataset cmems_mod_glo_wav_my
- `dac1993copa201` — [Final report, in Spanish:] Copa Flight 201 Boeing 737-204 Advanced - 6 June 1992 - near T
- `fprg2016satcomlogs` — Internal study regarding SATCOM ground-station logs
- `india1978airindia855` — [Report of the Court of Inquiry into the accident to Air India Boeing 747 VT-EBD 'Emperor 
- `russia1994aeroflot593` — Report on the investigation into the crash of A310-308, registration F-OGQS, on 22 March 1

For the Boeing airport-planning document the year is on the document's own revision page; it needs reading off the copy we hold rather than guessing.

## 5. Candidate citations used in prose but absent from the library

Author–date patterns appearing three or more times in project prose that match no entry, no entry key and no institution field in the library. Organisation names and product codes are mixed in with real missing sources; the point of the list is that each one is either a citation the library is missing or a phrase that should not look like a citation.

| Appears as | Occurrences | My reading |
|---|---|---|
| OI 2018 | 160 | Ocean Infinity's 2018 search — a real citable source (its operations report / ATSB record), and the single most-used uncited string in the project |
| OI 2025 | 64 | Ocean Infinity's 2025 search resumption — citable, and current |
| FSST 2016 | 13 | not yet assessed |
| Leroy 2021 | 10 | not yet assessed |
| HL 2019 | 10 | a product or run code, not a citation |
| RA 2021 | 9 | a reanalysis product code, not a citation |
| Al-Qattan 2023 | 9 | not yet assessed |
| Nesterov 2018 | 9 | drift / windage literature — real missing entry |
| SUS 2003 | 8 | the SUS charge reference data — needs a proper source entry |
| Kerguelen 2014 | 8 | not yet assessed |
| NATSAR 2026 | 7 | not yet assessed |
| Miller 2021 | 7 | not yet assessed |
| Casey 2014 | 7 | not yet assessed |
| Orr 1976 | 7 | not yet assessed |
| JASDF 2019 | 7 | check: an organisation abbreviation in prose |
| Vance 2018 | 6 | bib key vance2018 (added 8 Nov 2026); copy not held; VERIFY publisher and ISBN |
| GA 2017 | 6 | Geoscience Australia 2017 — bathymetry survey data, citable |
| Brocher 1995 | 6 | not yet assessed |
| Leroy 2016 | 6 | not yet assessed |
| Franz 1959 | 6 | not yet assessed |
| Shukla 2018 | 6 | not yet assessed |
| FSST 2021 | 6 | not yet assessed |
| May-June 2003 | 5 | not yet assessed |
| Lyne 2024 | 5 | bib key lyne2024 (added 8 Nov 2026); title and DOI confirmed; issue date VERIFY |
| LaCasce 2008 | 5 | statistics of Lagrangian dispersion — real missing entry |
| DONE 2026 | 5 | not yet assessed |
| March-April 2014 | 5 | not yet assessed |
| Pengam 2016 | 5 | not yet assessed |
| Truscott 2014 | 5 | not yet assessed |
| Li 2021 | 5 | not yet assessed |
| Glowacki 2020 | 5 | not yet assessed |
| EDH 2014 | 5 | not yet assessed |
| Generator 2026 | 5 | our own generated output, not a citation |
| Kenyon 2020 | 4 | not yet assessed |
| LSCE 2016 | 4 | not yet assessed |
| Nosov 2007 | 4 | not yet assessed |
| Blackman's 2003 | 4 | not yet assessed |
| In 2014 | 4 | not yet assessed |
| NTRS 1973 | 4 | not yet assessed |
| Maximenko 2018 | 4 | surface-drift climatology — real missing entry |

**Finding.** On this evidence the library is roughly 15 to 20 entries short of what the project's own prose already relies on, and the largest single gap is the Ocean Infinity searches, referred to several hundred times and cited nowhere. The searched-areas likelihood rests on them. Closing this is the next citation task.

## 6. The library

Printed pages are deliberately **not** a column here. JON's Harvard style admits an in-text page only for a direct quotation (`JON-RULES.md` §6), and pages in this project are a property of a *claim*, not of a reference. They live with the claim in the module prose ledgers and will be carried into the reference draft. A reference-level page column would invite exactly the detachment of claim from page that it appears to prevent.

| Key | Reference (JON Harvard style) | Grade | Verification | Used by | Copy held |
|---|---|---|---|---|---|
| `aaiasb2006helios522` | Air Accident Investigation & Aviation Safety Board, Hellenic Republic (2006). Aircraft Accident Report: Helios Airways Flight HCY522, Boeing 737-31S, at Grammatiko, Hellas, on 14 August 2005. AAIASB, 11/2006. https://www.faa.gov/sites/faa.gov/files/2022-11/Helios737_AccidentReport.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `aaic1993lauda004` | Aircraft Accident Investigation Committee of Thailand (1993). Lauda Air Luftfahrt Aktiengesellschaft Boeing 767-300ER Registration OE-LAV, Dan Chang District, Suphan Buri Province, Thailand, 26 May B.E. 2534 (A.D. 1991). Aircraft Accident Investigation Committee, Thailand. https://www.faa.gov/sites/faa.gov/files/LaudaAccidentReport_0.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `abbott2016` | Abbott, Abbott, Abbott and others (2016). Observation of Gravitational Waves from a Binary Black Hole Merger. Physical Review Letters. https://doi.org/10.1103/physrevlett.116.061102. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `af447seabed2011` | Recovery of AF447 victims from the seabed, 2011 (secondary: Encyclopaedia Britannica; Al Jazeera, 16 June 2011) (2011). | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `allen1978` | Allen (1978). Automatic earthquake recognition and timing from single traces. Bulletin of the Seismological Society of America. https://doi.org/10.1785/bssa0680051521. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `andersen2005` | Andersen, A., Pesavento, U. and Wang, Z. J. (2005). Unsteady aerodynamics of fluttering and tumbling plates. Journal of Fluid Mechanics, 541, 65–90. | peer-reviewed | UNVERIFIED, NO DOI | settling (3 files) | - |
| `andersen2005b` | Andersen, A., Pesavento, U. and Wang, Z. J. (2005). Analysis of transitions between fluttering, tumbling and steady descent of falling cards. Journal of Fluid Mechanics, 541, 91–104. | peer-reviewed | UNVERIFIED, NO DOI | settling (3 files) | - |
| `anderson2001` | Anderson, Brady, Creighton and others (2001). Excess power statistic for detection of burst sources of gravitational radiation. Physical Review D. https://doi.org/10.1103/physrevd.63.042003. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `anderson2018` | Anderson (2018). Report on two shipwrecks found during the MH370 search. Western Australian Museum, for the ATSB. | official | UNVERIFIED, NO DOI | settling (6 files) | - |
| `antoni2006` | Antoni (2006). The spectral kurtosis: a useful tool for characterising non-stationary signals. Mechanical Systems and Signal Processing. https://doi.org/10.1016/j.ymssp.2004.09.001. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `antoni2007` | Antoni (2007). Fast computation of the kurtogram for the detection of transient faults. Mechanical Systems and Signal Processing. https://doi.org/10.1016/j.ymssp.2005.12.002. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `ap2014handheld` | Associated Press (2014). Ships race to site of signal in jet search. https://www.pressreader.com/usa/the-denver-post/20140407/281500749225589. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `Arons1954` | Arons, A. B. (1954). Underwater explosion shock wave parameters at large distances from the charge. J. Acoust. Soc. Am., 26, 343–346. https://doi.org/10.1121/1.1907339. | peer-reviewed | METADATA VERIFIED | hydroacoustics (12 files) | - |
| `ashton2015` | Ashton, C., Shuster Bruce, A., Colledge, G. and Dickinson, M. (2015). The Search for MH370. The Journal of Navigation, 68, 1–22. https://doi.org/10.1017/S037346331400068X. | peer-reviewed | METADATA VERIFIED | end of flight, hydroacoustics (25 files) | - |
| `atsb2011qf72` | Australian Transport Safety Bureau (2011). In-flight upset, 154 km west of Learmonth, WA, 7 October 2008, VH-QPA, Airbus A330-303. ATSB Transport Safety Report, Aviation Occurrence Investigation AO-2008-070, Final. ATSB, AO-2008-070. https://www.atsb.gov.au/investigations/ao-2008-070. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `atsb2014fpu` | Australian Transport Safety Bureau (2014). MH370 – Flight Path Analysis Update. ATSB. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | candidate |
| `atsb2015searchareas` | Australian Transport Safety Bureau (2015). MH370 – Definition of Underwater Search Areas. Australian Transport Safety Bureau, AE-2014-054. https://www.atsb.gov.au/sites/default/files/2022-12/AE-2014-054_MH370-Definition%20of%20Underwater%20Search%20Areas_3Dec2015.pdf. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `atsb2015searchareasa` | Australian Transport Safety Bureau (2014). MH370 – Definition of Underwater Search Areas. Australian Transport Safety Bureau, AE-2014-054. https://www.atsb.gov.au/sites/default/files/media/5668327/ae2014054_mh370__search_areas_30jul2015.pdf. | official | UNVERIFIED, NO DOI | - (no use traced) | - |
| `atsb2016sdu` | Australian Transport Safety Bureau (2016). MH370 – Search and debris examination update. ATSB, AE-2014-054. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `atsb2017operational` | Australian Transport Safety Bureau (2017). The Operational Search for MH370. Australian Transport Safety Bureau, AE-2014-054. | official | UNVERIFIED, NO DOI | searched areas, settling (no use traced) | candidate |
| `b777acaps` | Boeing Commercial Airplanes (2024). 777-200/-200ER/-300 Airplane Characteristics for Airport Planning. Boeing Commercial Airplanes, D6-58329, Rev. E. https://www.boeing.com/commercial/airports/plan-manuals. Accessed [DATE NOT RECORDED]. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `bahrain2002gulfair072` | Civil Aviation Affairs, Kingdom of Bahrain (2002). Accident Investigation Report: Gulf Air Flight GF-072, Airbus A320-212, Reg. A40-EK, on 23 August 2000 at Bahrain. Civil Aviation Affairs, Bahrain. https://bea.aero/fileadmin/documents/docspa/2000/a40-ek000823a/htm/a40-ek000823a.html. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `baillard2013` | Baillard, Crawford, Ballu and others (2013). An Automatic Kurtosis-Based P- and S-Phase Picker Designed for Local Seismic Networks. Bulletin of the Seismological Society of America. https://doi.org/10.1785/0120120347. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `barniv1985` | Barniv (1985). Dynamic Programming Solution for Detecting Dim Moving Targets. IEEE Transactions on Aerospace and Electronic Systems. https://doi.org/10.1109/taes.1985.310548. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `barrett2014` | Barrett and Beroza (2014). An Empirical Approach to Subspace Detection. Seismological Research Letters. https://doi.org/10.1785/0220130152. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `barton1958` | Barton and David (1958). Non-Randomness in a Sequence of Two Alternatives: II. Runs Test. Biometrika. https://doi.org/10.2307/2333062. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `bea2009frwg` | Bureau d'Enquêtes et d'Analyses (2009). Flight Data Recovery Working Group Report. BEA. | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `bea2012af447` | Bureau d'Enquêtes et d'Analyses (2012). Final Report on the accident on 1st June 2009 to the Airbus A330-203 registered F-GZCP operated by Air France, flight AF 447 Rio de Janeiro – Paris. BEA. https://bea.aero. | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `bea2016germanwings9525` | Bureau d'Enquêtes et d'Analyses pour la sécurité de l'aviation civile (2016). Final Report: Accident on 24 March 2015 at Prads-Haute-Bléone (Alpes-de-Haute-Provence, France) to the Airbus A320-211 registered D-AIPX operated by Germanwings. BEA, BEA2015-0125. https://bea.aero/uploads/tx_elydbrapports/BEA2015-0125.en-LR.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `beggan2026igrf14` | Beggan, C. D., Kloss, C., Xiong, C. and Matsushima, M. (2026). Special issue ``International Geomagnetic Reference Field: The Fourteenth Generation''. Earth, Planets and Space, 78, 196. https://doi.org/10.1186/s40623-026-02504-w. | peer-reviewed | METADATA VERIFIED | - (no use traced) | - |
| `benjamini1995` | Benjamini and Hochberg (1995). Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing. Journal of the Royal Statistical Society Series B: Statistical Methodology. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `blackman2004` | Blackman, de Groot-Hedlin, Harben and others (2004). Testing low/very low frequency acoustic sources for basin-wide propagation in the Indian Ocean. The Journal of the Acoustical Society of America, 116, 2057–2066. https://doi.org/10.1121/1.1786711. | peer-reviewed | METADATA VERIFIED | hydroacoustics (25 files) | - |
| `blackman2004b` | Blackman, de Groot-Hedlin, Orcutt and others (2004). Methods for Calibrating Basin-Wide Hydroacoustic Propagation in the Indian Ocean. Lawrence Livermore National Laboratory, UCRL-TR-207323. https://doi.org/10.2172/15011808. | official | METADATA VERIFIED | hydroacoustics (25 files) | - |
| `blackman2004ucrl` | Blackman and others (2004). UCRL-TR-207323: 2001 airgun calibration shots at H01 and H08 (held as digitised source). | grey | UNVERIFIED, NO DOI | hydroacoustics (25 files) | - |
| `boeingeofsims2016` | The Boeing Company (2016). End-of-flight engineering-simulator exports, ten cases. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `borio2009` | Borio and Akos (2009). Noncoherent Integrations for GNSS Detection: Analysis and Comparisons. IEEE Transactions on Aerospace and Electronic Systems. https://doi.org/10.1109/taes.2009.4805285. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `brown1975` | Brown (1975). 400: A Method for Combining Non-Independent, One-Sided Tests of Significance. Biometrics. https://doi.org/10.2307/2529826. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `brown2008` | Brown, Beroza and Shelly (2008). An autocorrelation method to detect low frequency earthquakes within tremor. Geophysical Research Letters. https://doi.org/10.1029/2008gl034560. | peer-reviewed | METADATA VERIFIED | hydroacoustics (3 files) | - |
| `brown2026` | Brown, McFadden, McCormack and others (2026). A search for hydroacoustic signals from bolides. Icarus. https://doi.org/10.1016/j.icarus.2026.117106. | peer-reviewed | METADATA VERIFIED | hydroacoustics (42 files) | - |
| `Brown2026` | Brown, P., McFadden, L., McCormack, D., Adams, M. and Vida, D. (2026). A search for hydroacoustic signals from bolides. Icarus. https://doi.org/10.48550/arXiv.2604.12723. | grey | METADATA VERIFIED | hydroacoustics (42 files) | - |
| `caac2022mu5735` | Civil Aviation Administration of China, Office of Aviation Safety (2022). Guanyu '3·21' Donghang MU5735 hangkongqi feixing shigu diaocha chubu baogao de qingkuang tongbao [Notice on the preliminary report of the investigation into the '3·21' China Eastern MU5735 aircraft accident] (in Chinese). CAAC. https://www.caac.gov.cn/XXGK/XXGK/TZTG/202204/t20220420_212895.html. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `cansi1995` | Cansi (1995). An automatic seismic event processing for detection and location: The P.M.C.C. Method. Geophysical Research Letters. https://doi.org/10.1029/95gl00468. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `capano2017` | Capano, Dent, Hanna and others (2017). Systematic errors in estimation of gravitational-wave candidate significance. Physical Review D. https://doi.org/10.1103/physrevd.96.082002. | peer-reviewed | METADATA VERIFIED | hydroacoustics (4 files) | - |
| `carlson1994` | Carlson, Evans and Wilson (1994). Search radar detection and track with the Hough transform. I. system concept. IEEE Transactions on Aerospace and Electronic Systems. https://doi.org/10.1109/7.250410. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `carver2023arcoera5` | Carver, R. W. and Merose, A. (2023). ARCO-ERA5: An Analysis-Ready Cloud-Optimized Reanalysis Dataset. 22nd Conference on Artificial Intelligence for Environmental Science, AMS Annual Meeting. https://github.com/google-research/arco-era5. | peer-reviewed | UNVERIFIED, NO DOI | ocean drift / transport (4 files) | - |
| `ccaa2010kenya507` | Cameroon Civil Aviation Authority (2010). Technical Investigation into the Accident of the B737-800 Registration 5Y-KYA Operated by Kenya Airways that Occurred on the 5th of May 2007 in Douala. CCAA. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `cdse2026` | European Space Agency (2026). Copernicus Data Space Ecosystem OData catalogue. https://catalogue.dataspace.copernicus.eu/odata/v1. Accessed 2026-10-18. | official | UNVERIFIED, NO DOI | - (no use traced) | - |
| `celestrak2026` | Kelso, T. S. (2026). CelesTrak SATCAT. https://celestrak.org/satcat/. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `cenipa2008gol1907` | Centro de Investigação e Prevenção de Acidentes Aeronáuticos (CENIPA), Command of Aeronautics, Brazil (2008). Final Report A-022/CENIPA/2008: PR-GTD and N600XL, B-737 8EH and EMB-135 BJ Legacy, 29 September 2006. CENIPA, A-022/CENIPA/2008. https://sistema.cenipa.fab.mil.br/cenipa/paginas/relatorios/rf/en/RF_PR-GTD_N600XL_29_09_06_Eng..pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `cfr14s25337` | Federal Aviation Administration (2016). 14 CFR 25.337 Limit maneuvering load factors. https://www.ecfr.gov/current/title-14/section-25.337. Accessed 2026-11-07. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `chamberlain2021bran2020` | Chamberlain, M. A. and others (2021). Next generation of Bluelink ocean reanalysis with multiscale data assimilation: BRAN2020. Earth System Science Data, 13, 5663–5688. https://doi.org/10.5194/essd-13-5663-2021. | peer-reviewed | METADATA VERIFIED | ocean drift / transport (3 files) | - |
| `chu2006` | Chu, P. C. and Fan, C. (2006). Prediction of falling cylinder through air-water-sediment columns. Journal of Applied Mechanics, 73, 300–314. | peer-reviewed | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `ciada1997austral2553` | Comisión Investigadora de Accidentes de Aviación, Dirección Nacional de Aviación Civil e Infraestructura Aeronáutica, Uruguay (n.d.). Informe final de accidente de aviación: McDonnell Douglas DC-9-32, Austral Líneas Aéreas Cielos del Sur S.A., LV-WEG, Nuevo Berlín, R.O.U., 10 de octubre de 1997 (in Spanish). CIADA. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `cmems_glo_wav_001_032` | E.U. Copernicus Marine Service Information (n.d.). Global Ocean Waves Reanalysis (GLOBAL_MULTIYEAR_WAV_001_032), dataset cmems_mod_glo_wav_my_0.2deg_PT3H-i, version 202411. https://doi.org/10.48670/moi-00022. Accessed [DATE NOT RECORDED]. | grey | METADATA MISMATCH | ocean drift / transport (1 file) | - |
| `cmems_mob_015_003` | E.U. Copernicus Marine Service Information (2024). Global Total (COPERNICUS-GLOBCURRENT), Ekman and Geostrophic currents at the Surface and 15m, MULTIOBS_GLO_PHY_MYNRT_015_003, version 202411. https://data.marine.copernicus.eu/product/MULTIOBS_GLO_PHY_MYNRT_015_003/description. Accessed [DATE NOT RECORDED]. | official | UNVERIFIED, NO DOI | ocean drift / transport (no use traced) | - |
| `CMST2014` | Duncan, A. J., Gavrilov, A. N. and McCauley, R. D. (2014). Analysis of low frequency underwater acoustic signals possibly related to the loss of Malaysian Airlines Flight MH370. Centre for Marine Science and Technology, Curtin University, CMST 1308, Report 2014-30. | official | UNVERIFIED, NO DOI | hydroacoustics (11 files) | - |
| `cmst2014report` | Curtin University Centre for Marine Science and Technology (2014). CMST report 2014-30: analysis of IMOS and IMS records for MH370 (held; pdf sha256 1c19b353562ff4cd...). | official | UNVERIFIED, NO DOI | hydroacoustics (12 files) | - |
| `cn12371_2014` | Xinhua / PLA Daily, via 12371.cn (2014). Zhongguo kongjun zai nan Yinduyang faxian piaofuwu [Chinese Air Force finds floating objects in the southern Indian Ocean]. https://news.12371.cn/2014/04/06/ARTI1396738988082649.shtml. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `coles2001` | Coles (2001). An Introduction to Statistical Modeling of Extreme Values. Springer Series in Statistics. https://doi.org/10.1007/978-1-4471-3675-0. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `Collins1993` | Collins, M. D. (1993). A split-step Padé solution for the parabolic equation method. J. Acoust. Soc. Am., 93, 1736–1742. https://doi.org/10.1121/1.406739. | peer-reviewed | METADATA VERIFIED | hydroacoustics (4 files) | - |
| `copernicusmarine_toolbox` | Copernicus Marine Service (2026). Copernicus Marine Toolbox (copernicusmarine) 2.5.0. https://toolbox-docs.marine.copernicus.eu. Accessed [DATE NOT RECORDED]. | official | UNVERIFIED, NO DOI | ocean drift / transport (no use traced) | - |
| `daai2016lam470` | Directorate of Aircraft Accident Investigations, Republic of Namibia (2016). Civil Aircraft Accident Report: Aircraft C9-EMC, Embraer 190, Bwabwata National Park, 29 November 2013. DAAI. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `dac1993copa201` | Dirección de Aeronáutica Civil, Republic of Panama (n.d.). [Final report, in Spanish:] Copa Flight 201 Boeing 737-204 Advanced - 6 June 1992 - near Tucuti, Darien - Republic of Panama. Dirección de Aeronáutica Civil, Panama. https://data.ntsb.gov/Docket?ProjectID=15961. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `dallosto2019` | Dall'Osto (2019). Source triangulation utilizing three-dimensional arrivals: Application to the search for the ARA San Juan submarine. The Journal of the Acoustical Society of America. https://doi.org/10.1121/1.5125251. | peer-reviewed | METADATA VERIFIED | hydroacoustics (10 files) | - |
| `dallosto2023` | Dall'Osto and Duncan (2023). Revisiting acoustic detections made in the Indian Ocean at the time of the loss of MH370. The Journal of the Acoustical Society of America. https://doi.org/10.1121/10.0022760. | peer-reviewed | METADATA VERIFIED | hydroacoustics (13 files) | - |
| `davey2007` | Davey, Rutten and Cheung (2007). A Comparison of Detection Performance for Several Track-before-Detect Algorithms. EURASIP Journal on Advances in Signal Processing. https://doi.org/10.1155/2008/428036. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `davey2016` | Davey, S., Gordon, N., Holland, I., Rutten, M. and Williams, J. (2016). Bayesian Methods in the Search for MH370. Springer. https://doi.org/10.1007/978-981-10-0379-0. | official | METADATA VERIFIED | end of flight, hydroacoustics, ocean drift (149 files) | yes |
| `dawid1984` | Dawid, A. P. (1984). Present Position and Potential Developments: Some Personal Views: Statistical Theory: The Prequential Approach. Journal of the Royal Statistical Society. Series A (General), 147, 278–290. https://doi.org/10.2307/2981683. | peer-reviewed | METADATA VERIFIED | end of flight (1 file) | - |
| `delmoral2006` | Del Moral, P., Doucet, A. and Jasra, A. (2006). Sequential Monte Carlo samplers. Journal of the Royal Statistical Society Series B: Statistical Methodology, 68, 411–436. https://doi.org/10.1111/j.1467-9868.2006.00553.x. | peer-reviewed | METADATA MISMATCH | - (no use traced) | - |
| `dnv2010` | Det Norske Veritas (2010). Risk Assessment of Pipeline Protection. DNV, DNV-RP-F107. | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `duncan2023` | Duncan and Dall'Osto (2023). Long-range underwater acoustic detection of aircraft surface impacts—The influence of acoustic propagation conditions and impact parameters. The Journal of the Acoustical Society of America, 154, A49. https://doi.org/10.1121/10.0022761. | peer-reviewed | METADATA VERIFIED | hydroacoustics (12 files) | - |
| `DuncanDallOsto2023lay` | Duncan, A. J. and Dall'Osto, D. R. (2023). The loss of an F35 fighter aircraft and the search for Malaysian Airlines flight MH370. https://acoustics.org/the-loss-of-an-f35-fighter-aircraft-and-the-search-for-malaysian-airlines-flight-mh370/. Accessed [DATE NOT RECORDED]. | grey | UNVERIFIED, NO DOI | hydroacoustics (12 files) | candidate |
| `durgadoo2021` | Durgadoo, J. V., Biastoch, A., New, A. L., Rühs, S., Nurser, Aylmer J. G., Drillet, Y. and Bidlot, J.-R. (2021). Strategies for simulating the drift of marine debris. Journal of Operational Oceanography, 14, 1–12. https://doi.org/10.1080/1755876X.2019.1602102. | peer-reviewed | METADATA VERIFIED | ocean drift (6 files) | - |
| `eaaid2024ms804` | Egyptian Aircraft Accident Investigation Directorate, Ministry of Civil Aviation (2024). [Final investigation report: accident to the Airbus A320-232 SU-GCC, EgyptAir flight MS804, Mediterranean Sea, 19 May 2016]. EAAID. https://bea.aero/en/investigation-reports/notified-events/detail/accident-to-the-airbus-a320-registered-su-gcc-and-operated-by-egyptair-on-05-19-2016-in-cruise-off-the-egyptian-coast-investigation-led-by-aib-egypt/. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `eaib2022et302` | Aircraft Accident Investigation Bureau, Federal Democratic Republic of Ethiopia (2022). Investigation Report on Accident to the B737-MAX8 Reg. ET-AVJ Operated by Ethiopian Airlines, 10 March 2019. EAIB, AI-01/19. https://bea.aero/fileadmin/user_upload/ET_302__B737-8MAX_ACCIDENT_FINAL_REPORT.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `easa2023cs25` | European Union Aviation Safety Agency (2023). Certification Specifications and Acceptable Means of Compliance for Large Aeroplanes (CS-25), Amendment 28. https://www.easa.europa.eu/en/document-library/certification-specifications/cs-25-amendment-28. Accessed 2026-11-07. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `era5` | Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A., Muñoz-Sabater, J., Nicolas, J., Peubey, C., Radu, R., Schepers, D., Simmons, A., Soci, C., Abdalla, S., Abellan, X., Balsamo, G., Bechtold, P., Biavati, G., Bidlot, J., Bonavita, M., De Chiara, G., Dahlgren, P., Dee, D., Diamantakis, M., Dragani, R., Flemming, J., Forbes, R., Fuentes, M., Geer, A., Haimberger, L., Healy, S., Hogan, R. J., Hólm, E., Janisková, M., Keeley, S., Laloyaux, P., Lopez, P., Lupu, C., Radnoti, G., de Rosnay, P., Rozum, I., Vamborg, F., Villaume, S. and Thépaut, J.-N. (2020). The ERA5 global reanalysis. Quarterly Journal of the Royal Meteorological Society, 146, 1999–2049. https://doi.org/10.1002/qj.3803. | peer-reviewed | METADATA VERIFIED | Pleiades, ocean drift, ocean drift / transport (6 files) | - |
| `esdu-windmill` | ESDU (1981). Estimation of windmilling drag and airflow of turbo-jet and turbo-fan engines. ESDU International, 81009, Amendment A (1 April 1984). | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `esdu84004` | ESDU (1984). Estimation of spillage drag for a wide range of axisymmetric intakes at M less than 1. ESDU International, 84004, Amendment A (1 June 1984). | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `esdu84005` | ESDU (1984). Estimation of drag due to inoperative turbo-jet and turbo-fan engines using Data Item Nos 81009 and 84004. ESDU International, 84005, Amendment A (1 March 1989). | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `esr2021oscar` | ESR and Dohan, K. (2021). Ocean Surface Current Analyses Real-time (OSCAR) Surface Currents - Final 0.25 Degree (Version 2.0). PO.DAAC. https://doi.org/10.5067/OSCAR-25F20. Accessed [DATE NOT RECORDED]. | grey | METADATA VERIFIED | ocean drift / transport (5 files) | - |
| `faa2024part60` | Federal Aviation Administration (2024). 14 CFR Part 60, Flight Simulation Training Device Initial and Continuing Qualification and Use, Appendix A, Attachment 2, Table A2A: Full Flight Simulator Objective Tests. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `FDSNIM` | Various Institutions (1965). International Miscellaneous Stations (FDSN network IM; IMS hydroacoustic station metadata). International Federation of Digital Seismograph Networks. https://doi.org/10.7914/vefq-vh75. Accessed [DATE NOT RECORDED]. | grey | METADATA MISMATCH | hydroacoustics (1 file) | - |
| `field1997` | Field, S. B., Klaus, M., Moore, M. G. and Nori, F. (1997). Chaotic dynamics of falling disks. Nature, 388, 252–254. https://doi.org/10.1038/40817. | peer-reviewed | METADATA VERIFIED | settling (3 files) | - |
| `fox2001` | Fox, Matsumoto and Lau (2001). Monitoring Pacific Ocean seismicity from an autonomous hydrophone array. Journal of Geophysical Research: Solid Earth. https://doi.org/10.1029/2000jb900404. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `fprg2016satcomlogs` | MH370 Flight Path Reconstruction Group, SATCOM Subgroup (n.d.). Internal study regarding SATCOM ground-station logs. MH370 Flight Path Reconstruction Group. | official | UNVERIFIED, NO DOI | - (no use traced) | - |
| `france1976thy981` | Secrétariat d'État aux Transports, Commission d'enquête (1976). Turkish Airlines DC-10 TC-JAV: Report on the accident in the Ermenonville Forest, France on 3 March 1974. Translation of the report published by the French Secretariat of State for Transport. Accidents Investigation Branch, Department of Trade, Aircraft Accident Report 8/76. Secrétariat d'État aux Transports, AIB Aircraft Accident Report 8/76. https://assets.publishing.service.gov.uk/media/5422eedde5274a1317000247/8-1976_TC-JAV.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `FrancoisGarrison1982a` | Francois, R. E. and Garrison, G. R. (1982). Sound absorption based on ocean measurements: Part I: Pure water and magnesium sulfate contributions. J. Acoust. Soc. Am., 72, 896–907. https://doi.org/10.1121/1.388170. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `FrancoisGarrison1982b` | Francois, R. E. and Garrison, G. R. (1982). Sound absorption based on ocean measurements. Part II: Boric acid contribution and equation for total absorption. J. Acoust. Soc. Am., 72, 1879–1890. https://doi.org/10.1121/1.388673. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `ga2017searchareas` | Geoscience Australia (2017). MH370 search area survey geometry. | grey | UNVERIFIED, NO DOI | searched areas (no use traced) | - |
| `GaspinShuler1971` | Gaspin, J. B. and Shuler, V. K. (1971). Source Levels of Shallow Underwater Explosions. Naval Ordnance Laboratory, NOLTR 71-160. | official | UNVERIFIED, NO DOI | hydroacoustics (10 files) | - |
| `gdp6h` | Lumpkin, R. and Centurioni, L. (2019). Global Drifter Program quality-controlled 6-hour interpolated data from ocean surface drifting buoys. NOAA National Centers for Environmental Information. https://doi.org/10.25921/7ntx-z961. Accessed [DATE NOT RECORDED]. | official | METADATA MISMATCH | ocean drift, ocean drift / transport (6 files) | - |
| `GEBCO2026` | GEBCO Bathymetric Compilation Group 2026 (2026). The GEBCO_2026 Grid – a continuous terrain model for oceans and land at 15 arc-second intervals. NERC EDS British Oceanographic Data Centre NOC. https://doi.org/10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa. Accessed [DATE NOT RECORDED]. | grey | METADATA VERIFIED | hydroacoustics, ocean drift / transport (8 files) | - |
| `gelman2013bda` | Gelman, A., Carlin, J. B., Stern, H. S., Dunson, D. B., Vehtari, A. and Rubin, D. B. (2013). Bayesian Data Analysis. Chapman and Hall/CRC. https://doi.org/10.1201/b16018. | official | METADATA VERIFIED | end of flight (1 file) | candidate |
| `gibbons2006` | Gibbons and Ringdal (2006). The detection of low magnitude seismic events using array-based waveform correlation. Geophysical Journal International. https://doi.org/10.1111/j.1365-246x.2006.02865.x. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `gilks2001` | Gilks, W. R. and Berzuini, C. (2001). Following a moving target–-Monte Carlo inference for dynamic Bayesian models. Journal of the Royal Statistical Society Series B: Statistical Methodology, 63, 127–146. https://doi.org/10.1111/1467-9868.00280. | peer-reviewed | METADATA MISMATCH | - (no use traced) | - |
| `globaltimes2014expanded` | Global Times (2014). Ships try to pick up suspicious signals detected by Haixun 01. https://www.globaltimes.cn/content/853171.shtml. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `glorys12` | E.U. Copernicus Marine Service Information (2018). Global Ocean Physics Reanalysis (GLOBAL_MULTIYEAR_PHY_001_030). Mercator Ocean International. https://doi.org/10.48670/moi-00021. Accessed [DATE NOT RECORDED]. | official | METADATA MISMATCH | Pleiades, ocean drift, ocean drift / transport (4 files) | - |
| `gordon1993` | Gordon, N. J., Salmond, D. J. and Smith, A. F. M. (1993). Novel approach to nonlinear/non-Gaussian Bayesian state estimation. IEE Proceedings F (Radar and Signal Processing), 140, 107–113. https://doi.org/10.1049/ip-f-2.1993.0015. | peer-reviewed | METADATA MISMATCH | - (no use traced) | - |
| `graeber2004` | Graeber and Piserchia (2004). Zones ofT-wave excitation in the NE Indian ocean mapped using variations in backazimuth over time obtained from multi-channel correlation of IMS hydrophone triplet data. Geophysical Journal International. https://doi.org/10.1111/j.1365-246x.2004.02301.x. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `griffa1996stochastic` | Griffa, A. (1996). Applications of stochastic particle models to oceanographic problems. Stochastic Modelling in Physical Oceanography. Birkhäuser. | official | UNVERIFIED, NO DOI | ocean drift / transport (1 file) | - |
| `griffin2016parti` | Griffin, D. A., Oke, P. R. and Jones, E. M. (2016). The search for MH370 and ocean surface drift. CSIRO Oceans and Atmosphere, EP167888. https://doi.org/10.4225/08/5892224dec08c. | official | METADATA VERIFIED | ocean drift (8 files) | - |
| `griffin2017partii` | Griffin, D. A., Oke, P. R. and Jones, E. M. (2017). The search for MH370 and ocean surface drift – Part II. CSIRO Oceans and Atmosphere, EP172633. | official | UNVERIFIED, NO DOI | ocean drift, ocean drift / transport (14 files) | - |
| `griffin2017partiii` | Griffin, D. A. and Oke, P. R. (2017). The search for MH370 and ocean surface drift – Part III. CSIRO Oceans and Atmosphere, EP174155. | official | UNVERIFIED, NO DOI | ocean drift (14 files) | - |
| `gross2010` | Gross and Vitells (2010). Trial factors for the look elsewhere effect in high energy physics. The European Physical Journal C. https://doi.org/10.1140/epjc/s10052-010-1470-8. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `gshhg237` | Wessel, P. and Smith, Walter H. F. (2017). GSHHG: Global Self-consistent, Hierarchical, High-resolution Geography Database, version 2.3.7. https://www.soest.hawaii.edu/pwessel/gshhg/. Accessed [DATE NOT RECORDED]. | grey | UNVERIFIED, NO DOI | ocean drift / transport (no use traced) | - |
| `gur2010drag` | Gur, O., Mason, W. H. and Schetz, J. A. (2010). Full-Configuration Drag Estimation. Journal of Aircraft, 47, 1356–1367. https://doi.org/10.2514/1.47557. | peer-reviewed | METADATA VERIFIED | end of flight (1 file) | - |
| `HandleyLemos2019` | Handley, W. and Lemos, P. (2019). Quantifying tensions in cosmological parameters: Interpreting the DES evidence ratio. Physical Review D, 100, 043504. https://doi.org/10.1103/PhysRevD.100.043504. | peer-reviewed | METADATA VERIFIED | Pleiades (7 files) | - |
| `hanson2001` | Hanson, Le Bras, Dysart and others (2001). Operational Processing of Hydroacoustics at the Prototype International Data Center. Pure and Applied Geophysics. https://doi.org/10.1007/pl00001190. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `harris2006` | Harris and Paik (2006). Subspace Detectors: Efficient Implementation. https://doi.org/10.2172/898451. | grey | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `harris2011` | Harris and Dodge (2011). An Autonomous System for Grouping Events in a Developing Aftershock Sequence. Bulletin of the Seismological Society of America. https://doi.org/10.1785/0120100103. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `hastings1970` | Hastings, W. K. (1970). Monte Carlo sampling methods using Markov chains and their applications. Biometrika, 57, 97–109. https://doi.org/10.1093/biomet/57.1.97. | peer-reviewed | METADATA VERIFIED | end of flight (1 file) | - |
| `heffley1972cr2144` | Heffley, R. K. and Jewell, W. F. (1972). Aircraft Handling Qualities Data. National Aeronautics and Space Administration, NASA CR-2144. | official | UNVERIFIED, NO DOI | end of flight (5 files) | - |
| `heyburn2020` | Heyburn, Bowers and Green (2020). Seismic and hydroacoustic observations from recent underwater events in the South Atlantic Ocean. Geophysical Journal International. https://doi.org/10.1093/gji/ggaa291. | peer-reviewed | METADATA VERIFIED | hydroacoustics (3 files) | - |
| `hinata2017` | Hinata, H., Mori, K., Ohno, K., Miyao, Y. and Kataoka, T. (2017). An estimation of the average residence times and onshore-offshore diffusivities of beached microplastics based on the population decay of tagged meso- and macrolitter. Marine Pollution Bulletin, 122, 17–26. https://doi.org/10.1016/j.marpolbul.2017.05.012. | peer-reviewed | METADATA VERIFIED | ocean drift (3 files) | - |
| `holland2018` | Holland, I. D. (2018). MH370 Burst Frequency Offset Analysis and Implications on Descent Rate at End-of-Flight. IEEE Aerospace and Electronic Systems Magazine, 33, 24–33. https://doi.org/10.1109/MAES.2018.170048. | peer-reviewed | METADATA VERIFIED | end of flight (9 files) | yes |
| `holland2018oacopy` | Holland, I. D. (2018). MH370 Burst Frequency Offset Analysis and Implications on Descent Rate at End-of-Flight (author's accepted version). https://arxiv.org/abs/1702.02432v3. Accessed 12 October 2026. | grey | UNVERIFIED, NO DOI | - (9 files) | yes |
| `hull2007` | Hull, D. G. (2007). Fundamentals of Airplane Flight Mechanics. Springer. https://doi.org/10.1007/978-3-540-46573-7. | official | METADATA VERIFIED | end of flight (1 file) | - |
| `iac2007pulkovo612` | Interstate Aviation Committee, Technical Commission (2007). Okonchatel'nyi otchet po rezul'tatam rassledovaniya aviatsionnogo proisshestviya s samoletom Tu-154M RA-85185 aviakompanii 'Pulkovo' 22.08.2006 v raione n.p. Sukhaya Balka Konstantinovskogo raiona Donetskoi oblasti, Ukraina [Final report on the investigation of the accident to Tu-154M RA-85185 of Pulkovo Airlines, 22 August 2006, Donetsk Region, Ukraine] (in Russian). IAC. https://mak-iac.org/rassledovaniya/tu-154-ra-85185-22-08-2006/. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `iac2015tatarstan363` | Interstate Aviation Committee, Air Accident Investigation Commission (2015). Okonchatel'nyi otchet po rezul'tatam rassledovaniya aviatsionnogo proisshestviya: Boeing 737-500 (53A) VQ-BBN, Kazan International Airdrome, 17.11.2013 [Final report on the results of the investigation of the aviation accident: Boeing 737-500 (53A) VQ-BBN, Kazan, 17 November 2013] (in Russian). IAC. https://mak-iac.org/upload/iblock/ba0/report_vq-bbn.pdf. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `iac2019flydubai981` | Interstate Aviation Committee, Air Accident Investigation Commission (2019). Final Report: Boeing 737-8KN A6-FDN, fatal accident at Rostov-on-Don aerodrome, Rostov Region, Russian Federation, 19 March 2016 (English translation; the Russian original is the text of reference). IAC. https://mak-iac.org/upload/iblock/1e8/report_a6-fdn_eng.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `iac2019saratov703` | Interstate Aviation Committee, Air Accident Investigation Commission (2019). Okonchatel'nyi otchet po rezul'tatam rassledovaniya aviatsionnogo proisshestviya: samolet An-148-100V RA-61704, Moskovskaya oblast', Ramenskii raion, 11.02.2018 [Final report on the results of the investigation of the aviation accident: An-148-100V RA-61704, Moscow Region, 11 February 2018] (in Russian). IAC. https://mak-iac.org/upload/iblock/560/report_ra-61704.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `iannello2018` | Iannello, V. (2018). End-of-flight simulations (web article; VERIFY title and URL from the archive snapshot). | grey | UNVERIFIED, NO DOI | end of flight (12 files) | - |
| `icao2014wp30` | Australia (2014). MH370 Search and Rescue Response – JRCC Australia. | official | UNVERIFIED, NO DOI | - (no use traced) | - |
| `IMOSANMNPA` | IMOS (2026). Australian National Mooring Network passive acoustic observatories (Curtin University CMST loggers). https://imos-data.s3-ap-southeast-2.amazonaws.com/IMOS/ANMN/Acoustic/. Accessed [DATE NOT RECORDED]. | grey | UNVERIFIED, NO DOI | hydroacoustics (1 file) | - |
| `india1978airindia855` | Government of India, Court of Inquiry (Justice M. N. Chandurkar) (n.d.). [Report of the Court of Inquiry into the accident to Air India Boeing 747 VT-EBD 'Emperor Ashoka' off Bombay on 1 January 1978]. Government of India. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `ioc2010teos10` | IOC, S. and IAPSO (2010). The international thermodynamic equation of seawater – 2010: Calculation and use of thermodynamic properties. Intergovernmental Oceanographic Commission, UNESCO, 56. | grey | UNVERIFIED, NO DOI | ocean drift / transport (no use traced) | - |
| `ishii2005` | Ishii, Shearer, Houston and others (2005). Extent, duration and speed of the 2004 Sumatra–Andaman earthquake imaged by the Hi-Net array. Nature. https://doi.org/10.1038/nature03675. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `iso2533` | International Organization for Standardization (1975). Standard Atmosphere. International Organization for Standardization, ISO 2533:1975. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `jacc2014map012` | Joint Agency Coordination Centre (2014). Position of signals received by Hai Xun 01 (5 April 2014) and Ocean Shield (6 April 2014) [map]. http://web.archive.org/web/20140407112329/http://www.jacc.gov.au/media/releases/2014/april/mr_012-1.jpg. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `jacc2014map013` | Joint Agency Coordination Centre (2014). Planned search areas 08 April 2014, sonobuoy search 250 sq km [map]. http://web.archive.org/web/20150318144905/http://www.jacc.gov.au/media/releases/2014/april/mr_013-5.jpg. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `jacc2014mr010` | Joint Agency Coordination Centre (2014). Media Reporting on Chinese Ship Detection of Electronic Pulse Signals. http://web.archive.org/web/20140405191319/http://www.jacc.gov.au/media/releases/2014/april/mr010.aspx. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `jacc2014mr011` | Joint Agency Coordination Centre (2014). Search and recovery continues for Malaysian flight MH370. http://web.archive.org/web/20140406022110/http://www.jacc.gov.au/media/releases/2014/april/mr011.aspx. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | candidate |
| `jacc2014tr006` | Joint Agency Coordination Centre (2014). Transcript of Press Conference, 6 April 2014. http://web.archive.org/web/20140408000655/http://www.jacc.gov.au/media/interviews/2014/april/tr006.aspx. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `jacc2014tr007` | Joint Agency Coordination Centre (2014). Transcript of Press Conference, 7 April 2014. http://web.archive.org/web/20140408153652/http://www.jacc.gov.au/media/interviews/2014/april/tr007.aspx. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `jacc2014tr008` | Joint Agency Coordination Centre (2014). Transcript of Press Conference, 9 April 2014. http://web.archive.org/web/20140412010244/http://www.jacc.gov.au/media/interviews/2014/april/tr008.aspx. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `jacc2014tr009` | Joint Agency Coordination Centre (2014). Transcript of Press Conference, 14 April 2014. http://web.archive.org/web/20140415082809/http://www.jacc.gov.au/media/interviews/2014/april/tr009.aspx. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `Jeffreys1961` | Jeffreys, H. (1961). Theory of Probability. Oxford University Press. | official | UNVERIFIED, NO DOI | hydroacoustics (3 files) | - |
| `Jensen2011` | Jensen, F. B., Kuperman, W. A., Porter, M. B. and Schmidt, H. (2011). Computational Ocean Acoustics. Springer. https://doi.org/10.1007/978-1-4419-8678-8. | official | METADATA VERIFIED | hydroacoustics (4 files) | - |
| `jiaa1996birgenair301` | Junta Investigadora de Accidentes Aéreos, Dirección General de Aeronáutica Civil, Dominican Republic (1996). Final Aviation Accident Report: Birgenair Flight ALW-301, Puerto Plata, Dominican Republic, February 6, 1996. JIAA. https://www.faa.gov/sites/faa.gov/files/Birgenair301_Accident_Report.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `jiaac2010wca708` | Junta Investigadora de Accidentes de Aviación Civil, República Bolivariana de Venezuela (2010). Informe Final Caso West Caribbean HK4374X, vuelo WCW708, Machiques, Estado Zulia, 16 de agosto de 2005 (in Spanish). JIAAC, Expediente JIAAC-9-058-2005. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `kadri2017` | Kadri, Crivelli, Parsons and others (2017). Rewinding the waves: tracking underwater signals to their source. Scientific Reports. https://doi.org/10.1038/s41598-017-14177-3. | peer-reviewed | METADATA VERIFIED | hydroacoustics (23 files) | - |
| `kadri2019` | Kadri (2019). Effect of sea-bottom elasticity on the propagation of acoustic–gravity waves from impacting objects. Scientific Reports, 9, 912. https://doi.org/10.1038/s41598-018-37626-z. | peer-reviewed | METADATA VERIFIED | hydroacoustics (28 files) | - |
| `kadri2024` | Kadri (2024). Underwater acoustic analysis reveals unique pressure signals associated with aircraft crashes in the sea: revisiting MH370. Scientific Reports, 14, 10102. https://doi.org/10.1038/s41598-024-60529-1. | peer-reviewed | METADATA VERIFIED | hydroacoustics (65 files) | - |
| `kadri2025snt` | Kadri (2025). CTBTO Science and Technology Conference 2025 poster on MH370 hydroacoustic signals (held as digitised source). | official | UNVERIFIED, NO DOI | hydroacoustics (10 files) | - |
| `KadriAbdolaliKirby2025` | Kadri, U., Abdolali, A. and Kirby, J. T. (2025). Acoustic-gravity quantum tunnelling analogy. J. Fluid Mech., 1018, A18. | peer-reviewed | UNVERIFIED, NO DOI | hydroacoustics (10 files) | - |
| `kahn1955` | Kahn, H. (1955). Use of Different Monte Carlo Sampling Techniques. RAND Corporation, P-766. https://www.rand.org/pubs/papers/P766.html. | official | UNVERIFIED, NO DOI | end of flight (1 file) | - |
| `kaiser1990` | Kaiser (1990). On a simple algorithm to calculate the 'energy' of a signal. International Conference on Acoustics, Speech, and Signal Processing. https://doi.org/10.1109/icassp.1990.115702. | peer-reviewed | METADATA MISMATCH | hydroacoustics (1 file) | - |
| `kao2004` | Kao and Shan (2004). The Source-Scanning Algorithm: mapping the distribution of seismic sources in time and space. Geophysical Journal International. https://doi.org/10.1111/j.1365-246x.2004.02276.x. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `Karney2013` | Karney, C. F. F. (2013). Algorithms for geodesics. J. Geodesy, 87, 43–55. https://doi.org/10.1007/s00190-012-0578-z. | peer-reviewed | METADATA VERIFIED | hydroacoustics, ocean drift / transport (3 files) | - |
| `KassRaftery1995` | Kass, R. E. and Raftery, A. E. (1995). Bayes Factors. J. Am. Stat. Assoc., 90, 773–795. https://doi.org/10.1080/01621459.1995.10476572. | peer-reviewed | METADATA VERIFIED | hydroacoustics (4 files) | - |
| `killick2012` | Killick, Fearnhead and Eckley (2012). Optimal Detection of Changepoints With a Linear Computational Cost. Journal of the American Statistical Association. https://doi.org/10.1080/01621459.2012.737745. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `kiser2017` | Kiser and Ishii (2017). Back-Projection Imaging of Earthquakes. Annual Review of Earth and Planetary Sciences. https://doi.org/10.1146/annurev-earth-063016-015801. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `kish1965` | Kish, L. (1965). Survey Sampling. John Wiley and Sons. | official | UNVERIFIED, NO DOI | end of flight (1 file) | - |
| `kitagawa1996` | Kitagawa, G. (1996). Monte Carlo filter and smoother for non-Gaussian nonlinear state space models. Journal of Computational and Graphical Statistics, 5, 1–25. https://doi.org/10.1080/10618600.1996.10474692. | peer-reviewed | METADATA VERIFIED | - (no use traced) | - |
| `knijnenburg2009` | Knijnenburg, Wessels, Reinders and others (2009). Fewer permutations, more accurate P -values. Bioinformatics. https://doi.org/10.1093/bioinformatics/btp211. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `knkt2015airasia8501` | Komite Nasional Keselamatan Transportasi (2015). Aircraft Accident Investigation Report: PT. Indonesia Air Asia, Airbus A320-216; PK-AXC, Karimata Strait, Coordinate 3°37'19"S - 109°42'41"E, Republic of Indonesia, 28 December 2014. Final. KNKT, KNKT.14.12.29.04. https://bea.aero/uploads/tx_elydbrapports/Final_Report_PK-AXC-reduite.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `knkt2019lionair610` | Komite Nasional Keselamatan Transportasi (2019). Final KNKT.18.10.35.04 Aircraft Accident Investigation Report: PT. Lion Mentari Airlines, Boeing 737-8 (MAX); PK-LQP, Tanjung Karawang, West Java, Republic of Indonesia, 29 October 2018. KNKT, KNKT.18.10.35.04. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `knkt2022sriwijaya182` | Komite Nasional Keselamatan Transportasi (2022). Final KNKT.21.01.01.04 Aircraft Accident Investigation Report: PT Sriwijaya Air, Boeing 737-500; PK-CLC, Kepulauan Seribu District, DKI Jakarta, Republic of Indonesia, 9 January 2021. KNKT, KNKT.21.01.01.04. https://knkt.go.id/Repo/Files/Laporan/Penerbangan/2021/KNKT.21.01.01.04-Final-Report.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `kong1994` | Kong, A., Liu, J. S. and Wong, W. H. (1994). Sequential Imputations and Bayesian Missing Data Problems. Journal of the American Statistical Association, 89, 278–288. https://doi.org/10.1080/01621459.1994.10476469. | peer-reviewed | METADATA VERIFIED | end of flight (1 file) | - |
| `kulldorff1997` | Kulldorff (1997). A spatial scan statistic. Communications in Statistics - Theory and Methods. https://doi.org/10.1080/03610929708831995. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `kunsch1989` | Kunsch (1989). The Jackknife and the Bootstrap for General Stationary Observations. The Annals of Statistics. https://doi.org/10.1214/aos/1176347265. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `lawchune2021waverys` | Law-Chune, S. and others (2021). WAVERYS: a CMEMS global wave reanalysis during the altimetry period. Ocean Dynamics, 71, 357–378. https://doi.org/10.1007/s10236-020-01433-w. | peer-reviewed | METADATA VERIFIED | ocean drift / transport (1 file) | - |
| `lebanon2012et409` | Republic of Lebanon, Ministry of Public Works & Transport (2012). Investigation Report on the Accident to Ethiopian 409, Boeing 737-800, Registration ET-ANB, at Beirut, Lebanon, on 25th January 2010. Ministry of Public Works & Transport, Lebanon. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `lellouche2021glorys12` | Lellouche, J.-M. and others (2021). The Copernicus Global 1/12° Oceanic and Sea Ice GLORYS12 Reanalysis. Frontiers in Earth Science, 9, 698876. https://doi.org/10.3389/feart.2021.698876. | peer-reviewed | METADATA VERIFIED | ocean drift / transport (5 files) | - |
| `li2008` | Li and Gavrilov (2008). Localization of Antarctic ice breaking events by frequency dispersion of the signals received at a single hydroacoustic station in the Indian Ocean. The Journal of the Acoustical Society of America. https://doi.org/10.1121/1.2932527. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `ljung1978` | Ljung and Box (1978). On a measure of lack of fit in time series models. Biometrika. https://doi.org/10.1093/biomet/65.2.297. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `locarnini2024woa23t` | Locarnini, R. A. and others (2024). World Ocean Atlas 2023, Volume 1: Temperature. https://doi.org/10.25923/54bh-1613. | official | METADATA VERIFIED | ocean drift / transport (3 files) | - |
| `lorden1971` | Lorden (1971). Procedures for Reacting to a Change in Distribution. The Annals of Mathematical Statistics. https://doi.org/10.1214/aoms/1177693055. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `mali2016ah5017` | Commission d'enquête sur les accidents d'aviation civile, Ministère de l'Équipement, des Transports et du Désenclavement, République du Mali (2016). Final Report: Accident on 24 July 2014 near Gossi (Mali) to the McDonnell Douglas DC-9-83 (MD-83) registered EC-LTV operated by Swiftair S.A.. Mali Commission of Inquiry. https://bea.aero/fileadmin/uploads/tx_elydbrapports/ec-v140724.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `margo1990` | Board of Inquiry (Margo Commission) (1990). Report of the Board of Inquiry into the Helderberg Air Disaster. Board of Inquiry (Margo Commission). | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `mca2006flash604` | Ministry of Civil Aviation, Arab Republic of Egypt (2006). Final Report of the Accident Investigation: Flash Airlines Flight 604, January 3, 2004, Boeing 737-300 SU-ZCF, Red Sea off Sharm El-Sheikh, Egypt. Ministry of Civil Aviation, Egypt. https://bea.aero/docspa/2004/su-f040103a/pdf/su-f040103a.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `mca2006fsh604` | Egyptian Ministry of Civil Aviation (2006). Final Report of the Accident Investigation, Flash Airlines Flight 604, January 3, 2004, Boeing 737-300 SU-ZCF, Red Sea off Sharm El-Sheikh, Egypt. Ministry of Civil Aviation, Egypt. | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `McDougallBarker2011` | McDougall, T. J. and Barker, P. M. (2011). Getting started with TEOS-10 and the Gibbs Seawater (GSW) Oceanographic Toolbox. SCOR/IAPSO WG127. | grey | UNVERIFIED, NO DOI | hydroacoustics, ocean drift / transport (5 files) | - |
| `mearns1994` | Mearns, D. L. (1994). MV Derbyshire survey report. International Transport Workers' Federation. | grey | UNVERIFIED, NO DOI | settling (2 files) | - |
| `metron2011` | Stone, L. D., Keller, C. M., Kratzke, T. M. and Strumpfer, J. P. (2011). Search Analysis for the Location of the AF447 Underwater Wreckage. Metron Inc., Reston, Virginia. https://bea.aero/fileadmin/uploads/tx_elyextendttnews/metron.search.analysis_01.pdf. | grey | UNVERIFIED, NO DOI | settling (10 files) | - |
| `metropolis1953` | Metropolis, N., Rosenbluth, A. W., Rosenbluth, M. N., Teller, A. H. and Teller, E. (1953). Equation of State Calculations by Fast Computing Machines. The Journal of Chemical Physics, 21, 1087–1092. https://doi.org/10.1063/1.1699114. | peer-reviewed | METADATA VERIFIED | end of flight (1 file) | - |
| `metz2022` | Metz, Obana and Fukao (2022). Remote Hydroacoustic Detection of an Airplane Crash. Pure and Applied Geophysics, 180, 1343–1351. https://doi.org/10.1007/s00024-022-03117-6. | peer-reviewed | METADATA VERIFIED | hydroacoustics (8 files) | yes |
| `metz2022b` | Metz (2022). Analysis of International Monitoring System hydrophone triplet data: Identifying the August 2021 eruption at Fukutoku-Okanoba, 24.3°N Bonin Arc. Acoustical Science and Technology. https://doi.org/10.1250/ast.43.125. | peer-reviewed | METADATA VERIFIED | hydroacoustics (6 files) | - |
| `mh370caption_oi_tracings` | MH370-CAPTION community (2026). Traced outlines of the Ocean Infinity 2018 and 2025–26 search areas. | official | UNVERIFIED, NO DOI | searched areas (no use traced) | - |
| `minchin2017pleiades` | Minchin, S., Mueller, N., Lewis, A., Byrne, G. and Tran, M. (2017). Summary of imagery analyses for non-natural objects in support of the search for Flight MH370: Results from the analysis of imagery from the PLEIADES 1A satellite undertaken by Geoscience Australia. Geoscience Australia, Record 2017/013. https://doi.org/10.11636/record.2017.013. | official | METADATA VERIFIED | Pleiades (7 files) | - |
| `mot2015factual` | Malaysian ICAO Annex 13 Safety Investigation Team for MH370 (2015). Factual Information: Safety Investigation for MH370, Malaysia Airlines MH370 Boeing B777-200ER (9M-MRO), 08 March 2014. Ministry of Transport Malaysia, MH370/01/15. | official | UNVERIFIED, NO DOI | - (no use traced) | - |
| `mot2017` | Malaysian ICAO Annex 13 Safety Investigation Team for MH370 (2017). Summary of Possible MH370 Debris Recovered (updated 30 April 2017). Ministry of Transport Malaysia. | official | UNVERIFIED, NO DOI | ocean drift (no use traced) | - |
| `mot2018mh370` | Malaysian ICAO Annex 13 Safety Investigation Team for MH370 (2018). Safety Investigation Report, Malaysia Airlines Boeing B777-200ER (9M-MRO), 08 March 2014. Ministry of Transport Malaysia, MH370/01/2018. | official | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `mousavi2023` | Mousavi and Beroza (2023). Machine Learning in Earthquake Seismology. Annual Review of Earth and Planetary Sciences. https://doi.org/10.1146/annurev-earth-071822-100323. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `nasacmr2026` | NASA Earthdata (2026). Common Metadata Repository granule search: MOD02QKM, MYD02QKM v6.1, VNP02IMG, ASTER L1T, EO-1, Sentinel-1A (ASF). https://cmr.earthdata.nasa.gov/search. Accessed 2026-10-18. | official | UNVERIFIED, NO DOI | - (no use traced) | - |
| `nasacsda2026` | NASA Commercial SmallSat Data Acquisition Program (2026). CSDA Maxar L1B collections (WV01, WV02, GE01, QB02, IKONOS) in CMR. https://cmr.earthdata.nasa.gov/search. Accessed 2026-10-18. | official | UNVERIFIED, NO DOI | - (no use traced) | - |
| `naus1965` | Naus (1965). The Distribution of the Size of the Maximum Cluster of Points on a Line. Journal of the American Statistical Association. https://doi.org/10.1080/01621459.1965.10480810. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `neal2001` | Neal, R. M. (2001). Annealed importance sampling. Statistics and Computing, 11, 125–139. https://doi.org/10.1023/A:1008923215028. | peer-reviewed | METADATA VERIFIED | - (no use traced) | - |
| `neidell1971` | Neidell and Taner (1971). SEMBLANCE AND OTHER COHERENCY MEASURES FOR MULTICHANNEL DATA. GEOPHYSICS. https://doi.org/10.1190/1.1440186. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `nielsen2020` | Nielsen, Zampolli, Le Bras and others (2020). CTBTO’s Data and Analysis Pertaining to the Search for the Missing Argentine Submarine ARA San Juan. Pure and Applied Geophysics. https://doi.org/10.1007/s00024-020-02445-9. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `ntsb1975nw6231` | National Transportation Safety Board (1975). Aircraft Accident Report: Northwest Airlines, Inc., Boeing 727-251, N274US, near Thiells, New York, December 1, 1974. NTSB, NTSB-AAR-75-13. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR7513.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `ntsb1981twa841` | National Transportation Safety Board (1981). Aircraft Accident Report: Trans World Airlines, Inc., Boeing 727-31, N840TW, near Saginaw, Michigan, April 4, 1979. NTSB, NTSB-AAR-81-8. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR8108.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `ntsb1986ci006` | National Transportation Safety Board (1986). Aircraft Accident Report: China Airlines Boeing 747-SP, N4522V, 300 Nautical Miles Northwest of San Francisco, California, February 19, 1985. NTSB, NTSB/AAR-86/03. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR8603.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `ntsb1989psa1771` | National Transportation Safety Board (1989). Aviation Investigation Final Report: British Aerospace BAe-146-200, N350PS, Pacific Southwest Airlines, San Luis Obispo, California, December 7, 1987. NTSB, Accident number DCA88MA008. https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/15893/pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `ntsb1999usair427` | National Transportation Safety Board (1999). Aircraft Accident Report: Uncontrolled Descent and Collision with Terrain, USAir Flight 427, Boeing 737-300, N513AU, near Aliquippa, Pennsylvania, September 8, 1994. NTSB, NTSB/AAR-99/01. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR9901.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `ntsb2002alaska261` | National Transportation Safety Board (2002). Aircraft Accident Report: Loss of Control and Impact with Pacific Ocean, Alaska Airlines Flight 261, McDonnell Douglas MD-83, N963AS, about 2.7 Miles North of Anacapa Island, California, January 31, 2000. NTSB, NTSB/AAR-02/01. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR0201.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `ntsb2002egyptair990` | National Transportation Safety Board (2002). Aircraft Accident Brief: EgyptAir Flight 990, Boeing 767-366ER, SU-GAP, 60 Miles South of Nantucket, Massachusetts, October 31, 1999. NTSB, NTSB/AAB-02/01. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAB0201.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `ntsb2007pinnacle3701` | National Transportation Safety Board (2007). Aircraft Accident Report: Crash of Pinnacle Airlines Flight 3701, Bombardier CL-600-2B19, N8396A, Jefferson City, Missouri, October 14, 2004. NTSB, NTSB/AAR-07/01. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR0701.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `ntsb2010` | National Transportation Safety Board (2010). Loss of Thrust in Both Engines After Encountering a Flock of Birds and Subsequent Ditching on the Hudson River, US Airways Flight 1549. NTSB, NTSB/AAR-10/03. | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `ntsb2020atlas3591` | National Transportation Safety Board (2020). Rapid Descent and Crash into Water, Atlas Air Inc. Flight 3591, Boeing 767-375BCF, N1217A, Trinity Bay, Texas, February 23, 2019. NTSB, Aircraft Accident Report NTSB/AAR-20/02. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR2002.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `ntsc2000silkair185` | National Transportation Safety Committee, Department of Communications, Republic of Indonesia (2000). Aircraft Accident Report: SilkAir Flight MI 185, Boeing B737-300, 9V-TRF, Musi River, Palembang, Indonesia, 19 December 1997. Final Report. NTSC. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `ntsc2008adamair574` | National Transportation Safety Committee, Republic of Indonesia (2008). Aircraft Accident Investigation Report: PT. Adam SkyConnection Airlines (AdamAir) Flight DHI 574, Boeing 737-4Q8, PK-KKW, Makassar Strait, Sulawesi, Republic of Indonesia, 1 January 2007. NTSC, KNKT/07.01/08.01.36. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `ntsc2008dki574` | National Transportation Safety Committee (2008). Aircraft Accident Investigation Report, PK-KKW. NTSC Indonesia. | grey | UNVERIFIED, NO DOI | settling (no use traced) | candidate |
| `oceaninfinity2018conclusion` | Ocean Infinity (2018). Conclusion of current search for Malaysian Airlines flight MH370. https://oceaninfinity.com/news/conclusion-of-current-search-for-malaysian-airlines-flight-mh370/. Accessed 2026-10-12. | grey | UNVERIFIED, NO DOI | searched areas (no use traced) | candidate |
| `oceaninfinity2018gebco` | Ocean Infinity (2018). Ocean Infinity donates 120,000 square kilometres of data for missing Malaysian airliner to GEBCO Seabed 2030 project. https://oceaninfinity.com/news/ocean-infinity-donates-120000-square-kilometres-of-data-for-missing-malaysian-airliner-to-gebco-seabed-2030-project/. Accessed 2026-10-12. | official | UNVERIFIED, NO DOI | searched areas (no use traced) | - |
| `oceaninfinity2026conclusion` | Ocean Infinity (2026). Conclusion of the search for Malaysian Airlines flight MH370. https://oceaninfinity.com/news/conclusion-of-the-search-for-malaysian-airlines-flight-mh370/. Accessed 2026-10-12. | grey | UNVERIFIED, NO DOI | searched areas (no use traced) | candidate |
| `okal2001` | Okal (2001). T-phase Stations for the International Monitoring System of the Comprehensive Nuclear-Test Ban Treaty: A Global Perspective. Seismological Research Letters. https://doi.org/10.1785/gssrl.72.2.186. | peer-reviewed | METADATA VERIFIED | hydroacoustics (4 files) | - |
| `oke2013ofam3` | Oke, P. R. and others (2013). Evaluation of a near-global eddy-resolving ocean model. Geoscientific Model Development, 6, 591–615. https://doi.org/10.5194/gmd-6-591-2013. | peer-reviewed | METADATA VERIFIED | ocean drift / transport (1 file) | - |
| `oliveira2025` | Oliveira, Prior, Lin and others (2025). Underwater explosions recorded at IMS hydroacoustic stations from well-defined experiments. https://doi.org/10.5194/egusphere-egu24-7649. | grey | METADATA VERIFIED | hydroacoustics (no use traced) | - |
| `page1954` | Page (1954). CONTINUOUS INSPECTION SCHEMES. Biometrika. https://doi.org/10.1093/biomet/41.1-2.100. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `pasyanos2025` | Pasyanos, Pilger and Wang (2025). Advances in geophysical forensic event monitoring. Nature Reviews Earth &amp; Environment. https://doi.org/10.1038/s43017-025-00702-w. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `peng2009` | Peng and Zhao (2009). Migration of early aftershocks following the 2004 Parkfield earthquake. Nature Geoscience. https://doi.org/10.1038/ngeo697. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `people2014floating` | People's Daily / Xinhua (2014). Wo soujiu chuan tingdao yisi heixiazi xinhao [Our rescue ship hears suspected black-box signal]. http://cpc.people.com.cn/n/2014/0406/c87228-24835605.html. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `phipson2010` | Phipson and Smyth (2010). Permutation P-values Should Never Be Zero: Calculating Exact P-values When Permutations Are Randomly Drawn. Statistical Applications in Genetics and Molecular Biology. https://doi.org/10.2202/1544-6115.1585. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `pickands1975` | Pickands III (1975). Statistical Inference Using Extreme Order Statistics. The Annals of Statistics. https://doi.org/10.1214/aos/1176343003. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `pollschumann2021` | Poll, D. I. A. and Schumann, U. (2021). An estimation method for the fuel burn and other performance characteristics of civil transport aircraft in the cruise. Part 1: fundamental quantities and governing relations for a general atmosphere. The Aeronautical Journal, 125, 257–295. | peer-reviewed | UNVERIFIED, NO DOI | end of flight (1 file) | - |
| `Porter1992` | Porter, M. B. (1992). The KRAKEN Normal Mode Program. Naval Research Laboratory, NRL/MR/5120-92-6920. | official | UNVERIFIED, NO DOI | hydroacoustics (2 files) | - |
| `prior2011` | Prior, Meless, Bittner and others (2011). Long-Range Detection and Location of Shallow Underwater Explosions Using Deep-Sound-Channel Hydrophones. IEEE Journal of Oceanic Engineering. https://doi.org/10.1109/joe.2011.2154390. | peer-reviewed | METADATA VERIFIED | hydroacoustics (4 files) | - |
| `pti2014deccan` | Press Trust of India (2014). Missing jet: Chinese ship detects pulse signal. https://www.deccanherald.com/archives/missing-jet-chinese-ship-detects-2185601. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `puri2013access` | Puri, K., Dietachmayer, G., Steinle, P., Dix, M. and others (2013). Implementation of the initial ACCESS numerical weather prediction system. Australian Meteorological and Oceanographic Journal, 63, 265–284. https://doi.org/10.22499/2.6302.001. | peer-reviewed | METADATA VERIFIED | - (no use traced) | - |
| `pyram` | Donnelly, M. (2025). pyram 1.3.0: Python adaptation of the Range-dependent Acoustic Model (RAM). https://github.com/marcuskd/pyram. Accessed [DATE NOT RECORDED]. | grey | UNVERIFIED, NO DOI | hydroacoustics (1 file) | - |
| `rahimi2007random` | Rahimi, A. and Recht, B. (2007). Random features for large-scale kernel machines. Advances in Neural Information Processing Systems 20. | peer-reviewed | UNVERIFIED, NO DOI | ocean drift / transport (1 file) | - |
| `raumer2025` | Raumer, Bazin, Royer and others (2025). Hydroacoustic geophony automatic detection: an open benchmark dataset with an open model. https://doi.org/10.5194/egusphere-egu24-5256. | grey | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `reagan2024woa23s` | Reagan, J. R. and others (2024). World Ocean Atlas 2023, Volume 2: Salinity. https://doi.org/10.25923/70qt-9574. | official | METADATA VERIFIED | ocean drift / transport (4 files) | - |
| `RHUMRUM_YV` | RESIF (2011). RHUM-RUM experiment, 2011–2015 (FDSN network YV). | grey | UNVERIFIED, NO DOI | hydroacoustics (no use traced) | - |
| `robert2004mcsm` | Robert, C. P. and Casella, G. (2004). Monte Carlo Statistical Methods. Springer. https://doi.org/10.1007/978-1-4757-4145-2. | official | METADATA VERIFIED | end of flight (1 file) | candidate |
| `rohling1983` | Rohling (1983). Radar CFAR Thresholding in Clutter and Multiple Target Situations. IEEE Transactions on Aerospace and Electronic Systems. https://doi.org/10.1109/taes.1983.309350. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `romania2000tarom371` | Ministry of Transport, Romania, Administrative Investigation Commission (2000). [Final report on the accident to the Airbus A310-324 YR-LCC, TAROM flight ROT 371, Balotești, 31 March 1995]. Ministry of Transport, Romania. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `roquet2015polynomial` | Roquet, F., Madec, G., McDougall, T. J. and Barker, P. M. (2015). Accurate polynomial expressions for the density and specific volume of seawater using the TEOS-10 standard. Ocean Modelling, 90, 29–43. https://doi.org/10.1016/j.ocemod.2015.04.002. | peer-reviewed | METADATA VERIFIED | ocean drift / transport (1 file) | - |
| `rost2002` | Rost and Thomas (2002). ARRAY SEISMOLOGY: METHODS AND APPLICATIONS. Reviews of Geophysics. https://doi.org/10.1029/2000rg000100. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `royer2015` | Royer, Chateau, Dziak and others (2015). Seafloor seismicity, Antarctic ice-sounds, cetacean vocalizations and long-term ambient sound in the Indian Ocean basin. Geophysical Journal International. https://doi.org/10.1093/gji/ggv178. | peer-reviewed | METADATA VERIFIED | hydroacoustics (7 files) | - |
| `royer2016report` | Royer (2016). OHASISBIO hydroacoustic analysis for MH370, report LDO-201608 (held as project artifact royer-2016-LDO-201608.pdf). | grey | UNVERIFIED, NO DOI | hydroacoustics (52 files) | - |
| `russia1994aeroflot593` | Aircraft Accident Investigation Commission (Russian Government Commission) (n.d.). Report on the investigation into the crash of A310-308, registration F-OGQS, on 22 March 1994 near the city of Mezhdurechensk (English translation). Aircraft Accident Investigation Commission, Russia. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `saragiotis2002` | Saragiotis, Hadjileontiadis and Panas (2002). PAI-S/K: A robust automatic seismic P phase arrival identification scheme. IEEE Transactions on Geoscience and Remote Sensing. https://doi.org/10.1109/tgrs.2002.800438. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `schaff2010` | Schaff and Waldhauser (2010). One Magnitude Unit Reduction in Detection Threshold by Cross Correlation Applied to Parkfield (California) and China Seismicity. Bulletin of the Seismological Society of America. https://doi.org/10.1785/0120100042. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `schreiber1996` | Schreiber and Schmitz (1996). Improved Surrogate Data for Nonlinearity Tests. Physical Review Letters. https://doi.org/10.1103/physrevlett.77.635. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `schwardt2022` | Schwardt, Pilger, Gaebler and others (2022). Natural and Anthropogenic Sources of Seismic, Hydroacoustic, and Infrasonic Waves: Waveforms and Spectral Characteristics (and Their Applicability for Sensor Calibration). Surveys in Geophysics. https://doi.org/10.1007/s10712-022-09713-4. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `shelly2007` | Shelly, Beroza and Ide (2007). Non-volcanic tremor and low-frequency earthquake swarms. Nature. https://doi.org/10.1038/nature05666. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `shk2016westair294` | Statens haverikommission (Swedish Accident Investigation Authority) (2016). Final report RL 2016:11e: Accident in Oajevágge, Norrbotten County, Sweden on 8 January 2016 involving the aeroplane SE-DUX of the model CL-600-2B19, operated by West Atlantic Sweden AB. SHK, RL 2016:11e (file no. L-01/16). https://shk.se/download/18.2d6f089b18faca29dc81cffa/1700491384504/RL-2016_11e.pdf. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `sina2014haixun` | Sina Military (2014). Zhongguo haixun chuan lianxu 2 tian faxian yisi MH370 heixiazi xinhao [Chinese patrol ship detects suspected MH370 black-box signal on two consecutive days]. https://mil.news.sina.com.cn/2014-04-06/0838772468.html. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `sir2018` | Malaysian ICAO Annex 13 Safety Investigation Team for MH370 (2018). Safety Investigation Report: MH370 (9M-MRO). Ministry of Transport Malaysia, MH370/01/2018. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | candidate |
| `sir2018app16e` | The Boeing Company (2018). Performance Analysis – Malaysian Airlines 777 9M-MRO Missing Occurrence. Malaysian ICAO Annex 13 Safety Investigation Team for MH370. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | candidate |
| `spinoccia2017mh370` | Spinoccia, M. (2017). MH370 Phase 1 150m Bathymetry datasets (GA-4421, GA-4422 & GA-4430). Geoscience Australia. https://pid.geoscience.gov.au/dataset/ga/100315. Accessed [DATE NOT RECORDED]. | official | UNVERIFIED, NO DOI | ocean drift / transport (1 file) | - |
| `stead2014` | Stead (2014). Seismic and hydroacoustic analysis relevant to MH370. https://doi.org/10.2172/1136454. | grey | METADATA VERIFIED | hydroacoustics (15 files) | - |
| `stone2014` | Stone, L. D., Keller, C. M., Kratzke, T. M. and Strumpfer, J. P. (2014). Search for the Wreckage of Air France Flight AF 447. Statistical Science, 29, 69–80. https://doi.org/10.1214/13-STS420. | peer-reviewed | METADATA VERIFIED | settling (22 files) | - |
| `sutherland2020` | Sutherland, G., Soontiens, N., Davidson, F., Smith, G. C., Bernier, N., Blanken, H., Schillinger, D., Marcotte, G., Röhrs, J., Dagestad, K.-F., Christensen, K. H. and Breivik, Ø. (2020). Evaluating the leeway coefficient of ocean drifters using operational marine environmental prediction systems. Journal of Atmospheric and Oceanic Technology, 37, 1943–1954. https://doi.org/10.1175/JTECH-D-20-0013.1. | peer-reviewed | METADATA VERIFIED | ocean drift (5 files) | - |
| `sutherland2020leeway` | Sutherland, G. and others (2020). Evaluating the leeway coefficient of ocean drifters using operational marine environmental prediction systems. Journal of Atmospheric and Oceanic Technology, 37, 1943–1954. | peer-reviewed | UNVERIFIED, NO DOI | ocean drift / transport (5 files) | - |
| `talandier2006` | Talandier, Hyvernaud, Reymond and others (2006). Hydroacoustic signals generated by parked and drifting icebergs in the Southern Indian and Pacific Oceans. Geophysical Journal International. https://doi.org/10.1111/j.1365-246x.2006.02911.x. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `Taylor1921` | Taylor, G. I. (1921). Diffusion by continuous movements. Proceedings of the London Mathematical Society, s2-20, 196–212. https://doi.org/10.1112/plms/s2-20.1.196. | peer-reviewed | METADATA MISMATCH | Pleiades (5 files) | - |
| `tcds777` | Federal Aviation Administration (2025). Type Certificate Data Sheet T00001SE, Revision 48: Boeing 777-200, -200LR, -300, -300ER, 777F. U.S. Department of Transportation, Federal Aviation Administration, T00001SE Rev. 48. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `tcdstrent800` | European Union Aviation Safety Agency (2019). Type-Certificate Data Sheet No. EASA E.047 for RB211 Trent 800 series engines, Issue 04. European Union Aviation Safety Agency, EASA E.047 Issue 04. https://www.easa.europa.eu/en/document-library/type-certificates. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `TEOS10` | IOC, SCOR and IAPSO (2010). The International Thermodynamic Equation of Seawater – 2010: Calculation and Use of Thermodynamic Properties. Intergovernmental Oceanographic Commission, UNESCO, 56. | grey | UNVERIFIED, NO DOI | hydroacoustics (no use traced) | - |
| `theiler1992` | Theiler, Eubank, Longtin and others (1992). Testing for nonlinearity in time series: the method of surrogate data. Physica D: Nonlinear Phenomena. https://doi.org/10.1016/0167-2789(92)90102-s. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `thresher1963` | US Navy (1963). Court of Inquiry into the loss of USS Thresher. US Navy. | official | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `tolstoy1950` | Tolstoy and Ewing (1950). The T phase of shallow-focus earthquakes*. Bulletin of the Seismological Society of America. https://doi.org/10.1785/bssa0400010025. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `tolstoy2004` | Tolstoy, Diebold, Webb and others (2004). Broadband calibration of R/V Ewing seismic sources. Geophysical Research Letters. https://doi.org/10.1029/2004gl020234. | peer-reviewed | METADATA VERIFIED | hydroacoustics (7 files) | yes |
| `tonissen1996` | Tonissen and Evans (1996). Peformance of dynamic programming techniques for Track-Before-Detect. IEEE Transactions on Aerospace and Electronic Systems. https://doi.org/10.1109/7.543865. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `tsb2003` | Transportation Safety Board of Canada (2003). Aviation Investigation Report A98H0003: In-Flight Fire Leading to Collision with Water, Swissair Flight 111. TSB, A98H0003. | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `ukmod2014echo` | UK Ministry of Defence (2014). HMS Echo continues hunt for missing Malaysian airliner. https://www.globalsecurity.org/military/library/news/2014/04/mil-140414-ukmod02.htm. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `ukmod2014tireless` | UK Ministry of Defence (2014). HMS Tireless stands down in search for missing aircraft. https://www.gov.uk/government/news/hms-tireless-stands-down-in-search-for-missing-aircraft. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `ulich2018north25` | Ulich, B. (2018). Search for MH370 north of 25S unlikely. | grey | UNVERIFIED, NO DOI | - (5 files) | candidate |
| `urkowitz1967` | Urkowitz (1967). Energy detection of unknown deterministic signals. Proceedings of the IEEE. https://doi.org/10.1109/proc.1967.5573. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `usgsstac2026` | U.S. Geological Survey (2026). Landsat Collection 2 Level-1 STAC catalogue (landsat-c2l1). https://landsatlook.usgs.gov/stac-server. Accessed 2026-10-18. | official | UNVERIFIED, NO DOI | - (no use traced) | - |
| `usman2016` | Usman, Nitz, Harry and others (2016). The PyCBC search for gravitational waves from compact binary coalescence. Classical and Quantum Gravity. https://doi.org/10.1088/0264-9381/33/21/215004. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `vergoz2021` | Vergoz, Cansi, Cano and others (2021). Analysis of Hydroacoustic Signals Associated to the Loss of the Argentinian ARA San Juan Submarine. Pure and Applied Geophysics. https://doi.org/10.1007/s00024-020-02625-7. | peer-reviewed | METADATA VERIFIED | hydroacoustics (13 files) | - |
| `Vincenty1975` | Vincenty, T. (1975). Direct and inverse solutions of geodesics on the ellipsoid with application of nested equations. Survey Review, 23, 88–93. https://doi.org/10.1179/sre.1975.23.176.88. | peer-reviewed | METADATA VERIFIED | hydroacoustics (3 files) | - |
| `wald1940` | Wald and Wolfowitz (1940). On a Test Whether Two Samples are from the Same Population. The Annals of Mathematical Statistics. https://doi.org/10.1214/aoms/1177731909. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `wald1945` | Wald (1945). Sequential Tests of Statistical Hypotheses. The Annals of Mathematical Statistics. https://doi.org/10.1214/aoms/1177731118. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `wessel1996gshhg` | Wessel, P. and Smith, Walter H. F. (1996). A global, self-consistent, hierarchical, high-resolution shoreline database. Journal of Geophysical Research: Solid Earth, 101, 8741–8743. https://doi.org/10.1029/96JB00104. | peer-reviewed | METADATA VERIFIED | ocean drift / transport (3 files) | - |
| `wilson2019` | Wilson (2019). The harmonic mean p -value for combining dependent tests. Proceedings of the National Academy of Sciences. https://doi.org/10.1073/pnas.1814092116. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `withers1998` | Withers, Aster, Young and others (1998). A comparison of select trigger algorithms for automated global seismic phase and event detection. Bulletin of the Seismological Society of America. https://doi.org/10.1785/bssa0880010095. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `WOA23` | Reagan, J. R., Boyer, T. P., García, H. E., Locarnini, R. A., Baranova, O. K., Bouchard, C., Cross, S. L., Mishonov, A. V., Paver, C. R., Seidov, D., Wang, Z. and Dukhovskoy, D. (2023). World Ocean Atlas 2023. NOAA National Centers for Environmental Information. https://doi.org/10.25921/va26-hv25. Accessed [DATE NOT RECORDED]. | official | METADATA VERIFIED | hydroacoustics, ocean drift / transport (3 files) | - |
| `ws2009` | Wąs, Bizouard, Brisson and others (2009). On the background estimation by time slides in a network of gravitational wave detectors. Classical and Quantum Gravity. https://doi.org/10.1088/0264-9381/27/1/015005. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `xinhua2014pulse` | Xinhua (2014). Chinese ship searching for MH370 detects pulse signal (as carried by CGTN America). https://america.cgtn.com/2014/04/05/chinese-ship-searching-for-missing-jet-detects-pulse-signal/. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `xinmin2014haixun` | Xinmin Evening News (2014). Haixun 01 2 tian 2 ci tingdao heixiazi maichong xinhao [Haixun 01 hears black-box pulse twice in two days]. https://www.chinanews.com.cn/gn/2014/04-05/6034302.shtml. Accessed 2026-10-18. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `yeh2016` | Yeh, Zhu, Ulanova and others (2016). Matrix Profile I: All Pairs Similarity Joins for Time Series: A Unifying View That Includes Motifs, Discords and Shapelets. 2016 IEEE 16th International Conference on Data Mining (ICDM). https://doi.org/10.1109/icdm.2016.0179. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |
| `yoon2015` | Yoon, O’Reilly, Bergen and others (2015). Earthquake detection through computationally efficient similarity search. Science Advances. https://doi.org/10.1126/sciadv.1501057. | peer-reviewed | METADATA VERIFIED | hydroacoustics (1 file) | - |

## 6a. Davey et al. (2016) has chapter-level DOIs — and they resolve the page conflict

Every chapter of the book is separately registered with its own DOI and its own printed page range. Retrieved from CrossRef and verified 12 October 2026:

| Ch. | Title | Printed pages | DOI |
|---|---|---|---|
| 1 | Introduction | 1–5 | `10.1007/978-981-10-0379-0_1` |
| 2 | Factual Description of Accident and Available Information | 7–9 | `10.1007/978-981-10-0379-0_2` |
| 3 | The Bayesian Approach | 11–17 | `10.1007/978-981-10-0379-0_3` |
| 4 | Aircraft Prior Based on Primary Radar Data | 19–22 | `10.1007/978-981-10-0379-0_4` |
| 5 | Measurement Model, Satellite Communications | 23–34 | `10.1007/978-981-10-0379-0_5` |
| 6 | Aircraft Cruise Dynamics | 35–46 | `10.1007/978-981-10-0379-0_6` |
| 7 | Aircraft Manoeuvre Dynamics | 47–54 | `10.1007/978-981-10-0379-0_7` |
| 8 | Particle Filter Implementation | 55–61 | `10.1007/978-981-10-0379-0_8` |
| 9 | Validation Experiments | 63–86 | `10.1007/978-981-10-0379-0_9` |
| 10 | Application to the MH370 Accident | 87–100 | `10.1007/978-981-10-0379-0_10` |
| 11 | Ongoing Refinement | 101–109 | `10.1007/978-981-10-0379-0_11` |

**This is the way out of the conflict in §6.** A chapter citation is a *reference*, not an in-text page, so it is fully Harvard-compliant, and it is far more precise than citing a 109-page book. The particle filter implementation is chapter 8, pp. 55–61; the satellite communications measurement model is chapter 5, pp. 23–34; the manoeuvre dynamics our sampler modifies are chapter 7, pp. 47–54. Each can be cited as its own reference-list entry with a resolvable DOI and its printed pages, which is what the project's traceability rule actually wants.

Recommended practice for the paper: cite `(Davey et al., 2016)` for the work as a whole and the chapter entry where a specific model element is meant. The printed page ranges above also give an independent check on the project's printed-page = PDF-page − 13 rule for this book.

## 6b. Legitimate copies held, by provenance

| Source | Copy held | Provenance | Citable pagination |
|---|---|---|---|
| Davey et al. (2016) | publisher PDF | Pete's Google Drive; CC BY-NC 4.0 | printed pages, from the running headers |
| Holland (2018) | author's accepted version | **green open access, arXiv:1702.02432v3, 15 Jan 2018**, retrieved via Unpaywall 12 Oct 2026 | **NOT the printed pagination.** The copy is numbered 1–10; the printed article is *IEEE Aerospace and Electronic Systems Magazine* 33(2), 24–33. Locate quotations by section, not page, unless the published version is obtained |
| Large (2019) | `~/Downloads/Dissertation.pdf`, 285 pp. | Pete's own work, published open access by him; he confirmed on 12 Oct 2026 that there are no restrictions | its own printed folios; note that the text layer has a broken character map, so quotations must be read from the rendered page |

## 7. Open items

1. Fold in the prose ledgers `results/*-references.md`, which carry printed pages, per-claim provenance and the module's own verification notes. The `.bib` files are the skeleton; the prose files are where the work is.
2. Sweep Pete's Google Drive and `deskstar` for held copies and for sources cited nowhere in the repository.
3. Close the gaps in §5, starting with Ocean Infinity 2018 and 2025, and Large (2019).
4. Record an access date for every URL-only entry (§4.3).
5. Confirm the heuristic grades on the 21 `misc` entries.
6. Decide the dataset, software and thesis reference formats with the Editorial Office (`JON-RULES.md` §6), then regenerate.
7. Add the engine itself as a citable software entry once a release or commit is nominated for the paper.

---

*Regenerate with `python build_citation_library.py && python write_citation_outputs.py`. Last run 12 October 2026.*
