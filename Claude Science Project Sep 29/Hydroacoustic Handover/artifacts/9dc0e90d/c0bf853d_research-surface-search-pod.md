# 2014 MH370 aerial and ship surface search: probability of detection (POD), search geometry and weather

Compiled 17 Oct 2026. All access dates are 17 Oct 2026. Page numbers are the printed page numbers unless "PDF p." is written.

**Source grades.** A = official or peer-reviewed primary source, read in this session with page numbers. A* = official primary source, read by an earlier session of this project on 17 Oct 2026 (project ledger `aerial_surface_search_source_ledger.md`) and not re-read here. B = official, cited but not read. C = independent analyst, community or press; used as argument, not as data.

## Scope reductions and substitutions (declared)

1. **IAMSAR Manual Vol. II Appendix N tables were not read.** The IAMSAR Manual is a paid IMO/ICAO publication. I substituted the Australian National SAR Manual (NATSAR), February 2026 edition, which AMSA states was "developed with due regard to" IAMSAR. NATSAR notes that its weather table differs from IAMSAR for "other search objects" in winds over 15 kt. The 2026 NATSAR values may differ from the edition AMSA used in March-April 2014; I did not find the 2014 edition. All sweep-width numbers in this file are therefore **provisional as a description of what AMSA used in 2014**.
2. **USCG Addendum (COMDTINST M16130.2 series) sweep-width tables were not read.** The USCG server returns 403 to automated clients (earlier session). Grade B.
3. **ATSB (2017) was read as a text extraction** of Pete's Google Drive copy (41.7 MB, over the 10 MB connector limit). Figures 19 and 20 (coverage and CSIRO POD maps) were not viewed. Daily-table columns are collapsed in the extraction; area and track spacing are reliable, the count columns are not.
4. **AMSA media releases for 29-31 March 2014 were not obtained.** Internet Archive returned "Temporarily Offline" during this session, so no new captures were made; the 49 AMSA PDFs and 59 JACC releases captured by the earlier session were re-read from the project artifacts.
5. **Duncan Steel's website** (host of the RNZAF image set) did not answer from the sandbox. The Dropbox copies linked by Iannello were not downloaded (Dropbox redirects cannot be allowlisted).
6. Items marked A* (Ivić et al. 2020; Malaysian SIR; PM transcript; GA polygon statistics; CSIRO Part II/III wording other than what is quoted below; CSIRO digitised cumulative POD) were carried over from the earlier session and were not re-verified here.

---

## Q1. What POD did CSIRO assume for the 2014 surface search, and what did ATSB say?

**Short answer.** CSIRO did not assume 100 % detection inside every searched polygon, and it did not compute POD from sweep width and track spacing. It took **AMSA's own daily POD estimate for each daily search box** and applied it equally to every modelled debris parcel inside that box, then combined days as cumulative POD = 1 − ∏(1 − POD_day). Part I (Dec 2016, p.23) states that AMSA coordinators made the daily POD estimates "based on the weather, number of search assets deployed, the size of the search area and other factors", and that these estimates "assume that there is only a single target", which CSIRO called "conservative" because many items were afloat. Part IV (Oct 2017, pp.1-2) gives the values: the POD was "low (10 or 20%) on days of very poor weather or wide (>20NM) track spacing but high (often 100%) on other days", and it was "assumed to be equal for all items within the search boxes, regardless of location relative to completed search lines". Part IV also concedes this "would be an over-estimate" for any single item outside an aircraft's detection range, and that the values were meant to represent a debris field, not single items. The daily AMSA POD values themselves were **never published** (NOT FOUND in ATSB 2017, CSIRO I-IV, ICAO WP30 or the AMSA/JACC releases). Part IV's supporting argument for a 30.5°S impact is an expected-count estimate N·P·W/S (N = 200 items, P = 0.5 in the box, W/S = 0.1) giving about 10 detections per day, and 12 over 5 days if N and W are halved (p.3). The First Principles Review (Dec 2016, p.18) gives no POD numbers; it says the lack of detections "argues quite strongly" against 32°S-25°S. ATSB (2017, p.34) says AMSA analysed daily "coverage confidence" from coverage reports and visibility, that confidence "was low on some days due to poor weather or the large size of the search areas", and that the 28 March move north gave "a high probability of detecting debris" for impacts between about 26°S and 32.5°S.

**Wording and method, by document.**

| Document | Page | Statement (short quotation) |
|---|---|---|
| CSIRO Part I, EP167888 (8 Dec 2016) | 23 | Daily POD estimates "were made by the search coordinators at AMSA"; they "assume that there is only a single target being searched, so they are conservative". Search "strongly contra-indicates regions north of 32°S"; "mildly contra-indicates" 32-34°S; 34-38°S "highly likely to have escaped detection". |
| CSIRO Part I | 24 (Fig. 4.1) | Items start within 45 NM of the 7th arc, windage 1.2 %; right panel = cumulative POD map; flaperon case in online appendix. |
| CSIRO Part IV, EP177204 (3 Oct 2017) | 1 | POD "assumed to be equal for all items within the search boxes, regardless of location relative to completed search lines"; "low (10 or 20%)" on very poor weather or track spacing >20 NM, "high (often 100%) on other days"; "would be an over-estimate" if read as single-item POD. |
| CSIRO Part IV | 2 | Two boxes at 50 % give cumulative 75 %; map = spatially binned arithmetic mean over adjacent parcels; Fig. 1.1 caption: search "effectively ruled out crash sites north of about 33°S but ineffectively searched latitudes south of 34°S". |
| CSIRO Part IV | 3 | 30°S debris field targeted 28 Mar-1 Apr by 8-11 aircraft at 12-16 NM spacing, several with marine surveillance radar; daily areas 164,087-298,636 km²; single-item POD "cannot reliably be estimated"; N·P·W/S argument. |
| CSIRO Part IV | 6 | "fairly high chance" of detecting a debris field near Broken Ridge; recommends field measurement of radar detection ranges of real debris (e.g. the flaperon). |
| Griffin, CSIRO web page (entry of 3 Oct 2017) | n/a | Probability on any single overflight "may have been low (and probably very low for any particular item)", but cumulative probability of detecting at least one item "was quite high". |
| ATSB First Principles Review (20 Dec 2016) | 18 | Lack of detections "argues quite strongly" the aircraft did not enter the water between 32°S and 25°S; no POD numbers. |
| ATSB, The Operational Search for MH370 (3 Oct 2017) | 34 | AMSA analysed daily "coverage confidence"; first days "fairly ineffective"; 28 Mar move gave "a high probability of detecting debris" for 26°S-32.5°S; Fig. 20 (p.35) = CSIRO POD map. No numeric POD, sweep width or polygon coordinates. |

**Note for the likelihood.** At the 12-16 NM track spacing of the decisive days, single-item coverage from the textbook sweep width (Q2) is C ≈ 0.14-0.19, below NATSAR's statement that "A coverage factor of less than 0.5 is unsatisfactory" (NATSAR 2026, para 4.3.49, p.221). AMSA's "often 100 %" is therefore not a single-item POD in the IAMSAR sense; it is closer to a field-level or area-confidence statement. The two CSIRO reports describe it differently (Part I: single-target, conservative; Part IV: over-estimate for single items). This inconsistency should be stated in the paper.

**Obtainable and how.** CSIRO Parts I-IV and ATSB reports: public download from atsb.gov.au (the site does not answer automated clients from this sandbox; copies are on Pete's Drive). AMSA daily POD / coverage-confidence records: not published; **request from AMSA** (JRCC Australia) — they exist per ATSB 2017 p.34 and CSIRO Part I p.23.

---

## Q2. Baseline SAR detection probabilities: sweep widths, corrections and the detection law

**Short answer.** The SAR planning chain is W = W_u × f_w × f_v × f_f (uncorrected sweep width times weather, speed and fatigue corrections), coverage C = W/S for parallel sweeps (C = Z/A in general, with effort Z = W × L), and POD from C. IAMSAR (MSC.1/Circ.1686, 2025 amendments, glossary PDF p.27) defines "C = W/S". The worked IAMSAR example (para 5.3.68, PDF p.45) gives **4.3 km (2.3 NM)** for a fixed-wing aircraft at 300 m (1,000 ft) searching for a 4-person liferaft "on a clear, calm day". NATSAR 2026 Table D-5:6(1) gives the same 2.3 NM at 1,000 ft and visibility >40 km. The weather correction for rafts and boats under 10 m is 1.0 / 0.5 / 0.25 for winds <15 kt / 15-25 kt / >25 kt (or seas 0-1 / 1-1.5 / >1.5 m); for "other search objects" NATSAR uses 1.0 / 0.8 / 0.5 and states this differs from IAMSAR. NATSAR tables stop at 2,000 ft (600 m); there is **no NATSAR row for 1,000 m (about 3,300 ft)** and **no row for aircraft debris** (NOT FOUND). NATSAR's coverage-to-POD example (Table 4-2, p.222: C = 1 → 78 %, C = 0.5 → 47 %, five searches at C = 0.5 → 95.8 %) is consistent with the inverse-cube ("ideal conditions") law POD = erf(√π·C/2), not with the exponential law; I computed 0.790 and 0.469 for the inverse-cube law, and 0.632 and 0.393 for the exponential law POD = 1 − exp(−C). IAMSAR (para 5.3.2, PDF p.44) says POD for the same coverage is lower under "normal" than "ideal" conditions, and conditions are "normal" whenever corrected W ≤ ½ the ideal value or navigation error ≥ W (para 5.3.68). Under normal conditions the exponential law is the appropriate one (standard search theory; Koopman 1980 not read here, grade B).

**Table Q2-a. Uncorrected visual sweep width W_u (NM), fixed-wing aircraft, maritime.** Source: NATSAR 2026, Tables D-5:6(1) (printed p.400) and D-5:6(2) (printed p.402). Visibility is meteorological visibility.

| Object                      | Altitude        |   Vis 2 km |   Vis 5 km |   Vis 10 km |   Vis 20 km |   Vis 30 km |   Vis >40 km |
|:----------------------------|:----------------|-----------:|-----------:|------------:|------------:|------------:|-------------:|
| Person in water             | 500 ft (150 m)  |        0   |        0.1 |         0.1 |         0.1 |         0.1 |          0.1 |
| Person in water             | 1000 ft (300 m) |        0   |        0.1 |         0.1 |         0.1 |         0.1 |          0.1 |
| Raft 1 person               | 500 ft (150 m)  |        0.3 |        0.7 |         0.9 |         1.2 |         1.4 |          1.4 |
| Raft 1 person               | 1000 ft (300 m) |        0.3 |        0.7 |         0.9 |         1.2 |         1.4 |          1.4 |
| Raft 4 Person               | 500 ft (150 m)  |        0.4 |        1   |         1.3 |         1.8 |         2   |          2.2 |
| Raft 4 Person               | 1000 ft (300 m) |        0.3 |        1   |         1.3 |         1.8 |         2.1 |          2.3 |
| Raft 6 Person               | 500 ft (150 m)  |        0.4 |        1.1 |         1.5 |         2.2 |         2.5 |          2.8 |
| Raft 6 Person               | 1000 ft (300 m) |        0.4 |        1.1 |         1.6 |         2.2 |         2.6 |          2.8 |
| Power Boat <5 m (15 ft)     | 500 ft (150 m)  |        0.4 |        0.9 |         1.2 |         1.5 |         1.7 |          1.8 |
| Power Boat <5 m (15 ft)     | 1000 ft (300 m) |        0.4 |        1   |         1.3 |         1.7 |         1.8 |          2   |
| Power Boat 5-8 m (15-25 ft) | 500 ft (150 m)  |        0.5 |        1.7 |         2.4 |         3.6 |         4.3 |          4.8 |
| Power Boat 5-8 m (15-25 ft) | 1000 ft (300 m) |        0.5 |        1.7 |         2.5 |         3.7 |         4.4 |          5   |
| Person in Water             | 1500 ft (450 m) |        0   |        0   |         0   |         0   |         0   |          0.1 |
| Person in Water             | 2000 ft (600 m) |        0   |        0   |         0   |         0   |         0   |          0   |
| Raft 1 person               | 1500 ft (450 m) |        0.2 |        0.7 |         0.9 |         1.3 |         1.4 |          1.4 |
| Raft 1 person               | 2000 ft (600 m) |        0.1 |        0.6 |         0.9 |         1.2 |         1.4 |          1.4 |
| Raft 4 person               | 1500 ft (450 m) |        0.3 |        1   |         1.3 |         1.9 |         2.1 |          2.3 |
| Raft 4 person               | 2000 ft (600 m) |        0.2 |        0.9 |         1.3 |         1.9 |         2.2 |          2.3 |
| Raft 6 person               | 1500 ft (450 m) |        0.3 |        1.1 |         1.6 |         2.3 |         2.6 |          2.9 |
| Raft 6 person               | 2000 ft (600 m) |        0.2 |        1.1 |         1.6 |         2.3 |         2.7 |          2.9 |
| Power Boat <5 (15 ft)       | 1500 ft (450 m) |        0.3 |        1   |         1.3 |         1.7 |         2   |          2.1 |
| Power Boat <5 (15 ft)       | 2000 ft (600 m) |        0.2 |        1   |         1.3 |         1.8 |         2   |          2.2 |
| Power Boat 6 (20 ft)        | 1500 ft (450 m) |        0.4 |        1.7 |         2.5 |         3.7 |         4.5 |          5.1 |
| Power Boat 6 (20 ft)        | 2000 ft (600 m) |        0.3 |        1.7 |         2.5 |         3.8 |         4.6 |          5.1 |

NATSAR notes: person-in-water values at 500 ft may be multiplied by 4 if a flotation device is worn. Rows for 8-25-person rafts, larger boats and ships are in the same tables and were not copied here.

**Table Q2-b. Correction factors.** Source: NATSAR 2026.

| Factor | Condition | Person in water, raft or boat <10 m | Other search objects | Page |
|---|---|---|---|---|
| Weather f_w (Table D-5:4) | Winds <15 kt or seas 0-1 m | 1.0 | 1.0 | 401 |
| | Winds 15-25 kt or seas 1-1.5 m | 0.5 | 0.8 | 401 |
| | Winds >25 kt or seas >1.5 m | 0.25 | 0.5 | 401 |
| Speed f_v, fixed wing (Table D-5:8) | ≤150 kt / 180 kt / 210 kt, raft 1-4 person | 1.1 / 1.0 / 0.9 | — | 407 |
| Fatigue f_f | Crew fatigued (worked example, para 4.3.40) | 0.9 | 0.9 | 220 |
| Rule | Use the worst of wind and sea row (para 4.3.39) | | | 220 |

IAMSAR's own weather table (Appendix N) was not read; NATSAR says its "other search objects" column differs from IAMSAR above 15 kt. There is no separate whitecap or cloud-cover multiplier in NATSAR; whitecaps are described qualitatively (paras 4.3.11-4.3.13: with numerous whitecaps "small objects are unlikely to be detected at all"). The 45 min after sunrise and before sunset are "commonly discounted" for visual search (para 4.3.31-4.3.32, p.219).

**Table Q2-c. Illustrative single-item, single-pass POD** (computed here; W = W_u × f_w only, no speed or fatigue factor).

| Case                               |   Fw |   S (NM) |   C=W/S |   POD exponential |   POD inverse cube |
|:-----------------------------------|-----:|---------:|--------:|------------------:|-------------------:|
| 4-person raft, 1000 ft, vis >40 km | 1    |        4 |   0.575 |             0.437 |              0.529 |
| 4-person raft, 1000 ft, vis >40 km | 1    |       12 |   0.192 |             0.174 |              0.19  |
| 4-person raft, 1000 ft, vis >40 km | 1    |       16 |   0.144 |             0.134 |              0.143 |
| 4-person raft, 1000 ft, vis >40 km | 0.5  |        4 |   0.287 |             0.25  |              0.281 |
| 4-person raft, 1000 ft, vis >40 km | 0.5  |       12 |   0.096 |             0.091 |              0.096 |
| 4-person raft, 1000 ft, vis >40 km | 0.5  |       16 |   0.072 |             0.069 |              0.072 |
| 4-person raft, 1000 ft, vis >40 km | 0.25 |        4 |   0.144 |             0.134 |              0.143 |
| 4-person raft, 1000 ft, vis >40 km | 0.25 |       12 |   0.048 |             0.047 |              0.048 |
| 4-person raft, 1000 ft, vis >40 km | 0.25 |       16 |   0.036 |             0.035 |              0.036 |
| 4-person raft, 1000 ft, vis 10 km  | 1    |        4 |   0.325 |             0.277 |              0.316 |
| 4-person raft, 1000 ft, vis 10 km  | 1    |       12 |   0.108 |             0.103 |              0.108 |
| 4-person raft, 1000 ft, vis 10 km  | 1    |       16 |   0.081 |             0.078 |              0.081 |
| 4-person raft, 1000 ft, vis 10 km  | 0.5  |        4 |   0.163 |             0.15  |              0.161 |
| 4-person raft, 1000 ft, vis 10 km  | 0.5  |       12 |   0.054 |             0.053 |              0.054 |
| 4-person raft, 1000 ft, vis 10 km  | 0.5  |       16 |   0.041 |             0.04  |              0.041 |
| 4-person raft, 1000 ft, vis 10 km  | 0.25 |        4 |   0.081 |             0.078 |              0.081 |
| 4-person raft, 1000 ft, vis 10 km  | 0.25 |       12 |   0.027 |             0.027 |              0.027 |
| 4-person raft, 1000 ft, vis 10 km  | 0.25 |       16 |   0.02  |             0.02  |              0.02  |
| 1-person raft, 1000 ft, vis >40 km | 1    |        4 |   0.35  |             0.295 |              0.339 |
| 1-person raft, 1000 ft, vis >40 km | 1    |       12 |   0.117 |             0.11  |              0.116 |
| 1-person raft, 1000 ft, vis >40 km | 1    |       16 |   0.087 |             0.084 |              0.087 |
| 1-person raft, 1000 ft, vis >40 km | 0.5  |        4 |   0.175 |             0.161 |              0.174 |
| 1-person raft, 1000 ft, vis >40 km | 0.5  |       12 |   0.058 |             0.057 |              0.058 |
| 1-person raft, 1000 ft, vis >40 km | 0.5  |       16 |   0.044 |             0.043 |              0.044 |
| 1-person raft, 1000 ft, vis >40 km | 0.25 |        4 |   0.087 |             0.084 |              0.087 |
| 1-person raft, 1000 ft, vis >40 km | 0.25 |       12 |   0.029 |             0.029 |              0.029 |
| 1-person raft, 1000 ft, vis >40 km | 0.25 |       16 |   0.022 |             0.022 |              0.022 |

**AF447 precedent.** Metron's 2011 report for the BEA (section 4.2, printed pp.12-17) reconstructed the 1-6 June 2009 French and Brazilian sorties in SAROPS from altitude, speed, aircraft type, visibility and sea state, with the target modelled as a **four-person life raft** taken as a surrogate for "a large piece of debris such as the galley". High-altitude radar patrols (two R-99, one E-3F) and some Brazilian sorties were not credited. The report does **not tabulate per-sortie POD values** (NOT FOUND). Stone et al. (2014, Statistical Science, p.76) state the method: USCG tables give per-leg detection probability as a function of speed, altitude, closest-approach range and visibility, cloud cover and sea state; legs are treated as independent. They then judged the search could have been ineffective "for reasons unknown to us" and set **1 − p_d(n) = 0.7 + 0.3 q(n)**, i.e. the surface-search POD for any particle is capped at 0.3. Metron 2011 (printed pp.17-18) equivalently gave the surface-search posterior a 30 % weight against 70 % for the flight-dynamics prior because it "depends heavily on estimates of currents". The AF447 surface search found the first debris on day 6 (Metron p.2).

**Empirical validation for aircraft debris.** No measured sweep width for floating aircraft debris was found (NOT FOUND). CSIRO Part IV (p.6) itself recommended field measurement of radar detection ranges on real debris; no evidence was found that this was done. The USCG R&D Center visual-detection experiments with life rafts and 16-ft boats (1979, DTIC ADA083565, abstract only) found "a more rapid degradation of sweep width ... for deteriorating environmental conditions" than the then National SAR Manual predicted. Ivić et al. (2020, Scientific Reports 10:19640, A*) replicated the JACC areas by simulation (aircraft only, 1.5 km detection radius) and detected 33.7 % of targets for drifted Area A; this is a model, not a validation.

**Obtainable and how.** NATSAR 2026: public download (AMSA). IAMSAR Vol. II Appendix N: purchase from IMO/ICAO. USCG Addendum Appendix H: public on dco.uscg.mil but blocked to automated clients; Pete can download by browser. Metron 2011: on Pete's Drive (BEA publication). Stone 2014: public (arXiv 1405.4720).

---

## Q3. Are the 2014 daily search polygons and AMSA planning data public?

**Short answer.** The **daily search-box polygons are public**: the Geoscience Australia-hosted ArcGIS feature service `Search_And_Rescue_Search_Area2014` holds 387 polygons named by incident day D11 (18 Mar) to D52 (28 Apr) (A*: count and day mapping from the earlier session). I confirmed in this session that the service description reads "Surface Search Area conducted by Australian Maritime Safety Authority (AMSA) March 17 2014 to 29 April 2014", that the only attribute fields are `FID` and `Name`, and that the copyright text is "Australian Maritime Safety Authority (AMSA)". **No licence statement** is given in the service metadata (NOT FOUND); treat it as AMSA copyright and ask AMSA for re-use permission or cite as a data source. The polygons are search boxes, not flown tracks, and carry no POD, sweep width or track spacing. Daily area, track spacing, aircraft and vessel counts, SLDMB drops and sightings are tabulated in ATSB (2017) Tables 10-18 (pp.23-33); the ATSB report is licensed under Creative Commons Attribution 3.0 Australia (copyright page). Sweep widths, flown tracks (sortie logs) and the daily POD/coverage-confidence values are **not public** (NOT FOUND). AMSA media releases and daily charts (17-28 Mar) and JACC releases (1 Apr onward) give daily areas, assets and weather; the AMSA chart images were not georeferenced and their original links now return "access denied" (A*). CSIRO's `Surface Search MH370 2014.kmz` (daily polygons) is listed in Griffin's index but no copy was found (A*); CSIRO reports are "all rights reserved" (copyright page, Parts I and IV).

| Item | Where | Status / licence | Obtainable |
|---|---|---|---|
| Daily search-box polygons, D11-D52 | services1.arcgis.com/wfNKYeHsOyaFyPw3/arcgis/rest/services/Search_And_Rescue_Search_Area2014/FeatureServer/0 | Public; © AMSA; no licence text | Public download (saved by earlier session as `ga_search_and_rescue_search_area_2014.geojson`) |
| Daily area, track spacing, assets, sightings | ATSB 2017 Tables 10-18, pp.23-33 | CC BY 3.0 AU | Public download |
| AMSA daily releases and charts, 17-28 Mar | www.amsa.gov.au/media/documents/… (Internet Archive) | Original links dead | Internet Archive; project artifact `amsa_mh370_media_2014.zip` |
| JACC daily releases, Apr-May 2014 | www.jacc.gov.au (defunct; Internet Archive) | Domain defunct | Internet Archive; project artifact `jacc_releases_2014_text.txt` |
| AMSA daily POD / coverage confidence, sweep widths, sortie tracks | AMSA JRCC internal records (ATSB p.34) | Unpublished | Request from AMSA |
| CSIRO daily-polygon kmz | marine.csiro.au/~griffin/MH370/ (index only) | Not archived | Request from CSIRO (D. Griffin) |
| CSIRO cumulative POD maps (GIF) | marine.csiro.au/~griffin/MH370/br15_pwent2d/… (Internet Archive) | © CSIRO | Internet Archive (A*) |
| ATSB animation of daily areas | ATSB YouTube channel (ATSB 2017 p.33) | Public video | Public |

---

## Q4. The 29 March 2014 RNZAF photographs discussed by Iannello (Nov 2017)

**Short answer.** The photographs were taken by a **Royal New Zealand Air Force P-3 Orion** during the AMSA-coordinated search; they were released to Independent Group member Brian Anderson after an October 2015 request, posted on Duncan Steel's website, and re-shared by Iannello as a 1 GB Dropbox zip with an Excel file of image times and positions (Iannello 2017, post text; grade C). Positions came from RNZAF follow-up answers and from image metadata extracted by Don Thompson (same post). Iannello gives these positions for 29 March: debris fields of small fragments at **28.3927°S 97.7750°E (image 5832)** and **29.19333°S 95.1250°E (image 5853)**; a suitcase-like object near 28.3176°S 97.8234°E (image 5833); a panel-with-wires-like object near 28.8867°S 96.0844°E (image 5847); and a box-like object near 29.1936°S 95.1094°E (image 5854). The earlier session's CSV of Iannello's spreadsheet holds 26 images for 29 March (07:44-09:20 UTC, 9 with positions); it lists image 5847 at 28.87167°S 96.13°E, which differs from the figure caption, so the figure caption values above should be preferred until the spreadsheet is checked. None of the objects was recovered, and Iannello's forward drift from 29.7°S on the 7th arc is consistent with the positions. Iannello reports that the ATSB "had record of the detection of some of the objects" on 29 March but "no record of the detection of the two debris fields" (second-hand, grade C). David Griffin's email of 29 Nov 2017, printed with permission in the 5 April 2018 update, says CSIRO would not comment on what the images show, that the RNZAF items "were NOT all conclusively proven NOT to be from MH370", that a single origin near 29.7-29.8°S is plausible in BRAN2015/2016, and that a strong temperature front near 29°S would collect buoyant material "MH370-related or not". **No official ATSB or CSIRO report mentions the RNZAF photographs**: I searched the ATSB 2017 text and CSIRO Parts I-IV for "RNZAF", "New Zealand", "Orion" and "29 March" with no relevant hit (NOT FOUND). For the day before, AMSA Update 25 (28 Mar 2014) says an RNZAF P-3 Orion "reported sighting a number of objects white or light in colour and a fishing buoy", relocated by a RAAF P-3 that saw "two blue/grey rectangular objects". ATSB 2017 Table 14 (p.28) lists 50 sightings on 28 Mar and 16 on 29 Mar (column assignment from text extraction; provisional).

**Obtainable and how.** Post: public, live (HTTP 200 on 17 Oct 2026). Images: Dropbox zip and Excel linked from the post (download by browser; not fetched here); Duncan Steel site did not answer. Official RNZAF originals: request from NZ Defence Force (RNZAF) or AMSA.

---

## Q5. Weather and sea state during the surface search

**Short answer.** There is **no official consolidated weather summary** for the 2014 surface search (NOT FOUND). ATSB (2017, p.34) says only that coverage confidence "was low on some days due to poor weather"; ICAO WP30 (Aug 2014, para 2.2(f), p.2) lists "Poor weather and search conditions on a number of days" among the search challenges, and para 2.2(e) notes two tropical cyclones affecting drift modelling. Day-by-day conditions are in the AMSA releases (to 28 Mar) and the JACC releases (from 1 Apr), mostly as **forecasts**, not observations. Days with no aviation search for weather: **25 Mar** (all air and sea search suspended; forecast sea state 7-8, waves up to 2 m, swell up to 4 m, gale-force winds up to 80 km/h, cloud base 200-500 ft — AMSA Update 16) and **27 Mar** (ATSB Table 12 footnote 18, "No aviation search due to weather"); **27 Apr** (air and surface search suspended, JACC mr039; ATSB Table 18 records 0 km²). JACC also announced suspension of the planned air search on **22 Apr** and **23 Apr** (mr032, mr034; ex-Tropical Cyclone Jack, heavy seas, poor visibility), but ATSB Table 18 records 31,627 km² and 32,680 km² searched on those days at 4 NM spacing, so these two days were probably partial; the sources conflict. On that count 3 to 5 of the 42 days were lost or largely lost to weather (provisional). Forecast visibility fell to 1 km on 23-26 Apr, with winds up to 35 kt and swell 3-4 m on 24 Apr.

**Table Q5. Weather statements, official releases** (forecast unless stated).

| Date (2014) | Source | Statement |
|---|---|---|
| 20 Mar | AMSA release (possible debris) | Weather moderate; "Poor visibility has been reported." |
| 21 Mar | AMSA Update 9 | Visibility "much better than on Thursday"; weather fair (observed) |
| 22 Mar | AMSA Update 10 | Good weather, visibility about 10 km, moderate seas (observed) |
| 23 Mar | AMSA Update 12 | Early sea fog in western areas, improving (observed) |
| 24 Mar | AMSA Update 13 | Expected to deteriorate, rain likely |
| 25 Mar | AMSA Update 16 | All sea and air search suspended; sea state 7-8; winds up to 80 km/h; cloud base 200-500 ft |
| 27 Mar | AMSA Update 20; ATSB Table 12 fn 18 | Expected to deteriorate; no aviation search due to weather |
| 28 Mar | AMSA Update 23 | Weather better in revised area |
| 1 Apr | JACC mr001 | Poor, areas of low visibility |
| 2 Apr | JACC mr002 / mr003 | Marginal: broken cloud, sea fog, thunderstorms / fair, ~10 km (observed) |
| 3-8 Apr | JACC mr004-mr013 | Fair to good, ~10 km or more; cloud base 1,000-2,500 ft |
| 10-16 Apr | JACC mr015-mr023 | SE winds 10-15 kt, swell 1-2 m, visibility 3-5 km in showers |
| 17-20 Apr | JACC mr025-mr029 | Isolated/scattered showers, SE winds |
| 21 Apr | JACC mr030 | Deteriorating in north as TC Jack moves south |
| 22 Apr | JACC mr031 / mr032 | Swell up to 3 m, visibility 4 km / planned air search suspended |
| 23 Apr | JACC mr033 / mr034 | Heavy rain, low cloud, swell 2.5 m, visibility 1 km / planned air search suspended |
| 24 Apr | JACC mr036 | Heavy rain, low cloud, SE winds up to 35 kt, swell 3-4 m, visibility 1 km |
| 25 Apr | JACC mr037 | SE winds up to 25 kt, swell 2-3 m, visibility 1-3 km |
| 26 Apr | JACC mr038 | SE winds up to 20 kt, swell 2-2.5 m, visibility 1-3 km |
| 27 Apr | JACC mr039 | Planned air and surface search suspended (deteriorating weather) |
| 28 Apr | JACC mr040 | Cold front clearing; swell 4-5 m |

**Obtainable and how.** Releases: Internet Archive (project artifacts). Observed metocean fields for the search days: public reanalyses (e.g. ERA5 winds and waves, satellite altimeter wave height) — not checked here; Bureau of Meteorology search-area forecasts: request from BoM/AMSA.

---

## Source list

1. ATSB (2017). *The Operational Search for MH370*, AE-2014-054, 3 Oct 2017. https://www.atsb.gov.au/media/5773565/operational-search-for-mh370_final_3oct2017.pdf — read from Drive copy https://drive.google.com/file/d/1zwSCCwXcsryJdi4kHb4WE13_9-WIb4J4/view (text extraction); pp.23-35. Grade A. CC BY 3.0 AU.
2. Griffin DA, Oke PR, Jones EM (2016). *The search for MH370 and ocean surface drift*, CSIRO EP167888. http://www.atsb.gov.au/media/5772119/mh370_ocean_driftv29.pdf — Drive copy https://drive.google.com/file/d/1JFy39Xsfjmw7-Px3yf2T-Mxzj3r5lelA/view; pp.iv, 23-25. Grade A.
3. Griffin DA, Oke PR, Jones EM (2017). Part II, EP172633. https://www.atsb.gov.au/media/5772655/mh370_ocean_driftii_final.pdf — Drive https://drive.google.com/file/d/1S-WCMaRKt0lRlV0Uv3bfVSKZvEd8TjDf/view; p.iv. Grade A (p.15-16 wording A*).
4. Griffin DA, Oke PR (2017). Part III, EP174155. https://www.atsb.gov.au/media/5773371/mh370_csiro-ocean-drift-iiil.pdf — Drive https://drive.google.com/file/d/1iwxd8kz_bvpHvXU4QYhRaF23zaG1ARiD/view; searched for RNZAF only. Grade A.
5. Griffin DA, Oke PR (2017). Part IV, EP177204, 3 Oct 2017. https://www.atsb.gov.au/sites/default/files/media/5773567/mh370_ocean_driftiv_oct2017.pdf — Drive https://drive.google.com/file/d/1P2hMQUu4Pux3rah7sYccn1bboRf83umY/view; pp.iv, 1-3, 6. Grade A.
6. Griffin D. CSIRO MH370 drift web page (entries 16 Aug 2017-10 Aug 2018). http://www.marine.csiro.au/~griffin/MH370/ — Drive print https://drive.google.com/file/d/1St61jC0TmlxsO6BztYD5vpH_mqNTTDF6/view. Grade A (official CSIRO page).
7. ATSB (2016). *MH370 - First Principles Review*, 20 Dec 2016. http://www.atsb.gov.au/media/5772107/ae2014054_final-first-principles-report.pdf (Internet Archive capture, project artifact); p.18. Grade A.
8. AMSA (2026). *National Search and Rescue Manual*, Feb 2026. https://www.amsa.gov.au/sites/default/files/2026-03/natsar-manual-2026.pdf — paras 4.3.6-4.3.58 (pp.215-223); Tables D-5:4, D-5:6, D-5:8 (pp.400-407). Grade A.
9. IMO (2025). MSC.1/Circ.1686, amendments to the IAMSAR Manual. https://www.mardep.gov.hk/filemanager/en/share/msnote/pdf/msin2532anx1.pdf — PDF pp.27, 44-45. Grade A.
10. Stone LD, Keller C, Kratzke TL, Strumpfer J (2011). *Search Analysis for the Location of the AF447 Underwater Wreckage*, Metron report to BEA. Drive https://drive.google.com/file/d/1_FpHT5nsRBMo9L2808j281wvBRKzQH9l/view; printed pp.2, 12-18. Grade A.
11. Stone LD, Keller CM, Kratzke TM, Strumpfer JP (2014). Search for the wreckage of Air France Flight AF 447. *Statistical Science* 29(1):69-80. https://doi.org/10.1214/13-STS420 — Drive https://drive.google.com/file/d/1RVOgpgVKrAC1wDarH_VRUJQGjIv6Mf1Z/view; p.76. Grade A.
12. Australia (2014). *MH370 Search and Rescue Response - JRCC Australia*, ICAO APANPIRG ATM/SG/2-WP30. Drive https://drive.google.com/file/d/1DJG-kkcV5JiofBZQFA0YCVnajIrwcIWJ/view; paras 2.2, 2.21-2.22 (pp.2, 6). Grade A.
13. AMSA media releases and charts, 17-28 Mar 2014 (Updates 1-25). Original www.amsa.gov.au/media/documents/…; Internet Archive captures (project artifact `amsa_mh370_media_2014.zip`). Grade A.
14. JACC media releases mr001-mr042, 1 Apr-2 May 2014. Original www.jacc.gov.au/media/releases/2014/… (defunct); Internet Archive captures (project artifact `jacc_releases_2014_text.txt`). Grade A.
15. Geoscience Australia / AMSA ArcGIS service. https://services1.arcgis.com/wfNKYeHsOyaFyPw3/arcgis/rest/services/Search_And_Rescue_Search_Area2014/FeatureServer/0 — metadata read this session. Grade A (geometry).
16. Iannello V (2017, updated 5 Apr 2018). Possible MH370 Debris Seen in Aerial Search in March 2014. https://mh370.radiantphysics.com/2017/11/25/possible-mh370-debris-seen-in-aerial-search-in-spring-2014/ — Drive PDF https://drive.google.com/file/d/1k1spe4FTmfO7bJfbY5we03Wl9pJeWlQn/view; pp.1-7. Grade C. Image zip: https://www.dropbox.com/s/f5y52owr8tcl3jw/2017-11-24%20Debris%20from%20RNZAF%20Surface%20Search.zip?dl=0 ; Excel: https://www.dropbox.com/s/fynm1exhhcbvger/2017-11-26%20RNZAF%20Image%20Data.xlsx?dl=0 (not downloaded).
17. USCG R&D Center (1979). Visual detection experiments, DTIC ADA083565 (abstract via search listing). https://apps.dtic.mil/sti/pdfs/ADA083565.pdf — Grade B (abstract only).
18. USCG Addendum to the US National SAR Supplement, COMDTINST M16130.2H. https://www.dco.uscg.mil/Portals/9/CG-5R/MassRescueOps/CGADD%20COMDINST%2016130_2H.pdf — 403 to automated clients. Grade B.
19. Ivić S et al. (2020). *Scientific Reports* 10:19640. https://doi.org/10.1038/s41598-020-76274-0 — Grade A* (earlier session).
20. Koopman BO (1980). *Search and Screening*. Grade B (not read).

## What is obtainable and how (one line per item)

- CSIRO POD method and wording (Parts I-IV): public download (atsb.gov.au; Drive copies).
- AMSA daily single-target POD / coverage confidence values: not published — request from AMSA JRCC.
- ATSB/FPR statements on surface-search effectiveness: public download.
- IAMSAR Appendix N sweep-width and correction tables: purchase from IMO/ICAO.
- NATSAR sweep-width and correction tables (2026): public download; 2014 edition: request from AMSA or national library deposit.
- USCG sweep-width tables (Appendix H): public, browser download (blocked to scripts).
- Measured sweep width for floating aircraft debris: not available (never measured, per search).
- AF447 Metron/Stone POD method: public (Stone 2014) / on Drive (Metron 2011); per-sortie POD values: not available.
- 2014 daily search-box polygons: public download (GA/AMSA ArcGIS); licence: not stated — request AMSA permission.
- Daily area, track spacing, assets: public (ATSB 2017 tables).
- Sortie tracks and per-aircraft sensor logs: not available publicly — request from AMSA/ADF.
- RNZAF 29 Mar 2014 photographs: public via Iannello's Dropbox links (browser); originals — request from NZDF.
- Official comment on the RNZAF photographs: not available (none found in ATSB/CSIRO reports).
- Daily weather (forecast) statements: public via Internet Archive (AMSA/JACC releases).
- Observed metocean conditions for each search day: public reanalysis download (not done here).
