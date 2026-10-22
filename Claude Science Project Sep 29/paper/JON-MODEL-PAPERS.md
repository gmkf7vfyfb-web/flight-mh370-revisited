# Model papers in *The Journal of Navigation*: format evidence

Survey prepared to set a section, figure and table budget for our Bayesian particle-filter
reconstruction of MH370.

**Accessed:** 12 October 2026 (all retrievals and all CrossRef metadata queries on this date).
**Compiled by:** paper drafting and citations assistant.
**Status of this file:** evidence record. Every number below is traceable to a retrieved
source; estimates are labelled as such.

---

## 0. Coverage and shortfalls (read first)

| Item | Status |
|---|---|
| Papers found in scope | 9 retrieved in full text, from a CrossRef pool of 161 distinct *Journal of Navigation* records gathered across 26 subject queries |
| Papers read in full | 9 of 9 — all analysed below were downloaded as publisher PDFs from Cambridge Core and the text extracted |
| Anchor reference included | Yes — Ashton et al., 68(1), 1–22 |
| Particle-filter papers in the journal | 3 identified; not retrieved — ask Pete (metadata and publisher abstract only); listed in §3, excluded from the detailed table until a copy is supplied |
| Date window | Requested "last ~8 years"; 5 of the 9 are 2019 or later. Four older ones (2015, 2015, 2016, 2016) were kept because they are the only close subject or method matches in the journal — the three MH370 papers and the two Bayesian-inference papers. This is a declared departure from the date preference, made for subject fit |
| Word counts | **Approximate.** Counted from extracted PDF text between the "Introduction" heading and the reference list, so they include figure captions, table cell text and equation tokens, and exclude the abstract, keywords, end-matter declarations, references and appendices. Treat as ±10 % |
| Equation counts | Counted by recovering numbered equation tags from extracted text. Where extraction dropped a tag this is stated per paper |
| Data-availability and AI-use statements | Searched for in every full text; **none found in any of the nine**. This is a negative finding on the papers surveyed, not a statement about current journal policy |
| Unpaywall | Not reachable from this environment. Open-access status was established instead by requesting each paper's Cambridge Core landing page and testing for a free PDF link, and by `fetch_article_fulltext` |

No other reductions.

---

## 1. The nine papers, in detail

Ordered by closeness to our subject.

---

### P1 — Ashton, Shuster Bruce, Colledge and Dickinson (2015), 'The Search for MH370'

**Full reference.** Ashton, C., Shuster Bruce, A., Colledge, G. and Dickinson, M. (2015). The
Search for MH370. *The Journal of Navigation*, 68(1), 1–22. DOI 10.1017/S037346331400068X.
Published online 7 October 2014; print issue January 2015. CrossRef records the issue date as
2015; both later papers surveyed here cite it as "(2014)".

**What was obtained.** Full text (publisher PDF, 22 pages, retrieved via `fetch_article_fulltext`
from the Cambridge Core open link, 12 October 2026).

**Section structure** (headings as printed, run-in, small capitals, numbered with trailing stop):

```
1. INTRODUCTION
2. SATELLITE SYSTEM OVERVIEW
3. ARCS AND PROBABLE TRACKS
   3.1. Initial BTO Analysis
   3.2. Refined BTO Analysis
   3.3. Log-on Sequence BTO Measurements
   3.4. Initial Flight Path Reconstruction
4. FREQUENCY CALCULATION
   4.1. Theory
   4.2. Initial Results
5. REFINED FREQUENCY CALCULATION
   5.1. GES AFC Compensation
   5.2. Satellite Thermal Modelling
   5.3. Refinement of BFO Samples
   5.4. Validation of BFO Equation
   5.5. BFO Calculation Sensitivity
6. HYPOTHETICAL FLIGHT PATH RECONSTRUCTION
   6.1. Early Flight Path
   6.2. Late Flight Path
   6.3. Consolidated Flight Path
7. CONCLUSIONS
ACKNOWLEDGEMENTS
REFERENCES
```

**Approximate main-text word count.** ~7,120 words, counted from the extracted full text as
described in §0.

**Figures and tables.** 17 numbered Figures, 9 numbered Tables, in 22 printed pages. This is by
some distance the most figure-dense paper in the survey.

**Mathematics.** Only 3 numbered display equations in the whole paper. The BTO and BFO models
are given largely as named terms and described in prose and in tables of contributions, not as a
developed derivation. There is no symbol table or nomenclature list. No appendices. Sensitivity
of the BFO calculation is carried in two tables (§5.5), not algebraically.

**References in practice.** Author–date in text, e.g. "(ATSB, 2014)". The end list contains
**exactly two entries**, both agency reports with bare URLs and no access dates:
"ATSB. (2014). Australian Transport Safety Bureau (August 2014) Transport Safety Report
AE-2014-054, "MH370—definition of underwater search areas" http://…" and an equivalent entry for
the Malaysian Government data communication logs. No in-text page numbers anywhere.

**Keywords.** Three, printed as "1. MH370. 2. Air Accident. 3. Satellite Communications."

**Declarations.** Acknowledgements only. No supplementary material, no data-availability
statement, no competing-interests declaration, no AI-use declaration.

---

### P2 — Pleter, Constantinescu and Jakab (2016), 'Reconstructing the Malaysian 370 Flight Trajectory by Optimal Search'

**Full reference.** Pleter, O. T., Constantinescu, C. E. and Jakab, B. I. (2016). Reconstructing
the Malaysian 370 Flight Trajectory by Optimal Search. *The Journal of Navigation*, 69(1), 1–23.
DOI 10.1017/S0373463315000570. Published online 30 July 2015; print issue January 2016.

**What was obtained.** Full text (publisher PDF, 23 pages, 12 October 2026).

**Section structure.**

```
1. INTRODUCTION
2. MH370 FLIGHT FACTS
3. CALCULATION OF QUASI-CIRCLES
4. SOLVING TRAJECTORY EQUATIONS
   4.1. The Time to Turn Unknown (TTT)
   4.2. The Track Unknown (TK)
   4.3. The Flight Level Unknown (FL)
   4.4. The Mach Number Unknown (M)
   4.5. Assumptions for the Last Segment of the Flight
   4.6. Trajectory Equations
5. THE DYNAMIC MODEL FLIGHT SIMULATOR
6. ANALYSIS OF RESULTS
7. CONCLUSIONS
ACKNOWLEDGEMENTS
REFERENCES
```

**Approximate main-text word count.** ~8,535 words — the longest in the survey.

**Figures and tables.** 9 numbered Figures, 9 numbered Tables, in 23 printed pages.

**Mathematics.** Numbered display equations run consecutively to **(20)**; 18 of the 20 tags were
recovered directly from the extracted text, the remaining two ((11) and (16)) were lost to text
extraction but the sequence is continuous. Derivations — WGS-84 quasi-circle geometry, the speed
triangle, lift and drag — are all in the main text; there are no appendices. No nomenclature
list: symbols are defined inline at first use.

**References in practice.** Author–date in text with semicolon-separated multiple citations,
e.g. "(Ashton et al., 2014; Hradecky, 2014)", "(Boeing, 1992a)". End list is author–date with
full stop after the year. Notably this paper **does** give access dates for web sources:
"ATSB. (2014a). … Accessed 6 October 2014. http://…". No in-text page numbers.

**Keywords.** Three: "1. MH370. 2. Trajectory. 3. Search and Rescue (SAR)."

**Declarations.** Acknowledgements only. No supplementary material, data-availability,
competing-interests or AI-use statement.

---

### P3 — Lyne (2024), 'Final two MH370 communications suggest controlled eastward descent'

**Full reference.** Lyne, V. (2024). Final two MH370 communications suggest controlled eastward
descent. *The Journal of Navigation*, 77(2), 201–218. DOI 10.1017/S0373463324000262. Published
online 3 December 2024; print issue March 2024.

**What was obtained.** Full text (publisher PDF, 18 pages, 12 October 2026). `fetch_article_fulltext`
did not find an OA location for this DOI; the free PDF link was found on the Cambridge Core
landing page and downloaded directly.

**Section structure** (modern house style: sentence case, no trailing stop):

```
Abstract
1. Introduction
2. Method
3. Results
4. Discussion
5. Conclusions
Acknowledgements
Funding
Conflicts of interest
References
```

**Approximate main-text word count.** ~8,310 words.

**Figures and tables.** 8 numbered Figures, 2 numbered Tables, in 18 printed pages.

**Mathematics.** Only 2 numbered display equations. The argument is carried by geometry figures
and by numerical comparison of BFO residuals, not by algebra. No nomenclature list, no appendices.

**References in practice.** Author–date, e.g. "(Ashton et al., 2014)", "(ATSB, 2017)". End list is
author–date with full publication details and DOIs or URLs where applicable. **This paper is the
one direct precedent in the survey for citing a source with a page or locator.** Two examples,
both quoted verbatim from the retrieved PDF:

> "… could be due to the aircraft being readied for a 'very unlikely' controlled ditching (ATSB, 2017. p. 101)."

> "… could not be resolved and statistically assimilated into their horizontal flight model (Davey et al., 2016. Table 10·1)."

Neither is a direct quotation of the cited source — both are paraphrase supported by a precise
locator. Note the punctuation actually printed: a **full stop** after the year, then the locator.
The corresponding end-list entry is:

> "Davey, S., Gordon, N., Holland, I., Rutten, M. and Williams, J. (2016). Bayesian Methods in the Search for MH370. Canberra Australia: Springer Briefs in Electrical and Computer Engineering. Springer Singa[pore]."

**Keywords.** Four, semicolon-separated, lower case: "burst frequency offset; burst timing offset;
MH370; Doppler shift".

**Declarations.** Acknowledgements; "Funding. This research received no external funding.";
"Conflicts of interest. The author declares no conflict of interest." No supplementary material,
no data-availability statement, no AI-use declaration.

---

### P4 — Milner, Macabiau and Thevenon (2016), 'Bayesian Inference of GNSS Failures'

**Full reference.** Milner, C., Macabiau, C. and Thevenon, P. (2016). Bayesian Inference of GNSS
Failures. *The Journal of Navigation*, 69(2), 277–294. DOI 10.1017/S0373463315000697. Published
online 21 September 2015; print issue March 2016.

**What was obtained.** Full text (publisher PDF, 18 pages, 12 October 2026).

**Section structure.**

```
1. INTRODUCTION
2. FOUNDATIONS
   2.1. Acceptance of the Performance Standard
   2.2. Fault Tree Analysis
   2.3. Empirical Approach
3. FAILURES AND FEARED EVENTS
4. FAILURE RATE MODEL
5. BAYESIAN INFERENCE
6. FAULT HISTORY
7. NEW CONSTELLATIONS
8. DISCRETE TIME EVENTS
9. ALL EVENTS MODEL
10. CONCLUSIONS
REFERENCES
APPENDIX
```

**Approximate main-text word count.** ~5,885 words.

**Figures and tables.** 6 numbered Figures, 11 numbered Tables, in 18 printed pages — the most
table-heavy paper in the survey. The APPENDIX, which falls **after** the reference list, holds
further tables of confidence bounds for different failure counts and priors.

**Mathematics.** Numbered display equations recovered as (2)–(13); the tag for (1) was lost in
text extraction but the sequence is continuous, so **13 numbered equations** in the main text.
Priors (uniform, Albert, Jeffreys and four engineered "positive" to "highly conservative"
settings) are tabulated rather than derived. No nomenclature list. The appendix carries results,
not derivations.

**References in practice.** Author–date in text with semicolons, e.g. "(Pullen et al., 2006; Lee
and Van Dyke, 2002)", "(FAA, 2010; Blanch et al., 2013)". End list author–date; **books are cited
without page numbers**, e.g. "Box, G.E.P. and Tiao, G.C. (1973). Bayesian Inference in Statistical
Analysis. Wiley, ISBN 0-471-57428-7." and "Cox, D. R. and Isham, V. I. (1980). Point Processes.
Chapman & Hall. ISBN 0-412-21910-7." No in-text page numbers.

**Keywords.** Four: "1. Integrity. 2. GNSS Vulnerability. 3. Failure Modes and Effects Analysis.
4. Bayesian."

**Declarations.** None found — no acknowledgements, supplementary material, data-availability,
competing-interests or AI-use statement.

---

### P5 — Zhang and Gui (2015), 'A new Bayesian RAIM for Multiple Faults Detection and Exclusion in GNSS'

**Full reference.** Zhang, Q. and Gui, Q. (2015). A new Bayesian RAIM for Multiple Faults
Detection and Exclusion in GNSS. *The Journal of Navigation*, 68(3), 465–479.
DOI 10.1017/S0373463314000721. Published online 4 November 2014; print issue May 2015.

**What was obtained.** Full text (publisher PDF, 15 pages, 12 October 2026).

**Section structure.**

```
1. INTRODUCTION
2. MULTIPLE FAULTS DETECTION AND EXCLUSION BASED ON CLASSIFICATION VARIABLES
   2.1. Model and rule
   2.2. Prior distributions of the unknown parameters
3. COMPUTATION OF THE POSTERIOR PROBABILITIES
4. IMPLEMENTATION FOR MULTIPLE FAULTS DETECTION AND EXCLUSION BASED ON BAYESIAN METHODS
5. EXAMPLES AND ANALYSIS
   5.1. Example 1
   5.2. Example 2
   5.3. Example 3
6. CONCLUSIONS
ACKNOWLEDGEMENTS
REFERENCES
APPENDIX
```

**Approximate main-text word count.** ~4,670 words — the second shortest in the survey, and the
most mathematically dense per word.

**Figures and tables.** 8 numbered Figures, 3 numbered Tables, in 15 printed pages.

**Mathematics.** **23 numbered display equations**, (1)–(23), in the main text: the prior
specification, the posterior for the classification variables, and the detection rule. An APPENDIX
after the reference list carries the supporting algebra. No nomenclature list; symbols are defined
inline ("It is assumed that *n* denotes the number of visible satellites …"). The detection
algorithm is given as a flow chart (figure) with cross-references of the form "Compute the
posterior probabilities of the classification variables by Equation (23) and detect outliers by
the rule proposed in Section 2.1."

**References in practice.** Author–date, e.g. "(Koch, 1999; Gui et al., 2011)", "(Berger, 1985;
Koch, 2007)". End list author–date; **books cited without pages**, e.g. "Berger, J. O. (1985).
Statistical decision theory and Bayesian analysis. Wiley, New York." No in-text page numbers.

**Keywords.** Four: "1. RAIM. 2. Multiple satellite faults. 3. Classification variables.
4. Bayesian methods."

**Declarations.** Acknowledgements only.

---

### P6 — Mori (2019), 'Analysis of Speed Prediction Error on Oceanic Flights'

**Full reference.** Mori, R. (2019). Analysis of Speed Prediction Error on Oceanic Flights.
*The Journal of Navigation*, 72(6), 1469–1480. DOI 10.1017/S0373463319000432. Published online
31 May 2019; print issue November 2019.

**What was obtained.** Full text (publisher PDF, 12 pages, 12 October 2026).

**Section structure.**

```
1. INTRODUCTION
2. DETAILS OF SPEED PREDICTION ERROR AND DATA USED
   2.1. Definition of speed prediction error
   2.2. Possible sources of speed prediction error
   2.3. Data used for analysis
3. DATA ANALYSIS
   3.1. Distribution model
   3.2. GS error caused by wind prediction error
   3.3. Temperature error
   3.4. Mach tracking error
   3.5. Speed prediction error by ADS-C
4. DISCUSSIONS AND FURTHER ANALYSIS
   4.1. Summary of the QAR data analysis
   4.2. Data analysis of ADS-C
   4.3. Discussion
5. CONCLUSIONS
ACKNOWLEDGMENT
REFERENCES
```

**Approximate main-text word count.** ~3,920 words — the shortest in the survey, in 12 pages.

**Figures and tables.** 8 numbered Figures, 3 numbered Tables.

**Mathematics.** 10 numbered display equations, (1)–(10), all in the main text; no appendices,
no nomenclature list. The error budget is presented as a table that cross-references the equations
and sections where each term was derived — "Wind prediction error 4·78 kt (see Table 1 in Section
3.2) / Temperature error 1·29 kt (see Equation (9) in Section 3.3) / Mach tracking error 0·32 kt
(see Equation (9) in Section 3.4) / Total error √(wind² + Temp² + Mach²) 4·96 kt" — and the
independently computed ADS-C figure of 3·97 kt is set beside it as a check.

**References in practice.** Author–date, e.g. "(Nagaoka et al., 2002; Fujita, 2007; Falk, 2013)",
"(ICAO, 2017)". End list author–date; working papers to ICAO panels are cited by document number,
e.g. "ICAO SASP-WG/WHL/23, WP16." No in-text page numbers. Only 11 end-list entries.

**Keywords.** Four: "1. Flight time. 2. Estimated Time of Arrival (ETA). 3. Separation standard.
4. Wind."

**Declarations.** Acknowledgment only.

---

### P7 — Kallinen, Barry and McFadyen (2023), 'Collision risk quantification for pairs of recorded aircraft trajectories'

**Full reference.** Kallinen, V., Barry, S. and McFadyen, A. (2023). Collision risk quantification
for pairs of recorded aircraft trajectories. *The Journal of Navigation*, 76(2–3), 181–199.
DOI 10.1017/S0373463323000085. Published online 26 April 2023; print issue March 2023.

**What was obtained.** Full text (publisher PDF, 19 pages, 12 October 2026).

**Section structure.**

```
Abstract
1. Introduction
2. Background
   2.1. Intervention time model
   2.2. Aldis model
3. Model development
   3.1. Intervention model
   3.2. Aircraft position uncertainty
   3.3. Vertical overlap probability
   3.4. Degenerate cases
4. Model validation
   4.1. Classical case
   4.2. Midair collision case
   4.3. Same track case
5. Metric comparisons
6. Discussion
7. Conclusion
References
```

**Approximate main-text word count.** ~8,270 words.

**Figures and tables.** 9 numbered Figures and **no numbered Tables at all** — all results are
presented graphically.

**Mathematics.** 21 numbered display equations, using **section-decimal numbering**: (2.1)–(2.12),
(3.1)–(3.8), (5.1). This is the only paper in the survey to number equations by section. All
derivation is in the main text; there are no appendices and no nomenclature list. Existing models
(the intervention-time model and the Aldis model) are restated compactly in §2 with citations
rather than re-derived, and the paper's own contribution is developed in §3.

**References in practice.** Author–date, including the ICAO working-paper convention and
disambiguated years: "(Anderson and Lin, 1996; Anderson 2000a, 2000b, 2003, 2005)",
"(Aldis and Barry, 2015)". End list author–date; note that author initials are printed **after**
the surname without a comma, e.g. "Aldis G. and Barry S. (2015)…", "Anderson D. (2000a)…".
No in-text page numbers; cross-references within the paper are by section, e.g. "further
mathematical description in Section 3.1".

**Keywords.** Three, semicolon-separated: "risk; traffic management; aviation".

**Declarations.** None found — no acknowledgements, supplementary material, data-availability,
competing-interests or AI-use statement.

---

### P8 — Ng, Zhong, Groves and Hsu (2024), 'Grid-based 3DMA GNSS with clustering and Doppler velocity using factor graph optimisation'

**Full reference.** Ng, H.-F., Zhong, Q., Groves, P. and Hsu, L.-T. (2024). Grid-based 3DMA GNSS
with clustering and Doppler velocity using factor graph optimisation. *The Journal of Navigation*,
77(5–6), 658–676. DOI 10.1017/S0373463325000220. Published online 26 May 2025; print issue
September 2024.

**What was obtained.** Full text (publisher PDF, 19 pages, 12 October 2026).

**Section structure.**

```
Abstract
1. Introduction
2. Integrated 3DMA GNSS with clustering and velocity using FGO
   2.1. Overview of the integration on 3DMA GNSS with clustering and Doppler frequency
   2.2. Candidate sampling and integration of shadow matching and likelihood-based ranging 3DMA GNSS
   2.3. Clustering sampled candidates with a region-growing algorithm
      2.3.1. Selection of the cluster and visibility estimation
   2.4. Integration of 3DMA GNSS and Doppler velocity using factor graph optimisation (FGO)
      2.4.1. Loosely coupled
      2.4.2. Hybrid-coupled
   [2.5 — the text states "Section 2.5 discusses the operation mode of FGO" but no 2.5 heading
    was recoverable from the extracted PDF text; recorded here as an extraction gap, not as absence]
3. Experiment results and analysis
   3.1. Experiment setup
   3.2. Positioning results
      3.2.1. Static experiments
      3.2.2. Vehicular experiment
4. Conclusions and future work
Acknowledgements
Funding statement
Competing interests
References
```

**Approximate main-text word count.** ~7,800 words.

**Figures and tables.** 10 numbered Figures, 2 numbered Tables, in 19 printed pages.

**Mathematics.** 20 numbered display equations, (1)–(20), all in the main text; no appendix and
no nomenclature list. **This paper is the clearest model in the survey for handling inherited
mathematics by reference rather than restatement**: supporting equations are cited to the authors'
earlier paper by that paper's own equation numbers — "a statistical model, which can be found in
Equations (A1) and (A2) of Zhong [and Groves]…" and "Remapping of the measurement innovation …
is described by Equations (A6)–(A11) of Zhong…". The likelihood scoring surface is likewise
delegated: "The likelihood scoring surface evaluation follows the study by Zhong and Groves
(2022b)."

**References in practice.** Author–date, e.g. "(Groves, 2013a)", "(Hsu et al., 2016; Miura et al.,
2015)". End list author–date with full journal details. No in-text page numbers.

**Keywords.** Four, semicolon-separated: "3DMA GNSS; 3D building model; NLOS; Urban Canyon".

**Declarations.** "Acknowledgements." (thanking a company and an institution for hardware);
"Funding statement." (named grants); "Competing interests. The author(s) declare none."
No supplementary material, no data-availability statement, no AI-use declaration.

---

### P9 — Hörteborn and Eidem (2025), 'Probability of active navigational failures: incident analyses for use in ship-bridge allision risk models'

**Full reference.** Hörteborn, A. and Eidem, M. E. (2025). Probability of active navigational
failures: incident analyses for use in ship-bridge allision risk models. *The Journal of
Navigation*, 78(2–3), 171–189. DOI 10.1017/S0373463325101100. Published online 8 August 2025;
print issue May 2025.

Included as the most recent full paper retrieved, for current house-style evidence; its subject
(probabilistic failure rates estimated from accident, incident and AIS records) is a weaker match
to ours than P1–P8.

**What was obtained.** Full text (publisher PDF, 19 pages, 12 October 2026).

**Section structure.**

```
Abstract
1. Introduction
2. Methodology
   2.1. Lessons learnt from accidents
   2.2. Lessons learnt from incidents
   2.3. Identification based solely on AIS data
3. Results
   3.1. Accident probabilities
   3.2. Incident frequencies
   3.3. AIS-identified failure frequencies
   3.4. Failure duration
4. Discussion
   4.1. Extended analysis
5. Conclusion
Acknowledgement
Competing interests
Author contributions
References
Appendix A
```

**Approximate main-text word count.** ~7,040 words, excluding Appendix A.

**Figures and tables.** 10 numbered Figures, 4 numbered Tables.

**Mathematics.** Only 2 numbered display equations. Appendix A, placed **after** the reference
list, holds the geographic filter definitions used to extract each bridge's AIS traffic — a
reproducibility annex of criteria ("Must pass / Cannot pass / Cannot end or start in" polygons for
twelve named bridges), not derivations. No nomenclature list.

**References in practice.** Author–date, e.g. "(Rawson and Brito, 2022; Yu et al., 2020)",
"(Fujii and Shiobara, 1971; Macduff, 1974)". End list author–date with DOIs. No in-text page
numbers. Internal cross-references are by **chapter**, not section: "Chapter 3 presents a case
study … Chapter 4 discusses the findings from this paper and Chapter 5 concludes the main
findings."

**Keywords.** Four, semicolon-separated: "AIS; navigation; risk; ship collision".

**Declarations.** "Acknowledgement."; "Competing interests. The authors declare that they have no
known competing financial interests or personal relationships that could have appeared to
influence the work reported in this paper."; "Author contributions." with a CRediT-style role
list. No supplementary material, no data-availability statement, no AI-use declaration.

---

## 2. Summary table

Word counts are approximate (§0); page counts are printed pages, confirmed against each paper's
printed page range.

| # | Short reference | Vol(iss), pages | Printed pp. | Main text (approx. words) | Figs | Tables | Numbered eqns | End-list refs | Appendix |
|---|---|---|---|---|---|---|---|---|---|
| P1 | Ashton et al. (2015) | 68(1), 1–22 | 22 | ~7,120 | 17 | 9 | 3 | 2 | no |
| P2 | Pleter et al. (2016) | 69(1), 1–23 | 23 | ~8,535 | 9 | 9 | 20 | 17 | no |
| P3 | Lyne (2024) | 77(2), 201–218 | 18 | ~8,310 | 8 | 2 | 2 | 28 | no |
| P4 | Milner et al. (2016) | 69(2), 277–294 | 18 | ~5,885 | 6 | 11 | 13 | 26 | yes (tables) |
| P5 | Zhang and Gui (2015) | 68(3), 465–479 | 15 | ~4,670 | 8 | 3 | 23 | 27 | yes (algebra) |
| P6 | Mori (2019) | 72(6), 1469–1480 | 12 | ~3,920 | 8 | 3 | 10 | 11 | no |
| P7 | Kallinen et al. (2023) | 76(2–3), 181–199 | 19 | ~8,270 | 9 | 0 | 21 (section-decimal) | 34 | no |
| P8 | Ng et al. (2024) | 77(5–6), 658–676 | 19 | ~7,800 | 10 | 2 | 20 | 35 | no |
| P9 | Hörteborn and Eidem (2025) | 78(2–3), 171–189 | 19 | ~7,040 | 10 | 4 | 2 | 34 | yes (criteria) |

**Medians across the nine:** 19 printed pages; ~7,120 words of main text; 9 Figures; 3 Tables;
13 numbered equations; 27 end-list references.
**Ranges:** 12–23 pages; ~3,920–8,535 words; 6–17 Figures; 0–11 Tables; 2–23 equations;
2–35 references.

---

## 3. Particle-filter papers in the journal — metadata only

A title search of the journal for "particle filter" returned the following recent papers. The
three are not retrieved — ask Pete; the Cambridge Core landing pages carry no free PDF link and
`fetch_article_fulltext` found no open-access location. **Only the metadata and publisher
abstract were read; nothing about their internal structure is reported here.**

- Gu, Y., Song, Q., Li, Y. and Ma, M. (2015). Foot-mounted Pedestrian Navigation based on Particle
  Filter with an Adaptive Weight Updating Strategy. *The Journal of Navigation*, 68(1), 23–38.
  DOI 10.1017/S0373463314000496. Metadata only (CrossRef, 12 October 2026).
- Li, X., Gao, W. and Zhang, J. (2020). A Novel Hybrid Unscented Particle Filter based on Firefly
  Algorithm for Tightly-Coupled Stereo Visual-Inertial Vehicle Positioning. *The Journal of
  Navigation*, 73(3), 613–627. DOI 10.1017/S0373463319000845. Publisher abstract and metadata only.
- Shang, R., Meng, X., Gao, C., Pan, S., Gao, W. and Peng, Z. (2020). Particle Filter-Based
  Inter-System Positioning Model for Non-Overlapping Frequency Code Division Multiple Access
  Systems. *The Journal of Navigation*, 73(4), 953–970. DOI 10.1017/S0373463320000077. Publisher
  abstract and metadata only.

Two further observations from the search itself, which bear on our Introduction:

- A CrossRef title search of the journal returns **only two papers with "MH370" in the title**
  (P1 and P3) and one with "Malaysian 370" (P2). The journal has published very little on this
  subject, which is favourable to our novelty case.
- **No paper in the journal was found that applies a particle filter to aircraft trajectory
  reconstruction or to search-area estimation.** The three particle-filter papers above are all
  terrestrial or vehicular positioning. This is a negative finding from the 26 CrossRef queries
  run on 12 October 2026 and is bounded by those queries, not a proof of absence.

---

## 4. Synthesis

### 4.1 What a paper in this journal actually looks like, against the stated guidance

The stated guidance is 6,000–8,000 words on average and up to 20 pages including figures and
tables. Practice in the nine papers surveyed matches that closely, with two qualifications.

The median is **19 printed pages and ~7,120 words of main text**, squarely inside both limits.
Seven of the nine are at or under 19 pages. Only the two early MH370 papers exceed 20 pages —
P1 at 22 and P2 at 23 — and both of those are 2015/2016, from before the current rules as we
verified them. **Every paper from 2019 onward in this survey is 19 pages or fewer.** Word counts
sit between ~3,920 and ~8,535; the four most recent papers cluster at ~7,000–8,300 words, i.e. at
the upper end of the 6,000–8,000 band rather than the middle.

Figures are the dominant use of page space: the median is **9 Figures and 3 Tables**. The figure
count is remarkably stable — seven of the nine have 8, 9 or 10 Figures, the exceptions being P1
(17) and P4 (6). Table counts vary far more
(0 to 11) and appear to be a style choice: P7 uses none at all and presents everything
graphically, while P4 uses 11 tables and only 6 figures. Taking the median of 9 figures plus 3
tables as a working planning figure, a paper can expect to spend roughly 5 to 7 of its 19 or 20
pages on display items.

Reference lists are short by the standards of many journals: median 27 entries, range 2 to 35.
None of the nine exceeds 35. The reference list occupies roughly 1 to 1·5 printed pages in the
modern two-column-equivalent layout, and on the evidence here it is printed within the paper's own
page range, so it consumes part of the page budget.

**Planning implication for us:** budget 19 printed pages, ~7,500 words of main text, 9 figures,
3 tables and no more than about 35 references. If we need more than that, the precedent for
exceeding 20 pages is a decade old and is not a safe basis.

### 4.2 How heavy mathematics is handled within that length

Three distinct strategies are visible, and they are not mutually exclusive.

**First, compress by reference to prior work.** This is the strongest and most directly applicable
precedent, and P8 (Ng et al., 2024) is the model. Rather than restating the likelihood-scoring and
innovation-remapping machinery it inherits, it cites the originating paper *by that paper's own
equation numbers* — "can be found in Equations (A1) and (A2) of Zhong…", "described by Equations
(A6)–(A11) of Zhong…" — and states plainly that "The likelihood scoring surface evaluation follows
the study by Zhong and Groves (2022b)." P7 does the same thing at a coarser grain, restating the
Aldis and intervention-time models compactly in a §2 "Background" with citations, then spending §3
entirely on its own contribution. This is precisely the structure our one-paper scope needs: a
short Background that points at Davey et al. and Ashton et al., and a Methodology that develops
only what we changed or added.

**Second, use appendices — but for supporting algebra and reproducibility criteria, not for the
core argument.** Three of the nine have appendices, all printed *after* the reference list: P5 for
supporting algebra, P4 for additional result tables, P9 for the geographic filter definitions.
None moves the paper's central derivation out of the main text.

**Third, accept that the main text carries the equations, and keep the count moderate.** The
median is 13 numbered display equations and the maximum in any paper surveyed is 23 (P5, in a
15-page paper). There is no correlation in this sample between equation count and length: P5 has
23 equations in ~4,670 words, while P3 has 2 equations in ~8,310 words. Papers that are heavy on
algebra buy the space by having fewer figures and shorter prose, not by growing.

Two practices worth copying. **Numbering by section** — P7's (2.1)–(2.12), (3.1)–(3.8), (5.1) — is
accepted by the journal and makes a long methods section navigable; it is the minority style but
it exists in a recent paper. And **the cross-referencing error budget** of P6, where a results
table names the equation and section that produced each term (" … 1·29 kt (see Equation (9) in
Section 3.3)"), is an efficient way to tie numbers to derivations without repeating them.

**Not one of the nine papers has a nomenclature list or symbol table.** Every one defines symbols
inline at first use. If we want a symbol table, we should expect it to be unusual for this journal
and should budget for it being cut.

### 4.3 Citing a book with page numbers in the text

Our convention wants printed-page precision for Davey et al. (2016). The journal's Harvard style,
as verified, admits an in-text page only for a direct quotation. The practice evidence is as
follows.

**Eight of the nine papers use no in-text page numbers at all.** Books appear in the end list with
publisher and sometimes ISBN, and never with page ranges: "Box, G.E.P. and Tiao, G.C. (1973).
Bayesian Inference in Statistical Analysis. Wiley, ISBN 0-471-57428-7." (P4); "Berger, J. O.
(1985). Statistical decision theory and Bayesian analysis. Wiley, New York." (P5).

**P3 (Lyne, 2024) is the exception, and it is the most useful precedent we have**, because it
cites the Davey book itself, in this journal, recently, with a locator, and *without* a direct
quotation:

- "(Davey et al., 2016. Table 10·1)" — a table locator in a book, supporting a paraphrase of what
  the Davey Bayesian model did with the log-on exchange BFOs.
- "(ATSB, 2017. p. 101)" — a page locator in an agency report, supporting a paraphrase.

So in-text locators for paraphrase are not only tolerated by this journal, they have been printed
for the Davey book specifically. Two cautions. The printed punctuation is "(Author, YEAR. locator)"
with a full stop after the year, which is not the usual Harvard comma; whether that is house style
or an unchallenged author habit cannot be determined from a single paper. And it is a single
instance against eight papers that use no locators at all, so we should expect a copy editor to
query it.

**Recommended approach, on this evidence:** use in-text locators sparingly and only where the
precision does work — where we attribute a specific model element, table or assumption to a
specific place in Davey et al. — and follow the P3 pattern, which is already in print in this
journal. Carry the full printed-page record in our own ledger regardless, and be prepared to
convert locators to prose ("Davey et al. (2016) set out the branching resampler in their Chapter
8") if the journal objects.

### 4.4 Simulation-based versus experimentally supported results

The journal's statement that papers verified only by simulation are judged less favourably than
those with extensive experimentation is visibly reflected in what these papers do. None of the
nine rests on synthetic data alone. Four distinct ways of satisfying it appear.

**Validate against real recorded operational data.** P6 (Mori) is built entirely on Quick Access
Recorder data and ADS-C reports from real oceanic flights — the words "simulation" and "Monte
Carlo" do not occur in it — and it cross-checks its QAR-derived error budget (4·96 kt) against an
independently computed ADS-C figure (3·97 kt). P8 (Ng et al.) runs static and vehicular field
trials in the City of London with a reference system, and the word "experiment" occurs 25 times
against 3 occurrences of "simulat". P9 uses recorded accident, incident and AIS records. P7 uses
recorded aircraft trajectory pairs.

**Validate the model against previously published models and against known cases.** P7 devotes a
whole numbered section — §4 Model validation, with three subsections: Classical case, Midair
collision case, Same track case — to reproducing established results before presenting new ones.
This is a structural commitment of roughly four pages to validation.

**Validate the measurement model against independent observations of the same quantity.** P1
(Ashton et al.) is the closest precedent to our situation, because it too is a one-off event with
no possibility of a controlled experiment. It does three things: it devotes §5.4 to "Validation of
BFO Equation" by applying the technique to previous flights of the same aircraft; it devotes §5.5
to BFO calculation sensitivity, presented in two tables; and the word "validat" occurs 6 times and
"sensitivity" 8 times, while "simulat" occurs not at all. The paper's verification is entirely
calibration against independent measured data plus sensitivity analysis.

**Where simulation is the method, say so and anchor it in measured inputs.** P2 (Pleter et al.)
uses a dynamic model flight simulator (§5; "simulat" occurs 30 times) but anchors it in the
published Inmarsat log, the real wind field for the day, published Boeing 777-200ER performance
data and the WGS-84 ellipsoid, and compares its result with other published analyses. P3 (Lyne)
similarly presents simulated flight tracks but the evidential weight is on re-analysis of the
recorded BFO values.

**Implication for us.** Our reconstruction cannot be experimentally verified in the ordinary
sense; neither could Ashton et al.'s, and the journal published it. The precedent says we should
present, as first-class numbered content rather than as remarks: (i) the reproduction of Davey
et al. as a validation of the implementation against a published result; (ii) validation of each
measurement model against independent data where any exists; (iii) explicit sensitivity analysis,
tabulated, as P1 did for BFO; and (iv) honest statement of what is simulated and what is measured.
P7's dedicated §4 "Model validation" with named cases is a good structural model for presenting
the Davey reproduction, and P1's §5.4/§5.5 pairing of validation and sensitivity is a good model
within a methods section.

---

## 5. Method and provenance

- **Candidate discovery.** 26 CrossRef queries against `https://api.crossref.org/works` filtered
  to `issn:0373-4633` (*The Journal of Navigation*, print ISSN) on 12 October 2026, using both
  `query.bibliographic` and `query.title`, across the subject areas named in the brief. 161
  distinct journal records were pooled.
- **Open-access screening.** `api.unpaywall.org` is not reachable from this environment. Each
  candidate's Cambridge Core landing page
  (`https://www.cambridge.org/core/product/identifier/<SUFFIX>/type/journal_article`) was requested
  instead and tested for a free PDF link; 31 of the 109 candidates probed carried one.
- **Retrieval.** P1, P2 and P4 were retrieved via `fetch_article_fulltext` (Unpaywall-brokered,
  Cambridge Core PDFs). P3 and P5–P9 were downloaded directly from the free PDF links found on
  their Cambridge Core landing pages. All on 12 October 2026.
- **Text analysis.** Text extracted with `pypdfium2`. Headings recovered by regular-expression
  scan for the journal's numbering conventions and verified by targeted search where the first
  pass left gaps; the one unrecovered heading (P8 §2.5) is flagged in place. Word counts taken
  between the Introduction heading and the final "References"/"REFERENCES" heading of the
  extracted text, after removing running headers and footers. Equation counts recovered from
  numbered tags in both the modern `(n)` and the older Cambridge ligature `ðnÞ` encodings, and
  from section-decimal `(n.m)` tags for P7.
- **Bibliographic details.** Volume, issue, page range, author lists and print/online dates taken
  from CrossRef work records retrieved individually on 12 October 2026, and cross-checked against
  the printed page ranges in the PDFs (all nine matched).
