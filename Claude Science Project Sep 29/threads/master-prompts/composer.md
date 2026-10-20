# Composer — mission and master prompt

**Status.** Written 8 October 2026 by the architecture session. **Amended 17 October 2026 at Pete's request: §0 (mission and evidence balance) added; it takes
precedence over the later sections.** ARCHITECTURE decision 1 was superseded
on ownership the same day: **the composer is its own piece of work; the runner stage stays with the core
estimator.** The dividing line is which files the work edits — the composer reads `impacts.npy` and
writes a new crate; the runner edits `main.rs` and `config.rs`.

**Authority.** This file; `ISO Sept 28 Status/threads/master-prompts/core-stages.txt` §D6, which is the
starting specification and is reproduced in substance below; `ISO Sept 28 Status/threads/master-prompts/common.txt`
for the eight composition rules; `Claude Science Project Sep 29/ARCHITECTURE.md`.

**Location.** New crate `crates/compose`. Branch `core/composer`, cut from `claude-science-sep29`.

---

## 0. Mission and evidence balance — amended 17 October 2026 (Pete)

Read this before §1. Where this section and a later one disagree, this section wins.

**Purpose.** No single evidence type can locate the aircraft. Satcom with flight dynamics, debris drift,
hydroacoustics, searched areas and the conditional hypotheses are each sparse and under-determined, and each
has wide uncertainty. If a solution exists, it comes from all of them together, each weighted by its own
uncertainty. The composer is where they are combined. Its job is to give the posterior over seabed location
given ALL the evidence, to show the true spread of that uncertainty and where the probability peaks, and to
show which evidence makes each feature. Prior work relied mostly on one evidence type. This work must not.

**False precision is a defect.** The satcom posterior peaks near 37 S, but solutions that agree with the
satcom data exist far up the arc, and only one of them has to be true. A narrow composed region is a result
only if it passes the checks in §0.1–§0.7. If a result is narrow because of the sampling, an understated
model error or one dominant factor, report that as the result.

**Not allowed.** Do not down-weight an evidence type by hand: no likelihood powers below 1 in a reported
product, no fixed weights, no dropping a factor because it disagrees. Balance comes from (i) honest model
error inside each likelihood, (ii) samples that cover the whole arc, and (iii) showing each evidence type's
own view, so that a reader can see the triangulation and need not trust it. Tempering inside a sampler is
permitted when it ends at power 1.

### 0.1 Three views for every evidence type

For each evidence type E (satcom + flight core; drift; hydroacoustics; searched areas; the Pléiades / COSMO
conditional; settling where it changes the seabed), compute:

- **(a) E alone:** E's likelihood on a prior that is uniform along the 7th arc over the full span that the
  flight prior covers, with the same end-of-flight impact model. For the core, view (a) is the flight + end-of-flight
  posterior.
- **(b) core + E.**
- **(c) all except E** (leave-one-out), and **all**.

For each view report: median latitude along the arc, 50 % and 90 % HPD regions and their areas, mass per
latitude band (§0.7) and ESS. A view that is not estimable is reported as a coverage gap, not dropped.

### 0.2 Disagreement between evidence types

For each E, between view (a) and the core, and between view (c) and all: the ln evidence ratio (state what it
is conditional on); the overlap of the 90 % HPD regions (the share of each region inside the other, and the
Bhattacharyya coefficient on the equal-area grid); the shift of the median along the arc. This generalises
the Pléiades tension test of passes 0 and 1 to every evidence type. A large disagreement is a result, not a
defect: it goes in the headline table, not in an appendix.

### 0.3 Influence of each factor

For each factor: the KL divergence (nats) from the base to the composed posterior, and the change in median
and 90 % area when the factor is removed. Flag a factor that carries more than half of the total KL
divergence of "all". Flag separately **model dominance**: one flight family or one mode carrying more than
95 % of a product. Run I measured 0.995–0.997 for waypoints (`results/composer-north-ess-run-i.md`).

### 0.4 Arc-wide sample set (core and end-of-flight request)

A composed posterior is a reweighting of the impact samples. If the samples come only from the satcom
posterior, other evidence can only reweight the places where satcom put samples. Measured on run I
(`results/composer-north-ess-run-i.md`): with drift and searches, 0.177 of the mass is north of 33 S, on an
implied effective sample of 66 (seed range 0.096–0.268). The north is under-sampled, not excluded.

Required: an impact sample set whose proposal covers the full arc, for example the defensive mixture
q = (1 − α) p_core + α q_arc, where q_arc is uniform along the arc span and uses the same end-of-flight descent
model, with the importance weight p/q carried on each row. The prior does not change; only the sampling
changes. The core and end-of-flight sessions own the method (the arc-kernel impacts of the searched-areas M3
fixture are one candidate starting point). Target: at least 1,000 effective samples in each 5° latitude
band that holds more than 1 % of the mass of any view (a) or any composed product.

Until that sample set exists: every composed result carries the label "north of 33 S under-sampled
(effective sample n)", with n measured; and view (a) uses the best arc-uniform set available, labelled
with what it is.

### 0.5 Model error and false-precision sensitivities

Every factor's likelihood carries explicit model error (composition rule 4), with its validation source.
The composer checks that each module declares it, and does not put a factor into a headline without it.
Labelled sensitivities for each factor: model-error scale doubled; and a heavy-tailed version (for example
Student-t, ν = 4) where the module supplies one. Report how far the headline moves. For the satcom core
(BTO / BFO noise and the BFO bias-drift model) the likelihood is inside the filter: ask the core session for
the sensitivity runs and compose them; do not change the core likelihood yourself.

### 0.6 Shared inputs between modules

Apart from the named alternatives, check that each input shared by two or more modules (ocean model,
windage, impact energy and angle, end-of-flight family and its assumptions, the 00:19 option) is declared as
a shared alternative or carried as an `ImpactView` column, so that it is marginalised jointly. An undeclared
shared input is a dependence gap: report it in the COVERAGE section.

### 0.7 Outputs describe the whole probability space

Headline outputs: mass per 1° latitude band along the full arc span, with Monte Carlo error from the seed
scatter; every mode with its mass; 50 / 90 / 95 % HPD regions on the equal-area grid; and the probability
that the seabed is inside versus outside the searched areas, by region. Median and peak are shown with
these, never alone. Results are per end-of-flight hypothesis first (§1, item 6). Charts and notes follow
the project rules for titles, footnotes and language.

### 0.8 Tests added to §3

8. **Arc-wide proposal:** the importance weights alone recover the uniform prior along the arc on a
   fixture, and a factor composed onto the mixed proposal gives the same posterior as on a direct sample
   from the target, within Monte Carlo error.
9. **Views and influence:** on a synthetic fixture with two factors that disagree by a known amount, the
   composer recovers views (a)–(c), the ln evidence ratio, the HPD overlap and the KL influence of each
   factor against the closed form.

---

## 1. What the composer does

Stage 4 of the estimator. Given the shared impact samples and the log-likelihood columns returned by
whichever impact-level modules are selected, it:

1. **Sums the selected columns per impact sample.** Legitimate only because every module scored the
   **same** samples and used each observation once — composition rules 2 and 3 exist to protect exactly
   this. Refuse if two modules declare the same observation ID.
2. **Marginalises declared alternatives over their priors** — **jointly** where two modules declare the
   same alternative by name, e.g. `Σ_m P(m) · L_drift,m · L_pleiades,m` for `ocean-model`. Never
   marginalise each module's alternative separately and then multiply: that treats a shared uncertainty
   as two independent ones.
3. **Reweights the impact samples** to give the posterior over impact location, time, energy and any
   prediction columns transform modules add.
4. **Reports** evidence increments per (replicate, mode) so `summary.rs` pooling stays correct; ESS per
   factor; the posterior probability of each alternative; split-half replicate agreement.
5. **Writes** composed PDFs on a 2-D equal-area grid in `summary.json`, **extending `summary.rs`** —
   use its `stats()` / `upper_edge`; do not add a second summariser.
6. **Presents results per end-of-flight hypothesis first.** Any average across hypotheses appears only
   beside a prior sensitivity (common.txt).

The hard part is the bookkeeping on alternatives and absolute scale, not the arithmetic.

## 2. Rules the composer enforces rather than trusts

- **Absolute scale.** Only modules declaring `absolute_scale = true` may be mixed across alternatives
  (rule 1). A relative-scale module may be composed only within a single alternative.
- **0.0 versus NaN** (ruled 8 October for hydroacoustics, applies to all): `0.0` means "module selected,
  no data used" and is exact; `NaN` means "this sample could not be computed". A NaN is **never**
  treated as zero and never as minus infinity. Report the count and the weight of NaN samples per module;
  refuse to compose if NaN samples carry more than a declared fraction of posterior weight.
- **No double application.** The residual-PDF views searched areas needs are this composer's output with
  that module enabled versus disabled. The composer must refuse to compose a module's column onto a
  posterior that already contains it. Every composed product records exactly which columns it contains.
- **Evidence sets from config**: e.g. `core`, `core+drift`, `all`, or conditional on an alternative.
- **Conditionals are labelled.** A conditional hypothesis (Pléiades) is reported as conditional on every
  output, with P(H | D) and the mixture alongside p(x | D, H).
- **Report unconverged as unconverged.** If ESS after composition falls below a declared floor, say so
  rather than plot.

## 3. Tests, which come before any real data

From core-stages.txt plus this project's additions:

1. **Analytic composition:** a Gaussian factor on a Gaussian prior, against the closed-form posterior and
   evidence.
2. **Joint marginalisation:** two modules sharing an alternative by name, against a hand-computed case
   where separate marginalisation gives a different and wrong answer.
3. **Rejection of an observation-ownership overlap.**
4. **0.0 / NaN semantics**, including the refusal threshold.
5. **Double-application refusal.**
6. **Per-(replicate, mode) evidence pooling** agrees with `summary.rs` on a fixture.
7. **The synthetic composer test hydroacoustics asked for**: the move in the impact PDF caused by a
   synthetic detection at one, two or three stations — the composer must make that computable.

## 4. Inputs while no real impact samples exist

Build and test against **synthetic `impacts.npy` fixtures you generate yourself**, with known answers.
Then the end-of-flight smoke impacts when published, labelled provisional. The searched-areas M3
fixture (44,190 arc-kernel impacts, 2 replicates) is a realistic shape test — "plumbing, not evidence".

## 5. Core boundary

The composer touches **no** core file except one: the workspace `Cargo.toml` members line. Raise it as a
core request in `coordination/CORE_STAGES.md`; on the composer branch the line may be present so the
crate builds, declared in the commit message. `summary.rs` is core-owned: **propose** the extension as a
patch for the core session to land, rather than editing it on a shared branch.

---

## 6. Review of the first increment — 9 October 2026, architecture

`core/composer` at `5d2a206`, built by an architecture sub-agent. **Scope verified by the architect
against the merge base `e149ff5`:** five files, 1,740 insertions — `crates/compose/{Cargo.toml,
src/lib.rs, src/tests.rs}` plus the declared workspace `members` line and its `Cargo.lock` entry. No
core source file touched. All seven section-3 tests pass. **Not yet run on real or smoke impacts** —
synthetic in-memory fixtures only, because the crate has no `.npy` reader; file I/O belongs to the
runner stage (core request C).

**Rulings on the items it marked provisional:**

1. **NaN rows are carried at their (replicate, mode) mean likelihood ratio of the computed rows.**
   Accepted as the default — it leaves an uncomputed sample at the average reweighting rather than
   inventing evidence for or against it. It is a modelling choice: every composed product reports it,
   and the refusal threshold still applies. **Add later** the sensitivity that drops NaN rows instead,
   and report both where they differ.
2. **Tolerance implemented as refusal.** Correct; it is what this brief says. The `config.rs` doc
   wording is core's to fix, under request C.
3. **ESS floor default 1,000 effective parents per replicate.** Accepted; matches the terminal-stage
   convention.
4. **"Per end-of-flight hypothesis first" as per descent family within one run.** Accepted for now;
   the cross-run comparison of V1a / V1b / V2 belongs to the report.
5. **Equal-area grid** (0.25° longitude × equal steps of authalic latitude, 769.3 km² cells). Accepted.
6. **Test 6 compares against a transcription of `summary.rs` pooling**, not the function itself; the
   real-function test lives in the unlanded patch. Closes when core lands patch B.
7. **Relative-scale modules declaring a trajectory alternative are refused.** Correct under rule 1.

**Core requests raised:** A — workspace membership; B — `results/composer-summary-rs.patch`; C — the
runner stage replacing the `[[compose]]` rejection at `main.rs:71`.


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
