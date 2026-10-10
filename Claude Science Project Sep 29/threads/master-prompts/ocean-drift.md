# Ocean drift — mission and master prompt

Supersedes `ISO Sept 28 Status/threads/master-prompts/ocean-drift.txt`, which remains correct on
the evidence table, the data sources, what to port and — most valuable — its measured learnings,
and is stale on four things: `crates/ocean` is no longer yours, the old `/jackbox/home` paths are
gone, the thread identifiers no longer exist, and the source region is now derived from the impact
posterior rather than fixed at ±100–150 NM around the arc.

Read `ISO Sept 28 Status/threads/master-prompts/common.txt` first for the four-stage architecture
and the eight composition rules, then `ARCHITECTURE.md` for the decisions already ruled. Both are
binding.

Split deliberately: **§2 and §3 are the contract and must not drift. §6 onward is the line of
enquiry and is expected to.**

**Coordination.** There is no live channel between sessions. Read `coordination/OCEAN_DRIFT.md` at
the start of each working session and after any long gap; write anything the architecture session
must act on to `coordination/architecture.md`. The repo is the channel.

---

## 1. Mission

Take the posterior of impact locations, drift it forward under a diverse set of ocean models with
the uncertain parameters marginalised rather than fixed, and return **the likelihood of the
observed recovery pattern given each impact location**. The principal output is how the impact
PDF is modified — which source locations are up-weighted and which are down-weighted once the
recovered debris is admitted as evidence.

**Forward physics, reverse inference by Bayes.** You run drift forwards only. You return
`L_s = p(debris evidence | impact sample s)`; the composer forms `w_s L_s / Σ_r w_r L_r`. No
reverse drift is required anywhere, and reverse drift is not to be used as the estimator: the
early AF447 search phases failed partly through over-trusting it, and it cannot represent a
non-recovery at all. Use it as a diagnostic or not at all.

### The expertise this module is expected to bring

Act as an expert in ocean drift and ocean transport modelling, simulation and analysis, working
from the body of literature that defines world-class standards in the field — not from this
project's own prior code. Be informed by the available prior studies and investigation cases in
aviation and maritime search, and **weight most heavily those cases where a subsequent ground
truth became available to calibrate against**, because they are the only ones that tell you
whether a method works rather than whether it looks reasonable.

Review the prior work on *this* case critically and with an eye to improving the rigour of the
statistical estimation — including the Bayesian methods, which you are expected to know
thoroughly rather than to apply by recipe. The prior work in this repository contains both
genuine measurements and known errors; §9 lists the ones already found. Finding more is part of
the job, and a documented negative result about a published method is a contribution.

---

## 2. The contract — stable; changes need architecture review

1. **Return a likelihood, never a map.** A map normalised over source cells already contains a
   source prior and the cell areas. Multiplying weighted impact samples by cell masses counts both
   twice. The weighted-sample update needs **no** source-cell area factor. Areas are for
   integrating or displaying a density, not for scoring samples.
2. **Each observation is used once per run**, with declared IDs. The debris record is one body of
   evidence; do not let the same find enter twice through two groupings.
3. **Score the shared impact samples.** Do not construct a competing sample set and do not move
   impact samples onto grid-cell centres. The grid is a numerical device (§4), not a second
   posterior.
4. **Smooth, with explicit model error, no floors. "Not computed" is not "impossible".** A sample
   outside the evaluated support is flagged and the support is enlarged, or it is computed
   separately. It is never silently given zero. In the earlier work, enlarging the source domain
   moved 13% of the mixture mass west of the original boundary.
5. **Be accurate where the other evidence has mass** — the current core estimate is a median of
   −37.225° with a 50% interval of [−37.85, −37.00] and 90% of [−38.35, −35.50] — not only near
   your own peak. The old drift answer peaked at 30.7°S, far north of that, so this rule is not
   rhetorical here.
6. **Measure Monte Carlo adequacy and report unconverged as unconverged.** See §5 for what
   acceptance means in this module specifically; it is not a smooth-looking drift map.
7. **Ocean models are declared alternatives, not independent evidence.** They are competing
   explanations of the same observations. Combine as `L(x) = Σ_m π_m L_m(x)` with declared
   weights. **Do not rescale each model to peak at one, or to integrate to one over source
   locations, before combining** — that gives a model which fits the data badly the same influence
   as one which fits it well. Until the observation model supports comparable likelihoods across
   models, label the combination a **sensitivity mixture**, not a Bayesian model average. The
   alternative is named `ocean-model` and is shared with Pleiades, so the composer marginalises it
   jointly — declare it by exactly that name.
8. **Marginalise the shared environment once, outside the product over objects.** Every recovered
   object travelled through the same ocean. The joint likelihood has the structure
   `L(x) = Σ_m π_m ∫ p(η|m) Π_j L_j(x | m, η) dη`, with object-specific parameters marginalised
   inside each `L_j`. Treating objects as independent lets each one select whichever ocean model
   happens to fit it best. Pieces from the same parent component may need further grouping.
9. **Sampling a range is marginalisation only if the distribution is declared.** A uniform range
   is a prior choice, not a neutral one. State the sampling distribution or the quadrature
   weights. An object's windage must persist or evolve under a model, not be redrawn independently
   at every integration step.
10. **Do not double-count waves.** An empirically fitted effective leeway coefficient may already
    absorb Stokes drift. The literature distinguishes implicit from explicit treatments
    (arXiv:2005.09527); adding both without reconciling their definitions inflates the transport.
11. **One synthetic-recovery test plus hand-computed fixtures.**

---

## 3. Interfaces

**What you consume.** The shared impact samples: position, time, weight, and the `ImpactView`
fields. In the first pass you use position and time only — see §6.

**What you return.** A log-likelihood per impact sample, with coverage and numerical-quality
flags, plus a drift-only diagnostic map clearly labelled with its display prior.

**What you do not own.** `crates/ocean` belongs to the shared ocean transport module, not to you.
That was Part A of the old brief and it has been reassigned, because settling and Pleiades need
the same transport. You are `hypotheses/debris-drift` and you are a consumer of an API you do not
control. Agree the product shape with the transport owner through the architecture session: it
must serve debris-find likelihoods over months to years, object positions on 23 March 2014 for
Pleiades, and drifted positions on the 2014 aerial-search dates.

---

## 4. The method: a source grid as a numerical device

The question is how to evaluate `L(x)` at a million impact samples without running a drift
ensemble for each. Three facts decide it.

An arrival at a particular coast is a rare event, so a small ensemble gives a noisy estimate, and
two nearby samples can receive very different scores purely through simulation noise. There are
far too many impact samples to give each one a large ensemble. But the likelihood surface itself
is smooth on the scale over which drift spreads an ensemble, which after months at sea is large.

So: lay a grid of source cells over the region, release **one large reusable ensemble per cell**,
shared by every debris record, and read the resulting surface at each impact sample by **linear
interpolation of relative likelihood**. Never interpolate cell probability mass, and never
extrapolate outside the evaluated support.

Three things this is not. It is not a second sample set — impact samples stay where they are. It
is not a physical smoothing assumption, unless you deliberately spread releases around each node,
in which case declare that as a separate modelling choice. And it is not a use of the posterior
inside the likelihood: **the posterior decides where to put cells, never what the likelihood is
worth.** If the prior enters the likelihood the composer applies it twice.

"One ensemble per cell" means one reusable ensemble *collection* per cell — separate cases for
ocean model, object class and release time — not one generic cloud reused for every object.

A recovery-observation layer then converts simulated journeys into the probability of the observed
coast segment and discovery interval, integrating over plausible beach-arrival times, discovery
delay, retention and, where supported, refloating. **Arrival time and discovery time are different
quantities** and the delay between them is modelled, not chosen to fit. Do not select the delay
that gives the best match.

If the first version conditions on an object having been recovered — "given that this kind of
object was recovered, how plausible are its location and timing for this source?" — that is a
defensible starting question, but its conditioning denominator can depend on source location.
Specify the denominator rather than removing it by renormalising simulated arrivals.

---

## 5. Sizing the grid, and what acceptance means

**The extent is derived from the impact posterior, not fixed.** Make both the coverage level and
the cell spacing configuration parameters — 50 / 90 / 95 / 99% of impact mass, and the spacing in
nautical miles — so the module can be re-pointed at any later core run without a rewrite. The
impact posterior is the primary input and it will change.

The extent dial is not smooth, because the posterior is not unimodal. Taking a band along the 7th
arc at ±100 NM, with 1° of latitude costing 60/sin 48° ≈ 81 NM along an arc crossed at 48°:

| coverage | latitude span | along-arc | cells at 5 NM | at 10 NM | at 20 NM |
|---|---|---|---|---|---|
| 50% | 0.85° | 69 NM | 549 | 137 | 34 |
| 90% | 2.85° | 231 NM | 1,841 | 460 | 115 |
| 99% main body | 6.80° | 551 NM | 4,392 | 1,098 | 275 |
| 99% including the detached island | 13.40° | 1,086 NM | 8,655 | 2,164 | 541 |

50% → 90% costs 3.4×; 90% → 99% main body another 2.4×; and 99% *including* the detached northern
mode at 26–31°S costs 2× again, almost all of it buying the empty gap at 31.5–34.5°S which carries
0.38% of mass. **So build a main band plus an optional separate patch over the island**, each sized
on its own mass, rather than one box spanning 13° of latitude. The island patch is a labelled
sensitivity.

**Cell spacing is measured, not chosen.** The quantity that sets it is the correlation length of
the likelihood surface — how far a release point must move before the predicted recovery pattern
changes appreciably. Linear interpolation error falls as the square of the spacing while cell
count rises as the inverse square, so error × cost is roughly invariant and the trade is direct
once the gradient is known.

**Particles per cell are set by the rarest arrival probability you must resolve**, with relative
standard error ≈ 1/√(Np): at p = 10⁻³, N = 10⁴ gives 32% and N = 10⁵ gives 10%. The 32% is
plausibly what the old brief meant by "dominated by Monte Carlo noise". p is unmeasured.

### The pilot, which comes first

**Agreed starting point: the 99% extent at 10 NM spacing with 10⁴ particles per cell.** It is cheap
on any plausible throughput and it measures the three numbers the production sizing depends on:

1. the field-evaluation throughput on this machine;
2. the arrival probability p at each coast segment;
3. how fast relative likelihood changes with source separation.

Those three set the production spacing and particle count. **Then** run production once, and try
5 NM as the refinement. Order-of-magnitude costs on a 6-hour step matched to the drifter cadence,
730 days, RK2, and an assumed 2 × 10⁷ field evaluations per second per core over 16 cores — the
throughput is the assumption the pilot replaces, so treat the hours as indicative and the ratios as
robust:

| configuration | trajectories | indicative wall time |
|---|---|---|
| 99% main, 10 NM, 10⁴ (the pilot) | 11 M | 0.06 h |
| 99% main, 10 NM, 10⁵ | 110 M | 0.56 h |
| 99% main, 5 NM, 10⁵ | 439 M | 2.2 h |
| 99% + island, 5 NM, 10⁵ | 866 M | 4.4 h |
| per-sample alternative, 10⁶ × 10⁴ | 10,000 M | 51 h, and not reusable |

### A prediction to test, stated before the compute is spent

If the correlation length of the drift likelihood exceeds the impact posterior's own width — the
50% interval is 0.85°, about 51 NM — then **drift cannot reweight much inside the main body**, and
its influence falls on the tails and on the northern island rather than on the peak. The headline
would then be a change in the shoulder rather than a shift of the mode. The pilot measures this
directly. If it holds, say so: it is a result about what this evidence can and cannot do.

### Acceptance

**Seed-to-seed and grid-refinement stability of the updated impact posterior**, not of the drift
map. A frozen random seed gives reproducibility, not convergence. Report both the drift-only
diagnostic and the updated posterior, and quote the stability of the second.

This matters because the grid is not a cure for Monte Carlo noise — it makes the calculation
reusable and controlled, which is different. The prior session's own figures, carried here as it
reported them: uncertainty-marginalised maps differed between seeds by a total variation of about
0.065; selecting only the best-fitting windage raised that to about 0.23; and four-object **joint**
maps differed by 0.96–0.98, close to completely different distributions, and were marked
unreliable. The stable pooled maps answered a different question and are not a substitute for the
joint common-origin likelihood.

---

## 6. The first pass, deliberately simple

Agreed scope for the first working version:

- **Release at the impact point, at the time of impact.** Assume the recovered objects originated
  there. State the assumed release time and initial floating state explicitly.
- **No family-dependent release.** Two samples at the same place and time with different impact
  families get the same drift score. Their final weights can still differ through their incoming
  weights and other evidence.
- **No resurfacing**, and no impact-dependent object inventory.
- **Consequently, the first pass does not wait on settling.** Settling's element classes and its
  sink-versus-float partition become inputs at the *refinement*, not now. When they arrive, take
  them from settling rather than defining a second partition — one physical question, one answer.

The first version must not claim to test the mechanisms it has assumed away.

---

## 7. Evidence and data

**The evidence table** is `debris-evidence-audit.csv`, 41 rows, hand-curated from Pete's
spreadsheet and checked against the Malaysian MOT summary of 30 December 2018 and Durgadoo et al.
2021. It carries dates, locality coordinates, Malaysian classification, stringent / expanded /
circularity flags and motion class. The Mossel Bay date differs between sources — carry both, do
not silently pick one.

**Use the stringent identity set.** The expanded set is circular: 8 of its 11 additions cite
agreement with CSIRO drift modelling as part of the identification. Admitting them would let the
evidence be partly constituted by the answer.

**Published comparators are an overlay, never evidence.** Some of those results already incorporate
SATCOM or aerial-search information, so scoring against them would reuse the same observations.

**Context that governs how the debris is used.** All of the roughly twenty identified pieces come
from western Indian Ocean shorelines — Réunion, Mozambique, South Africa, Mauritius, Madagascar,
Tanzania — and the ATSB graded 18 of 20 very likely or almost certain. No debris has been found on
Australian shores; the June 2016 Kangaroo Island item was found not consistent with Boeing
commercial manufacturing specifications. The Australian-coast absence is genuine disconfirming
evidence, but it enters as a likelihood with explicit model error and declared alternatives,
**never as a veto**, and the ATSB's findings are evidence to be weighed rather than fact.

**Ocean products.** GLORYS12 with WAVERYS; OSCAR v2 Final (0.25°, daily, observation-based) as an
independent alternative, noting that it is coarser, weak near coasts and carries its own
wind-driven term, so do not add windage on top without reconciling; BRAN2016 via NCI OPeNDAP.
**Native HYCOM is dropped** — it ends in July 2015 and did worse in drifter replay. GDP drifters,
6-hourly, 2014–16, for validation.

**Provisioning is not done.** The old harness's cache paths are gone, and the Copernicus products
need a login. Raise provisioning with the shared ocean transport owner through the architecture
session before downloading anything large; the disk is the binding constraint on this machine.

---

## 8. Port and discard

Port from the archive: the transport equations and their three or four analytic tests; the field
rule **"renormalise across land only, never fill with zero"**; and the drifter-replay validation
split by drogue state, which caught a real bug — keep that split, drogued and undrogued drifters
do not behave alike. The Pleiades bundle's transport core implements the same physics and is a
useful cross-check.

Discard: the per-event sequential Monte Carlo sampling and source-area code, the isotope work, the
old hand-offs, and the Python apart from the retrieval scripts and the product converters.

---

## 9. What the prior work measured, and where it went wrong

These are the most valuable part of the old brief. They are measurements, not opinions.

- **Object response dominates.** A Stokes factor of ×0.5, ×1 and ×1.5 moved the mode to 11.9, 18.0
  and 34.9°S, while changing the current product moved it 1.2°. So integrate object response per
  object class inside the likelihood; a global factor is the wrong shape.
- **Coastline resolution decides which paths survive.** The 1:110m mask omitted Réunion — the
  island where the first confirmed piece was found.
- **Multiplying rare arrival probabilities is dominated by Monte Carlo noise**, and floors and
  pseudocounts set the old modes. Hence: one forward ensemble per source cell shared by all finds;
  find **episodes**, not objects; smooth estimators such as transfer operators or an analytic
  spread rather than particle histograms.
- **Weight by termination or inherit survivor bias** — that is what produced the old 34°S artefact.
- **Diffusivity was never tested.** The old code used 100 m²/s; CSIRO used a 5 NM/day random walk.
  That is an untested lever on a quantity the answer is known to be sensitive to.
- **A uniform reporting rate cancels.** The Western Australia non-recovery term needs relative
  search effort by coast, which is why it is deferred rather than cheap.
- **The old final answer was 29.7–35.8°S with a mode at 30.7°S and was unconverged**, sitting north
  of the core estimate. The combined result will depend on drift's southern tail, so converge
  there specifically.

One methodological warning inherited from the Pleiades work: **averaging object scores and
combining evidence from several objects answer different questions.** That averaging rule suited
one unknown object among candidate detections. A set of securely attributed aircraft parts is a
different observation problem, and its maps being stable is not a reason to inherit it.

---

## 10. Deliverables, in order

1. A short plan, as your first reply.
2. The critical review of the prior work on this case, with the specific improvements you propose.
3. The pilot of §5 and the three numbers it measures.
4. The transport and recovery-observation layers, with the sizing fixed by the pilot.
5. The sample-scoring interface: log-likelihoods at the original impact samples with coverage and
   quality flags.
6. The production run, and the 5 NM refinement.
7. Report pages — PDFs with PNGs alongside: the drift-only diagnostic map with its display prior
   labelled, the updated impact posterior, and the stability of the second across seeds and
   refinement.
8. `core_requests` in `hypothesis.toml`, and a note to `coordination/architecture.md` when the
   branch is ready for review.

## 11. Tests

Analytic displacement under a constant current. Random-walk RMS against its closed form. The
land rule: renormalise across land, never fill with zero. Drifter replay against GDP, split by
drogue state. One synthetic-recovery test: generate finds from a known source and check coverage.
Plus hand-computed fixtures.

## 12. Scope and reporting

`make scope H=debris-drift` must pass before you hand back — nothing outside
`hypotheses/debris-drift/`. No new `.md` inside `engine/`; assumptions and sources go in the
`lib.rs` doc comment, status in `hypothesis.toml`, write-ups in the project-level `results/`.
`make smoke H=debris-drift` is the code-path check; **`make hypothesis H=debris-drift` runs at full
scale**. Wrap anything expected to exceed ~10 minutes or ~4 GB in
`lockf -k /tmp/.mh370-heavy.lock <command>` so heavy jobs queue rather than compete.

## 13. Deferred, and to be raised again

- **Western Australia non-recovery.** Disconfirming evidence with real uncertainty, and it needs
  relative search effort by coast. First get a working arrival likelihood without it, then bring it
  in. **Raise this with Pete once the first pass is stable** — he asked to be reminded.
- **The absence of buoyant cabin material** — no lifejacket, seat cushion, personal effect or
  luggage fragment, against hundreds aboard and 777 cushions being flotation-rated. Deferred with
  debris-configuration evidence, as for end of flight. When it arrives, note that absence is
  confounded by detection in a way presence is not: nobody searched East African beaches before
  July 2015, large composite panels survive and are recognised while soft items degrade or are
  taken, and high-windage items drift differently. It is weak evidence **symmetrically** — it does
  not support a ditching either.
- **Family-dependent release, resurfacing, and settling's float partition.** The refinement.
- **The 2014 aerial search** — 387 day-labelled polygons, licence still under review, no detection
  probability, and drift-dependent. Coordinate with searched areas when it is cleared.

## 14. Open, needing the architecture session

1. The shared transport API shape, agreed across drift, settling and Pleiades.
2. Provisioning of the ocean products on this machine.
3. The grouping of debris records into find episodes, which affects how the shared environmental
   uncertainty is marginalised.
4. Whether the island patch is run by default or only as a labelled sensitivity.

---

## Amendments, 9 October 2026 — accepted from the module's critical review

1. §5's seed-TV figures (0.065 / 0.23 / 0.96–0.98) are **Pléiades imagery numbers, not drift**. Drift's
   own figures on record are 0.232–0.283 and 0.394.
2. §9 claim 5 (survivor bias as the cause of the 34°S peak) **could not be found** in the prior work and
   is withdrawn. Of the seven §9 claims, 2 are backed, 4 partly backed, 1 not found.
3. Davey's single-flaperon update **reproduces** (+2.75 NM north on our reference) and its smallness is
   due to the information in one find, **not** to kernel width. See the corrected D3.
4. Only a global constant in identification probability cancels; **block levels are latent**.
5. The prior drift answer was Monte Carlo noise where the core posterior has its mass: minimum per-find
   ESS 1.0–8.9 particles in 35.3–38.5°S.


## Side questions (standing rule, Pete, 10 Oct 2026)

Pete, 10 Oct 2026: when he asks a side question, answer it and then go back at once to the work you were doing. If that work is complete, start the next item in your backlog. Do not end your turn after a side answer while you have work in progress or a backlog. End your turn only when the backlog is empty or every item is blocked on something you cannot do yourself. Before you end it, write here which items are blocked and on what. An approved run whose gates you can execute is not blocked: start it.


## Sampling coverage (standing rule, Pete, 10 Oct 2026)

The aim is to sample the whole kinematically feasible space of the 777-200ER, within its performance and limits, and let the evidence select. Under-sampling silently conditions the result on an assumption nobody made. Earlier studies may have done this, for example by sampling mainly cruise at altitude to fuel exhaustion followed by an uncontrolled descent.
1. Keep three sets apart and state each one: (a) the **feasible set**: what the aircraft can physically do, with sources; (b) the **model's reach**: what your physics and parameter ranges can produce at all; (c) the **proposal's coverage**: where your samples actually land, with ESS per region.
2. Any part of (a) that (b) cannot produce, or that (c) does not reach with adequate ESS, is a **gap**. Close it, or declare it as an explicit conditional hypothesis and name it in the label of every result it affects. A silent gap is a defect.
3. You may concentrate samples for precision (importance sampling, aimed proposals, tempering, strata). The prior must still cover the feasible set, and the weights must carry the proposal correction. Sampling may follow a hypothesis; weight comes only from the evidence.
4. Do not limit the scenarios to those that fit one reading of the data. Example: sampling descents only for the R600 BFO and not the Holland-type or other rapid descents. Every standard 00:19 option and every hypothesis family (A1, A2, B) must be estimable from the same sample set. If one is not estimable (low ESS), report it as a coverage gap and propose the fix; do not drop it.
5. A parameter bound narrower than the feasible range is a gap unless it has a source. A model cap (for example on descent rate or on unloading) is a reach gap, not a sampling choice.
6. Every results note has a **COVERAGE** section: the three sets, the gaps and their status, ESS per option, family and declared region, and parameter bounds with sources. Every review checks coverage first.

This rule is in every module profile from your next turn, and in the master prompts. Architecture keeps the gap register in ARCHITECTURE.md (section "Coverage register").
