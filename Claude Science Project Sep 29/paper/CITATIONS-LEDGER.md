# Master citation ledger — MH370 paper

Owner: paper drafting and citations module (`PAPER_CITATIONS_MODULE`).
Generated 12 October 2026 by `write_citation_outputs.py` from `build_citation_library.py`.
Companion file: `paper/references.bib` (generated from the same index — never
hand-edited). Reference style follows `paper/JON-RULES.md` §6 (Harvard).

## 1. What was gathered

| Source | Result |
|---|---|
| Module bibliographies under `results/*.bib` | 7 files, 112 raw entries |
| After deduplication by DOI, else by first author, year and title | **98 entries** |
| Repository files scanned for in-text use | 730 (`results/**/*.md`, `ARCHITECTURE.md`, `README.md`, `RUNBOOK.md`, `threads/master-prompts/`, `coordination/`, and the engine's Rust, TOML and Python) |
| Entries whose use in the project could be traced to a file | 65 of 98 |
| Local candidate copies indexed (`~/Downloads`, `mh370-exchange`) | 619 files |

Still to be folded in, and therefore **not** represented in the counts below:
Pete's Google Drive; `deskstar`; the prose ledgers `results/*-references.md` (which carry the printed pages and the per-claim provenance); `results/davey-2016-reference.md`; `results/hydroacoustics-bibliography.csv`; `results/seabed-search-references.md`.

## 2. Counts by grade

Grades follow the module brief §1: **official** (publisher, agency, standards body), **peer-reviewed**, **grey** (reports, theses, preprints), **unofficial** (blogs, forums, independent analysts).

| Grade | Entries |
|---|---|
| official | 30 |
| peer-reviewed | 36 |
| grey | 32 |
| unofficial | 0 |
| **total** | **98** |

Every grade below is assigned by rule from the entry type and the publisher, institution or URL field, and each entry records the basis. **The grades are heuristic and need Pete's or architecture's confirmation on the `misc` entries in particular**, where the entry type carries no information.

No entry graded **unofficial** is present in the module bibliographies. That is worth noting rather than celebrating: independent analysts' work (for example 370location.org) is cited in project prose and in the hydroacoustics discussion, so either those citations are missing from the bibliographies or they are being used without being cited. See §5.

## 3. Verification status

Of **98** entries, **41** carry a DOI and **57** do not. Every DOI was looked up at CrossRef and, on a 404 there, at DataCite — 31 are registered with CrossRef and 10 with DataCite (datasets, data products and arXiv deposits are DataCite's, and 404 at CrossRef without being broken).

| Status | Entries | Meaning |
|---|---|---|
| METADATA VERIFIED | 37 | the DOI resolves and the registered title and year agree with ours |
| METADATA MISMATCH | 4 | the DOI resolves but a field disagrees — listed in §4 |
| UNVERIFIED, no DOI | 57 | the entry carries no DOI, so there was nothing to check automatically |
| UNVERIFIED, DOI not found | 0 | a DOI is recorded but neither registry knows it — these need attention, listed in §4.5 |
| **total** | **98** | |

Arithmetic check, so the table can be audited: 41 with a DOI = 37 verified + 4 mismatched + 0 not found; 37 + 4 + 0 + 57 without a DOI = 98.

**None is yet VERIFIED against the source document** in the brief's strongest sense — that requires opening the work and checking the claim it is cited for, which happens claim by claim as the draft is written, not in bulk.

Legitimate held copies located on this machine: 9 candidate matches, of which 3 are confident. Title-token matching against downloaded filenames is weak for agency reports whose filenames bear no relation to their titles, so this count is a floor, not a finding. The Drive sweep will raise it.

## 4. Entries that need a decision

### 4.1 Four year disagreements that are not errors

CrossRef's `issued` date is the earliest registered date, which for a journal article is the online-first date. In four cases our year is the **printed issue** year and is the right one for a Harvard reference list:

| Key | Our year | CrossRef print | CrossRef online | Venue |
|---|---|---|---|---|
| `durgadoo2021` | 2021 | 2021 | 2019 | Journal of Operational Oceanography |
| `ashton2015` | 2015 | 2015 | 2014 | Journal of Navigation |
| `Metz2023` | 2023 | 2023 | 2022 | Pure and Applied Geophysics |
| `Karney2013` | 2013 | 2013 | 2012 | Journal of Geodesy |

**No change needed.** This includes `ashton2015` — Ashton et al. in *The Journal of Navigation* — which is one of the paper's two anchor references. It is cited elsewhere in the literature as both 2014 and 2015; the printed issue is 2015 and that is what we will use. Worth stating once in the ledger so that nobody 'corrects' it later.

### 4.2 4 genuine mismatches against the registry

**Year (2).** The registered title agrees, the year does not:

- **`gdp6h`** — Lumpkin, Rick and Centurioni, Luca, *Global Drifter Program quality-controlled 6-hour interpolated data fro*. Ours: 2019; DataCite records 2010 in NOAA National Centers for Environmental Information.
- **`Taylor1921`** — Taylor, G. I., *Diffusion by continuous movements*. Ours: 1921; CrossRef records 1922 in Proceedings of the London Mathematical Society s2-20, 196-212.

  **Recommendation:** take the year from the registry record of the version we actually cite, and keep this note so the choice stays visible. Pete's call on each. Note that a dataset's registered publication year is the year the *series* was first published, which is not the year of the product version used in a run — so for data products the run's own configuration is the better authority and the reference should name the version, not just the year.

**Title (2).** The DOI resolves, but to a differently titled record — in each case a data product cited under a working name rather than its registered title:

- **`glorys12`** — ours: *Global Ocean Physics Reanalysis (GLOBAL_MULTIYEAR_PHY_001_030)*; registered as *Global Ocean Physics Reanalysis* (Mercator Ocean International, 2018).
- **`cmems_glo_wav_001_032`** — ours: *Global Ocean Waves Reanalysis (GLOBAL_MULTIYEAR_WAV_001_032), *; registered as *Global Ocean Waves Reanalysis WAVERYS* (Mercator Ocean International, 2019).

  **Recommendation:** cite the registered title, and give the working name only if the paper needs it for continuity with the figures. A referee checking the DOI must land on the thing the reference names.

### 4.3 The 57 entries with no DOI

These are mostly agency reports, where a DOI often does not exist. They are not suspect — but under JON's website/dataset format each needs a **URL and an access date**, and the access date is recorded for almost none of them. Entries missing both a DOI and a URL cannot be formatted in JON style at all:

**45 entries have neither a DOI nor a URL:**

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
- `atsb2017` (techreport, official) — The Operational Search for MH370
- `b777acaps` (manual, official) — 777-200/300 Airplane Characteristics for Airport Planning
- `bea2009frwg` (techreport, grey) — Flight Data Recovery Working Group Report
- `boeingeofsims2016` (misc, official) — End-of-flight engineering-simulator exports, ten cases
- `chu2006` (article, peer-reviewed) — Prediction of falling cylinder through air-water-sediment columns
- `dnv2010` (techreport, grey) — Risk Assessment of Pipeline Protection
- `esdu-windmill` (misc, grey) — ESDU 81009, 84004, 84005
- `fprg2016satcomlogs` (techreport, grey) — Internal study regarding SATCOM ground-station logs
- `griffa1996stochastic` (incollection, official) — Applications of stochastic particle models to oceanographic problems
- `griffin2017partii` (techreport, official) — The search for MH370 and ocean surface drift – Part II
- `griffin2017partiii` (techreport, official) — The search for MH370 and ocean surface drift – Part III
- `iannello2018` (misc, grey) — End-of-flight simulations (web article; VERIFY title and URL from the archive snapshot)
- `ioc2010teos10` (manual, grey) — The international thermodynamic equation of seawater – 2010: Calculation and use of thermodynam
- `iso2533` (standard, grey) — Standard Atmosphere
- `lock1964` (article, peer-reviewed) — The prediction of the drag of aerofoils and wings at high subsonic speeds
- `margo1990` (techreport, grey) — Report of the Board of Inquiry into the Helderberg Air Disaster
- `mca2006fsh604` (techreport, grey) — Final Report of the Accident Investigation, Flash Airlines Flight 604, January 3, 2004, Boeing 
- `mearns1994` (techreport, grey) — MV Derbyshire survey report
- `mot2017` (techreport, official) — Summary of Possible MH370 Debris Recovered (updated 30 April 2017)
- `mot2018mh370` (techreport, official) — Safety Investigation Report, Malaysia Airlines Boeing B777-200ER (9M-MRO), 08 March 2014
- `ntsb2010` (techreport, grey) — Loss of Thrust in Both Engines After Encountering a Flock of Birds and Subsequent Ditching on t
- `ntsc2008dki574` (techreport, grey) — Aircraft Accident Investigation Report, PK-KKW
- `pollschumann2021` (article, peer-reviewed) — An estimation method for the fuel burn and other performance characteristics of civil transport
- `rahimi2007random` (inproceedings, peer-reviewed) — Random features for large-scale kernel machines
- `sir2018` (techreport, official) — Safety Investigation Report: MH370 (9M-MRO)
- `sir2018app16e` (techreport, official) — Performance Analysis – Malaysian Airlines 777 9M-MRO Missing Occurrence
- `sutherland2020leeway` (article, peer-reviewed) — Evaluating the leeway coefficient of ocean drifters using operational marine environmental pred
- `tcds777` (misc, grey) — Boeing 777 Type Certificate Data Sheet
- `tcdstrent800` (misc, grey) — Rolls-Royce Trent 800 Series Type Certificate Data Sheet
- `thresher1963` (techreport, official) — Court of Inquiry into the loss of USS Thresher
- `tsb2003` (techreport, grey) — Aviation Investigation Report A98H0003: In-Flight Fire Leading to Collision with Water, Swissai

Each needs a locator before submission. For agency reports the report number plus the issuing body is usually enough for a Harvard entry, and most of these have one; the gap is a retrievable URL for the reader.

### 4.4 Entries that cannot yet be formatted completely

JON requires full details "even if the list of authors is extensive" (`JON-RULES.md` §6), so an author list abbreviated in the module bibliography cannot go into the reference list as it stands.

**11 entries have a truncated author list** (`and others` / `et al.` in the stored author field):

- `WOA23` — Reagan, J. R. and Boyer, T. P. and García, H. E. and Locarnini, R. A. and Barano — World Ocean Atlas 2023
- `chamberlain2021bran2020` — Chamberlain, Matthew A. and others — Next generation of Bluelink ocean reanalysis with multiscale data assi
- `era5` — Hersbach, Hans and others — The ERA5 global reanalysis
- `lawchune2021waverys` — Law-Chune, Stéphane and others — WAVERYS: a CMEMS global wave reanalysis during the altimetry period
- `lellouche2021glorys12` — Lellouche, Jean-Michel and others — The Copernicus Global 1/12° Oceanic and Sea Ice GLORYS12 Reanalysis
- `locarnini2024woa23t` — Locarnini, Ricardo A. and others — World Ocean Atlas 2023, Volume 1: Temperature
- `metron2011` — Stone, Lawrence D. and others — Search Analysis for the Location of the AF447 Underwater Wreckage
- `oke2013ofam3` — Oke, Peter R. and others — Evaluation of a near-global eddy-resolving ocean model
- `reagan2024woa23s` — Reagan, James R. and others — World Ocean Atlas 2023, Volume 2: Salinity
- `sutherland2020` — Sutherland, Graig and Soontiens, Nancy and Dufois, François and others — Evaluating the leeway coefficient of ocean drifters using operational 
- `sutherland2020leeway` — Sutherland, Graig and others — Evaluating the leeway coefficient of ocean drifters using operational 

**9 entries have no year**, and print as `(n.d.)`:

- `FDSNIM` — IMS hydroacoustic station metadata, FDSN network IM
- `IMOSANMNPA` — Australian National Mooring Network passive acoustic observatories (Curtin University CMST
- `b777acaps` — 777-200/300 Airplane Characteristics for Airport Planning
- `cmems_glo_wav_001_032` — Global Ocean Waves Reanalysis (GLOBAL_MULTIYEAR_WAV_001_032), dataset cmems_mod_glo_wav_my
- `esdu-windmill` — ESDU 81009, 84004, 84005
- `fprg2016satcomlogs` — Internal study regarding SATCOM ground-station logs
- `glorys12` — Global Ocean Physics Reanalysis (GLOBAL_MULTIYEAR_PHY_001_030)
- `tcds777` — Boeing 777 Type Certificate Data Sheet
- `tcdstrent800` — Rolls-Royce Trent 800 Series Type Certificate Data Sheet

For the Boeing airport-planning document the year is on the document's own revision page; it needs reading off the copy we hold rather than guessing.

## 5. Candidate citations used in prose but absent from the library

Author–date patterns appearing three or more times in project prose that match no entry, no entry key and no institution field in the library. Organisation names and product codes are mixed in with real missing sources; the point of the list is that each one is either a citation the library is missing or a phrase that should not look like a citation.

| Appears as | Occurrences | My reading |
|---|---|---|
| OI 2018 | 131 | Ocean Infinity's 2018 search — a real citable source (its operations report / ATSB record), and the single most-used uncited string in the project |
| Infinity 2018 | 57 | same as above, matched on the second word |
| OI 2025 | 37 | Ocean Infinity's 2025 search resumption — citable, and current |
| Vergoz 2021 | 19 | hydroacoustic source-localisation literature — a real missing entry |
| Nielsen 2021 | 13 | hydroacoustics — a real missing entry |
| HL 2019 | 10 | a product or run code, not a citation |
| Infinity 2025 | 8 | same as above |
| Nesterov 2018 | 7 | drift / windage literature — real missing entry |
| GA 2017 | 6 | Geoscience Australia 2017 — bathymetry survey data, citable |
| Chapman 1988 | 6 | underwater acoustics — real missing entry |
| JASDF 2019 | 6 | check: an organisation abbreviation in prose |
| RA 2021 | 5 | a reanalysis product code, not a citation |
| Breivik 2008 | 5 | leeway / windage literature — real missing entry |
| Generator 2026 | 5 | our own generated output, not a citation |
| SUS 2003 | 4 | the SUS charge reference data — needs a proper source entry |
| Maximenko 2018 | 4 | surface-drift climatology — real missing entry |
| Miron 2019 | 4 | transition-matrix drift modelling — real missing entry |
| Heaney 1991 | 4 | long-range acoustic propagation — real missing entry |
| LaCasce 2008 | 3 | statistics of Lagrangian dispersion — real missing entry |
| Breivik 2011 | 3 | leeway / windage literature — real missing entry |
| Drévillon 2013 | 3 | Mercator/PSY ocean analysis system — real missing entry |
| Jansen 2016 | 3 | check which Jansen; likely drift or acoustics |
| Matsumoto 2016 | 3 | hydroacoustics — real missing entry |
| ETOPO 2022 | 3 | NOAA ETOPO 2022 bathymetry — a data product needing a dataset entry |

**Finding.** On this evidence the library is roughly 15 to 20 entries short of what the project's own prose already relies on, and the largest single gap is the Ocean Infinity searches, referred to several hundred times and cited nowhere. The searched-areas likelihood rests on them. Closing this is the next citation task.

## 6. The library

Printed pages are deliberately **not** a column here. JON's Harvard style admits an in-text page only for a direct quotation (`JON-RULES.md` §6), and pages in this project are a property of a *claim*, not of a reference. They live with the claim in the module prose ledgers and will be carried into the reference draft. A reference-level page column would invite exactly the detachment of claim from page that it appears to prevent.

| Key | Reference (JON Harvard style) | Grade | Verification | Used by | Copy held |
|---|---|---|---|---|---|
| `af447seabed2011` | Recovery of AF447 victims from the seabed, 2011 (secondary: Encyclopaedia Britannica; Al Jazeera, 16 June 2011) (2011). | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `andersen2005` | Andersen, A., Pesavento, U. and Wang, Z. J. (2005). Unsteady aerodynamics of fluttering and tumbling plates. Journal of Fluid Mechanics, 541, 65–90. | peer-reviewed | UNVERIFIED, NO DOI | settling (3 files) | - |
| `andersen2005b` | Andersen, A., Pesavento, U. and Wang, Z. J. (2005). Analysis of transitions between fluttering, tumbling and steady descent of falling cards. Journal of Fluid Mechanics, 541, 91–104. | peer-reviewed | UNVERIFIED, NO DOI | settling (3 files) | - |
| `anderson2018` | Anderson (2018). Report on two shipwrecks found during the MH370 search. Western Australian Museum, for the ATSB. | official | UNVERIFIED, NO DOI | settling (1 file) | - |
| `Arons1954` | Arons, A. B. (1954). Underwater explosion shock wave parameters at large distances from the charge. J. Acoust. Soc. Am., 26, 343–346. https://doi.org/10.1121/1.1907339. | peer-reviewed | METADATA VERIFIED | hydroacoustics (4 files) | - |
| `ashton2015` | Ashton, C., Shuster Bruce, A., Colledge, G. and Dickinson, M. (2015). The Search for MH370. The Journal of Navigation, 68, 1–22. https://doi.org/10.1017/S037346331400068X. | peer-reviewed | METADATA VERIFIED | end of flight (24 files) | - |
| `atsb2014fpu` | Australian Transport Safety Bureau (2014). MH370 – Flight Path Analysis Update. ATSB. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | candidate |
| `atsb2016sdu` | Australian Transport Safety Bureau (2016). MH370 – Search and debris examination update. ATSB. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `atsb2017` | Australian Transport Safety Bureau (2017). The Operational Search for MH370. ATSB, AE-2014-054. | official | UNVERIFIED, NO DOI | settling (no use traced) | candidate |
| `b777acaps` | The Boeing Company (n.d.). 777-200/300 Airplane Characteristics for Airport Planning. The Boeing Company. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `bea2009frwg` | Bureau d'Enquêtes et d'Analyses (2009). Flight Data Recovery Working Group Report. BEA. | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `bea2012af447` | Bureau d'Enquêtes et d'Analyses (2012). Final Report on the accident on 1st June 2009 to the Airbus A330-203 registered F-GZCP operated by Air France, flight AF 447 Rio de Janeiro – Paris. BEA. https://bea.aero. | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `Blackman2004JASA` | Blackman, D. K., de Groot-Hedlin, C., Harben, P., Sauter, A. and Orcutt, J. A. (2004). Testing low/very low frequency acoustic sources for basin-wide propagation in the Indian Ocean. J. Acoust. Soc. Am., 116, 2057–2066. https://doi.org/10.1121/1.1786711. | peer-reviewed | METADATA VERIFIED | hydroacoustics (14 files) | - |
| `Blackman2004UCRL` | Blackman, D. K., de Groot-Hedlin, C., Orcutt, J. A. and Harben, P. E. (2004). Methods for Calibrating Basin-Wide Hydroacoustic Propagation in the Indian Ocean. Lawrence Livermore National Laboratory, UCRL-TR-207323. https://doi.org/10.2172/15011808. | official | METADATA VERIFIED | hydroacoustics (14 files) | - |
| `boeingeofsims2016` | The Boeing Company (2016). End-of-flight engineering-simulator exports, ten cases. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `Brown2026` | Brown, P., McFadden, L., McCormack, D., Adams, M. and Vida, D. (2026). A search for hydroacoustic signals from bolides. Icarus. https://doi.org/10.48550/arXiv.2604.12723. | grey | METADATA VERIFIED | hydroacoustics (13 files) | - |
| `carver2023arcoera5` | Carver, R. W. and Merose, A. (2023). ARCO-ERA5: An Analysis-Ready Cloud-Optimized Reanalysis Dataset. 22nd Conference on Artificial Intelligence for Environmental Science, AMS Annual Meeting. https://github.com/google-research/arco-era5. | peer-reviewed | UNVERIFIED, NO DOI | ocean drift / transport (4 files) | - |
| `chamberlain2021bran2020` | Chamberlain, M. A. and others (2021). Next generation of Bluelink ocean reanalysis with multiscale data assimilation: BRAN2020. Earth System Science Data, 13, 5663–5688. https://doi.org/10.5194/essd-13-5663-2021. | peer-reviewed | METADATA VERIFIED | ocean drift / transport (2 files) | - |
| `chu2006` | Chu, P. C. and Fan, C. (2006). Prediction of falling cylinder through air-water-sediment columns. Journal of Applied Mechanics, 73, 300–314. | peer-reviewed | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `cmems_glo_wav_001_032` | E.U. Copernicus Marine Service Information (n.d.). Global Ocean Waves Reanalysis (GLOBAL_MULTIYEAR_WAV_001_032), dataset cmems_mod_glo_wav_my_0.2deg_PT3H-i, version 202411. https://doi.org/10.48670/moi-00022. Accessed [DATE NOT RECORDED]. | grey | METADATA MISMATCH | ocean drift / transport (1 file) | - |
| `cmems_mob_015_003` | E.U. Copernicus Marine Service Information (2024). Global Total (COPERNICUS-GLOBCURRENT), Ekman and Geostrophic currents at the Surface and 15m, MULTIOBS_GLO_PHY_MYNRT_015_003, version 202411. https://data.marine.copernicus.eu/product/MULTIOBS_GLO_PHY_MYNRT_015_003/description. Accessed [DATE NOT RECORDED]. | official | UNVERIFIED, NO DOI | ocean drift / transport (no use traced) | - |
| `CMST2014` | Duncan, A. J., Gavrilov, A. N. and McCauley, R. D. (2014). Analysis of low frequency underwater acoustic signals possibly related to the loss of Malaysian Airlines Flight MH370. Centre for Marine Science and Technology, Curtin University, CMST 1308, Report 2014-30. | official | UNVERIFIED, NO DOI | hydroacoustics (6 files) | - |
| `Collins1993` | Collins, M. D. (1993). A split-step Padé solution for the parabolic equation method. J. Acoust. Soc. Am., 93, 1736–1742. https://doi.org/10.1121/1.406739. | peer-reviewed | METADATA VERIFIED | hydroacoustics (4 files) | - |
| `copernicusmarine_toolbox` | Copernicus Marine Service (2026). Copernicus Marine Toolbox (copernicusmarine) 2.5.0. https://toolbox-docs.marine.copernicus.eu. Accessed [DATE NOT RECORDED]. | official | UNVERIFIED, NO DOI | ocean drift / transport (no use traced) | - |
| `davey2016` | Davey, S., Gordon, N., Holland, I., Rutten, M. and Williams, J. (2016). Bayesian Methods in the Search for MH370. Springer. https://doi.org/10.1007/978-981-10-0379-0. | official | METADATA VERIFIED | end of flight, hydroacoustics, ocean drift (121 files) | yes |
| `dnv2010` | Det Norske Veritas (2010). Risk Assessment of Pipeline Protection. DNV, DNV-RP-F107. | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `DuncanDallOsto2023` | Duncan, A. J. and Dall'Osto, D. R. (2023). Long-range underwater acoustic detection of aircraft surface impacts–-the influence of acoustic propagation conditions and impact parameters. J. Acoust. Soc. Am., 154, A49. https://doi.org/10.1121/10.0022761. | peer-reviewed | METADATA VERIFIED | hydroacoustics (5 files) | - |
| `DuncanDallOsto2023lay` | Duncan, A. J. and Dall'Osto, D. R. (2023). The loss of an F35 fighter aircraft and the search for Malaysian Airlines flight MH370. https://acoustics.org/the-loss-of-an-f35-fighter-aircraft-and-the-search-for-malaysian-airlines-flight-mh370/. Accessed [DATE NOT RECORDED]. | grey | UNVERIFIED, NO DOI | hydroacoustics (5 files) | candidate |
| `durgadoo2021` | Durgadoo, J. V., Biastoch, A., New, A. L., Rühs, S., Nurser, Aylmer J. G., Drillet, Y. and Bidlot, J.-R. (2021). Strategies for simulating the drift of marine debris. Journal of Operational Oceanography, 14, 1–12. https://doi.org/10.1080/1755876X.2019.1602102. | peer-reviewed | METADATA VERIFIED | ocean drift (6 files) | - |
| `era5` | Hersbach, H. and others (2020). The ERA5 global reanalysis. Quarterly Journal of the Royal Meteorological Society, 146, 1999–2049. https://doi.org/10.1002/qj.3803. | peer-reviewed | METADATA VERIFIED | Pleiades, ocean drift, ocean drift / transport (4 files) | - |
| `esdu-windmill` | ESDU (n.d.). ESDU 81009, 84004, 84005. ESDU. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `esr2021oscar` | ESR and Dohan, K. (2021). Ocean Surface Current Analyses Real-time (OSCAR) Surface Currents - Final 0.25 Degree (Version 2.0). PO.DAAC. https://doi.org/10.5067/OSCAR-25F20. Accessed [DATE NOT RECORDED]. | grey | METADATA VERIFIED | ocean drift / transport (5 files) | - |
| `FDSNIM` | IMS hydroacoustic station metadata, FDSN network IM (n.d.). https://service.earthscope.org/fdsnws/station/1/query. Accessed [DATE NOT RECORDED]. | grey | UNVERIFIED, NO DOI | hydroacoustics (no use traced) | - |
| `field1997` | Field, S. B., Klaus, M., Moore, M. G. and Nori, F. (1997). Chaotic dynamics of falling disks. Nature, 388, 252–254. https://doi.org/10.1038/40817. | peer-reviewed | METADATA VERIFIED | settling (3 files) | - |
| `fprg2016satcomlogs` | MH370 Flight Path Reconstruction Group, SATCOM Subgroup (n.d.). Internal study regarding SATCOM ground-station logs. MH370 Flight Path Reconstruction Group. | grey | UNVERIFIED, NO DOI | - (no use traced) | - |
| `FrancoisGarrison1982a` | Francois, R. E. and Garrison, G. R. (1982). Sound absorption based on ocean measurements: Part I: Pure water and magnesium sulfate contributions. J. Acoust. Soc. Am., 72, 896–907. https://doi.org/10.1121/1.388170. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `FrancoisGarrison1982b` | Francois, R. E. and Garrison, G. R. (1982). Sound absorption based on ocean measurements. Part II: Boric acid contribution and equation for total absorption. J. Acoust. Soc. Am., 72, 1879–1890. https://doi.org/10.1121/1.388673. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `GaspinShuler1971` | Gaspin, J. B. and Shuler, V. K. (1971). Source Levels of Shallow Underwater Explosions. Naval Ordnance Laboratory, NOLTR 71-160. | official | UNVERIFIED, NO DOI | hydroacoustics (7 files) | - |
| `gdp6h` | Lumpkin, R. and Centurioni, L. (2019). Global Drifter Program quality-controlled 6-hour interpolated data from ocean surface drifting buoys. NOAA National Centers for Environmental Information. https://doi.org/10.25921/7ntx-z961. Accessed [DATE NOT RECORDED]. | official | METADATA MISMATCH | ocean drift, ocean drift / transport (6 files) | - |
| `GEBCO2026` | GEBCO Bathymetric Compilation Group 2026 (2026). The GEBCO_2026 Grid – a continuous terrain model for oceans and land at 15 arc-second intervals. NERC EDS British Oceanographic Data Centre NOC. https://doi.org/10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa. Accessed [DATE NOT RECORDED]. | grey | METADATA VERIFIED | hydroacoustics, ocean drift / transport (6 files) | - |
| `glorys12` | E.U. Copernicus Marine Service Information (n.d.). Global Ocean Physics Reanalysis (GLOBAL_MULTIYEAR_PHY_001_030). https://doi.org/10.48670/moi-00021. Accessed [DATE NOT RECORDED]. | grey | METADATA MISMATCH | Pleiades, ocean drift, ocean drift / transport (4 files) | - |
| `griffa1996stochastic` | Griffa, A. (1996). Applications of stochastic particle models to oceanographic problems. Stochastic Modelling in Physical Oceanography. Birkhäuser. | official | UNVERIFIED, NO DOI | ocean drift / transport (1 file) | - |
| `griffin2016parti` | Griffin, D. A., Oke, P. R. and Jones, E. M. (2016). The search for MH370 and ocean surface drift. CSIRO Oceans and Atmosphere, EP167888. https://doi.org/10.4225/08/5892224dec08c. | official | METADATA VERIFIED | ocean drift (5 files) | - |
| `griffin2017partii` | Griffin, D. A., Oke, P. R. and Jones, E. M. (2017). The search for MH370 and ocean surface drift – Part II. CSIRO Oceans and Atmosphere, EP172633. | official | UNVERIFIED, NO DOI | ocean drift, ocean drift / transport (9 files) | - |
| `griffin2017partiii` | Griffin, D. A. and Oke, P. R. (2017). The search for MH370 and ocean surface drift – Part III. CSIRO Oceans and Atmosphere, EP174155. | official | UNVERIFIED, NO DOI | ocean drift (9 files) | - |
| `gshhg237` | Wessel, P. and Smith, Walter H. F. (2017). GSHHG: Global Self-consistent, Hierarchical, High-resolution Geography Database, version 2.3.7. https://www.soest.hawaii.edu/pwessel/gshhg/. Accessed [DATE NOT RECORDED]. | grey | UNVERIFIED, NO DOI | ocean drift / transport (no use traced) | - |
| `HandleyLemos2019` | Handley, W. and Lemos, P. (2019). Quantifying tensions in cosmological parameters: Interpreting the DES evidence ratio. Physical Review D, 100, 043504. https://doi.org/10.1103/PhysRevD.100.043504. | peer-reviewed | METADATA VERIFIED | Pleiades (5 files) | - |
| `holland2018` | Holland, I. D. (2018). MH370 Burst Frequency Offset Analysis and Implications on Descent Rate at End-of-Flight. IEEE Aerospace and Electronic Systems Magazine, 33, 24–33. https://doi.org/10.1109/MAES.2018.170048. | peer-reviewed | METADATA VERIFIED | end of flight (8 files) | yes |
| `holland2018oacopy` | Holland, I. D. (2018). MH370 Burst Frequency Offset Analysis and Implications on Descent Rate at End-of-Flight (author's accepted version). https://arxiv.org/abs/1702.02432v3. Accessed 12 October 2026. | grey | UNVERIFIED, NO DOI | - (8 files) | yes |
| `iannello2018` | Iannello, V. (2018). End-of-flight simulations (web article; VERIFY title and URL from the archive snapshot). | grey | UNVERIFIED, NO DOI | end of flight (9 files) | - |
| `IMOSANMNPA` | Integrated Marine Observing System (n.d.). Australian National Mooring Network passive acoustic observatories (Curtin University CMST loggers). https://imos-data.s3-ap-southeast-2.amazonaws.com/IMOS/ANMN/Acoustic/. Accessed [DATE NOT RECORDED]. | grey | UNVERIFIED, NO DOI | hydroacoustics (no use traced) | - |
| `ioc2010teos10` | IOC, S. and IAPSO (2010). The international thermodynamic equation of seawater – 2010: Calculation and use of thermodynamic properties. Intergovernmental Oceanographic Commission, UNESCO, 56. | grey | UNVERIFIED, NO DOI | ocean drift / transport (no use traced) | - |
| `iso2533` | International Organization for Standardization (1975). Standard Atmosphere. International Organization for Standardization, ISO 2533:1975. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `Jeffreys1961` | Jeffreys, H. (1961). Theory of Probability. Oxford University Press. | official | UNVERIFIED, NO DOI | hydroacoustics (3 files) | - |
| `Jensen2011` | Jensen, F. B., Kuperman, W. A., Porter, M. B. and Schmidt, H. (2011). Computational Ocean Acoustics. Springer. https://doi.org/10.1007/978-1-4419-8678-8. | official | METADATA VERIFIED | hydroacoustics (4 files) | - |
| `Kadri2019` | Kadri, U. (2019). Effect of sea-bottom elasticity on the propagation of acoustic–gravity waves from impacting objects. Scientific Reports, 9, 912. https://doi.org/10.1038/s41598-018-37626-z. | peer-reviewed | METADATA VERIFIED | hydroacoustics (3 files) | - |
| `Kadri2024` | Kadri, U. (2024). Underwater acoustic analysis reveals unique pressure signals associated with aircraft crashes in the sea: revisiting MH370. Scientific Reports, 14, 10102. https://doi.org/10.1038/s41598-024-60529-1. | peer-reviewed | METADATA VERIFIED | hydroacoustics (15 files) | - |
| `KadriAbdolaliKirby2025` | Kadri, U., Abdolali, A. and Kirby, J. T. (2025). Acoustic-gravity quantum tunnelling analogy. J. Fluid Mech., 1018, A18. | peer-reviewed | UNVERIFIED, NO DOI | hydroacoustics (5 files) | - |
| `Karney2013` | Karney, C. F. F. (2013). Algorithms for geodesics. J. Geodesy, 87, 43–55. https://doi.org/10.1007/s00190-012-0578-z. | peer-reviewed | METADATA VERIFIED | hydroacoustics, ocean drift / transport (3 files) | - |
| `KassRaftery1995` | Kass, R. E. and Raftery, A. E. (1995). Bayes Factors. J. Am. Stat. Assoc., 90, 773–795. https://doi.org/10.1080/01621459.1995.10476572. | peer-reviewed | METADATA VERIFIED | hydroacoustics (4 files) | - |
| `lawchune2021waverys` | Law-Chune, S. and others (2021). WAVERYS: a CMEMS global wave reanalysis during the altimetry period. Ocean Dynamics, 71, 357–378. https://doi.org/10.1007/s10236-020-01433-w. | peer-reviewed | METADATA VERIFIED | ocean drift / transport (1 file) | - |
| `lellouche2021glorys12` | Lellouche, J.-M. and others (2021). The Copernicus Global 1/12° Oceanic and Sea Ice GLORYS12 Reanalysis. Frontiers in Earth Science, 9, 698876. https://doi.org/10.3389/feart.2021.698876. | peer-reviewed | METADATA VERIFIED | ocean drift / transport (4 files) | - |
| `locarnini2024woa23t` | Locarnini, R. A. and others (2024). World Ocean Atlas 2023, Volume 1: Temperature. https://doi.org/10.25923/54bh-1613. | official | METADATA VERIFIED | ocean drift / transport (2 files) | - |
| `lock1964` | Lock, R. C. (1964). The prediction of the drag of aerofoils and wings at high subsonic speeds. | peer-reviewed | UNVERIFIED, NO DOI | end of flight (1 file) | - |
| `margo1990` | Board of Inquiry (Margo Commission) (1990). Report of the Board of Inquiry into the Helderberg Air Disaster. Board of Inquiry (Margo Commission). | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `mca2006fsh604` | Egyptian Ministry of Civil Aviation (2006). Final Report of the Accident Investigation, Flash Airlines Flight 604, January 3, 2004, Boeing 737-300 SU-ZCF, Red Sea off Sharm El-Sheikh, Egypt. Ministry of Civil Aviation, Egypt. | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `McDougallBarker2011` | McDougall, T. J. and Barker, P. M. (2011). Getting started with TEOS-10 and the Gibbs Seawater (GSW) Oceanographic Toolbox. SCOR/IAPSO WG127. | grey | UNVERIFIED, NO DOI | hydroacoustics, ocean drift / transport (5 files) | - |
| `mearns1994` | Mearns, D. L. (1994). MV Derbyshire survey report. International Transport Workers' Federation. | grey | UNVERIFIED, NO DOI | settling (2 files) | - |
| `metron2011` | Stone, L. D. and others (2011). Search Analysis for the Location of the AF447 Underwater Wreckage. Metron Inc., report to BEA. https://bea.aero/fileadmin/uploads/tx_elyextendttnews/metron.search.analysis_01.pdf. | grey | UNVERIFIED, NO DOI | settling (6 files) | - |
| `Metz2023` | Metz, D., Obana, K. and Fukao, Y. (2023). Remote hydroacoustic detection of an airplane crash. Pure Appl. Geophys., 180, 1343–1351. https://doi.org/10.1007/s00024-022-03117-6. | peer-reviewed | METADATA VERIFIED | hydroacoustics (6 files) | - |
| `minchin2017pleiades` | Minchin, S., Mueller, N., Lewis, A., Byrne, G. and Tran, M. (2017). Summary of imagery analyses for non-natural objects in support of the search for Flight MH370: Results from the analysis of imagery from the PLEIADES 1A satellite undertaken by Geoscience Australia. Geoscience Australia, Record 2017/013. https://doi.org/10.11636/record.2017.013. | official | METADATA VERIFIED | Pleiades (3 files) | - |
| `mot2017` | Malaysian ICAO Annex 13 Safety Investigation Team for MH370 (2017). Summary of Possible MH370 Debris Recovered (updated 30 April 2017). Ministry of Transport Malaysia. | official | UNVERIFIED, NO DOI | ocean drift (no use traced) | - |
| `mot2018mh370` | Malaysian ICAO Annex 13 Safety Investigation Team for MH370 (2018). Safety Investigation Report, Malaysia Airlines Boeing B777-200ER (9M-MRO), 08 March 2014. Ministry of Transport Malaysia, MH370/01/2018. | official | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `ntsb2010` | National Transportation Safety Board (2010). Loss of Thrust in Both Engines After Encountering a Flock of Birds and Subsequent Ditching on the Hudson River, US Airways Flight 1549. NTSB, NTSB/AAR-10/03. | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `ntsc2008dki574` | National Transportation Safety Committee (2008). Aircraft Accident Investigation Report, PK-KKW. NTSC Indonesia. | grey | UNVERIFIED, NO DOI | settling (no use traced) | candidate |
| `oke2013ofam3` | Oke, P. R. and others (2013). Evaluation of a near-global eddy-resolving ocean model. Geoscientific Model Development, 6, 591–615. https://doi.org/10.5194/gmd-6-591-2013. | peer-reviewed | METADATA VERIFIED | ocean drift / transport (1 file) | - |
| `pollschumann2021` | Poll, D. I. A. and Schumann, U. (2021). An estimation method for the fuel burn and other performance characteristics of civil transport aircraft in the cruise. Part 1: fundamental quantities and governing relations for a general atmosphere. The Aeronautical Journal, 125, 257–295. | peer-reviewed | UNVERIFIED, NO DOI | end of flight (1 file) | - |
| `Porter1992` | Porter, M. B. (1992). The KRAKEN Normal Mode Program. Naval Research Laboratory, NRL/MR/5120-92-6920. | official | UNVERIFIED, NO DOI | hydroacoustics (2 files) | - |
| `pyram` | Donnelly, M. (2025). pyram 1.3.0: Python adaptation of the Range-dependent Acoustic Model (RAM). https://github.com/marcuskd/pyram. Accessed [DATE NOT RECORDED]. | grey | UNVERIFIED, NO DOI | hydroacoustics (1 file) | - |
| `rahimi2007random` | Rahimi, A. and Recht, B. (2007). Random features for large-scale kernel machines. Advances in Neural Information Processing Systems 20. | peer-reviewed | UNVERIFIED, NO DOI | ocean drift / transport (1 file) | - |
| `reagan2024woa23s` | Reagan, J. R. and others (2024). World Ocean Atlas 2023, Volume 2: Salinity. https://doi.org/10.25923/70qt-9574. | official | METADATA VERIFIED | ocean drift / transport (3 files) | - |
| `RHUMRUM_YV` | RESIF (2011). RHUM-RUM experiment, 2011–2015 (FDSN network YV). | grey | UNVERIFIED, NO DOI | hydroacoustics (no use traced) | - |
| `roquet2015polynomial` | Roquet, F., Madec, G., McDougall, T. J. and Barker, P. M. (2015). Accurate polynomial expressions for the density and specific volume of seawater using the TEOS-10 standard. Ocean Modelling, 90, 29–43. https://doi.org/10.1016/j.ocemod.2015.04.002. | peer-reviewed | METADATA VERIFIED | ocean drift / transport (1 file) | - |
| `sir2018` | Malaysian ICAO Annex 13 Safety Investigation Team for MH370 (2018). Safety Investigation Report: MH370 (9M-MRO). Ministry of Transport Malaysia, MH370/01/2018. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | candidate |
| `sir2018app16e` | The Boeing Company (2018). Performance Analysis – Malaysian Airlines 777 9M-MRO Missing Occurrence. Malaysian ICAO Annex 13 Safety Investigation Team for MH370. | official | UNVERIFIED, NO DOI | end of flight (no use traced) | candidate |
| `spinoccia2017mh370` | Spinoccia, M. (2017). MH370 Phase 1 150m Bathymetry datasets (GA-4421, GA-4422 & GA-4430). Geoscience Australia. https://pid.geoscience.gov.au/dataset/ga/100315. Accessed [DATE NOT RECORDED]. | official | UNVERIFIED, NO DOI | ocean drift / transport (1 file) | - |
| `stone2014` | Stone, L. D., Keller, C. M., Kratzke, T. M. and Strumpfer, J. P. (2014). Search for the Wreckage of Air France Flight AF 447. Statistical Science, 29, 69–80. https://doi.org/10.1214/13-STS420. | peer-reviewed | METADATA VERIFIED | settling (13 files) | - |
| `sutherland2020` | Sutherland, G., Soontiens, N., Dufois, F. and others (2020). Evaluating the leeway coefficient of ocean drifters using operational marine environmental prediction systems. Journal of Atmospheric and Oceanic Technology. https://doi.org/10.1175/JTECH-D-20-0013.1. | peer-reviewed | METADATA VERIFIED | ocean drift (4 files) | - |
| `sutherland2020leeway` | Sutherland, G. and others (2020). Evaluating the leeway coefficient of ocean drifters using operational marine environmental prediction systems. Journal of Atmospheric and Oceanic Technology, 37, 1943–1954. | peer-reviewed | UNVERIFIED, NO DOI | ocean drift / transport (4 files) | - |
| `Taylor1921` | Taylor, G. I. (1921). Diffusion by continuous movements. Proceedings of the London Mathematical Society, s2-20, 196–212. https://doi.org/10.1112/plms/s2-20.1.196. | peer-reviewed | METADATA MISMATCH | Pleiades (5 files) | - |
| `tcds777` | Federal Aviation Administration (n.d.). Boeing 777 Type Certificate Data Sheet. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `tcdstrent800` | European Union Aviation Safety Agency (n.d.). Rolls-Royce Trent 800 Series Type Certificate Data Sheet. | grey | UNVERIFIED, NO DOI | end of flight (no use traced) | - |
| `TEOS10` | IOC, SCOR and IAPSO (2010). The International Thermodynamic Equation of Seawater – 2010: Calculation and Use of Thermodynamic Properties. Intergovernmental Oceanographic Commission, UNESCO, 56. | grey | UNVERIFIED, NO DOI | hydroacoustics (no use traced) | - |
| `thresher1963` | US Navy (1963). Court of Inquiry into the loss of USS Thresher. US Navy. | official | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `tsb2003` | Transportation Safety Board of Canada (2003). Aviation Investigation Report A98H0003: In-Flight Fire Leading to Collision with Water, Swissair Flight 111. TSB, A98H0003. | grey | UNVERIFIED, NO DOI | settling (no use traced) | - |
| `Vincenty1975` | Vincenty, T. (1975). Direct and inverse solutions of geodesics on the ellipsoid with application of nested equations. Survey Review, 23, 88–93. https://doi.org/10.1179/sre.1975.23.176.88. | peer-reviewed | METADATA VERIFIED | hydroacoustics (2 files) | - |
| `wessel1996gshhg` | Wessel, P. and Smith, Walter H. F. (1996). A global, self-consistent, hierarchical, high-resolution shoreline database. Journal of Geophysical Research: Solid Earth, 101, 8741–8743. https://doi.org/10.1029/96JB00104. | peer-reviewed | METADATA VERIFIED | ocean drift / transport (3 files) | - |
| `WOA23` | Reagan, J. R., Boyer, T. P., García, H. E., Locarnini, R. A., Baranova, O. K., Bouchard, C. and others (2023). World Ocean Atlas 2023. NOAA National Centers for Environmental Information. https://doi.org/10.25921/va26-hv25. Accessed [DATE NOT RECORDED]. | official | METADATA VERIFIED | hydroacoustics, ocean drift / transport (2 files) | - |

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
