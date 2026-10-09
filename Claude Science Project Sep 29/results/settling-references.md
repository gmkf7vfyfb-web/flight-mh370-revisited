# Ocean settling: citation ledger

The settling module's ledger, kept under the standing rule of 9 October (`coordination/architecture.md`,
~01:20 UTC) and stored in `results/` per the ~02:25 correction. The matching BibTeX is
`results/settling-references.bib`. Backfilled 9 Oct 2026 at the first pause after the sequence.

**Printed pages.** Most sources below were checked on the web on 9 Oct 2026 (the `verification` column
of `engine/hypotheses/settling/data/analogues.csv`) and **not yet read in primary form page by page**.
Where that is so, the row says "pages to be added". No page number is given that was not read. No
unauthorised copy of a copyrighted work is cited. Ocean products and TEOS-10 are cited under ocean
transport's keys in `results/ocean-references.md` and are not duplicated here.

| key | source | what it supports (pages where read) | used in | obtained from, licence |
|---|---|---|---|---|
| bea2012af447 | BEA (2012) *Final Report on the accident on 1st June 2009 to the Airbus A330-203 registered F-GZCP operated by Air France, flight AF 447 Rio de Janeiro - Paris*. Paris: BEA, July 2012. https://bea.aero | wreckage about 6.5 NM on radial 019 from the last known position, at about 3,900 m; last recorded vertical speed -10,912 ft/min and ground speed 107 kt (55.4 and 55.0 m/s; 78.1 m/s total). **Pages to be added** | `breakup.toml` broken-family anchor (P(broken) 0.85); `data/analogues.csv` AF447; `results/settling-d6/settling-d6.md` | BEA website, public report; cited, not redistributed |
| stone2014 | Stone, L. D., Keller, C. M., Kratzke, T. M., Strumpfer, J. P. (2014) "Search for the wreckage of Air France Flight AF 447". *Statistical Science* 29(1), 69-80. doi:10.1214/13-STS420 | BEA's 40 NM circle bounding post-LKP flight; first debris 38 NM from the LKP on day 6. **Pages to be added** | `data/analogues.csv` AF447; replies to Pete 9 Oct | publisher (IMS); cited |
| metron2011 | Stone, L. D. et al. (Metron Inc.) (2011) *Search Analysis for the Location of the AF447 Underwater Wreckage*. Report to BEA (2011; exact date to be confirmed). https://bea.aero/fileadmin/uploads/tx_elyextendttnews/metron.search.analysis_01.pdf | more than 1,000 pieces and 50 bodies recovered and their positions logged; 33 bodies located 6-10 June 2009 used for the reverse-drift prior; aerial and ship searches 1-26 June 2009. **Pages to be added** | the occupants class's AF447 calibration (`run.toml` [occupants], broken stays_afloat 0.22); architecture entries 9 Oct | BEA website, public report; cited |
| af447seabed2011 | Recovery of remains from the AF447 seabed wreckage, May-June 2011: 104 victims recovered, 74 never found; main debris field about 600 m x 200 m. SECONDARY: Encyclopaedia Britannica, "What Happened to Air France Flight 447?"; Al Jazeera, 16 June 2011; IEEE Spectrum, April 2011 (field size, quoting press reports) | counts and field size as stated; **a primary BEA source is to be found** | `results/settling-d6/settling-d6.md` (field size vs dense-class offsets); occupants class rationale | web, 9 Oct 2026; secondary, cited as such |
| margo1990 | *Report of the Board of Inquiry into the Helderberg Air Disaster* (Margo Commission), Pretoria, 1990 | SAA295 wreckage at about 4,400 m; north-east area about 900 x 450 m, centres about 600 m apart; light wreckage about 2.4 km north-west. **Pages to be added** (read via a Wikisource transcription of Part 1) | `data/analogues.csv` SAA295 | public inquiry report; cited |
| ntsb2010 | NTSB (2010) *Loss of Thrust in Both Engines After Encountering a Flock of Birds and Subsequent Ditching on the Hudson River, US Airways Flight 1549*. NTSB/AAR-10/03 | Table 2: contact speed and descent rate (about 64 m/s and 3.8 m/s down) | `breakup.toml` intact anchor (P(intact) 0.88) | NTSB, US Government work, public domain |
| tsb2003 | TSB Canada (2003) *Aviation Investigation Report A98H0003, Swissair 111*. Sections 1.12.6, 1.12.12 | contact about 154 m/s, 20 deg nose down; field and piece count (TSB chronology: 70 x 30 m, about two million pieces). **Pages to be added** | `breakup.toml` fragmented anchor (P(fragmented) 0.84) | TSB, public report |
| mca2006fsh604 | Egyptian Ministry of Civil Aviation (2006) *Final/Factual Report of Investigation of Accident, Flash Airlines Flight 604* (BEA-hosted) | depth about 1,000 m; impact values (416 kt, pitch 25.4 deg down) via secondary summaries. **Pages to be added** | `data/analogues.csv` FSH604 (rule gives P(fragmented) 0.97) | BEA-hosted PDF; cited |
| ntsc2008dki574 | NTSC Indonesia (2008) *Aircraft Accident Investigation Report, PK-KKW* | depth about 2,000 m (ULB positions); recorder separation about 1.4 km SECONDARY. **Pages to be added** | `data/analogues.csv` DKI574 | NTSC; cited |
| bea2009frwg | BEA (2009) *Flight Data Recovery Working Group report*, p. 26 | Yemenia IYE626 depth about 1,200 m | `data/analogues.csv` IYE626 | BEA website; cited |
| dnv2010 | DNV (2010) *DNV-RP-F107 Risk Assessment of Pipeline Protection*, October 2010, Table 10 (DNVGL-RP-F107, May 2017, Table 5-2 has the same angles) | angular deviation of dropped objects: flat/long 15 / 9 / 5 deg, box/round 10 / 5 / 3 / 2 deg; an independent order-of-magnitude check (sd 140-1,070 m at 4 km) | `data/analogues.csv` MODEL-DROPPED; `lib.rs` doc | DNV public recommended practice; cited |
| andersen2005 | Andersen, A., Pesavento, U., Wang, Z. J. (2005) "Unsteady aerodynamics of fluttering and tumbling plates". *J. Fluid Mech.* 541, 65-90; and "Analysis of transitions between fluttering, tumbling and steady descent of falling cards", *J. Fluid Mech.* 541, 91-104 | descent factor above one and glide for flat pieces (form only). **Pages to be added** | `physics.rs` (descent_factor, glide); `breakup.toml` flat-panel | publisher (CUP); bibliographic details checked in citing records |
| field1997 | Field, S. B., Klaus, M., Moore, M. G., Nori, F. (1997) "Chaotic dynamics of falling disks". *Nature* 388, 252-254. doi:10.1038/40817 | regimes of falling disks (steady, fluttering, tumbling, chaotic); form only | `physics.rs` glide memory | publisher; cited |
| chu2006 | Chu, P. C., Fan, C. W. (2006) "Prediction of falling cylinder through air-water-sediment columns". *J. Appl. Mech.* 73, 300-314 (IMPACT35) | trajectory-model comparator for dense cylinders. **Pages to be added** | `data/analogues.csv` MODEL-IMPACT35 | NPS Calhoun author copy; cited |
| mearns1994 | Mearns, D. L. (1994) ITF Derbyshire survey report; Colman, J. (2000) *Report of the Re-opened Formal Investigation into the Loss of the MV Derbyshire*; Faulkner (1998) | wreck at 4,210 m; stern about 600 m from bow; implosion during sinking. **Pages to be added**; the ~40 NM offset is UNVERIFIED | `data/analogues.csv` DERBYSHIRE; the implosion alternative's rationale | various; cited |
| thresher1963 | US Navy Court of Inquiry (1963); CTG 168 final report, quoted in Naval Submarine League archive articles | 8,250 ft; six parts within about 400 yd. SECONDARY quotation | `data/analogues.csv` THRESHER; implosion rationale | secondary; cited as such |
| anderson2018 | Anderson (2018) report for the ATSB on two 19th-century wrecks found in the MH370 search, Western Australian Museum | W1/W2 (West Ridge) as real sonar-detected seabed fields. **Pages to be added** | `data/analogues.csv` W1, W2 | WA Museum release; cited |
| atsb2017 | ATSB (2017) *The Operational Search for MH370*, AE-2014-054, 3 October 2017 | search zone 1,000-6,000 m deep; Diamantina Escarpment 638 m to about 5,800 m. **Pages to be added; the ATSB server refuses automated clients** (see the drift ledger) | D6 depths (5,800 m tail) | ATSB; cited |
| mot2018mh370 | Malaysian ICAO Annex 13 Safety Investigation Team (2018) *Safety Investigation Report, MH370/9M-MRO*, July 2018 (exact date to be confirmed) | 239 aboard (227 passengers, 12 crew). **Pages to be added** | occupants class `pieces = 239` | Malaysian MOT; cited |

Ocean data and standards, under ocean transport's keys (`results/ocean-references.md`):
`gebco2026` (seabed, `run.toml` [shared]); `reagan2024woa23`, `locarnini2024woa23t`, `reagan2024woa23s`
(density climatology); `ioc2010teos10`, `mcdougall2011gsw` (in-situ density); `lellouche2021glorys12`,
`cmems_glo_phy_001_030` (the 8 March 2014 surface-current percentiles behind `run.toml`'s 0.13 m/s and the
0.31 m/s variant). ETOPO 2022 (NOAA NCEI, doi:10.25921/fd45-gt74) underlies the posterior-weighted depth
percentiles; it is to be added to the ocean ledger or here.

**Open items:**
1. Pages for every row marked "pages to be added", read in primary form.
2. A primary BEA source for AF447's 2011 seabed recovery figures (104 recovered, 74 not found) and field size.
3. The body properties in the occupants class (density, frontal area, leeway) carry no source yet. They
   are declared assumptions; a forensic or SAR reference (for example, person-in-water leeway) is to be found.
