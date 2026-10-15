
# Core handover, and the item 10 work order — 15 October 2026

Pete's trade-off, adopted: the existing long core thread is used for ONE bounded turn to write a
handover, and no run. Everything after that happens in a fresh core thread.

---

## 1. Paste prompt for the EXISTING core thread (one turn, no run)

> Handover task only — no run, no build, no core request, and nothing that loads the machine.
> Write `Claude Science Project Sep 29/threads/work-orders/core-handover-2026-10-15.md` on
> branch `claude-science-sep29`, commit and push it, and then stop. It must be self-contained
> for a fresh thread that has never seen this one. Cover exactly these eight headings, and where
> you give a command give it verbatim:
>
> 1. **Build environment.** Toolchain path, CARGO_HOME, RUSTUP_HOME, XDG_CONFIG_HOME, the
>    absolute CARGO_TARGET_DIR rule, and why each is needed. Include the `core.excludesFile`
>    fix and the harmless keychain warning.
> 2. **Regression gates, with expected values.** The byte-identity check (seed 1 of the base
>    configuration returning log evidence −96.66146918417472 to every digit), `make scope`,
>    `make smoke`, the smoke byte-identity gate against the current binary, and what each one
>    would catch.
> 3. **Determinism and random-number discipline.** What preserves byte-identity when the step
>    loop is touched, and what silently breaks it.
> 4. **Core request 9, the targeted sampler**: what is built, which config keys drive it, what
>    has been tested, what has never been run, and what you expect to go wrong first.
> 5. **Configuration lineage**: davey2016 to no-exhaustion-prior to run I, what differs at each
>    step and which differences are model changes rather than sampler changes.
> 6. **Deskstar launch mechanism**: job chaining, the DONE markers, compaction, and staging back
>    to the Mac.
> 7. **Traps that have cost time**: at least the ones about `cargo test --release` not
>    rebuilding, float32 quantisation of stored times, `summary.json`'s single-partition
>    split-half, and anything else you would warn a successor about.
> 8. **Open core items** with their current state, including the aimed northern-arc proposal
>    and the 18:25:27 R600 epoch.
>
> Write what a successor needs, not a history. If something is uncertain, say so.

That is a writing task on knowledge the thread already holds, so it should be one turn and should
not need to re-read its own history in depth.

---

## 2. Item 10 work order — for the NEW core thread, after the handover lands

**Not to be started without Pete's explicit GO.**

### Standing facts
Core run I is not converged (all-partition split-half: waypoints 0.916, free flight 0.830,
against the 8-replicate floor 0.924). Free-flight convergence is limited by how many 18:01–22:41
lineages survive 00:11 — about 1,700 per seed — and a resample-move at 23:15 was tested and
changed nothing (ln Z delta −0.01, lineages identical), so refresh moves are not the remedy.
Read `core-handover-2026-10-15.md` before touching anything.

### The problem
Any arm scoring both 00:19 bursts is below 1,000 effective impacts, and Holland's two readings
are below 100. Measured effective hand-off parents per stratum per seed over 100,000 parents:
50,966 with no 00:19 data, 3,983 under the 00:19:29 burst, 216 under the 00:19:37 burst, 170
under both with the transient bias added, 38.8 under both as recorded — where the largest single
trajectory carries 12.3 per cent of the weight. In three of those arms the effective impacts
equal the effective parents, so one child in 32 carries the weight and no within-parent proposal
can help. **The constraint is the 00:11 hand-off: roughly ten of 100,000 cruise states can
produce the 00:19 pair.**

### The task
Wire and validate core request 9 so that the proposal already carries the 00:19 data — a
hand-off drawn with the 00:19 bursts in hand, with exact prior-to-proposal importance weights.
Then one core run of the four families.

### Acceptance
1. Byte-identity gate passes with the feature off.
2. Prior recovery under the importance correction: with the aim active and the likelihood off,
   every aimed latent recovers uniform on its full support. The end-of-flight aimed proposals
   reach a maximum deviation of 0.0030; use that as the standard.
3. Effective hand-off parents for `both/no-offset` and `both/startup-offset` reported before and
   after, per stratum per seed. The target is 1,000 effective impacts per arm; below that the
   arm stays unquotable and the run has not succeeded.
4. All-partition split-half for every stratum, against the count-dependent floor.
5. A COVERAGE section, and a statement of whether this changed the prior or only the precision.

### Out of scope
Any change to the 00:19 likelihood itself, the family priors, the fuel model, or the end-of-flight
stage. Widening any prior. Note that convergence for free flight and waypoints shares this run:
specify both before launching, so one run serves both.

### Stop conditions
Stop and report if prior recovery fails, if the byte-identity gate moves, or if the effective
parent count does not improve at smoke scale — in that last case the hand-off constraint is not
addressable by a proposal and that is itself the finding.
