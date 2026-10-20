# Shared contract for MH370 project threads (v1, 17 Oct 2026)

Replaces `ISO Sept 28 Status/threads/master-prompts/common.txt` (ISO-era; its machine, paths, thread IDs and
`iso` commands no longer apply). Every module brief points here. Keep this file short; module detail belongs in
the module brief, and changing state belongs in the module status file.

## How a thread uses the project files

A thread is opened for one task or question. It reads, in this order:
1. this file;
2. the brief of the module it works on, `threads/master-prompts/<module>.md` (purpose, contract, methods);
3. that module's status file, `threads/status/<module>.md` (current results, where they are, open questions).

The coordination inboxes (`coordination/<MODULE>.md`) are a log, not a source of truth. Read only the entries
the task needs. The shared memory store is a convenience: when the store and the repo disagree, the repo wins,
and a brief never tells a thread to rely on what it remembers.

When the task is done, the thread (a) commits its results, (b) updates the module status file, (c) adds one short
entry to the module inbox, and (d) reports to Pete. Steps (b) and (c) are what let the next thread start cold.

## Pete's research principle (17 Oct 2026)

No single type of evidence can solve this case. The satellite and flight-simulation data, ocean drift,
hydroacoustics, the searched areas and the imagery are each sparse and each leaves the problem
underdetermined. A solution, if there is one, comes from combining all of them. Prior work leaned too far on one
kind of evidence, and false precision is a real risk, especially from the satellite data: its posterior peaks near
37 S, but valid solutions exist far up the arc and only one has to be true. Therefore every module:
- reports what its own evidence says alone, with a flat prior along the 7th arc, as well as combined with the core;
- reports the disagreement between its evidence and the core with the named statistics of the composer protocol
  (shift of the mean latitude, log Bayes factor against a uniform reference, two-way 90 % region overlap, mode
  displacement in NM, ESS ratio), per alternative and for the mixture, with Monte Carlo error bars;
- never reduces a disagreement by down-weighting its own evidence or the core's.

## The estimator

1. Core filter: 18:01 (or 18:22) prior through the satellite data to the 00:11 hand-off.
2. End of flight: powered flight to takeover, descent to impact, scoring of the selected 00:19 data treatment
   (D0' held out, D1-D5 declared alternatives; Pete's ruling: sample all, pick none).
3. Impact-level modules each return a log-likelihood per impact sample (drift, Pleiades, hydroacoustics,
   searched areas, settling).
4. The composer combines a chosen set of modules, reports evidence, ESS and replicate agreement, per end-of-flight
   family and treatment first, averages only beside a prior sensitivity.

The current run is named in each status file (17 Oct 2026: core run J; end of flight run J, four families).

## Composition rules (all modules)

1. Return the likelihood of your data given the state, never a posterior; remove any internal reference prior.
   State whether the likelihood is on an absolute scale.
2. Each observation is used once per run, under declared IDs.
3. Score the shared impact samples. Never smooth privately over impact location.
4. Smooth, with explicit model error, no floors. "Not computed" (NaN) is not "impossible": flag it, count it, and
   carry it at the seed's weighted mean likelihood (ruling 15 Oct); a module whose not-computed share of core mass
   exceeds 10 % abstains for that run.
5. Be accurate where the other evidence has mass (the current core numbers are in the status files; do not copy
   them into briefs).
6. Measure Monte Carlo adequacy (ESS, split halves, seed bootstrap). Report unconverged results as unconverged;
   the fix is the sampler, never smoothing.
7. Discrete model choices shared between modules (e.g. `ocean-model`, shared by drift and Pleiades) are declared
   by the same name and marginalised jointly. Their weights follow the module brief's declared policy; weights
   learned from the same evidence the module scores are a labelled diagnostic, not the headline.
8. One synthetic-recovery test plus hand-computed fixtures per module.
9. Re-pointing a module at a new core or end-of-flight run is a scoring pass. A new transport or simulation run must
   be justified by a measured coverage or noise failure named in the module brief.

## Where things live

- Repo: github.com/gmkf7vfyfb-web/flight-mh370-revisited, branch `claude-science-sep29`, folder
  `Claude Science Project Sep 29/`. The `ISO Sept 28 Status/` and `Archive ISO Pre Sept 28/` folders are a frozen
  snapshot: read, never edit.
- Results: small results (tables, surfaces, figures, scripts) are committed under `results/<topic>-<date>/`.
  Large files go to `~/Downloads/mh370-exchange/<module>/` on the Mac with SHA256SUMS. Nothing that cost more than
  a few minutes may live only in a session workspace: workspaces are swept.
- Compute: the Mac (18 cores) and deskstar (`ssh:deskstar`, 88 threads, 36 GiB, heavy jobs under
  `flock ~/.mh370-heavy.lock`). Mac disk floor: 5 GB free (Pete, 10 Oct). Large copies off the Mac are Pete's.
- Ocean data: `~/Downloads/mh370-ocean-data` (Mac) and `~/.claude-science-scratch/ocean` (deskstar, 15-160 E).

## Reporting to Pete

- Plain language with numbers; say what is uncertain; never claim results from smoke runs.
- Charts: no project codes in titles, axes or legends; standard statistical terms used as they are; every chart
  has two short footnotes, a plain-English one (ASD-STE100 style) and a technical one, together no more than the
  bottom quarter, stating the key parameters and assumptions.
- Decisions that are Pete's (detection levels, priors, which evidence is primary) are asked, not assumed. Until he
  rules, the result is a labelled sensitivity.
