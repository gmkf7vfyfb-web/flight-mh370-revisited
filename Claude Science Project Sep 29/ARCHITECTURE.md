# Project architecture and how parallel sessions work together

Read this first if you are a session joining this project. It says who owns what, how sessions
coordinate, and what the binding constraints are. It is deliberately short; the science lives in
`results/`, and the reference the project reproduces is catalogued in
`results/davey-2016-reference.md`.

## What this project is

A reproduction and extension of Davey, Gordon, Holland, Rutten and Williams, *Bayesian Methods
in the Search for MH370* (Springer, 2016), aimed at a paper for the *Journal of Navigation*. The
chain runs from the 18:01:49 radar prior through the Inmarsat handshakes to 00:19, then onward
to ocean impact, drift, hydroacoustics, seafloor drift, searched-area disconfirming evidence and
conditional hypotheses.

Two things follow from "reproduction and extension", and every session must keep them apart:

- **Reproduction.** `config/davey2016.toml` is Davey's model on Davey's priors. It must stay
  byte-reproducible. Do not change its defaults. Everything the book specifies is audited in
  `results/davey-2016-reference.md`, including two places where the book contradicts itself.
- **Extension.** Fuel, vertical-rate BFO, tempering, branching, hypotheses. Every one of these
  is config-gated and defaults **off**. A result that needs an extension names it in its config.

## Modules and ownership

One session per module. The directory is the unit of ownership; two sessions editing one file is
the failure mode this document exists to prevent.

| module | owns | depends on |
|---|---|---|
| **core estimation** | `engine/crates/{flight,satcom,geo}`, `engine/crates/mh370/src/filter.rs`, `config/davey2016.toml` | — |
| **fuel** | `engine/crates/flight/src/fuel.rs`, `config/sensitivity/{stage2,endurance,reject}*` | core |
| **sampler** | `filter.rs` sampler blocks, `config.rs` `SamplerConfig`, `config/sensitivity/{tempered,branching}*` | core |
| **hypotheses** | `engine/crates/hypothesis`, `engine/hypotheses/`, waypoint and descent scenarios | core |
| **drift / acoustics** | downstream of 00:19; not yet started | core outputs |
| **reporting** | `engine/report/*.py` | reads every run |
| **paper** | `paper/`, figure selection, narrative | reads `results/` |

`filter.rs` is owned by two modules and is the one real conflict risk. If you are the fuel or
hypotheses session and need to touch it, say so in `RUNBOOK.md` first.

## How sessions coordinate

There is **no live channel between sessions.** Coordination is asynchronous through shared
state, and there are exactly three kinds:

1. **The git repo** — the source of truth. Branch `claude-science-sep29`. Commit and push before
   going quiet; a session that holds uncommitted work blocks everyone else.
2. **The artifact store** — project-scoped, so `host.artifacts()` from any session sees every
   figure, table and note any other session has saved. Prefer this to re-deriving.
3. **Project memory** — conventions, decisions and hard-won negatives. Good for "we tried X and
   it failed, here is the measurement". Bad as a task queue.

A session can read another session's transcript after the fact, but cannot message it. Anything
another session must act on goes in the repo, not in conversation.

## The binding constraint is compute, not context

This machine has **18 cores**. A full-scale run is 7M particles × 8 replicates and saturates all
of them; the fuel-plus-tempering configuration takes about six hours. Two sessions launching
full runs concurrently roughly halves both and makes the timings in `results/` meaningless.

**Rule: one heavy run at a time, claimed in `RUNBOOK.md` before launching.** Smoke tests at
200k particles per mode are cheap (under a minute) and need no claim. Figure and report work is
free — do it while someone else holds the machine.

## Conventions that are not obvious

- **Negative results are kept**, reproducible behind a config flag, not deleted. Four of the
  five sampler interventions failed and all four remain runnable; the pattern across them is a
  result in its own right.
- **Cite Davey by printed book page**, not PDF position — they differ by fourteen. See the
  verified mapping in `results/davey-2016-reference.md`. Page citations in results files written
  before the book was obtained are unverified and need auditing.
- **Report arc-miss distances in kilometres of slant range** and as ratios, never as a count of
  sigma.
- **Quote split-half as mean and range** over all balanced partitions, against a
  replicate-count-dependent floor: 0.896 at 4, 0.914 at 6, 0.924 at 8
  (`results/split-half-threshold.md`). The 0.90 in the code is ours, not Davey's.
- **Per-epoch ESS is not replicate agreement.** Raising the worst epoch's ESS 4.3× once changed
  no convergence measure at all. Chase ESS only where the degeneracy is a caustic.
- **Never commit** `data/fuel-tables.json` (Boeing-derived) or the large `.bin` grids. See
  `LARGE_FILES.md` and `results/PROVISIONING.md`.
- **The build needs** `CARGO_HOME` and `XDG_CONFIG_HOME` pointed inside the workspace, and
  `git config --local core.excludesFile ""`, or cargo fails on an unreadable `~/.config/git`.

## Current state

Reproduction verified against Fig. 10.3. Convergence addressed by annealed SMC at 18:39 and
19:41 (`results/tempering.md`): split-half 0.9416 against a 0.924 floor, replicate median span
tightened 27%, posterior unmoved. Davey's branching resampler implemented and measured
(`results/branching-resampler.md`): reproduces the evidence, does not fix 19:41. Fuel model
complete and validated, exercised by 16 of 51 configs, and being combined with the convergent
sampler for the first time in `config/sensitivity/best-model.toml`.

Open, in rough priority: no run reproduces more than about a third of Davey's shoulder mass and
the reason is unresolved; the descent stratum, which would make the implemented-but-inert
vertical-rate BFO term consequential; the conditional waypoint hypothesis; MH371 validation of
the vertical-rate term against ACARS truth; and a wider Mach prior now that fuel can constrain
it. Fidelity items outstanding: manoeuvre step 5 s where the book uses 1 s, R600 σ 63 µs where
the book says 62, and `locate()` in `environment.rs` silently clamping out-of-range queries.