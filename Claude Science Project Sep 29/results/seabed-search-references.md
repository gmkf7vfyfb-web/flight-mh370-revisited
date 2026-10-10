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
allowlist problem to work around. **Treat this as blocked, not as untried** — the next useful move is a copy
of the report obtained another way, not another fetch. Until then `q` for Phase 2 is reported as
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
