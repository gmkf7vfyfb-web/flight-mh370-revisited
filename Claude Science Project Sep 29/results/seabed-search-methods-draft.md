# Methods draft — the seabed searches as disconfirming evidence

Searched-areas module, 10 October 2026. A first draft of the paper's methods text for this module,
written against `results/seabed-search-references.md`; reference tags (D-n, S-n, A-n, H-n) are that
ledger's, and every printed page cited here has been read in primary form unless the ledger says
otherwise. **Draft, not a submission.** Numbers are labelled with the run that produced them.

---

## 1. What is claimed, and what is not

Three seabed search campaigns looked for the wreck of MH370 and did not find it. Each is an
observation: the aircraft was looked for, in a known place, with a sensor of known capability, and was
not seen. We treat non-detection as a likelihood on impact position and compose it with the other
evidence in the usual way.

**The method is not new.** Stone, Keller, Kratzke and Strumpfer applied exactly this construction to
AF447, building the posterior in four steps, one per increment of unsuccessful search (S-1, S-2).
Davey, Gordon, Holland, Rutten and Williams set it out for MH370 in chapter 11 of *Bayesian Methods in
the Search for MH370*, as equation (11.1)

  p(x_final | S, Z_K) ∝ [1 − P_D(x_final)] p(x_final | Z_K)

with P_D the probability that "the cumulative search effort would have detected the aircraft at any
particular location" (D-2, D-3), and named AF447 as the precedent (D-6). They do not apply it: chapter
11 carries no search-conditioned posterior, and (11.1) appears twice without a computed result (D-10).

**What is new here is the application to MH370**, at the scale of the completed search, with coverage
measured from the released sonar data rather than from display geometry, and with the detection
probability made conditional on data being present.

## 2. The non-detection likelihood

### 2.1 The detection event

Let *y* be the impact position and *W* the wreckage field it produces. Detection by campaign *k* is a
two-part event:

1. **the field is of a detectable class** — not buried, not inside terrain shadow, not so disaggregated
   that no piece returns a recognisable signature. This is a property of the wreck and the seabed, not
   of the campaign, and it is therefore **shared** between campaigns;
2. **given a detectable field, campaign k recognises it** — its sensor passed over the field, recorded
   valid data, and the data were interpreted correctly. This is a property of the campaign.

Writing ρ for the probability that the field is of the undetectable class, c_k(y) for the fraction of
the ground around *y* on which campaign *k* holds valid data, g_k(W) for the size response of its
sensor, and q_k for the probability of recognition given detectable data over the field,

  **P(no find | y) = ρ + (1 − ρ) ∏_k [1 − c_k(y) g_k(W) q_k]**                              (1)

and the module returns ln P(no find | y) as one column on the shared impact samples.

Recognition is treated at **campaign level, not per piece**: the event is "this campaign found the
wreck", and a campaign that images any recognisable part of the field has found it. Treating
recognition per piece and multiplying would make a larger field *harder* to find, which is wrong.

### 2.2 Why ρ is a separate term, and what it absorbs

ρ is the model error of the coverage layers. Without it a cell with data is ruled out to within 1 − q,
and a single raster error would veto a region on evidence the data cannot carry. Davey argue for ρ ≈ 0
on the quality-assurance grounds that "it is considered highly unlikely that the search would fail to
detect the aircraft if the correct location is searched" (D-8) — but the same paragraph names the
physical mechanisms, "sensor drop-out and terrain masking" producing small pockets missed on a first
pass, and proposes (11.1) as the way to prioritise revisiting them (D-9). ρ is those mechanisms moved
from the search plan into the likelihood. We take ρ = 0.05 as the reference and report a sweep over
{0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5}.

Because (1) is linear in ρ and in each q_k, an uncertain ρ or q_k with independent priors enters only
through its mean: the spread does not move the estimate, and no stratification over it is needed. This
is exact for the shared two-state model of §2.1 and **false** for a model in which campaigns re-roll
detectability independently, where averaging over a prior on ρ and evaluating at its mean differ
(0.1552 against 0.1296 in the module's own test case). The module therefore states which model it is
using wherever the mean-only property is relied on.

### 2.3 Dependence between campaigns

The product in (1) is over campaigns and runs on the **shared** model by default: a second campaign
over the same ground is a fresh chance to recognise a *detectable* field, not a fresh chance for the
field to be detectable. The alternative — independent misses, in which each campaign re-rolls
detectability — is available and reported as a labelled sensitivity.

This matters only where campaigns overlap, and the overlap is substantial: the ATSB Phase 2 union
hides **17,390.6 km² of repeat coverage over 18,129.6 km² of ground**, so 15.0% of the searched ground
was swept more than once (`results/seabed-repeat-search-dependence.md`). On the fixture, treating
Phase 2 as one union campaign gives evidence Z = 0.4040; splitting it into its four sensors with shared
misses gives 0.4001, and with independent misses 0.3966. The main estimate uses the union, which is
the conservative end (maximal dependence), with the split reported as a sensitivity.

### 2.4 Reduction to Davey (11.1)

For a point target (g_k ≡ 1), a single campaign, and ρ = 0, (1) becomes

  P(no find | y) = 1 − c(y) q = 1 − P_D(y),

which is exactly the factor in Davey's (11.1). This reduction is a module test
(`reduces_to_davey_eq_11_1_for_a_point_target_one_campaign_and_rho_zero`) and is the sense in which
the construction here is the published one with the coverage and detectability terms made explicit.

## 3. Coverage layers

Coverage is a 0.01° raster per campaign, read by bilinear interpolation between cell centres, so
c_k(y) is the covered fraction within about 1 km of *y*. Outside a raster c_k = 0: nobody searched
there.

| layer | area (authalic sphere) | source | q |
|---|---|---|---|
| ATSB Phase 2, 2014–2017 (union) | **120,486.5 km²** | the valid 5 m pixels of Geoscience Australia's four backscatter mosaics: deep-tow side-scan 103,921.5, GO Phoenix SAS 14,627.3, Dong Hai Jiu SAS 3,164.3, AUV side-scan 16,164.1 km² | 0.945 |
| Bluefin-21 / Phoenix *Artemis*, 2014 | 771.41 km² | GA's two display polygons | 0.900 |
| Ocean Infinity 2018 | 126,009.3 km² (traced outline less Phase 2 ground) | **inferred**, community tracing, grade C | 0.900 × coverage fraction 0.889–0.952 |
| Ocean Infinity 2025–26 | outboard band 9,696.9 km² | **inferred**, community tracing, grade C | 0.900 × coverage fraction 0.7808 |

The Phase 2 total is consistent with the ATSB's "in excess of 120,000 square kilometres" (A-1), and the
deep-tow pixel count agrees with GA's own vector L0 footprint (103,925 km²) to within 100 km².

**Only the ATSB layers enter the main estimate.** Ocean Infinity has released no survey geometry for
either of its campaigns; both layers are community tracings of published imagery and vessel tracks,
graded C, and are reported as separately labelled variants that are never merged into the ATSB-only
estimate. Every use carries the footnote in `coverage/PROVENANCE.md`.

Three things are deliberately excluded. **Bathymetric mapping is not search coverage** — the 2014–15
survey was not looking for debris and could not have detected it. **Planned coverage and contract areas
exclude nothing**: the 2025–26 contract area of about 15,840 km² is not searched ground, and the
reported 7,571 km² of survey is placed on the outboard band alone, which is what both the community
vessel tracks and the official 7,428.54 km² residual indicate. **The 2014 surface search belongs to
ocean drift**, not here: its likelihood is a function of the drifted debris field, not of impact
position.

## 4. Parameters and where they come from

| symbol | value | source |
|---|---|---|
| q, Phase 2 | 0.945 | ATSB Figure 73 (A-4): 97.4% of the area rated >95% confidence of detection, 2.1% at 70% on average, 0.5% data gaps at 0%. Gaps are already holes in the raster (c = 0), so the conditional value is (0.974 × 0.95 + 0.021 × 0.70)/0.995 = 0.945. The figure's definitions of the two confidence bands are verified (A-5); **the three percentages are read from inside the figure image and are not yet verified in primary form (A-8)**. The conditional value lies between 0.940 and 0.945 because the ATSB also rated terrain-avoidance gaps that hold some data at 0%. |
| q, Bluefin-21 | 0.900 | not assessed by the ATSB; Stone et al.'s cap, adopted because estimates from specifications and operators "tend to be optimistic" (S-3), and the value they used for side-looking sonar in both AF447 phases (S-5, S-6) |
| q, Ocean Infinity | 0.900 | as above; no published assessment exists |
| ρ | 0.05 reference, swept 0–0.5 | no published value. Davey argue ρ ≈ 0 (D-8) while naming the mechanisms it represents (D-9) |
| planning P_D for equation (11.2) | 0.9 | Stone et al.'s cap (S-3), for ground not yet searched; **not** the module's own q |
| coverage resolution | 0.01° | ≈1.1 km in latitude |

A note on the 0.9 that recurs: Stone et al. set it as a **ceiling on claimed sensor performance**
(S-3), and applied it as 1 − p_d = 0.1 inside searched rectangles (S-7). Davey quote the same 0.9 for
AF447 side-scan (D-7). It is used here only where no measured assessment exists, never in place of the
ATSB's own coverage statistics.

## 5. Composition

The module returns **one log-likelihood column on the shared impact samples**. It does not produce a
posterior. The residual PDF — the impact distribution reweighted by non-detection — is a *composer*
view, formed downstream, and the module never ingests a posterior that already contains its own
likelihood; the map script refuses to run on a sample set whose columns include `seabed-search:`.

The likelihood is on an **absolute scale**: it is the probability of the observed outcome, not a
relative weight, so the evidence Z = Σ w·P(no find) is the share of probability that survives the
searches and 1 − Z is the share they remove.

Where the wreckage field is drawn by the settling module, **alternative settling draws are alternative
outcomes**: their non-detection probabilities are averaged, never multiplied. Multiplying would treat
one wreck as many.

## 6. What is reported

1. **Evidence.** Z and 1 − Z per 00:19 data option, with the ρ sweep.
2. **Mass on searched ground.** Σ w·c_k before and after, per campaign.
3. **Residual views.** The impact PDF before and after, as 50/90/99% highest-posterior-density bands.
4. **Planning, Davey equation (11.2).** For an area A searched at constant P_D,
   P(find during search of A) = P_D ∫_A p(x | Z_K) dx (D-5). Reported as the cumulative
   P(find)-against-area curve over 0.5° candidate blocks ranked by residual mass, at a planning
   P_D = 0.9 — never as a top-N list, because block ordering needs far more samples than the aggregate
   evidence does.

On the reference-289 full-scale impacts (4 seeds × 3.2 × 10⁶, 289.7° prior track, 00:19 held out),
29.7% of the impact mass lies on Phase 2 coverage; Phase 2 removes 0.2805 of it at ρ = 0, Ocean
Infinity 2018 alone 0.0400, the two together 0.3202, and **Z = 0.7335 at ρ = 0.05**. On the residual,
P(find) = 25% needs the best 21 blocks and 51,977 km², 50% needs 62 blocks and 152,587 km², and 75%
needs 231 blocks and 580,334 km². Under `+alive` the same curve reads 24 blocks / 59,005 km²,
70 / 171,921 and 248 / 623,095 — about 13% more area, the same widening the residual views show.
The cumulative curve is the reportable object: a 0.5° block holds about 1.5% of the residual mass, so
block *ordering* is far less resolved than the curve, and no plan should be drawn from a ranking.

### The uncertainty budget

Measured at full scale on the held-out arm under `+alive` (`results/seabed-search-289-fullscale-alive/`),
in descending order of what each assumption is worth in the evidence Z:

| assumption | range tried | worth in Z | has a published value? |
|---|---|---|---|
| ρ, the undetectable fraction | 0 to 0.5 | 0.7059 to 0.8529 | **no** |
| Ocean Infinity 2018 included | in / out | 0.034–0.037 | the layer is a grade-C tracing |
| what counts as a detection | field fraction / any element | 0.023 | **no**; not resolvable from coverage data |
| q for Phase 2 | 0.90 to 0.98 | 0.023 | yes, ATSB Figure 73 (unverified, A-8) |
| repeat-search dependence | shared / independent | 0.002 | **no**; reported as a bracket |
| field model | point target / settled field | 0.0003 | measured against settling's fields |
| *upstream: which core run supplies the prior* | (a) against (b) | **not yet propagated** | — |

The last row is a placeholder and is marked as one. Core's one-engine variant (a) moves the source
posterior's 00:19 median to −36.89 against (b)'s −37.15, a shift of 0.26° — larger than this module's
`+alive` term (0.05°) and larger than the Ocean Infinity 2018 layer (0.17°). **What that is worth in
the evidence Z is unknown**, because this module has run on neither: the shift is in the prior, and a
shift along the arc moves probability through searched and unsearched ground in a way that cannot be
read off a median. It is listed so that the budget is not mistaken for complete, and it will be filled
in from the re-runs rather than estimated. Both core runs additionally carry a fuel defect — the
one-engine phase is about half its true length, because internal-v1's live-engine flow is twice its
source tables — so neither figure is final.

Two things follow for the paper. **The quantity that dominates has no published value**: ρ spans more
of the evidence than every measured input combined, and what it really controls is the share of
probability left *on searched ground*, 0.027 at ρ = 0 against 0.194 at ρ = 0.5 — the number a revisit
plan would use. And **the unverified Figure 73 percentages matter less than that**: the whole range
from Stone et al.'s 0.90 cap to an optimistic 0.98 is worth 0.023, so A-8 bounds a smaller quantity
than the one the analysis is most exposed to.

**A non-detection is not a localisation.** The searches remove a contiguous block from the middle of
the corridor and leave the ring, so the residual is usually *wider* than the input: the median moves
0.20° north, from −36.78 to −36.58, and the 90% region grows. Any statement of the form "the search
narrows the search" should be checked against this.

## 7. Convergence

Every result is reported with the effective sample size that supports it, and anything below 1,000
effective impacts is reported as unconverged, not as a result. This matters most where the 00:19
interpretation is sharp: on the reference-289 run, the arms that score both 00:19 bursts fall to 8–82
effective impacts out of 12.8 × 10⁶, and their areas and medians are not estimable. That limit sits in
the 00:11 hand-off, not in this module: of 100,000 cruise-posterior states per seed, about ten can
produce the 00:19 pair at all. The module's own likelihood is converged throughout (split-half 0.968
on the held-out arm after the search evidence).

## 8. Limitations

1. **The point target is measured, not assumed.** `g_k` is implemented
   (`results/seabed-size-response.md`) and saturates: a field of 40 pieces between 0.5 and 8.3 m long
   and 0.1 to 2.05 m proud gives `g_k` within 10⁻⁹ of 1, and it takes fragments about 0.12 m long and
   0.02 m proud to push it below 0.5 — three orders of magnitude below anything an aircraft breakup
   produces. Reading coverage at the impact position rather than over settling's whole settled field
   is likewise worth **0.0003 in Z** (`results/seabed-field-coverage-289/`, 40,000 outcomes and
   2.2 × 10⁶ settled elements). Runs made with the point target are the saturated limit of the full
   model, not a provisional stand-in.
2. **What counts as a detection is the live assumption, and it is worth 2.3 points.** Treating the
   field as one object with a covered fraction removes 26.6% of the probability; treating it as
   detected if *any* settled element fell on valid data removes 28.9%. This module reports the first,
   because recognition is a campaign-level event on a recognisable signature rather than on one imaged
   element, and publishes the second as the optimistic bound. The difference is carried entirely by
   the 2.3% of outcomes whose impact lies off searched ground while part of the field reaches onto it.
   Nothing in the coverage data resolves it.
3. **Coverage resolution.** The raster is 0.01° ≈ 1.1 km, while swath-scale structure — nadir gaps,
   terrain-avoidance holes — is at a few hundred metres. Averaging at 1 km conserves the uncovered
   *area*, which is what (1) needs, but it cannot represent the geometry of a gap.
4. **Ocean Infinity coverage is inferred**, as §3 states, and the 2018 layer is a four-point effect on
   the evidence, so the grade-C provenance is load-bearing rather than cosmetic.
5. **The Bluefin-21 layer is display geometry**, 771.41 km² against the ATSB's stated 860 km². The
   published polygons are 10.3% *smaller* than the stated coverage, where a display envelope would
   normally overstate it, so the layer is conservative. It cannot matter either way: that search is
   2,473 km from the posterior's mass and removes 0.0000 of it at every ρ.
6. **q for Phase 2 rests on three percentages read from inside a figure image** (A-8), not yet verified
   in primary form. The ATSB report is not reachable from this environment at present.
7. **The surface search is not here.** It is strong evidence and belongs to ocean drift.

## 9. Open items

- Verify A-8 against the figure itself and retire the last inherited value.
- Re-run the field-coverage comparison across all four 00:19 options on the next impacts; set A here
  is the held-out arm only.
- Re-run on the end-of-flight impacts built with the Boeing-checked dive class, and on whichever 00:19
  arms become estimable once the hand-off carries the 00:19 data.
