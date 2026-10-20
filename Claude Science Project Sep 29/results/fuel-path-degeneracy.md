# Why fuel breaks the filter, and the one remedy that reuses machinery already here

`results/convergence-ledger.md` establishes the fact: across 33 full-scale runs, none that scores
fuel against the satcom data has passed split-half (best 0.875) and none that omits it at Davey's
Mach prior has clearly failed (worst passing 0.907). The ranges do not overlap, and the control
run that scores fuel with *no* satcom data converges at 0.9965. This note says why, from the code,
and proposes the fix.

## Three fuel terms, and only one of them is local

Reading `crates/mh370/src/filter.rs`, fuel enters the weight in three places.

1. **The endurance proposal's correction**, `a.fuel_log_weight_correction`, accumulated step by
   step inside the dynamics and drained into the weight at each epoch. This is an exact
   prior-to-proposal ratio, so it is unbiased — but it is a *product over steps*, and its variance
   grows with path length. It is never reset.
2. **The doomed-path penalty**, `FUEL_REJECT_LOG_PENALTY = −50`, charged once as soon as
   `fuel_doomed` is set, and the deadline test at `require_power_until = m0011`. This one is well
   designed: it fires as early as the fuel state can prove the path cannot reach the deadline, so
   the resampling that follows can reallocate the share while there is still flight left to
   explore.
3. **The exhaustion-time likelihood**, `N(00:17:30, 300 s)` on `fuel_exhausted_unix_s`, applied
   **once, at the final step**, inside `if last`.

Term 3 is the problem. It is a 300-second Gaussian — sharp against a flight of more than six hours
— evaluated on a quantity that is a deterministic functional of the *entire* trajectory: every
Mach target, every altitude, every turn, from 18:01 onwards. It arrives after every satcom epoch
has been scored and resampled against. No resampling step before it can prepare for it,
because until the last step the filter has no term in the weight that says anything about where a
particle's exhaustion time is heading.

That is the textbook signature of **path degeneracy** rather than low effective sample size, and
it explains every anomaly in the ledger at once:

- Why tempering does nothing. Tempering anneals an epoch's own likelihood over 16 stages. It has
  no purchase on a term that is not evaluated at that epoch.
- Why per-epoch ESS and split-half agreement part company. ESS is measured at each epoch against
  that epoch's weights; the terminal shock is invisible to it.
- Why `endurance_1_fuel_only` converges perfectly at 0.9965. With no satcom likelihood the fuel
  term is the *only* term, so the proposal is drawn straight at it and there is no competition for
  the particles.
- Why wide Mach is worse than narrow. Widening the Mach prior widens the spread of achievable
  exhaustion times without widening the 300-second window they are scored against, so a larger
  fraction of the population is annihilated by the terminal term.
- Why reallocation might help but is unlikely to be sufficient. Moving particles into true track
  and lateral navigation raises the number that survive to the terminal term, but every surviving
  particle still meets the same unprepared shock.

## The first remedy: ask whether term 3 belongs in the likelihood at all

This note originally went straight to a sampler workaround. That was the wrong order, and the
point is the user's: **`exhaustion_target_utc` is a conditional hypothesis, not an observation.**
It asserts that the 00:19 log-on was caused by fuel exhaustion followed by an APU start. That is a
claim about the *cause* of the log-on, and it is disputed — Lyne among others proposes a different
cause. Conditioning the ensemble on it and then reading the posterior as evidence for it is
circular.

`config.rs` already draws this distinction in its own documentation, which makes the removal a
return to the design rather than a departure from it:

> `require_power_until` is an observation, not an assumption: the aircraft transmitted at that
> epoch, so a path whose tank ran dry earlier is inconsistent with the data.
> `exhaustion_target_utc` with `exhaustion_sd_s` is the weaker claim that the 00:19 log-on
> followed engine failure and an APU start, so exhaustion should sit shortly before it. Left
> absent, fuel constrains nothing beyond the hard requirement above.

Two consequences, and they point the same way.

**Methodologically**, removing it converts fuel exhaustion from an input to an output. The run
then produces a joint posterior over *when and where* the engines stopped, which can be laid over
00:17:30 and over the 6th and 7th arcs. Density that coincides with the hypothesised window
supports the hypothesis; density that does not questions it. Either way the test is a test, which
it cannot be while the filter is told the answer.

**For the sampler**, it removes the degeneracy at its source rather than working around it. Term 3
*is* the terminal shock. With it gone there is no quantity in the weight that depends on the whole
path and arrives only at the end.

What is retained: `require_power_until = "m0011"` and the early `fuel_doomed` rejection that
implements it. Those follow from the observed transmissions. The endurance proposal is unaffected
— `main.rs` builds its deadline from `require_power_until`, not from the exhaustion target, so the
proposal keeps aiming at the same place.

What is lost, and must be reported rather than discovered later: the term was penalising paths
that still held a lot of fuel at the end, which are the slow, low, short ones. Removing it admits
more of them, so the 00:19 posterior should widen and move north. The honest presentation is two
arms — base model without the term, declared conditional arm with it — in the same
declared-alternatives style the project uses for the 00:19 BFO interpretations.

`config/sensitivity/no-exhaustion-prior.toml` is `6temper-realloc` with those two keys removed and
nothing else changed. Smoke-gate it at 1M × 2 seeds against `6temper-realloc` at the same scale.

## The contingency: a fuel look-ahead, built the way the BTO look-ahead already is

If removing term 3 is not enough — or if the conditional arm that keeps it is also wanted at a
usable convergence — the sampler workaround stands, and it is this.

The engine already contains exactly the right mechanism, applied to a different problem. In
`filter.rs` the auxiliary look-ahead (Pitt & Shephard) scores each particle before a BTO epoch by
where a dead-reckoned continuation of its present velocity would land on that epoch's arc, folds
that into the resampling weights, and **divides it out again** after the real propagation and the
real likelihood. The comment on it states the principle precisely: the division is exact and the
auxiliary factor only has to be positive, so the approximation inside it cannot bias the posterior
— it only decides which particles get the effort.

The same construction applies to fuel, and every quantity it needs is already in the state:

> At each cruise epoch, project the particle's exhaustion time as
> `t_now + fuel_kg / flow`, where `flow` is `FuelTables::fuel_flow_kg_h` at the particle's current
> flight level, weight and Mach. Score that projection against the same exhaustion Gaussian used
> at the final step, with the standard deviation inflated — in quadrature, as the BTO look-ahead
> inflates its own — to reflect that the projection is a dead reckoning over hours of flight.
> Fold the result into the resampling weight, and divide it out at the next epoch.

Three properties make this the right shape:

- **It cannot bias the posterior.** The auxiliary factor is strictly positive and exactly divided
  out, by the same argument and the same code path as the BTO look-ahead.
- **It is a lower bound away from a necessary condition.** `FuelTables::min_flow_kg_h` already
  computes the cheapest burn any reachable level and speed can achieve, which is what makes
  `fuel_doomed` a *necessary* rejection rather than a guess. The same function gives the latest
  possible exhaustion, so the projection can be bracketed rather than point-estimated if the point
  estimate proves too aggressive.
- **It converts term 3 from a shock into a signal.** From 19:41 onward the filter would carry a
  weight component that says which particles are heading for the right exhaustion time, so twelve
  resampling steps can act on it instead of none.

## What to do, in order

1. **Run `no-exhaustion-prior` at smoke scale against `6temper-realloc`.** No code change, 20
   minutes, one variable. This is first because it is free and because it is the methodologically
   correct model whether or not it fixes the sampler.
2. If the two-seed split-half moves materially, run it full scale, eight replicates. Expect at
   most 11 h and probably less, since a likelihood term is being removed rather than added.
3. Report the resulting fuel-exhaustion posterior — time and position — against 00:17:30 and the
   6th and 7th arcs. That is the diagnostic the removal buys.
4. Keep `6temper-realloc` as the declared conditional arm and report the two side by side.

Only if steps 1–2 leave replicate agreement short, build the look-ahead:

1. Add `lookahead_fuel_sd_s` to `[sampler]`, defaulting to `None`, exactly parallel to
   `lookahead_bto_sd_us`. Off by default; the published model and `davey2016.toml` stay
   byte-reproducible.
2. Compute the projection and the auxiliary factor inside the existing `aux` vector so the
   division-out logic is shared rather than duplicated.
3. Smoke-gate it: 1M × 2 seeds, one case, fuel + 6 tempered epochs, against `f6` as the matched
   control. That run costs about 20 minutes. What to look at is **not** per-epoch ESS — the ledger
   has now twice shown that is the wrong gate — but the variance of the terminal weight
   contribution across the surviving population, and the two-seed split-half as a direction
   indicator only. The terminal contribution is not currently recorded directly: `residual[3]` is
   assigned inside the satcom-epoch block and the exhaustion term is added afterwards, in
   `if last`. It is reconstructible in post-processing from the saved `fuel_exhausted_unix_s`
   column and the declared target and standard deviation, which is enough for the smoke gate;
   recording it as its own column would be cleaner and costs one `f32`.
4. If the smoke gate shows the terminal weight variance falling, run it full scale against
   `6temper-realloc`, one variable changed.

## Cost

Unmeasured. The added work is one `fuel_flow_kg_h` lookup per particle per cruise epoch — of
order 7M × 10 lookups per replicate — against the endurance proposal's existing 16 flow-grid cells
per manoeuvre draw, which is what makes fuel 11.1× the no-fuel cost in the first place. On that
comparison the look-ahead should be a small fraction of the fuel overhead, but the smoke gate in
step 3 measures it rather than assuming it.

## What this does not fix

The accumulated proposal correction, term 1. If the terminal shock is removed and replicate
agreement still fails, that product-over-steps ratio is the next suspect, and the remedy there is
different: either reset it at each epoch by folding it into the resampling weight (which the drain
at each epoch already approximates) or bound it, which costs exactness. That is a separate
investigation and should not be started until term 3 is settled.
