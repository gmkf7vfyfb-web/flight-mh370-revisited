# Searched areas — reference ledger

Opened 9 October 2026 by the searched-areas module as deliverable 1 of its brief
(`threads/master-prompts/searched-areas.md` §7) and of the architecture entries in
`coordination/SEARCHED_AREAS.md` headed "2026-10-08 — architecture: overnight work plan" (which asked
for it) and "2026-10-09 ~00:30 UTC — architecture: start now; your sequence".

**Renamed 9 October** from `citation-ledger.md` under architecture ruling S3: this is the
**searched-areas module's** ledger, not a project-wide one. There is no separate project ledger — the
paper work merges the module ledgers. Other modules keep their own (`end-of-flight-references.md`,
`debris-drift-references.md`, and so on); `end-of-flight-references.md` still points at the old name.

**Purpose.** Every claim the paper makes about what the published work did, or did not do, in the
seabed-search line of argument is recorded here with the page on which it can be checked. A claim
that is not in this ledger is not citable.

**Convention.** Printed page numbers come from the running headers of the published object, not from
the position of the page in a PDF. Where only an author preprint is available the preprint page is
given as the primary anchor and any printed page is marked *derived*. Verbatim anchors are kept short
and in quotation marks so that a reader can find the passage; the ledger is not a substitute for the
source.

Other modules may append sections. Do not edit another module's section; add a dated correction under
it.

---

## 1. Davey, Gordon, Holland, Rutten and Williams (2016), ch. 11 "Ongoing Refinement"

*Bayesian Methods in the Search for MH370*, SpringerBriefs in Electrical and Computer Engineering,
Springer Singapore, DOI 10.1007/978-981-10-0379-0. Licence CC BY-NC 4.0 (Attribution-NonCommercial).
Chapter 11, **printed pp. 101–109** — the running headers and the Crossref record for
`10.1007/978-981-10-0379-0_11` agree on that range. Copies used: `results/davey-2016.pdf` (the full
124-page book) and the chapter PDF in the artifact store, `10.1007_978-981-10-0379-0_11.pdf`
(version `e006e598-5509-4be2-a6d4-b9652cf7a2c1`).

| ref | claim | printed page | anchor |
|---|---|---|---|
| D-1 | §11.1 is titled "Updating the Distribution Using Search Results" | 101 | section heading |
| D-2 | The search update, eq. (11.1): `p(x_final \| S, Z_K) ∝ [1 − P_D(x_final)] p(x_final \| Z_K)` | 101 | numbered equation (11.1) |
| D-3 | `P_D(x)` is defined as the probability that "the cumulative search effort would have detected the aircraft at any particular location" | 101 | sentence preceding (11.1) |
| D-4 | The aircraft is stationary, so "the prediction stage becomes degenerate" and the predicted pdf equals the previous posterior | 101 | paragraph preceding (11.1) |
| D-5 | The planning quantity, eq. (11.2): for an area `A` searched with constant `P_D`, `P(find during search of A) = P_D ∫_A p(x_final \| Z_K) dx_final` | 101 | numbered equation (11.2) |
| D-6 | AF447 is named as the precedent for the method — "This was used, for example, in the search for AF447 [40]" | 101 | §11.1, second sentence |
| D-7 | "the probability of detection for areas searched using side-scan sonar was modelled as 0.9 [40]" in the AF447 analysis | 102 | first paragraph |
| D-8 | The ρ ≈ 0 assumption: on the quality-assurance process, "it is considered highly unlikely that the search would fail to detect the aircraft if the correct location is searched" | 102 | second paragraph |
| D-9 | The same paragraph names the physical causes of non-detection on searched ground — "sensor drop-out and terrain masking" producing "small pockets" missed on a first pass — and proposes (11.1) to prioritise revisiting them | 102 | second paragraph |
| D-10 | **The update is set out and not applied.** Chapter 11 carries no search-conditioned posterior: its only figures are 11.1 and 11.2 (drifter trajectories and densities) and 11.3 (the Inmarsat posterior with and without the debris discovery). Eq. (11.1) appears twice in the chapter, at its definition and at D-9, and never with a computed result | 101–109 | whole chapter, figures 11.1–11.3 |

**D-9 matters for this module's defence of ρ.** Davey name terrain masking and sensor drop-out
explicitly, and treat them as a reason to revisit ground rather than as a probability. Our ρ is not a
disagreement with their physics; it is the same two mechanisms carried into the likelihood instead of
into search planning. The departure to record in the paper is therefore narrow and is about D-8 only.

## 2. Davey's reference [40], resolved

The brief required this to be confirmed against the book's own reference list before anything was
attributed to Stone. **Confirmed, and it is not the 2014 paper.** The book's reference list, printed
p. 114 (running header "114"; PDF page 124 of `results/davey-2016.pdf`), entry 40 reads:

> Stone LD, Keller C, Kratzke TL, Strumpfer J (2011) Search analysis for the location of the AF447
> underwater wreckage. Technical report Metron Scientific Solutions, Reston

| ref | claim | where |
|---|---|---|
| D-11 | Davey's [40] is the **2011 Metron/BEA technical report**, not Stone et al. (2014) in *Statistical Science* | Davey printed p. 114, entry 40 |
| D-12 | Stone et al. (2014) cite that same report as their own reference [10] — "Stone, L. D., Keller, C. M., Kratzke, T. M. and Strumpfer, J. P. (2011). Search Analysis for the Location of the AF447. Technical report, BEA." — so the 2014 paper is the published account, by the same four authors, of the analysis Davey cite | Stone 2014 reference list, preprint p. 11 |

**Rule that follows.** Statements D-6 and D-7 are Davey citing the 2011 technical report. The project
cites Stone et al. (2014) for the method and for the detection-probability cap, because it is the
published, peer-reviewed account and the project holds a legitimate copy of it; the 2011 report is
cited only as Davey's [40] where Davey's own attribution is being described. Never write "[40] is
Stone et al. 2014" — it is the same authors and the same analysis, not the same object.

## 3. Stone, Keller, Kratzke and Strumpfer (2014), "Search for the Wreckage of Air France Flight AF 447"

*Statistical Science* **29**(1):69–80, DOI 10.1214/13-STS420, © Institute of Mathematical Statistics
2014. Copy used: the author preprint arXiv:1405.4720v1 (19 May 2014), 12 pages, in IMS format, whose
own front matter carries the journal citation and DOI; in the artifact store as
`10.1214_13-STS420.pdf` (version `4db650ec-8042-4276-baf1-f9a748011020`). An authorised copy of the
typeset journal version was not obtained, so **preprint pages are the primary anchor**. The article
occupies twelve journal pages (69–80) and the preprint is twelve pages, so printed page = preprint
page + 68; that mapping is *derived from the page-count identity and has not been checked against the
published copy*, and any page cited that way is marked (derived).

| ref | claim | preprint page | printed (derived) | anchor |
|---|---|---|---|---|
| S-1 | The posterior is built in four steps, each accounting for an increment of unsuccessful search: §4.2 Step 1, unsuccessful surface search; §4.3 Step 2, passive acoustic search for the underwater locator beacons; §4.4 Step 3, active side-looking sonar, August 2009; §4.5 Step 4, active side-looking sonar, April–May 2010 | 8–10 | 76–78 | section headings |
| S-2 | §4.6 reports the posterior after the unsuccessful searches in steps 1–4 | 10 | 78 | section heading |
| S-3 | The detection cap and its reason: past experience is that estimates from manufacturers' specifications and operators "tend to be optimistic", so "we put a maximum of 0.9 on estimates of sensor detection probabilities" | 9 | 77 | §4.3 |
| S-4 | Beacon sensors: probability at least 0.9 of detection within 1730 m lateral range, and a combined `P_D = (1 − (0.1)²)(0.8)² + (0.9)(2(0.8)(0.2)) = 0.92` after allowing for destruction of one or both beacons | 9 | 77 | §4.3 |
| S-5 | Side-looking sonar, August 2009: "We assumed a 0.90 probability of detection in the searched region", described as a conservative subjective estimate | 9 | 77 | §4.4 |
| S-6 | Side-looking sonar, 2010: the sensors were estimated to have "achieved detection probability 0.9", on the execution of the search, the quality of the sonar records and the many small articles detected | 10 | 78 | §4.5 |
| S-7 | The update is applied as eq. (4.2): `1 − p_d(n) = 0.1` where the sample lies in the search rectangle and `1` otherwise, used in eq. (4.1) to reweight the particles | 10 | 78 | §4.4–§4.5 |

**S-7 is the structural precedent for this module's likelihood.** Stone leave a residual non-detection
probability of 0.1 on fully searched ground and apply it as a per-sample reweighting of an existing
posterior. Our `P(no detection | W) = ρ + (1 − ρ)·Π_k [1 − c_k q_k]` reduces to exactly that for a
point target, one campaign, `c = 1`, `q = 0.9`, `ρ = 0`.

## 4. ATSB (2017), *The Operational Search for MH370*

ATSB Transport Safety Report, External Aviation Investigation **AE-2014-054**, Final, 3 October 2017.
**Verified 9 October 2026** against the copy on the project Google Drive
(`operational-search-for-mh370_final_3oct2017.pdf`, 41,685,870 bytes), under architecture ruling S4
after `www.atsb.gov.au` did not respond. Printed pages are read from the running headers, which the
report prints as `› N ‹`.

| ref | claim | printed page | status |
|---|---|---|---|
| A-1 | The high-resolution sonar search "covered an area in excess of 120,000 square kilometres" | executive summary (unnumbered front matter, PDF p. 3) | **verified** |
| A-2 | Planning used "+25 NM and −25 NM from 7th arc across entire search area"; the completed underwater search area is "≈ 120,000 km²" | 76 | **verified** |
| A-3 | The outermost ("Purple") area runs "Outside 27.5 NM to 36 NM to the northwest and 25 NM to 41 NM to the southeast of the 7th arc", and is mainly deep-tow side-scan | 95 | **verified** |
| A-4 | **Figure 73**, "Coverage statistics and associated confidence of detection, using 100 m x 100 m data gap metric" | 96 | **verified that the figure is there** |
| A-5 | "'High Confidence Coverage' means a >95 per cent confidence of detection; 'Lower Confidence Coverage' means on average a 70 per cent confidence of detection" | 96 | **verified** |
| A-6 | A debris field at these depths "would be at least 100 m x 100 m and very likely to be greater than 200 m x 200 m" | 83 | **verified, and the module cited the wrong page** |
| A-7 | Testing showed "a 200 m by 200 m low lying debris field could be detected in the SSS data at an altitude of up to 200 m with a high degree of confidence", which is how long thin nadir data gaps were discounted | 89 | **verified** |
| A-8 | The per-area coverage percentages behind `q` — 97.4% rated >95%, 2.1% at 70% on average, 0.5% gaps at 0% | 96, inside Figure 73 | **NOT verified** |

**A-8, attempts to date.** The three percentages sit inside the Figure 73 image, so the Drive copy's
text extraction does not carry them, and `download_file_content` refuses a 41 MB file. Direct fetches
from `www.atsb.gov.au` (allowlisted) have now failed **five times across two sessions**: two timeouts
on 9 October (120 s and 300 s); on 10 October both published URLs returned `HTTP/2 stream reset by
server (error 0x2 INTERNAL_ERROR)`; and a forced HTTP/1.1 retry timed out after 900 s with zero bytes
received. The host accepts the connection and then delivers nothing, so this is not a protocol or
allowlist problem to work around. **Not retrieved — ask Pete:** the next useful move is a copy
of the report saved from the Drive into ~/Downloads, not another fetch. Until then `q` for Phase 2 is reported as
0.945 with the stated bound 0.940-0.945, and the limitation is carried in the methods draft.

**A-8 is the one that matters and it cannot be verified from the text.** Those three percentages are
drawn inside Figure 73, which is an image; the text extraction carries the figure's title and the
definitions of its categories (A-4, A-5) but not its numbers. The module's `q = 0.945` is derived
from them, so `q` stays flagged as inherited until someone reads the figure itself.

**A-6 corrects the module.** The module header attributed the debris-field size statement to p. 96;
it is on **p. 83**, and p. 89 carries the separate and more useful statement about what the sonar was
shown to detect. The two are different claims — how big a field is, and how big a field the sensor
could see — and the module's own detectable-target definition depends on keeping them apart.

## 5. Holland (2018), and what the ATSB actually did with the 00:19 BFOs

Ian D. Holland, "MH370 Burst Frequency Offset Analysis and Implications on Descent Rate at
End-of-Flight", Defence Science and Technology Group, **arXiv:1702.02432v3** (15 January 2018).
Verified 9 October 2026 against the arXiv copy; anchors are preprint pages.

| ref | claim | page | status |
|---|---|---|---|
| H-1 | The SDU is believed to have undergone a power outage between 00:11Z and 00:19Z, immediately preceding the last two SATCOM transmissions | 1 | **verified** |
| H-2 | End of §V: the 00:19:29Z log-on BFO was "between 17 and 136 Hz higher than it would have been if the OCXO in the SDU was in a steady state"; the 00:19:37Z log-on acknowledge was "between 17 and 130 Hz higher" | 7 | **verified** |
| H-3 | §VI bounds the **descent rate**, not the position: "Lower and upper bounds on its descent rate at this time were then derived" | 7–8 | **verified** |
| H-4 | **Hypothesis 1** — the log-on was a power interruption from fuel exhaustion and an APU reboot, so the oscillator was warming up and H-2's offsets apply. Table IV descent rates: 00:19:29Z 3,900 fpm (south) / 5,100 (north) to 13,600 / 14,800; 00:19:37Z 14,800 / 15,900 to 24,100 / 25,300 | 8–9 | **verified** |
| H-5 | **Hypothesis 2** — some other cause (software failure, loss of critical SDU input, or attitude blocking the line of sight), so no start-up drift and the BFOs are the recorded values with noise: 00:19:29Z [164, 210] Hz, 00:19:37Z [−20, 26] Hz | 9 | **verified** |
| H-6 | The downward acceleration over the 8 s between the two messages is about **0.68 g**, consistent with simulations of an uncontrolled descent | 9 | **verified** |
| H-7 | In-flight BFO error is assumed strictly bounded on [−28, +18] Hz, from all 2,501 valid in-flight BFO errors over the preceding 20 flights of 9M-MRO | 2 | **verified** |

**What this settles about the project's own BFO alternatives.** `config/integrated.toml` declares three
00:19 measurement models. Read against Holland:

- **`startup-offset` is Holland's Hypothesis 1.** Its parameters (`second_hz = [17, 130]`,
  `first_minus_second_hz = [0, 6]`) reconstruct H-2 exactly: 17–130 Hz on the acknowledge and 17–136 Hz
  on the log-on request.
- **`no-offset` is Holland's Hypothesis 2** — the recorded BFO with measurement noise and no start-up
  drift.
- **`inflated` is neither.** It is this project's declared sensitivity: independent zero-mean errors of
  34 Hz, which is (136 − 17)/√12, the standard deviation of a uniform distribution across the *width*
  of Holland's interval. It keeps the scale of his uncertainty and **drops his two structural
  assumptions — that the offset is positive, and that it is shared between the two bursts.** Holland
  asserts both.
- The log-on cause axis (`fuel-exhaustion` against `other`) is Holland's H1/H2 by another name, so
  `startup-offset` × `fuel-exhaustion` and `no-offset` × `other` are his two coherent cases; the cross
  terms are not combinations he puts forward.

**And what the ATSB used it for — which is not a position likelihood.** ATSB (2017), printed p. 101,
records that the flap-analysis report carried the summary of this work "performed by DST Group
scientists on the final two satellite transmissions", and that it "quantified the range of possible
rates of descent": **2,900 to 15,200 ft/min at the 7th arc, rising to 13,800 to 25,300 ft/min eight
seconds later**, which "ruled out a controlled unpowered glide with the intent to extend range".
Printed p. 76 records the consequence: with the flap examination and "the completion of DST Group's
BFO analysis indicating that the aircraft was probably in a high and increasing rate of descent the
SSWG recommended the search be limited to a width of **25 NM either side of the 7th arc**".

So the 00:19 BFOs entered the ATSB's search design **through the corridor width and the descent
kernel applied to DST Group's PDF**, not as a measurement likelihood reweighting positions along the
arc. No option in this project's sweep reproduces that use; the nearest analogue is the held-out
position likelihood combined with the end-of-flight module's own dynamic reach constraint.

*One discrepancy, reported not reconciled.* The ATSB's quoted rates (2,900–15,200 and
13,800–25,300 ft/min) have lower bounds about 1,000 ft/min below Holland's arXiv v3 Table IV
(3,900–14,800 and 14,800–25,300 across both tracks). The ATSB cites the November 2016 flap-analysis
report; v3 is January 2018. Quote whichever source a claim is attributed to, and do not merge them.

## 6. The 00:19 BTO treatments, and why only the R600 one is in the core set

Architecture's ruling of 10 October 2026 ~19:25 UTC, which this module applies. **These entries are
carried from that ruling and are NOT yet verified in primary form by this module** — the distinction
matters, and the ledger says so rather than implying a reading it has not made.

| ref | claim | source given | status |
|---|---|---|---|
| I-1 | The R600 log-on request BTO carries a fixed 4,600 µs offset, found from the terminal's own history; this is Inmarsat's recommended treatment | Ashton, Shuster Bruce, Colledge, Dickinson (2015), §3.3, printed pp. 7 and 16 | **cited from the ruling, not yet read here** |
| I-2 | Inmarsat states that the later log-on-sequence BTOs "should be ignored" | Ashton et al. (2015), printed p. 7 | **cited from the ruling, not yet read here** |
| D-13 | The alternative treatment — R600 BTO (σ 63 µs) with the anomalous R1200 BTO (σ 43 µs) corrected by −4 × 7,820 µs, no BFOs — is Davey's | Davey et al. (2016), Table 10.1, printed p. 88 | **cited from the ruling** |
| D-14 | The 7,820 µs correction is empirical, from logs that are not published, and its origin is not fully determined | Davey et al. (2016), printed pp. 26–27 | **cited from the ruling** |
| D-15 | 7,812.5 µs instead of 7,820 µs would shift the corrected value by about 30 µs, roughly 0.7σ | the ruling | **cited from the ruling** |
| D-16 | Under those σ values the R1200 BTO carries more weight than the R600 BTO, and the two residuals have opposite signs | Davey et al. (2016), printed p. 93 | **cited from the ruling** |

**Consequence for this module.** "00:19 R600 BTO Only" is a core option and is reported by default.
"00:19 Both BTOs (Davey)" is used only for comparisons with Davey and for the reproduction section,
and whenever it is shown it carries D-14 to D-16 as a technical footnote. This module's own derivation
of the R600-BTO-only arm (from the engine's exact decomposition of `loglik:r600/no-offset`) has been
superseded: end of flight now supplies the column, so the derivation is retired.

## 7. What this settles for the searched-areas module

1. **The method is not new, and the paper must not say it is.** Stone et al. applied search-conditioned
   Bayesian updating to AF447 and found the wreck (S-1 to S-7); Davey set out the same update for MH370
   (D-1 to D-5) and did not apply it (D-10). The defensible contribution is the application to MH370
   inside a full BTO/BFO particle-filter posterior, with a modelled seabed detection function, a
   modelled wreckage field, and four campaigns with their overlaps and disputed outlines.
2. **The ρ departure is from D-8, and is defended by S-3 and D-9.** Davey assume detection on searched
   ground is near-certain; Stone capped detection at 0.9 precisely because confident estimates had
   already proved optimistic, and Davey themselves name terrain masking and sensor drop-out as reasons
   a first pass misses ground. ρ = 0.05 is the reference case, reported with the full sweep.
3. **The reduction test is to D-2.** With ρ = 0, a point target and a single cumulative campaign the
   module must reproduce `[1 − P_D(x)]` to numerical precision.
4. **Eq. (11.2) is reported, not invented.** D-5 is the planning quantity; the module reports it for
   every residual view.

---

*Appended by: searched areas, 9 October 2026. Verification method: text extracted from the PDFs named
above; printed pages read from running headers; Davey's chapter page range cross-checked against
Crossref; Stone's journal citation read from the preprint's own front matter.*

## 8. The Ocean Infinity searches: primary sources, read 2026-10-12

Added on architecture's request of 12 October 2026 18:50Z (paper RECOMMENDATION 2). The paper module's
ledger §5 lists "OI 2018" as the single most-used uncited string in the project, 131 occurrences. These are
the sources, all three **read in primary form** on 2026-10-12 after network access to oceaninfinity.com was granted.
BibTeX in `results/seabed-search-references.bib`.

| Item | Source | Date | What this module takes from it | Grade |
|---|---|---|---|---|
| A-9 | Ocean Infinity, "Conclusion of current search for Malaysian Airlines flight MH370" | 29 May 2018 | "searched and collected high quality data from over 112,000 km2 of ocean floor" — the numerator of coverage fraction **0.889** on a 126,009.3 km2 layer | official (company statement) |
| A-10 | Ocean Infinity, "Ocean Infinity donates 120,000 square kilometres of data ... to GEBCO Seabed 2030" | 22 June 2018 | the 120,000 km2 behind the upper variant **0.952** | official (company statement) |
| A-11 | Ocean Infinity, "Conclusion of the search for Malaysian Airlines flight MH370" | 8 March 2026 | departure from the search area **23 January 2026**; 151 days at sea since 2018; "mapped more than 140,000 square kilometres of seafloor" | official (company statement) |

**Three readings, and two of them change how the layers must be described.**

1. **A-9 confirms the base coverage fraction.** 0.889 = 112,000 / 126,009.3 rests on Ocean Infinity's own
   words, and those words are "searched and collected high quality data from", which is a search claim, not a
   mapping claim. The base variant is on firm ground.
2. **A-10 is a DATA DONATION, not a searched area.** 120,000 km2 is the extent of bathymetric data given to
   GEBCO Seabed 2030. It is not area searched at a stated detection probability. That is the reason 0.952 is a
   labelled variant and not a correction to 0.889, and the reason the two are reported as a sensitivity (worth
   0.002 in Z) rather than one superseding the other. Until now this module's TOML described 0.952 only as "the
   data donation figure"; it is now sourced and the distinction is explicit.
3. **A-11's 140,000 km2 is a mapping figure and this module does not use it as coverage.** The brief is
   explicit that bathymetric mapping, planned coverage and contract areas exclude nothing. The two committed
   Ocean Infinity layers total about 133,600 km2, so the mapped figure **exceeds** them — which is exactly the
   direction in which an uncritical reading would inflate the searched area and wrongly remove probability.
   It is recorded so that nobody reaches for it. A-11 also gives **no** searched area specific to the 2025-26
   campaign, so the 7,571 km2 behind coverage fraction 0.7808 remains sourced elsewhere and unverified in
   primary form — a new open item, **A-12**.

**A-12 (open):** the 2025-26 reported survey area of 7,571 km2 and the official residual of 7,428.54 km2 are
not in Ocean Infinity's own releases as read on 2026-10-12. Locate them in primary form (Malaysian government
statement or Ocean Infinity contract reporting) or mark the 2025-26 layer's coverage fraction as unsourced.

<!-- memory-records:start (generated by registry/import_memory_records.py; do not edit by hand) -->

## External facts moved from memory (25 October 2026)

These rows are records of what project memory said about external sources. They are not verified facts unless the
status column says VERIFIED or CORRECTED, and even then the check was the memory track's check of the held source.
Status values: VERIFIED (claim found in the source), CORRECTED (claim corrected against the source; use the corrected
text), PARTIAL (part of the claim found), UNVERIFIABLE (no held copy, or the claim was not found). The last column gives
the finding of the independent verifier of 25 October 2026 where there is one. Text that names a restricted source is
withheld here; the memory export row holds it.

| mem_id | written (UTC) | memory text | status | source | method and evidence | corrected text | verifier |
|---|---|---|---|---|---|---|---|
| `mem_4bb8961ad306` | 2026-10-08 00:21 | THE SEARCHED-AREAS NOVELTY CLAIM MUST BE NARROWED OR A REVIEWER WILL CATCH IT. Stone et al. (2014), Statistical Science 29(1):69-80, already incorporated the failure of previous search phases as negative information for AF447, and classical search theory (Koopman onward) makes detection-conditioned updating textbook. The defensible claim: the method is established and was applied to AF447, but has NOT been applied to MH370 inside a full BTO/BFO particle-filter posterior with a modelled seabed detection function — AF447 had a far smaller prior region and a simpler coverage history, and nobody has carried MH370's four campaigns, their overlaps and their disputed outlines through an estimator of this kind. Cite Stone as prior art the method rests on, never as a parallel effort. | PARTIAL |  | needle snippets from held files; VERIFIED: 1 [Stone2014_StatSci.pdf, printed p. 69 (PDF p. 2), running head 'Statistical Science 2014, V] ; NOT_FOUND: 2 [Stone2014_StatSci.pdf, printed p. 69 (PDF p. 2), abstract; same text in Stone2014_StatSci.] |  |  |
| `mem_1132008635fa` | 2026-10-08 00:39 | DAVEY CH. 11 'Ongoing Refinement' VERIFIED 2026-10-08 (printed pp. 101-109, running headers; PDF in artifact store as 10.1007_978-981-10-0379-0_11.pdf, version e006e598-5509-4be2-a6d4-b9652cf7a2c1). Sec 11.1 p. 101 gives the search update p(x/S,Z) ∝ [1-P_D(x)] p(x/Z) (eq 11.1) and does NOT apply it; p. 102 cites AF447 side-scan P_D = 0.9 [their ref 40] and states it is 'highly unlikely that the search would fail to detect the aircraft if the correct location is searched' (i.e. rho ~ 0). Pete's recollection was right for searched areas. For DRIFT he was partly wrong: sec 11.2 DID perform a GDP undrogued-drifter flaperon update (eq 11.4, p. 103, 508+/-30 days) with result 'shifted very slightly to the North, but the effect is negligible' (p. 109), and declined to quantify absence of other debris because parameters 'cannot be reliably determined' (p. 103). | VERIFIED | Davey et al. 2016, Bayesian Methods in the Search for MH370 (publisher PDF /Users/pete/Downloads/davey-2016.pdf) | full source document read by session model; VERIFIED: Ch. 11 is printed pp. 101-109 [PDF pp. 113-121] ; VERIFIED: Eq. 11.1 search update, not applied [printed p. 101 (PDF p. 113)] ; VERIFIED: AF447 side-scan P_D = 0.9 [40]; 'highly unlikely that the search would fail to d [printed p. 102 (PDF p. 114)] ; VERIFIED: GDP undrogued drifter update, eq. 11.4, 508±30 days [printed p. 103 (eq. 11.4, 508 days); ±30 days in the Fig. 11.2 title, printed p. 107] |  |  |
| `mem_b7d613398c2c` | 2026-10-08 00:39 | STONE ET AL. 2014 (Statistical Science 29(1):69-80, DOI 10.1214/13-STS420, arXiv 1405.4720) saved in artifact store, version 4db650ec-8042-4276-baf1-f9a748011020. It computes the AF447 posterior in four steps each accounting for an increment of unsuccessful search, and caps sensor detection probabilities at 0.9 because manufacturer/operator estimates 'tend to be optimistic'. Davey's ref [40] still needs confirming against the book's reference list before being cited as Stone. | PARTIAL |  | needle snippets from held files; NOT_FOUND: 1 [Stone2014_StatSci.pdf, printed p. 69 (PDF p. 2); Stone2014_StatSci.txt PDF p. 1 (printed p] ; VERIFIED: 2 [Stone2014_StatSci.pdf, printed p. 76 (PDF p. 9), running head 'STONE, KELLER, KRATZKE AND ] | STONE ET AL. 2014 (Statistical Science 29(1):69-80, DOI 10.1214/13-STS420, arXiv 1405.4720) saved in artifact store, version 4db650ec-8042-4276-baf1-f9a748011020. [UNVERIFIED: the held snippets do not confirm that the AF447 posterior was computed in four steps, each accounting for an increment of unsuccessful search; the abstract (p. 69) only mentions 'two years of unsuccessful search'.] VERIFIED (p. 76): for the passive acoustic beacon search, the authors put a maximum of 0.9 on detection estimates because estimates based on manufacturers' specifications and operator estimates 'tend to be optimistic'. Davey's ref [40] still needs confirming against the book's reference list before being cited as Stone. |  |
| `mem_c43071d1047b` | 2026-10-09 05:46 | CORRECTION: the seabed-search module header attributed the ATSB debris-field size statement to p.96. It is printed p.83 ('at least 100 m x 100 m and very likely to be greater than 200 m x 200 m'); printed p.89 carries the DIFFERENT statement that a 200 m by 200 m low-lying field was shown detectable in side-scan at towfish altitudes under 200 m. Fixed in lib.rs and results/seabed-detectable-target.md. | VERIFIED |  | needle snippets from held files; VERIFIED: 1 [ART:atsb_p60_84.txt#61aec715 (ATSB 2017, AE-2014-054 extraction covering pp.60–84); printe] ; CONTRADICTED: 2 [ART:atsb_p84_98.txt#87069ebc (ATSB 2017, AE-2014-054 extraction covering pp.84–98); printe] |  | FAIL fixed: the 'correction' was wrong; ATSB 2017 printed p. 83 (debris field) and p. 89 (detection test) as the original row says. Original text restored. |
| `mem_7caf43b841c7` | 2026-10-09 05:53 | Davey's reference [40] is the 2011 Metron/BEA technical report (Stone, Keller, Kratzke, Strumpfer, 'Search analysis for the location of the AF447 underwater wreckage'), printed p.114 of the book — NOT Stone et al. 2014 Statistical Science 29(1):69-80 (was cited as [40]), which cites that same report as its own [10]. Cite Stone 2014 for the method and the 0.9 cap; cite [40] as the 2011 report only when describing Davey's own attribution. Architecture has corrected the [40] line in results/davey-ch11-alignment.md. The searched-areas ledger is results/seabed-search-references.md (renamed from results/citation-ledger.md under ruling S3 — there is no project-wide ledger; the paper work merges the module ledgers, and results/end-of-flight-references.md still points at the old name). | VERIFIED | Davey et al. 2016, Bayesian Methods in the Search for MH370 (publisher PDF /Users/pete/Downloads/davey-2016.pdf) | full source document read by session model; VERIFIED: Ref [40] is Stone, Keller, Kratzke, Strumpfer (2011), 'Search analysis for the l [printed p. 114 (PDF p. 124)] ; NOT_IN_THIS_DOC: Stone 2014 Statistical Science and ledger details [n/a] |  |  |
| `mem_5ed801596785` | 2026-10-12 19:15 | Ocean Infinity's three MH370 press releases, read in primary form 12 Oct 2026 (oceaninfinity.com allowlisted on request): (a) 29 May 2018 'Conclusion of current search' — 'searched and collected high quality data from over 112,000 km2', the numerator of the searched-areas module's coverage fraction 0.889; (b) 22 June 2018 GEBCO Seabed 2030 donation of 120,000 km2 — a DATA DONATION for bathymetric mapping, not a searched area, which is why 0.952 is a labelled variant not a correction; (c) 8 March 2026 'Conclusion of the search' — departed the search area 23 January 2026, 151 days at sea since 2018, 'mapped more than 140,000 square kilometres of seafloor'. The 140,000 is a MAPPING figure and must never be used as coverage: the two committed OI layers total about 133,600 km2, so it exceeds them. No release gives a searched area specific to the 2025-26 campaign, so the 7,571 km2 behind cover | UNVERIFIABLE |  | : ; held candidate files existed but the claims were not found in needle snippets or best-ranked full pages; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |
| `mem_ec430dd813fd` | 2026-10-17 18:32 | CSIRO's exclusion of 7th-arc latitudes north of about 33 S rested on the 2014 aerial/ship surface search (near-certain detection estimated north of ~33 S), not on drift. In this project that belongs in the searched-areas module as its own likelihood, never folded into drift. Because drift alone is flat from 26 to 31 S, the weight given to the aerial-search term largely decides between 33-36 S and further north. Paper framing: state that the drift Australian finding matches CSIRO's 2016-17 southern bound by a different method. In our model, though, a 35 S source still puts about 9 % of objects on Western Australia by mid-2016, so the 35 S window is less clean than CSIRO's. | VERIFIED |  | needle snippets from held files; VERIFIED: 1 [csiro_part2_apr2017.txt (Griffin & Oke, The search for MH370 and ocean surface drift – Par] | CSIRO's exclusion of 7th-arc latitudes north of about 33 S (strictly 32-27 S, with 34-33 S only lightly searched) rested on the 2014 aerial/ship surface search, not on drift. CSIRO said debris 'would very likely have been seen' there (Griffin & Oke 2017, Part II, p. 20). In this project that belongs in the searched-areas module as its own likelihood, never folded into drift. Because drift alone is flat from 26 to 31 S, the weight given to the aerial-search term largely decides between 33-36 S and further north. Paper framing: state that the drift Australian finding matches CSIRO's 2016-17 southern bound by a different method. In our model, though, a 35 S source still puts about 9 % of objects on Western Australia by mid-2016, so the 35 S window is less clean than CSIRO's. |  |
| `mem_397a38d13f3e` | 2026-10-17 19:42 | GA ArcGIS account services1.arcgis.com/wfNKYeHsOyaFyPw3 serves Bluefin_21_AreaSearched2014 (2 polygons, 769.3 km2 against the ATSB's 860) and MH370_Phase_2_contacts (43 points = 41 level-2 + 2 level-1, matching ATSB p.90). The AusSeabed WFS deep-tow SSS valid footprint is 104,104 km2; the GO Phoenix and DHJ WFS 'coverages' are coarse outlines, not footprints. | VERIFIED | ATSB 2017 The Operational Search for MH370 (Drive operational-search-for-mh370_final_3oct2017.pdf, text via read_file_content) | full source document read by session model; VERIFIED: ATSB Bluefin/AUV area 860 km2 [printed p. 42 (PDF p. 51)] ; VERIFIED: 41 level-2 + 2 level-1 contacts [printed p. 90 (PDF p. 99)] ; NOT_IN_THIS_DOC: GA ArcGIS / AusSeabed WFS layers and areas [n/a] |  |  |
| `mem_7013ea2c1275` | 2026-10-17 19:42 | ATSB 2017 Figure 73 (printed p.96, PDF p.105) percentages VERIFIED from the image on 17 Oct 2026, giving high/lower/gap %: Red ISA 98.7/1.1/0.2, Orange 91.5/7.8/0.7, Yellow 97.8/1.1/1.1, Purple 97.9/1.5/0.6, Combined 97.4/2.1/0.5. q=0.945 traces to EITHER the red value 0.987*0.95+0.011*0.70=0.94535 OR the combined value with gaps removed, 0.940/0.995=0.9447. The combined area-average is 0.940. Ledger artifact 28dbe9de-03c7-4ac6-9c1b-a670fc093647. | PARTIAL | ATSB 2017 The Operational Search for MH370 (Drive operational-search-for-mh370_final_3oct2017.pdf, text via read_file_content) | full source document read by session model; VERIFIED: Figure 73 is on printed p.96 (PDF p.105) [printed p. 96 (PDF p. 105)] ; NOT_FOUND: Figure 73 percentages (Red 98.7/1.1/0.2, Orange 91.5/7.8/0.7, Yellow 97.8/1.1/1. [printed p. 96 (PDF p. 105)] ; VERIFIED: High confidence >95%, lower ~70%, gaps 0% [printed p. 96 (PDF p. 105)] |  |  |
| `mem_f1622b68c060` | 2026-10-17 19:42 | OI 2025-26 is official (MOT/AAIB, 8 Mar 2026): Phase 1 25-28 Mar 2025, Phase 2 31 Dec 2025-23 Jan 2026, ~7,571 km2 surveyed. MOT 29 Jun 2026: agreement extended 1 Jul 2026-30 Jun 2027, remaining 7,428.54 km2, assets return Nov 2026-Apr 2027. CAPTION AIS shows Armada slow fixes in the outboard/SE band (OI2025A, 9,363.6 km2) and none in the inboard/NW band (OI2025B, 6,388.1 km2), so B is the inferred next area (grade C). The CAPTION layers are at trise5631.github.io/areas3.js plus track js files (domain allowlisted on request). | PARTIAL |  | needle snippets from held files; VERIFIED: 1 [mot_update_families_2026.pdf#ed004e8e, printed page not determined, PDF p. 1 (matches the ] ; NOT_FOUND: 2 [mot_extension_29jun2026.pdf#02742e37, printed page not determined, PDF p. 1 (Malay) and PD] |  |  |
| `mem_9ea5ee4e2518` | 2026-10-17 20:42 | AERIAL/SURFACE SEARCH 2014 verified (17 Oct 2026): Pete's screenshot wording 'effectively ruled out crash sites north of about 33°S but ineffectively searched latitudes south of 34°S' is the caption of CSIRO Part IV (Griffin & Oke, EP177204, 3 Oct 2017) Fig 1.1, printed p.2. The boundary differs by document: Part I and the First Principles Review say north of 32°S (not between 32°S and 25°S); ATSB 2017 p.34 says about 26–32.5°S. The method gives each daily box AMSA's single-target POD (0.1–0.2 on bad days or spacing >20 NM, often 1.0 otherwise; the values are unpublished) and combines days as POD_cum = 1 − ∏(1 − POD). Ledger artifact version 664b243f-08c2-4517-9835-6c6dffe223b7; digitised POD by latitude 85e7eb4d-5a20-42d9-9ec8-b1a95d4b6fbe. | CORRECTED |  | needle snippets from held files; CONTRADICTED: 1 [csiro-part-iii.pdf (#571717b4), printed p. 2 (footer '2 / The search for MH…'), PDF p. 8; ] ; NOT_FOUND: 2 [none (needle 'EP177204' not in held candidate files)] ; NOT_FOUND: 3 [atsb_p60_84.txt (#61aec715), printed page not determined (header shows '60' / 'Page 94'), ] | AERIAL/SURFACE SEARCH 2014: Pete's screenshot wording matches the CSIRO Part III caption (Griffin, Oke et al. 2017), Fig. 1.2 'Interpreting the surface search', printed p.2 (PDF p.8): the aerial search 'effectively ruled out crash sites north of 33°S but ineffectively searched latitudes south of 34°S'. The source has no 'about'. Not verified: that Part IV (EP177204, 3 Oct 2017) Fig 1.1 has the same caption (Part IV not held). The boundary differs by document: Part I and the First Principles Review say north of 32°S (not checked here). Not verified: ATSB 2017 p.34 giving about 26–32.5°S (the held ATSB text has only the underwater indicative area of 32.5–39.1°S). Method: each daily box gets AMSA's single-target POD (0.1–0.2 on bad days or spacing >20 NM, often 1.0 otherwise; the values are unpublished), combined as POD_cum = 1 − ∏(1 − POD). Ledger 664b243f-08c2-4517-9835-6c6dffe223b7; digi |  |
| `mem_2fce8482ae57` | 2026-10-17 20:53 | Surface-search detection evidence (17 Oct 2026 research): CSIRO Part IV Fig 1.1 p.2 says the aerial search 'effectively ruled out crash sites north of about 33S'; method = AMSA daily single-object POD per box (0.1-0.2 bad days or spacing >20 NM, 'often 1.0'), combined 1-prod(1-POD); AMSA daily POD values were never published. Digitised CSIRO cumulative POD: 0.81-0.99 at 26-33S, 0.45 at 33-34S, 0.06 at 34-35S, ~0 at 35-37S. Metron AF447 gave its surface-search posterior only 30% weight (rho ~0.7 equivalent). Ledger: aerial_surface_search_source_ledger.md v2 7520cf51. | CORRECTED |  | needle snippets from held files; CONTRADICTED: 1 [csiro-part-iii.pdf#571717b4, printed p. 2 (PDF p. 8); same text in csiro3.txt#db08617b (pr] ; NOT_FOUND: 2 [none (snippets checked: csiro_part1_dec2016_v29.txt PDF p. 1; csiro1.pdf printed p. 1)] ; CONTRADICTED: 3 [metron_af447_search_analysis.txt#9888c059, Sec. 3.3, printed page not determined (text jus] | Surface-search detection evidence (17 Oct 2026 research): CSIRO Part III Fig. 1.2 caption, printed p.2 (PDF p.8), says 'the aerial search effectively ruled out crash sites north of 33°S but ineffectively searched latitudes south of 34°S'. [UNVERIFIED, Part IV not held: method = AMSA daily single-object POD per box (0.1-0.2 bad days or spacing >20 NM, 'often 1.0'), combined 1-prod(1-POD); AMSA daily POD values never published.] Digitised CSIRO cumulative POD (project digitisation): 0.81-0.99 at 26-33S, 0.45 at 33-34S, 0.06 at 34-35S, ~0 at 35-37S. Metron AF447 report Sec. 3.3 (printed page not determined, ~PDF p.12): the prior before the surface search = 70% flight-dynamics (FD) prior + 30% reverse-drift (RD) prior. It does not give a 30% weight to a surface-search posterior. Ledger: aerial_surface_search_source_ledger.md v2 7520cf51. |  |
| `mem_63f62921d7f9` | 2026-10-17 20:53 | OFFICIAL 2014 SURFACE-SEARCH POLYGONS EXIST: Geoscience Australia ArcGIS service services1.arcgis.com/wfNKYeHsOyaFyPw3/.../Search_And_Rescue_Search_Area2014/FeatureServer/0 holds 387 polygons named by incident day D11 (18 Mar 2014) to D52 (28 Apr); day n = 7 Mar + n; D11 75,962 km2 vs AMSA 76,000. Union 1,726,495 km2, thinnest at 35-37 S. Search boxes only, no POD. Saved as ga_search_and_rescue_search_area_2014.geojson (17 Oct 2026). The same account has WideSearchArea and Generalised_Flight_Path_Probabilities. | PARTIAL | https://services1.arcgis.com/wfNKYeHsOyaFyPw3/arcgis/rest/services (+ Search_And_Rescue_Search_Area2014 FeatureServer) (fetched 25 Oct 2026, HTTP 200) | web fetch |  |  |
| `mem_bc2c86bb2dd8` | 2026-10-17 20:53 | Seabed sources (17 Oct 2026): ATSB 2017 Figure 73 (printed p.96) traced: combined 97.4% high / 2.1% lower / 0.5% gap; q=0.945 equals the red-area value or the combined value with gaps cut out; 0.940 on a gap-inclusive footprint, never both. OI 2025-26: 7,571 km2 searched + 7,428.54 km2 remaining = the 15,000 km2 contract; agreement extended to 30 Jun 2027, search can resume Nov 2026-Apr 2027 (MOT 29 Jun 2026). AIS puts 2025-26 work in CAPTION band A (outboard, 34.0-36.1S); inferred next area band B, 6,388 km2 at 33.2-35.1S. Ledger: seabed-surveys-and-searches-sources-ledger.md v2 72c935b8. | PARTIAL | ATSB 2017 The Operational Search for MH370 (Drive operational-search-for-mh370_final_3oct2017.pdf, text via read_file_content) | full source document read by session model; NOT_FOUND: Figure 73 (printed p.96) combined 97.4/2.1/0.5 [printed p. 96 (PDF p. 105)] ; NOT_IN_THIS_DOC: OI 2025-26, MOT 2026, AIS bands [n/a] |  |  |
| `mem_2a29d573585c` | 2026-10-17 20:59 | The 2014 surface search detection term most likely decides between 33–36 S and further north, and it is the weakest-supported number in the chain. The supporting figures are: - IAMSAR liferaft sweep width 2.3 NM at 12–16 NM line spacing gives about 0.10–0.17 per item per day. - Ivić et al. 2020 (Scientific Reports) replicated the search and detected 33.7% of debris items. - P(all missed) depends strongly on the number of items: about 0.005 with 10 items, about 0.35 with 2, over 5 days. Recommendation: treat it as a swept parameter, like the seabed ρ, and build it together with the northern-arc aimed proposal. | PARTIAL |  | best-ranked full pages of held files; VERIFIED: 1 [imo_msc1_circ1686.pdf (MSC.1/Circ.1686, amendments to IAMSAR Manual), Annex 2, printed p. ] ; NOT_FOUND: 2 [No snippet from Ivić et al. 2020 (Scientific Reports) provided; held file imo_msc1_circ168] |  |  |
| `mem_887d101a1307` | 2026-10-17 21:40 | Surface-search POD research file research-surface-search-pod.md (v c0bf853d-9cbe-4184-af5e-46bcb69cf11b, 17 Oct 2026). Key points: NATSAR 2026 (public AMSA PDF) stands in for paywalled IAMSAR App. N. It gives fixed-wing W_u 2.3 NM for a 4-person raft at 1000 ft with visibility >40 km, and weather factors 1.0/0.5/0.25 (rafts and boats) or 1.0/0.8/0.5 (other objects). Its Table 4-2 POD curve follows the inverse-cube law (C=1 gives 78%). Stone 2014 p.76 capped the AF447 surface-search POD at 0.3 (1-pd = 0.7+0.3q). The GA/AMSA polygon service shows copyright AMSA and carries no licence text. No official ATSB/CSIRO report mentions the RNZAF 29 Mar 2014 photos. Weather days lost: 25 and 27 Mar and 27 Apr (zero area); on 22-23 Apr JACC announced suspension but ATSB records partial areas. | PARTIAL |  | needle snippets from held files; NOT_FOUND: 1 [natsar2026.pdf, printed p. 5 (PDF p. 7) and printed p. 8 (PDF p. 10)] ; NOT_FOUND: 2 [natsar2026.pdf, printed p. 150 (PDF p. 152) and printed p. 178 (PDF p. 180)] ; VERIFIED: 3 [natsar2026.pdf, printed p. 222 (PDF p. 224)] ; NOT_FOUND: 4 [Stone2014_StatSci.pdf, printed p. 72 (PDF p. 5); Stone2014_StatSci.txt, printed page not d] |  |  |
| `mem_91afb08b1b8f` | 2026-10-18 00:49 | Haixun coverage provenance caveats for the searched-areas module. ATSB 2017 says sonobuoys covered the Haixun area, but the ATSB 2015 search-areas report lists only the Ocean Shield and Curtin-bearing areas, so treat sonobuoy coverage of the site as unconfirmed. The surface search covered the drifted Haixun report area on 13-17 Apr (ATSB 2017 Table 15, 10 n mile radius). Ocean Infinity AUV coverage near the site around 1-8 Jun 2018 is inferred only from AIS (Cole/Rupp); no official polygon exists. Echo/Tireless tracks and sonobuoy drop positions are unpublished; FOI is the route. | CORRECTED | ATSB AE-2014-054 MH370 search areas report (Drive PDF); ATSB 2017 The Operational Search for MH370 (Drive operational-search-for-mh370_final_3oct2017.pdf, text via read_file_content) | full source document read by session model; VERIFIED: ATSB 2015 search-areas report lists only the Ocean Shield and Curtin-bearing are [printed p. 13 (PDF p. 18)] ; NOT_IN_THIS_DOC: ATSB 2017 sonobuoy statement; Table 15 surface search 13-17 Apr; OI AIS inferenc [n/a] ; VERIFIED: ATSB 2017 says sonobuoys covered Haixun area [printed p. 41 (PDF p. 50)] ; CONTRADICTED: Surface search of drifted Haixun area 13-17 Apr (Table 15, 10 n mile radius) [printed p. 29 (Table 15); printed p. 32 (Table 17, PDF p. 41)] | Haixun coverage provenance caveats for the searched-areas module. ATSB 2017 (printed p. 41) says sonobuoys covered the Haixun area, but the ATSB 2015 search-areas report lists only the Ocean Shield and Curtin-bearing areas, so sonobuoy coverage of the site should be treated as unconfirmed. The surface search covered the drifted Haixun report area on 13–17 Apr (ATSB 2017 Table 15, printed p. 29). The 10 n mile radius comes from Table 17 (printed p. 32) and applies only to 13–14 Apr; 15–17 Apr are listed as 'green box D' with no radius. Ocean Infinity AUV coverage near the site around 1–8 Jun 2018 is inferred only from AIS (Cole/Rupp), and no official polygon exists. Echo/Tireless tracks and sonobuoy drop positions are unpublished; FOI is the route. |  |
| `mem_ecfdba3db991` | 2026-10-18 05:34 | Public record of the seabed searches, used when reasoning about the search term: ATSB searched about 120,000 km² from 40 S to about 33 S; Ocean Infinity has mapped more than 140,000 km² since 2018, from about 36 S to 25 S; the 2025-26 season (25-28 Mar 2025 and 31 Dec 2025-23 Jan 2026, 28 operational days) surveyed about 7,571 km² of a 15,000 km² priority area and found nothing. Malaysia extended the Ocean Infinity no-find-no-fee contract to 30 June 2027 for the remaining about 7,400 km², with work not expected to resume before November 2026. Ocean Infinity's own statement is 'it isn't where we looked'. | VERIFIED | ATSB 2017 The Operational Search for MH370 (Drive operational-search-for-mh370_final_3oct2017.pdf, text via read_file_content) | full source document read by session model; VERIFIED: ATSB searched about 120,000 km2 from 40S to about 33S [no printed folio (PDF p. 4, exec summary); printed pp. 72, 121] ; NOT_IN_THIS_DOC: Ocean Infinity 2018-2026 figures [n/a] |  |  |
| `mem_0c00f4990bcc` | 2026-10-18 13:58 | Calibration facts for the per-cell detection model. GA's 2022 Data Review re-examined about 4,900 km² of Phase 2 data and found 11 new contact sites (about 2.2 per 1,000 km², none aircraft). That is a measured imaged-and-dismissed rate (grade B, read from extracts). Metron's 2011 AF447 report used sonar POD 0.90 in high-confidence areas, 0.50 elsewhere and 0.10 on the ridge (pp. 28–34). The AF447 downward revision applied to the 2009 pinger search (beacon failure), not to sonar ratings. | VERIFIED | Metron 2011 AF447 Search Analysis (Drive PDF metron.search.analysis_01.pdf) | full source document read by session model; VERIFIED: Metron 2011 AF447 sonar POD 0.90 in high-confidence areas, 0.50 elsewhere, 0.10  [printed p. 28 (PDF p. 31); REMUS 0.90/0.10 on printed p. 34 (PDF p. 37)] ; VERIFIED: The AF447 downward revision applied to the 2009 pinger search (beacon failure),  [printed pp. 34–36 (PDF pp. 37–39)] ; NOT_IN_THIS_DOC: GA 2022 Data Review: ~4,900 km², 11 new contact sites [n/a] |  |  |
| `mem_7d5e6ede615a` | 2026-10-18 14:30 | Geoscience Australia publishes official daily polygons for the 2014 aerial and surface search. The ArcGIS layer is services1.arcgis.com/wfNKYeHsOyaFyPw3/arcgis/rest/services/Search_And_Rescue_Search_Area2014/FeatureServer/0. It holds 387 polygons named by incident day, D11 (18 Mar 2014) to D52 (28 Apr); day n = 7 Mar + n. Their union is 1,726,495 km², thinnest at 35–37 S. They are search boxes only, with no POD; AMSA's daily POD values were never published. Saved as artifact ga_search_and_rescue_search_area_2014.geojson (version a74cc2b4). | PARTIAL | https://services1.arcgis.com/wfNKYeHsOyaFyPw3/arcgis/rest/services (+ Search_And_Rescue_Search_Area2014 FeatureServer) (fetched 25 Oct 2026, HTTP 200) | web fetch |  |  |
| `mem_daaccaa6e766` | 2026-10-18 14:55 | Sources for geometry with no official polygon on the searched-areas maps. Ocean Shield TPL tracks of 4–14 Apr 2014 span about 103.8–104.25 E and 20.83–21.27 S, read off ATSB June 2014 Fig. 12 (artifact d3a5c183). Sonobuoy drop positions were never published; ATSB June 2014 p. 13 places the drops at the Ocean Shield area and along the Curtin hydrophone bearing, and each sortie covers about 3,000 km². The sea-level 7th arc is built by the lineage code of surface-search-2014-map.png: BTO 18,400 µs at 00:19:29, Inmarsat ephemeris, Perth GES, WGS84. | PARTIAL | ATSB AE-2014-054 MH370 search areas report (Drive PDF) | full source document read by session model; NOT_FOUND: Ocean Shield TPL tracks span about 103.8-104.25E, 20.83-21.27S, read off Fig. 12 [printed p. 13 (PDF p. 18)] ; VERIFIED: Sonobuoy drop positions not published; p. 13 places drops at the Ocean Shield ar [printed p. 13 (PDF p. 18)] ; VERIFIED: BTO 18,400 µs at 00:19:29; Perth GES [printed p. 55 (PDF p. 60)] ; NOT_IN_THIS_DOC: Lineage code of surface-search-2014-map.png, Inmarsat ephemeris, WGS84 [n/a] |  |  |
| `mem_010a3d654c62` | 2026-10-18 15:12 | Haixun 01 search geometry beyond the contact point (Xinhua via 12371.cn, Global Times, People's Daily, Apr 2014): 7 Apr re-check box of 144 km2 (two contact points as base, +-5 km E-W, +-6 km N-S) by Haixun 01, Dong Hai Jiu 101, naval vessels 999 and 998 and HMS Echo; 8 Apr expanded to 432 km2 (Haixun 01 west, DHJ 101 centre, 999 east, plus Echo). Chinese reports also give the 5 Apr position as 25.6 S 101.3 E, about 40 km from ATSB's 25.975 S 101.461 E. Earlier hand-held hydrophone dips from the boat had positions never published. From 30 Mar the Chinese ships' task area was 26-34 S, 91-104 E (Haixun 01, NHJ 115, DHJ 101 in the north half; four naval ships in the south half). HMS Echo covered about 6,000 sq mi listening by 14 Apr, no area published. | UNVERIFIABLE |  | : ; held candidate files existed but the claims were not found in needle snippets or best-ranked full pages; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |
| `mem_2ef51c54c7a0` | 2026-10-18 15:14 | Sonobuoy facts used on the search maps. Each RAAF AP-3C sortie carried up to 84 sonobuoys, each with a hydrophone about 300 m deep, and covered about 3,000 km² (about 60 km across). 'Dozens' were dropped around the Ocean Shield contact zone on 9 Apr 2014 (ABC). PM Abbott on 11 Apr spoke of a focused 600 km² recorder search area. At overview-map scale a 3,000 km² field is only a few millimetres, so the overview map shows sonobuoy fields at true size in an inset (19.6–27.6 S, 99.3–106.2 E) together with the pinger searches and the Haixun re-check boxes. | UNVERIFIABLE |  | : ; held candidate files existed but the claims were not found in needle snippets or best-ranked full pages; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |
| `mem_da5323a4c16a` | 2026-10-18 15:14 | Haixun 01 voyage context from community AIS notes (Wikipedia talk archive, grade C): on 24 Mar 2014 it was at about 103.4–105.7 E, 10.5–13.5 S; it was the first ship to reach the new search area on 28 Mar and was on-scene commander of the Chinese ships from 30 Mar; it left for Albany on 12 Apr and sailed back to the search area on 18 Apr. On 5 Apr Jinggangshan and Kunlunshan joined it in an area of 20–26 S, 101–104 E (Global Times). | UNVERIFIABLE |  | : ; held candidate files existed but the claims were not found in needle snippets or best-ranked full pages; searched: 729 Downloads PDFs + 658 artifact PDFs/texts (text needle search), Drive title search (97 queries), 15 named-report Drive searches |  |  |
| `mem_f2d650755bc4` | 2026-10-20 19:39 | Public record for the Ocean Infinity 2026-27 season, used for the decision-table deadline: Malaysia's Cabinet extended the no-find-no-fee contract from 1 July 2026 to 30 June 2027 to complete a remaining 7,428.54 km² of the 15,000 km² 2025-26 contract area (15,000 − 7,571 searched ≈ 7,429); vessels are expected on site between November 2026 and April 2027, with no confirmed resumption date. 'In time for November' is therefore the earliest plausible date, not a fixed one. | PARTIAL |  | needle snippets from held files; VERIFIED: 1 [mot_extension_29jun2026.pdf (Ministry of Transport media statement, 29 Jun 2026), printed ] ; NOT_FOUND: 2 [mot_extension_29jun2026.pdf, printed page not determined, PDF p. 1 (Malay) and PDF p. 2 (E] ; VERIFIED: 3 [mot_extension_29jun2026.pdf, printed page not determined, PDF p. 1 (Malay) and PDF p. 2 (E] |  |  |

<!-- memory-records:end -->
