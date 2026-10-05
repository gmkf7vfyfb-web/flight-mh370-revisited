# Architecture and coordination

Read this first if you are a session joining this project. It says what the estimator is, who
owns which part, how parallel sessions coordinate without a live channel, and which rules are
binding rather than advisory.

This document supersedes two earlier ones and merges them: the `ARCHITECTURE.md` written in this
workspace on 29 September, and `ISO Sept 28 Status/decisions/thread-coordination.md`, which
recorded the module structure built in the previous harness. Where the two disagreed, the older
one usually won: it had eleven modules and a four-stage estimator worked out in detail, and the
newer one had been written without knowledge of it.

## What this project is

A reproduction and extension of Davey, Gordon, Holland, Rutten and Williams, *Bayesian Methods
in the Search for MH370* (Springer, 2016), aimed at a paper for the *Journal of Navigation*. The
chain runs from the 18:01:49 radar prior through the Inmarsat handshakes to 00:19, then onward to
ocean impact, sinking, seafloor drift, surface drift, hydroacoustics, searched-area disconfirming
evidence and conditional hypotheses.

Two things follow from "reproduction and extension", and every session must keep them apart:

- **Reproduction.** `config/davey2016.toml` is Davey's model on Davey's priors. It must stay
  byte-reproducible. Do not change its defaults. Everything the book specifies is audited in
  `results/davey-2016-reference.md`, including two places where the book contradicts itself.
- **Extension.** Fuel, vertical-rate BFO, tempering, branching, hypotheses. Every one of these is
  config-gated and defaults **off**. A result that needs an extension names it in its config.

Published work is input, not truth. Departures from it are recorded — in `README.md` for the
core, in the `lib.rs` doc comment for a hypothesis — never left implicit.

## The estimator: one filter, four stages

1. **Core filter.** Runs from the 18:01 prior (or an 18:22 prior) through the SATCOM data. For
   the integrated estimate it stops at 00:11, and the hand-off resamples its posterior, carrying
   each trajectory's full state, as the starting distribution for stage 2.
2. **End of flight.** Continues each trajectory: powered flight on the core dynamics until the
   end-of-flight module takes over; the module simulates descents to impact; the runner scores
   whichever 00:19 messages the config selects.
3. **Impact-level modules.** Each returns a log-likelihood per impact sample.
4. **Composer.** Combines any chosen set of modules into one posterior. Reports evidence,
   effective sample size and replicate agreement, and writes `summary.json` for the report.
   Results are shown per end-of-flight hypothesis first; any average across them appears only
   beside a prior sensitivity.

### Build status, honestly

| stage | interface | model |
|---|---|---|
| 1 core filter | **built**, 53 tests pass | **built and validated** against Fig. 10.3 |
| 2 end of flight | **built** — `Terminal` trait (`families`, `latent_columns`, `takeover_time`, `descend`), `handoff.npy`, `terminal.rs`, `impacts.rs` | **placeholder only** — `hypotheses/arc-kernel` is plumbing, not a model; it returns NaN impact energies |
| 3 impact modules | **built** — `ImpactView`, `impact_log_likelihood`, `predict`, `mh370 evaluate` | **none** |
| 4 composer | **not built** — `main.rs:71` rejects a `[[compose]]` section | — |

So stage 1 is finished science, stages 2 and 3 are empty frames, and stage 4 does not exist. Any
plan that treats the downstream modules as nearly-done is wrong.

### The hook API

In the filter: `adjust_prior` (and `adjust_stratum_prior`), `extra_epochs`,
`epoch_log_likelihood`, `final_log_likelihood`, with `StateView`.

After it: `impact_log_likelihood(impact, choice)` and `predict(impact, out)` per impact sample,
with `ImpactView`; or the `Terminal` trait for the end-of-flight module.

Declarations: `observations()` (the observation IDs consumed, each used once per run, e.g.
`"m0019a.bfo"`), `alternatives()` (discrete choices with priors; an alternative shared across
modules is declared by the same name and marginalised jointly), `absolute_scale()` and
`prediction_columns()`.

`ImpactView` currently carries: parent, time, latitude, longitude, ENU velocity, flight-path
angle, mass, total and vertical kinetic energy, descent family, takeover time/place/altitude,
mode, alternative, latents. **Three fields the downstream modules will need are missing** — see
the open decisions below.

## Composition rules every module follows

These are carried forward unchanged from the previous harness. They are the reason modules can be
built independently and still combine into something defensible.

1. Return the likelihood of your data given the state, never a posterior. Remove any internal
   reference prior yourself. Say whether your likelihood is on an absolute scale; only
   absolute-scale likelihoods can be mixed across alternatives.
2. Each observation is used once per run. List the observation IDs you consume.
3. All impact modules use the same impact samples. Never smooth privately over impact location:
   the product of separately smoothed likelihoods is not the smoothed product.
4. Likelihoods must be smooth, with explicit model error. No floors. "Not computed" (NaN) is not
   "impossible". Cover the prior's support or refuse.
5. Be accurate where the other evidence is: where the flight posterior has its mass, roughly
   30–40°S along the 7th arc, not only near your own peak.
6. Measure Monte Carlo adequacy (ESS, split-half replicate agreement). Report unconverged results
   as unconverged; the fix is the sampler, never the smoothing.
7. Settle discrete model choices by evidence, or show them as labelled sensitivities. Never use
   fixed-weight averages of normalised maps.
8. Include one synthetic-recovery test (generate your data from a known state and check
   coverage), plus hand-computed fixtures.

## Modules and ownership

One session per module. The directory is the unit of ownership; two sessions editing one file is
the failure mode this document exists to prevent. The module set is the one established on
28 September, mapped onto this workspace's layout.

| module | owns | status |
|---|---|---|
| **architecture** | this file, `RUNBOOK.md`, merge order, `ImpactView` and hook changes. Writes no module code. | — |
| **core estimation & sampler** | `engine/crates/{geo,satcom,flight}`, `crates/mh370/src/{filter,config}.rs`, `config/davey2016.toml`, sampler configs | validated; convergence work ongoing |
| **fuel & performance** | `crates/flight/src/fuel.rs`, `config/sensitivity/{stage2,stage3,endurance,reject,fuel-smoke}*` | complete, validated, used by 16 of 51 configs |
| **core stages & composer** | `crates/mh370/src/{handoff,terminal,impacts,main}.rs`, `crates/hypothesis` | stages 1–3 built, **stage 4 to build** |
| **end of flight** | `hypotheses/end-of-flight` (to create); descent families, breakup | placeholder only |
| **ocean drift** | shared `crates/ocean`, then `hypotheses/debris-drift` | not started |
| **impact to seafloor (settling)** | `hypotheses/settling` | not started; brief written |
| **searched areas** | `hypotheses/seabed-search` | not started; rulings in `seabed-search-rulings.md` |
| **hydroacoustics** | `hypotheses/hydroacoustics` | not started |
| **Pleiades / COSMO-SkyMed** | `hypotheses/pleiades` | not started; sightings note exists |
| **antenna gain** | `hypotheses/antenna-gain` | **parked** deliberately, not integrated |
| **reporting & paper** | `engine/report/*.py`, `paper/` | report at 8 pages |

WSPR remains a low-priority option, worth doing mainly to establish whether it works at all.

`filter.rs` and `config.rs` are touched by core, fuel, sampler and every hypothesis that adjusts
a prior. They are the real conflict risk, and the reason the architecture session exists.

## How sessions coordinate

**There is no live channel between sessions.** A session can read another's transcript after the
fact but cannot message it. Anything another session must act on goes in the repo, not in
conversation. Coordination is asynchronous through exactly three shared stores:

1. **The git repo** — the source of truth. Each session gets its own workspace and therefore its
   own clone; the previous harness used git worktrees off one checkout, which does not apply
   here. One branch per module, pushed to the shared remote. Commit and push before going quiet:
   a session holding uncommitted work blocks everyone.
2. **The artifact store** — project-scoped, so `host.artifacts()` from any session sees every
   figure, table and note any other session has saved. Prefer this to re-deriving.
3. **Project memory** — conventions, decisions, hard-won negatives. Good for "we tried X, it
   failed, here is the measurement". Bad as a task queue.

Merge policy: a module merges its own branch when its tests pass **and** it owns every file it
touched. Anything touching `filter.rs`, `config.rs`, `main.rs` or `crates/hypothesis` goes to the
architecture session for review first.

## The binding constraint is compute, not context

This machine has **18 cores and 64 GB**. A full-scale run is 7M particles × 8 replicates and
saturates all of them; fuel plus tempering takes about six hours.

**Rule: wrap any job expected to exceed ~10 minutes or ~4 GB in**

```sh
lockf -k /tmp/.mh370-heavy.lock <command>
```

so heavy jobs **queue** instead of competing. (BSD `lockf` replaces Linux `flock`, which macOS
does not ship; `-k` keeps the lock file, and a second job waits indefinitely for the first —
verified.) Smoke runs at 200k particles per mode are cheap, under a minute, and need no lock.
Figure and report work is free; do it while someone else holds the machine.

This rule is mechanical, and it replaces the advisory "claim the machine in `RUNBOOK.md`" that
preceded it. The reason is a measured failure: on 4 October two 7M-particle runs of the same
configuration ran concurrently for some hours, and load average reached 210 with zero free cores.
The per-replicate times, from the `final.npy` mtimes, were 43 and 41 minutes for the two clean
replicates, then 316 and 317 minutes — **7.5×** — for the two that followed. That window also
contains a lid-close suspension, so the whole 7.5× is not attributable to contention alone. The
cleanly attributable figure is the next replicate, which overlapped the second process for about
half its length and took 74 minutes, **1.75×**. A lock would have made the second job wait.

Worse, the sandbox has **no process table** (`ps -A` returns nothing,
`pkill` reports "Cannot get process list") and the engine's only cancellation hook is an
in-process flag used by `serve`, so a runaway job cannot be signalled; the only way to stop one
is to make its output path unwritable and let its next write fail. Prevention is the only
control available.

**Never end a turn while a long run is in flight.** The session idles, the kernels are torn down,
and child processes are suspended with it. Hold an active poll instead.

## Conventions that are not obvious

- **Negative results are kept**, reproducible behind a config flag, not deleted. Four of the five
  sampler interventions failed and all four remain runnable; the pattern across them is a result
  in its own right.
- **Cite Davey by printed book page**, not PDF position — they differ by fourteen. See the
  verified mapping in `results/davey-2016-reference.md`. All existing citations have been audited
  against the book's anchor text; `shoulder-comparison.md` had cited PDF positions throughout and
  has been corrected. New citations must be verified the same way, not inferred by offset.
- **Report arc-miss distances in kilometres of slant range** and as ratios, never as a count of
  sigma.
- **Quote split-half as mean and range** over all balanced partitions, against a
  replicate-count-dependent floor: 0.896 at 4, 0.914 at 6, 0.924 at 8
  (`results/split-half-threshold.md`). The 0.90 in the code is ours; Davey published no
  quantitative convergence criterion at all.
- **Per-epoch ESS is not replicate agreement.** Raising the worst epoch's ESS 4.3× once changed no
  convergence measure. Chase ESS only where the degeneracy is a caustic.
- **Seed-stable estimates only; smoke runs are never evidence.**
- **Results as figures, not just numbers**, and save a PNG beside every PDF page.
- **Never commit** `data/fuel-tables.json` (Boeing-derived), the large `.bin` grids, or the Davey
  PDF (CC BY-NC, so not redistributable from a public repo). See `LARGE_FILES.md`,
  `results/PROVISIONING.md` and `.sources/davey-2016/README.md`.
- **The build needs** `CARGO_HOME` and `XDG_CONFIG_HOME` pointed inside the workspace, and
  `git config --local core.excludesFile ""`, or cargo fails on an unreadable `~/.config/git`.
- **Keep `ISO Sept 28 Status/` frozen.** It is a snapshot, not a working directory.

## Open architecture decisions

These need Pete's ruling before modules are tasked.

1. **Composer before end of flight.** Recommended. Stage 4 is the only stage with no
   implementation at all, it is small — combine log-likelihoods over shared impact samples, report
   evidence, ESS and replicate agreement — and until it exists no downstream module can be
   integration-tested. The end-of-flight model is by contrast a genuine modelling problem and can
   proceed in parallel against the `arc-kernel` placeholder. Building the composer first also
   forces `ImpactView` to be settled before five modules code against a frozen struct.
2. **Settling stays a separate module, and is not optional.** Searched areas must be compared
   against a **wreckage** PDF, not an impact PDF, so the transform from impact point to resting
   place sits between end-of-flight and searched areas on the critical path. It is a transform,
   not a likelihood: it exposes `prediction_columns()` and `predict()`, and returns no
   log-likelihood of its own.
3. **Three additions to `ImpactView`**, needed before modules freeze against it:
   - **attitude at impact** beyond flight-path angle (at least heading and bank), which the
     end-of-flight and hydroacoustic source models both need;
   - **dissipation duration τ**, without which the hydroacoustic source term η(γ, ż, attitude,
     breakup, τ) cannot be evaluated;
   - **debris class**, which both drift and settling need — a wing panel and an engine do not
     sink or drift alike.
4. **Who owns `crates/ocean`.** Surface drift and settling both need ocean transport. The
   previous harness gave the shared component to the drift module on a `core/ocean-transport`
   branch and had settling depend on it. That still looks right, but it makes settling wait.
