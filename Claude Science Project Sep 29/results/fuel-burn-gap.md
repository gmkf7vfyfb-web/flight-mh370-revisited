# A fifth of every trajectory burns no fuel at all

This started as a question about why only 36.8% of the `6temper-realloc` posterior has an empty
tank at 00:19:37, with a mass-weighted mean of 6,462 kg still aboard. The answer is not a
modelling choice. It is a defect, and the fuel model's central quantitative claim rests on it.

## The measurement

Mass-weighted over all 56,000,000 trajectories of `6temper-realloc`, the mean seconds each path
spends outside the Boeing tables, against a 22,668 s leg from 18:01:49 to 00:19:37:

| counter | mean seconds | share of the leg |
|---|---|---|
| `fuel_below_tables_s` | 4,432 | **19.55%** |
| `fuel_extrapolated_s` | 4,690 | 20.69% |
| `fuel_above_ceiling_s` | 1,426 | 6.29% |

And the implied burn:

| | total burn | rate |
|---|---|---|
| whole posterior | 30,147 kg | 4,788 kg/h |
| the 63.2% that never ran dry | 26,385 kg | **4,190 kg/h** |

For comparison, this project has read the same tables at FL350 and about 192 t and found the
cruise band spans **5,395 to 6,241 kg/h**. The aircraft began this leg at 210.8 t, heavier, which
burns more. So the typical surviving path is burning below the entire tabulated cruise band.

## What `fuel_below_tables_s` is actually counting

Its doc comment says "seconds flown with the flight level below FL060, where only one speed
schedule is tabulated and the flow is taken at FL060 instead". That cannot be what fired here.
Across all 56M particles the final altitude spans exactly 25,000 to 43,000 ft — the configured
`altitude_range_ft` — and **no probability mass sits below 6,000 ft**. The occupied flight levels
run FL250 to FL430 and nothing else. The FL060 clamp never engages.

The counter is incremented in two places in `Aircraft::burn_fuel`. One is `cover.below_tables`,
the FL060 clamp, which we have just ruled out. The other is the early return when
`FuelTables::fuel_flow_kg_h` yields `None`:

```rust
let Some((flow_kg_h, cover)) = model.tables.fuel_flow_kg_h(self.alt_ft / 100.0, weight_t, self.mach) else {
    self.fuel_below_tables_s += dt;
    return;            // <- no fuel is burnt for this step
};
```

So **19.55% of every trajectory, on average, is flown with the engines consuming nothing.** The
counter that would have made this visible is mislabelled as an altitude clamp, and the comment
beside the early return blames the weight grid — "outside the weight grid entirely, which the
prior cannot reach" — which is also wrong: the flow tables are gridded 140 to 300 t and the
aircraft spans 210.8 down to 174.2 t, comfortably inside.

## Why this explains every surprising number at once

Burning nothing for 19.6% of the leg means the effective rate is about 80% of the true one.
5,950 × 0.805 = 4,790 kg/h, which is the measured whole-posterior figure to three significant
figures. The same deficit carries straight through:

- the tank does not empty, so only 36.8% of paths run dry;
- the mean remaining is 6,462 kg over the posterior and 10,225 kg over the never-dry paths;
- and the exhaustion-time term, already worth only 0.09 nats, is applied to a fuel state that is
  systematically too full.

The 36.8%/63.2% split is therefore **an artefact, not a result**. Nothing in this project's fuel
conclusions that depends on the absolute fuel state survives unexamined.

## Where the lookup is failing, and what to do

Not yet pinned, and it should be instrumented rather than guessed. The likeliest candidate is the
last line of `fuel_flow_kg_h`. The flow between two bracketing schedules is fitted as
`a·M² + b/M²` — parasite plus induced drag at fixed altitude and weight, exact at both points —
and the function then returns

```rust
(per_engine.is_finite() && per_engine > 0.0).then_some((2.0 * per_engine, cover))
```

A two-point fit of that form, extrapolated well below the lower bracketing Mach, can return a
non-positive value. The Mach prior runs down to 0.73 while the bracketing schedules at a given
cell may be LRC near M0.84 and Holding far below it, so a wide extrapolation is routine. When the
fit goes non-positive the function returns `None` and the caller silently skips the burn. That
would also explain why `fuel_extrapolated_s` is high, 20.7%, in the same runs: extrapolation is
common, and where it is most extreme the fit fails.

The second candidate is `pts.is_empty()` surviving the step-down loop at FL250–FL290, where the
code's own comment records that M0.84, MRC and CI 52 are not tabulated and "a filler cell can
drop LRC".

Three things to do, in order, and none of them should be done while a comparison run is in
flight because they change the binary:

1. **Split the counter.** `fuel_below_tables_s` must not pool the FL060 clamp with a failed
   lookup; they have opposite effects on burn — the clamp burns at a much higher flow, the
   failure burns nothing. Add `fuel_no_flow_s` and record which branch fired.
2. **Make a failed lookup burn something.** The existing comment for the service ceiling has the
   right principle — "the alternative is to credit the step with no burn at all, which would make
   an unflyable path look more feasible than a flyable one" — and the `None` path violates
   exactly that principle. Fall back to the nearest valid schedule's flow, flag it, and never
   return without burning.
3. **Re-run the fuel conclusions.** Everything in `results/exhaustion-prior-is-nearly-inert.md`
   that cites an absolute fuel state — the 36.8% dry fraction, the 6,462 kg mean, the
   flame-out-conditioned posterior and its 0.676° shift — must be recomputed once the burn is
   right. The 0.09-nat arithmetic for the exhaustion term is unaffected, because that depends only
   on the 127 s lever arm and the 300 s standard deviation.

One prediction worth recording before the fix, so it can be checked afterwards: with the burn
corrected by about 20%, the typical path should consume close to its full 36,609 kg over the leg,
the dry fraction should rise well above 36.8%, and the flame-out-conditioned posterior should move
closer to the unconditioned one — because conditioning on an event that most paths now satisfy
selects much less strongly.
