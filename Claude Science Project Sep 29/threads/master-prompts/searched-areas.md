# Searched areas — mission and master prompt

**Status.** Aligned 8 October 2026 by the architecture session, from Pete's context of the same date,
the prior-agent notes he supplied on 7 October, the September ISO brief
(`ISO Sept 28 Status/threads/master-prompts/searched-areas.txt`), the prior architecture rulings at
`ISO Sept 28 Status/decisions/seabed-search-rulings.md`, and the existing analysis under
`ISO Sept 28 Status/results/worktree-searched-areas/seabed-search-analysis/`.

**Authority.** This file supersedes `searched-areas.txt` wherever they differ. Read
`ISO Sept 28 Status/threads/master-prompts/common.txt` for the shared contract and the eight
composition rules — they bind you and are not restated. Read `Claude Science Project Sep 29/ARCHITECTURE.md`
for how the module sits in the estimator.

**Module location.** `hypotheses/seabed-search/`. Branch `hypothesis/seabed-search`, cut from
`claude-science-sep29`.

---

## 1. Mission

Treat the seabed search as an **observation**: the wreck was looked for in specific places, at specific
times, with sensors of known capability, and it was not found. That non-detection is disconfirming
evidence, and this module returns it as a log-likelihood on the shared impact samples.

### What is new here, stated precisely so the paper can defend it

The method is not new. **Stone et al. (2014), "Search for the wreckage of Air France Flight AF 447",
*Statistical Science* 29(1):69–80**, built the AF447 posterior in four steps, each accounting for an
increment of unsuccessful search, and it is the prior art this module rests on. Behind it sits
classical search theory, where detection-conditioned updating is textbook.

Davey et al. (2016) set out the mathematics for MH370 and did not apply it. Their §11.1, "Updating the
Distribution Using Search Results" (printed p. 101), gives the posterior given search effort as

```
p(x_final | S, Z_K)  ∝  [1 − P_D(x_final)] · p(x_final | Z_K)          (Davey eq. 11.1)
```

and on p. 102 notes that the AF447 analysis modelled side-scan sonar detection probability as 0.9 —
their reference [40]; Stone's own text states the 0.9 as a deliberate cap, because manufacturer and
operator estimates "tend to be optimistic". Confirm [40] against the book's reference list before
citing it as Stone.

**The defensible claim is therefore:** the established method has not been applied to MH370 within a
full BTO/BFO particle-filter posterior, with a modelled seabed detection function, a modelled wreckage
field, and the four search campaigns with their overlaps and disputed outlines. That is the
contribution. Never write that nobody has done search-conditioned updating.

**One sentence in Davey must be addressed rather than inherited.** On p. 102 they write that, given the
search's quality-assurance process, "it is considered highly unlikely that the search would fail to
detect the aircraft if the correct location is searched". That is the assumption ρ ≈ 0. This project's
reference case is ρ = 0.05 (§5). The paper must state the departure, and why — and AF447 is the reason:
Stone's 0.9 cap exists because confident detection estimates had already failed once.

### The expertise this module is expected to bring

World-class knowledge of high-resolution ocean survey — deep-tow side-scan and synthetic aperture sonar,
AUV survey, bathymetric multibeam — and of its detection performance against real targets on real
terrain. Wreckage search and identification practice, including how contacts are classified, revisited
and dismissed. Thorough Bayesian competence, not recipe-following. General oceanographic knowledge,
particularly seabed geology and terrain in the Southern Indian Ocean.

Work from the body of literature that defines world-class practice rather than from this project's
prior code. Weight prior cases most heavily where a ground truth later became available to calibrate
against — AF447 above all, where the wreck was eventually found and the earlier searches' failure can
be explained. Review the prior work on this case critically, with an eye to the rigour of the
estimation, rather than reproducing it.

---

## 2. The contract — stable; changes need architecture review

**What the module returns.** `impact_log_likelihood` on the shared impact samples: the log of the
probability that the searches would have found nothing, given an impact at that sample.

```
L(s) = E[ P(no detection | W, θ_search) | s ]
```

where `W` is a settled wreckage configuration drawn by the settling module for impact sample `s`, and
`θ_search` the search record.

**Alternative settling draws are alternative outcomes, not extra wreckage. Average their non-detection
probabilities. Never multiply them.** Multiplying would treat each draw as an additional wreck that
also had to be missed, and would drive the likelihood towards zero for no physical reason. This is the
single easiest error to make in this module.

**Already ruled, and binding** (from `seabed-search-rulings.md` and the M3 migration approved
2026-09-28 at `b73541a`):

- `impact_log_likelihood` evaluates on latitude and longitude.
- `observations()` returns `search:<campaign>`, one per campaign.
- `absolute_scale` is true.
- `predict()` returns covered fraction per campaign, detectable miss, and P(no find).
- Bilinear `c_k(y)` between 0.01° cells is part of the data model, not private smoothing — approved
  under rule 3.
- **Off searched ground, `ln L = 0`, not NaN.** Not searched means no information, and impact samples
  can lie 400 NM beyond the arc.

**The residual PDF is a view, not a second pipeline.** Pete's intent is a residual PDF over any chosen
source — the reference posterior, a Pléiades conditional, a composed posterior. That is delivered by
the composer applying this module's likelihood column to whichever posterior is selected, and comparing
against the same posterior with search evidence disabled. Reweighting a different prior by the same
column is free, so every source Pete wants is available.

**What this forbids.** The module must **never ingest a posterior that already contains its own
likelihood**, or the search evidence is applied twice. Every residual figure names its source posterior
and states whether search evidence was already in it. The prior Pléiades deck has exactly this kind of
figure; getting that provenance wrong would be invisible in the output.

---

## 3. Define the detectable target before anything else

"The wreck" is not an object. It is a field of pieces with a size distribution and an extent, and
whether a search would have seen it depends on piece size against sonar resolution and on how much of
the field fell inside the swath. This is the module's hardest modelling problem, and it is why settling
emits wreckage **samples** rather than summary columns (ARCHITECTURE decision 2, option 3).

So define, before any likelihood is computed:

- what a detection *is* — a contact on a single piece, a cluster, or the field;
- the minimum detectable piece size per sensor, as a function of range, altitude and terrain;
- how a field partly inside a swath is scored.

**Coverage and detection modelling can proceed before settling is ready.** The earlier ruling that this
module "genuinely waits on settling" was too absolute. Use a point-target or a parametric field as a
placeholder, labelled provisional, and swap in settling's samples when they arrive.

---

## 4. Campaigns, provenance, and what does not count as searching

**Four campaigns, with search-date provenance preserved per campaign** — for drift (what was still
afloat when), for the development of the settled field, and for any later claim about what a campaign
could have detected at the time.

| campaign | treatment |
|---|---|
| ATSB Phase 2 (2014–2017) | main estimate. Deep-tow 103,921.5 km², GO Phoenix 14,627.3, DHJ 3,164.3, AUV 16,164.1; **union 120,486.5 km²**, matching ATSB's ~120,000 |
| Bluefin-21, 2014 | main estimate. 771.4 km² in the recovered layer against ATSB's stated 860 — reconcile or report the difference |
| Ocean Infinity 2018 | **main estimate as inferred coverage**, with an **ATSB-only arm as a required comparison** (Pete, 8 Oct). Traced outline 148,993.2 km², less Phase 2 = 126,009.3 km²; implied coverage 0.889–0.952 |
| Ocean Infinity 2025–26 | separately reported, much broader inferred variant, using the existing proposed-band reconstruction and vessel-track proxies |

**Areas cannot be added.** Overlapping campaigns overlap. The earlier claim that OI 2018 was ">112,000
km², larger than Phase 2" is not established and is withdrawn — Phase 2 itself covered over 120,000 km².

**The OI 2018 outline is a community tracing** (MH370-CAPTION KML) of unclear licence. **Never commit
it**; read it by path. Treat it as an envelope with boundary displacement and spatially coherent gaps,
not a mask. Its 0.75–0.81 figure is a campaign-level constraint, not a per-point probability.

**Measured, and it sets the priority:** on the existing fixture, mass removed at ρ = 0 is 0.6274 by
Phase 2 alone, **0.0125 by OI 2018 alone**, 0.6398 by both, and 0.0000 by Bluefin-21 alone. The
coverage-fraction uncertainty inside the OI outline is immaterial — 0.889 gives Z = 0.3922, 0.952 gives
0.3913. OI 2018 is a 1.2-point effect; do not spend effort on its outline proportionate to its
provenance problem.

**For 2025–26: never spread the reported 7,571 km² uniformly, and never treat the ~15,000 km² contract
area as searched.**

**What excludes nothing:**

- **Bathymetric mapping is not searching.** Multibeam survey of the seabed does not detect wreckage at
  the resolution that matters. Its use in this project is as terrain for hydroacoustic propagation and
  for terrain masking here — not as coverage.
- **Planned coverage is not executed coverage.**
- **Contract areas are not searched areas.**

**The surface search is not this module's.** The 2014 aerial and surface search found nothing floating.
That is a genuine non-detection, but it is a different detection model over a drifting field and it
belongs to the **ocean-drift** module's observation model. Seabed non-detection here; surface
non-detection there.

---

## 5. ρ — defined before any prior is put on it

**ρ is the chance the wreck could not have been found even where the sonar looked:** hidden by terrain,
buried, or imaged and dismissed. ATSB's detection ratings `q_k` cover data quality; ρ is what they do
not. That definition is from the existing module and it resolves the double-counting question: since
`q_k` does not absorb burial or obscuration, ρ does not double-count them.

```
P(no detection | W) = ρ(W) + [1 − ρ(W)] · Π_k [1 − c_k(W) · q_k(W)]
```

`q_k` must mean detection **conditional on the target being in the detectable class**. If a later
change lets `q_k` absorb terrain or burial, ρ double-counts, and the change must be refused.

**Reference case ρ = 0.05** (Pete, 8 Oct), with the full sweep reported beside it: 0, 0.02, 0.05, 0.1,
0.2, 0.3, 0.5. On the fixture, Z runs 0.3726 / 0.3852 / 0.4040 / 0.4353 / 0.4981 / 0.5608 / 0.6863 and
the share of mass on Phase 2 coverage 0.104 / 0.133 / 0.173 / 0.232 / 0.329 / 0.403 / 0.512.

**The marginal likelihood depends only on the mean of ρ.** So a broad prior on ρ does not make the
result conservative — it gives the same answer as a point mass at its mean. Report ρ as a swept
parameter, not as a distribution that appears to hedge.

**Model repeat-search dependence.** Where campaigns overlap, misses are not independent: terrain that
hid the wreck from one deep-tow pass hides it from the next. The prior Pléiades work reported both
dependent and independent treatments; carry both, with dependent as the default.

---

## 6. Resolution and integration

**Coverage representation: 0.01° cells with bilinear `c_k`** (Pete, 8 Oct), built and approved under
rule 3. About 1.1 km. **Raise ~500 m with Pete once the model is stable on real impact samples** — it
matches the spacing at which the ATSB footprint was actually extracted, despite the 5 m layer name. He
asked to be reminded.

**Settling draws per impact are set by integration error, not by map resolution.** 512 pilot draws per
representative case, refining to 4,096 where the likelihood is uncertain, targeting a 95% half-width of
about 0.02 in non-detection probability and switching to relative error where that probability is
small. A worst-case 0.02 half-width needs about 2,400 effective draws. This is the number settling has
been told to build to.

**Average likelihoods before normalising.** Never normalise per draw and then average.

---

## 7. Deliverables, in order

1. **The citation task, first.** Confirm Davey's reference [40] against the book's reference list and
   record §11.1 (p. 101), the 0.9 statement and the ρ ≈ 0 sentence (p. 102) in the project citation
   ledger, by printed page from the running header. Record Stone et al. 2014 with the four-step
   posterior and the 0.9 cap. Both PDFs are in the artifact store:
   `10.1007_978-981-10-0379-0_11.pdf` and `10.1214_13-STS420.pdf`.
2. **The detectable-target definition** of §3, written to `results/` before code.
3. **Port the M3 module to this branch** and reproduce the fixture numbers in §4 and §5. They come from
   arc-kernel placeholder impacts and are labelled in their own figures "plumbing, not evidence"; they
   establish that the port is faithful, nothing more.
4. **Repeat-search dependence**, dependent and independent.
5. **Run on end-of-flight impact samples** with a point-target placeholder, then on settling's wreckage
   samples when they exist.
6. **The residual-PDF views** via the composer: reference posterior, OI-inclusive and ATSB-only, across
   the ρ sweep — and against any other source posterior selected, each labelled with its source.
7. **The 2025–26 inferred variant**, separately reported.

---

## 8. Tests

- `make scope H=seabed-search` — note **core request 11**: it diffs against a stale base, so check the
  file list by hand against your module directory.
- Reproduce the fixture's mass-removed figures to tolerance.
- **The averaging test:** two identical settling draws must give the same likelihood as one. A module
  that multiplies draws fails it.
- **Off-ground test:** a sample with no coverage returns exactly 0.0.
- **ρ-mean test:** a broad ρ distribution and a point mass at its mean give the same marginal.
- **Double-application guard:** feeding a posterior already carrying this module's column must refuse.

---

## 9. Licence and provenance

Never commit the OI 2018 traced outline. The ATSB footprint data are public. Never cite an unauthorised
copy of a copyrighted document. Search dates and their sources are recorded per campaign.

---

## 10. Deferred, and to be raised again with Pete

- **~500 m coverage resolution**, once the model is stable on real impact samples. He asked to be
  reminded.
- A per-campaign revisit model — which contacts were revisited and dismissed.
- Terrain-masking maps derived from bathymetry, via the shared ocean-transport owner.

## 11. Open, needing the architecture session

- Whether the composer needs a dedicated residual-view output, or whether the existing
  enabled/disabled comparison suffices.
- The bathymetry dependency for terrain masking — the shared ocean-transport owner holds bathymetry.

## Amendment, 9 October 2026 - the Ocean Infinity outlines (Pete's decision)

This replaces every "never commit" instruction about the Ocean Infinity 2018 traced outline and the
2025-26 band tracing. Pete's decision: these outlines are our best and only proxy for those search
elements, and leaving them out would be worse.
- **Use them and commit them.**
- **Every use carries a footnote:** the source (the MH370-CAPTION community tracing, grade C), and that
  the outline is inferred from vessel tracks, not official geometry.
- The OI 2025-26 rule stands as before: the reported area goes on the outboard band only, never on the
  contract area.


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
