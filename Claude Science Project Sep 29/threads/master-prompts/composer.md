# Composer — mission and master prompt

**Status.** Written 8 October 2026 by the architecture session. ARCHITECTURE decision 1 was superseded
on ownership the same day: **the composer is its own piece of work; the runner stage stays with the core
estimator.** The dividing line is which files the work edits — the composer reads `impacts.npy` and
writes a new crate; the runner edits `main.rs` and `config.rs`.

**Authority.** This file; `ISO Sept 28 Status/threads/master-prompts/core-stages.txt` §D6, which is the
starting specification and is reproduced in substance below; `ISO Sept 28 Status/threads/master-prompts/common.txt`
for the eight composition rules; `Claude Science Project Sep 29/ARCHITECTURE.md`.

**Location.** New crate `crates/compose`. Branch `core/composer`, cut from `claude-science-sep29`.

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
