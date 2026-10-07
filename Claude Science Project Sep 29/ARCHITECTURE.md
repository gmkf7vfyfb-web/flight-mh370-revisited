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
| 4 composer | **not built** — `main.rs:71` rejects a `[[compose]]` section | **specified**, in `ISO Sept 28 Status/threads/master-prompts/core-stages.txt` §D6; needs no prompt of its own |

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
| **core stages & composer** | `crates/mh370/src/{handoff,terminal,impacts,main}.rs`, `crates/hypothesis` | stages 1–3 built, **stage 4 to build**, plus two core requests: the three `ImpactView` additions, and the wreckage-sample stage of decision 2 |
| **end of flight** | `hypotheses/end-of-flight` (to create); descent families, breakup | placeholder only |
| **shared ocean transport** | `crates/ocean` on `core/ocean-transport`. No hypothesis, no likelihood | not started. Created by decision 4; **three consumers wait on it**, so its API is specified from drift, settling and Pleiades together before it builds |
| **ocean drift** | `hypotheses/debris-drift` only — `crates/ocean` is **no longer** drift's, see decision 4 | not started; brief written, and stale on that ownership |
| **impact to seafloor (settling)** | `hypotheses/settling` | not started; brief revised as `threads/master-prompts/settling.md`. Emits **wreckage samples**, not summary columns. Uncommitted prior work in `ISO Sept 28 Status/code/uncommitted/settling-untracked.tar.gz` |
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

## Architecture decisions — ruled 6 October

The four decisions this section used to pose have been ruled. Recorded here as settled, with the
reasoning, because a module session needs to know what is decided and what is still moving.

1. **Composer before end of flight: reshaped, not adopted as posed.** The composer does not gate
   the end-of-flight *dynamics*, which is the long pole and depends on none of it. It must exist
   before the first end-of-flight impact samples are composed with anything. So it runs as a small
   parallel track rather than as a gate. It needs no master prompt of its own: `core-stages.txt`
   §D6 already specifies it — evaluate `impact_log_likelihood` on `impacts.npy` per enabled module
   and alternative; evidence sets from config; per-(replicate, mode) evidence increments so
   `summary.rs` pooling stays correct; ESS per factor and the posterior probability of each
   alternative; shared alternatives aligned **by name** and marginalised jointly across modules;
   composed PDFs on a 2-D equal-area grid extending `summary.rs` rather than a second summariser.
2. **Settling: separate, non-optional, and a transform.** Ruled as posed. It returns no
   log-likelihood of its own, because there is essentially no observed MH370 seabed debris to
   score and the one scoreable fact — the search having found nothing — belongs to searched areas.
   **Its output is carried as samples, not as summary columns**: each impact sample fans out into
   wreckage samples with the parent's weight split across them, the seabed analogue of the
   end-of-flight hand-off. The reason is that searched areas' detection probability depends on the
   extent and piece sizes of the field, not only on its centre, and summary moments discard
   exactly that. This needs a new runner stage — a core change owned by core stages & composer,
   not by settling and not by end of flight. The draw count is set by measuring what searched
   areas needs to resolve its coverage polygons; the column form stays as a cheap fallback.
3. **Three additions to `ImpactView`: ruled in.** Attitude at impact beyond flight-path angle (at
   least heading and bank); dissipation duration τ, without which the hydroacoustic source term
   η(γ, ż, attitude, breakup, τ) cannot be evaluated; and debris class, because a wing panel and
   an engine neither sink nor drift alike. Required by the end-of-flight module's own stated
   purpose, which is the position *and attitude* of arrival, the energy, and the *duration* of the
   surface-impact event. Granularity is settled: the impact sample carries a debris **class**, and
   settling generates the object ensemble from class plus energy and attitude. The sample is not
   variable-length.
   What a module *emits* is not what a consumer *conditions on*. Settling's first pass conditions
   breakup families on vertical and total kinetic energy plus flight-path angle only, carrying
   attitude and τ unused, because sink rate spans two orders of magnitude of seabed displacement
   while attitude at impact comes out of the least-constrained part of the dynamics. The fields are
   emitted anyway: the sensitivity test they permit is cheap, retrofitting them is not.
4. **`crates/ocean` goes to a third owner, not to drift.** A **shared ocean transport** module owns
   `crates/ocean` on branch `core/ocean-transport`, delivering the transport API, its data
   provisioning and its tests, with no hypothesis and no likelihood of its own. Drift, settling
   **and Pleiades** all depend on it — Pleiades included, because connecting an imaged debris field
   to an impact requires transport from impact time to sighting time. The cost accepted with this
   ruling: three consumers now wait on one producer, so its API must be specified from all three
   sets of requirements before it builds.

### Two standing conventions that came out of the same pass

- **A conditional is labelled on every figure.** Conditioning on a latent (exhaustion time) is
  legitimate; selecting trajectories by whether they could reach a hypothesised outcome is not.
  The Pleiades hypothesis enters as a log-likelihood on the shared impact samples, so its subset
  emerges as a posterior reweighting. Pre-selection is admissible only as a compute saving, and
  then the band must be a generous superset of the support with the boundary diagnostic attached.
- **`.md` files: none inside `engine/`.** That tree allows exactly three — `README.md`,
  `AGENTS.md`, `status.md`. Assumptions and sources go in the `lib.rs` doc comment; status goes in
  `hypothesis.toml`; write-ups go to the project-level `results/`, a sibling of `engine/`.

## Still open

1. The wreckage-draw count per impact, pending agreement with searched areas.
2. The freeze of the shared breakup field — the same object as the `ImpactView` debris class —
   pending requirements from settling, drift and hydroacoustics.
3. Provisioning of bathymetry and full-depth ocean reanalyses on this machine.
4. Whether the end-of-flight entry point stays the fuel-exhaustion-window conditional once the
   fuel burn defect is fixed and the dry fraction rises.
5. **Whether drift and Pleiades are downstream of settling.** Both need the sink-versus-float
   partition, and so does settling, from the same element-class physics. One partition owned by
   settling is correct on rules 3 and 4 but makes two modules wait; independent partitions give
   two incompatible answers to one physical question. A third arrangement — settling delivers the
   float partition first, ahead of its sinking physics — would unblock drift without splitting the
   physics. See `results/impact-interface-requirements.md` §6. This changes the merge order, so it
   is Pete's ruling, not the architect's.
6. Where seafloor-depth lookup lives in the shared layer: hydroacoustics and settling both need
   it, from one bathymetry surface, never computed twice.
