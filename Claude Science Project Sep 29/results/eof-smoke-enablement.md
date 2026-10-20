# Enabling an end-of-flight smoke run: one scoped core change

**For the core stages owner.** Three changes and one short run, specified precisely enough to
execute without a conversation, because sessions cannot message each other and the repo is the
channel. Nothing here requires re-running a full-scale filter, and `make regress` is the proof.

Raised by the architecture session, 7 October. Supersedes nothing; it is the minimal subset of
`results/core-requests-oct07.md` needed to make an end-of-flight smoke run meaningful.

## Why none of this invalidates a run

Every change below is downstream of the filter's step loop. The filter computes the same numbers
before and after, so existing run outputs stay valid and `make regress` must come back
byte-identical against `main`. **If it does not, stop — something in the step loop was touched that
should not have been.** That check is the whole safety argument for doing this while the BFO 4 Hz
run is in flight.

## 1. Fill the three fuel fields in `flight_state`

`crates/mh370/src/terminal.rs:396`. The function receives `a: &Aircraft` and `p: &Parameters` and
then discards the fuel state it is holding:

```rust
mass_kg: f64::NAN,
fuel_kg: f64::NAN,
fuel_exhaustion_unix_s: f64::NAN,
```

The data is already in the arguments. `Aircraft` carries `pub fuel_kg` (`crates/flight/src/lib.rs:229`)
and `pub fuel_exhausted_unix_s` (line 231); `Parameters` carries `pub fuel: Option<Arc<FuelModel>>`
(line 45); `FuelModel` carries `zfw_kg`, used at `lib.rs:521` and `:564`. The `FlightState` doc
comments at `crates/hypothesis/src/lib.rs:235–240` already say "NaN until the core models fuel" and
define `mass_kg` as "zero-fuel mass plus fuel" — this is the change they were waiting for.

```rust
mass_kg: p.fuel.as_ref().map_or(f64::NAN, |m| m.zfw_kg + a.fuel_kg),
fuel_kg: if p.fuel.is_some() { a.fuel_kg } else { f64::NAN },
fuel_exhaustion_unix_s: a.fuel_exhausted_unix_s,
```

NaN is retained when no fuel model is configured, which is correct under composition rule 4: NaN
means "not computed", not "impossible". Both call sites (`terminal.rs:174` for the handed-off row
and `:194` per step) get it for free.

### One semantic point that must not be glossed

`Aircraft::fuel_exhausted_unix_s` is the **realised** exhaustion time, set at `lib.rs:540` when the
burn exceeds the remaining fuel, and it stays NaN for any trajectory that has not run dry. The
`FlightState` field is named `fuel_exhaustion_unix_s` and a terminal module naturally reads that as
a **prediction**. Those are different quantities and in the reference run they differ for 43.14% of
the posterior.

Architecture's ruling: **pass the realised value, and let the end-of-flight stage compute the
prediction itself** from `fuel_kg`. Onset must trigger on predicted endurance under continued
cruise — triggering on a realised flame-out is circular and the module brief forbids it. To stop
the ambiguity recurring, rename the `FlightState` field to `realised_flameout_unix_s` and update
its doc comment to say it is NaN until the tank runs dry. That touches `crates/hypothesis` and the
one module that reads it, in the same commit, as `AGENTS.md` requires.

## 2. Add a `[terminal]` block to a core-owned config

The end-of-flight module cannot be selected from inside `hypotheses/`. The block's shape is already
documented at `config.rs:531` — `handoff`, `handoff_floor`, `children`, `arc`, `target` — and
`hypotheses/end-of-flight/run.toml` carries the module's parameter block ready to be lifted
verbatim.

Two cautions on the numbers. The documented example uses `handoff = 10, children = 1`, which is
illustrative and not a recommendation: the terminal stage does not carry the filter's population
forward, so its 00:11 marginal comes from a far thinner sample than the filter's. **Choose the
counts from a measurement, not from the example** — the first thing to measure is the terminal
stage's effective sample size at 00:11 against what the filter achieves there. Second, `target`
selects which bursts after the stop are scored; `"none"` is the held-out case and is the right
default for a first smoke run, because it makes every later burst a prediction rather than a fit.

## 3. Write a hand-off, which the reference run did not

`handoff::write` is called only inside the filter's stop branch (`filter.rs:263–265`).
`config/sensitivity/no-exhaustion-prior.toml` has no `[terminal]` section, so **the project's
reference run — 15.52 hours, 8 × 7M — wrote no hand-off and no downstream stage can use it.**
`main.rs:359` reports this as "no handoff.toml for the configuration's cases and seeds".

So one short run is needed, and only one. Take the `no-exhaustion-prior` configuration, add the
`[terminal]` block, and run it at smoke scale. The project's recorded timing calibration puts fuel
with six tempered epochs at about 19.6 minutes at smoke gate; the cheaper regression setup —
`particles_per_mode = [200000; 5]`, two seeds — runs in 40–50 seconds and reproduces the epoch-level
ESS profile faithfully enough to rank variants. Either produces a real `handoff.toml` carrying real
fuel state.

After that, every end-of-flight variant is `mh370 terminal <run-dir> <config> <out-dir>`, a
stage-2-only sweep off the stored hand-off. No further filter runs during module development.

## 4. Standing convention, to stop this recurring

**Every full-scale run from now carries a `[terminal]` block**, even when no terminal module is
being exercised, with `target = "none"` if nothing is to be scored after the stop. It costs almost
nothing during a run that is happening anyway, and without it the run is permanently unusable
downstream. This is now recorded in `ARCHITECTURE.md`.

## Acceptance

1. `make regress` byte-identical against `main`. This is the gate; nothing else matters if it fails.
2. The smoke hand-off run writes `handoff.toml` and `handoff.npy` per replicate.
3. In that file, `fuel_kg` is finite and positive for trajectories still holding fuel, and
   `realised_flameout_unix_s` is finite for those that ran dry and NaN for those that did not —
   with the finite fraction near the reference run's 56.86% at full scale, allowing for smoke-scale
   sampling noise.
4. `mh370 terminal` on that run directory selects the end-of-flight module. Confirm from
   `run.json` that `terminal.module` is `end-of-flight` and **not** `arc-kernel` — a previous smoke
   run silently used `arc-kernel`, so its impacts carried nothing from the model while looking like
   a result.

## Not in this change, deliberately

Core requests 2 (passing `takeover_time`'s draw into `descend`), 3 (the fuel-flow trait), 4 (the
`ImpactView` additions) and 5 (surface pressure altitude) are all still wanted and none is needed
for a first smoke run. Keeping them out holds this change small enough to review against
`make regress` in one sitting.
