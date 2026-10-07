# CORE_STAGES inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-08 - architecture

**Core request 10: `handoff_epochs`, a snapshot list that does not stop the filter.**

Pete wants one ~16 h run to deliver three things: the reference posterior at 00:19:37, a 22:41
hand-off for the planned-descent arms, and a 00:11 hand-off for the unpiloted arm. **The engine
cannot do that today.** `TerminalConfig` (config.rs:52) carries a single `arc: String`, and
`terminal.rs:67` refuses a block with no bursts after the stop. One run therefore yields one
hand-off epoch and no 00:19:37 posterior. Launching the run as Pete imagines it would consume
16 hours and deliver a third of what he expects.

The request, in the smallest form that fixes it:

- Add `handoff_epochs: Vec<String>` (empty by default) read at the top level of the run config,
  NOT inside `[terminal]`. Writing a snapshot and stopping the filter are separate concerns and
  the `[terminal]` refusal should not govern the former.
- At each named epoch, write the full 42-field state - every field the existing hand-off writes,
  including `mass_kg`, `fuel_kg` and `realised_flameout_unix_s` from f07e9f0 - and **carry on**.
- The snapshot is the **unscored filtering state** at that epoch. The engine does no terminal
  scoring for it. The downstream module owns every burst after the snapshot epoch.
- `[terminal]` keeps its present behaviour unchanged for runs that genuinely want the engine to
  stop and score. `handoff_epochs` is additive.
- Byte-identity gate: with `handoff_epochs = []` every output must be byte-identical to today.
  With it non-empty, `final.npy` must be byte-identical to the same run without it - writing a
  snapshot must not touch the RNG stream or the weights.

**A distinction that must be stated wherever these three outputs are used together.** The
00:19:37 posterior is conditioned on all the data. The 22:41 and 00:11 snapshots are the
filtering distributions at those instants and have not seen the later bursts. They are
different objects, not truncations of one another, and a figure that overlays them without
saying so is wrong. This is deliberate: the descent arms need an unconstrained-by-later-data
seed precisely because the module re-scores those bursts under its own dynamics.

If you judge a cleaner shape, say so in this file - the requirement is one run serving all three,
not this particular spelling.

## 2026-10-08 - architecture, on core request 10 as built

**Resume. Three notes, one of which changes a launch parameter.**

**1. Keep `handoff_epochs` in `[output]`. Do not move it.** The requirement was that it not live
in `[terminal]`, because the terminal block' refusal must not govern snapshot writing. `[output]`
satisfies that and is a better home than the top level. Spelling churn on a reviewer' preference
is not worth your time or the risk of touching a working tree before a 16-hour launch.

**2. Use the SAME seeds as `no-exhaustion-prior`, and make full-scale byte-identity the headline
acceptance check.** The datasheet records that `no-exhaustion-prior` reused `6temper-realloc`'
seeds, so seed reuse is already this project' convention. If this run is `no-exhaustion-prior`'
configuration plus the snapshots, then `final.npy` should come out **byte-identical to**
`no-exhaustion-prior`' `final.npy`. That is a far stronger test than the smoke-scale comparison
you have planned: it exercises the snapshot machinery against six-stage tempering at 7M particles,
where an interaction with the RNG could appear that a reduced configuration would never show. It
also gives every downstream figure a clean provenance sentence - the hand-offs come from the
reference posterior itself, not from a different realisation of it. If the file differs, we have
learned that on a run we needed anyway.

The alternative - fresh seeds, for 8 more replicates poolable with the existing 8 - is tempting
because the reference run FAILS convergence (split-half 0.9020 against a 0.924 floor for 8
replicates, replicate median span 0.339 deg). **Reject it here.** The split-half floor is itself
a function of replicate count, so it is not established that 16 replicates clears it, and
buying a convergence attempt as a side-effect of a hand-off run means a result we cannot cleanly
attribute to either purpose. Convergence deserves its own designed run.

**3. Your third check is the right one, and extend it by one line.** Confirming that the 00:11
snapshot from a carrying-on run gives the same mode probabilities as a run that stops at 00:11 is
exactly the test that proves the snapshot is a filtering distribution. Run the same comparison at
**22:41** as well. At smoke scale it costs minutes, and 22:41 is the epoch the descent arms depend
on, which is the one place an error would propagate furthest before anyone noticed.

Confirm `handoff_floor` is set - 200 was the figure in the sampling design - and the launch is
approved: 7 Hz, 8 seeds, snapshots at 22:41 and 00:11, 20,000 rows each.
