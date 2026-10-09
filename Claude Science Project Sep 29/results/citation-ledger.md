# Project citation ledger

Opened 9 October 2026 by the searched-areas module, as deliverable 1 of its brief
(`threads/master-prompts/searched-areas.md` §7) and of the architecture entry of 8 October in
`coordination/SEARCHED_AREAS.md`.

**Purpose.** Every claim the paper makes about what the published work did, or did not do, is recorded
here with the page on which it can be checked. A claim that is not in this ledger is not citable.

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

## 4. What this settles for the searched-areas module

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
