
# Item 5 — what the fuel model costs in log evidence, decomposed

15 October 2026. **Computed from log-evidence values already on record; no new run.** Every number
below is quoted from a run's recorded result, named beside it.

## The short answer

**The "fuel costs 8.2–8.45 nat" figure should not go in the paper.** It belongs to a configuration
that no longer exists. On the corrected fuel tables, with the exhaustion-timing term removed, the
fuel model costs **about 2.16 nat**, and that cost is not bookkeeping.

## The chain of measurements

| configuration | ln Z | source |
|---|---|---|
| Davey reproduction, no fuel (`davey2016`, 8 x 7M) | −96.26 | base run, 29 Sep |
| Same, tempered at 18:39 and 19:41 (sampler only) | −96.286 | `tempered-1839-1941` |
| Fuel, defective tables, with the 00:17:30 timing term (`stage2-fuel-narrowmach`) | −104.49 | the "8.2 nat" |
| Fuel, defective tables, with the timing term, six tempered epochs (`best-model`) | −104.734 | the "8.45 nat" |
| Fuel, defective tables, timing term, reallocated (`6temper-realloc`) | −104.678 | withdrawn results |
| **Fuel, corrected tables, timing term removed (`no-exhaustion-prior`)** | **−98.420** | reference, 7 Oct |

`no-exhaustion-prior` differs from `6temper-realloc` in exactly two things: the corrected fuel
tables, and the removal of the 00:17:30 term. Tempering and particle allocation do not change log
evidence in expectation — tempering was measured to move it from −96.2635 to −96.2860, inside
noise — so the comparison against the fuel-free base is fair.

## The decomposition

1. **Of the old 8.2–8.45 nat, about 6.6 nat was the normalising constant of a timing term.** This
   was measured directly at smoke scale: the 6.79 nat contributed by the 00:17:30 exhaustion term
   decomposed into 6.62 nat of Gaussian density normalisation, −log(300·√(2π)), and only 0.17 nat
   of real misfit. A Gaussian likelihood term adds its normalising constant to ln Z whatever the
   data say, so most of that "cost" was an artefact of having the term at all. The term has since
   been removed, so this part is gone.
2. **The fuel model as it now stands costs −98.420 − (−96.26) = −2.16 nat** (−2.13 against the
   tempered baseline). The eight-seed spread of ln Z on the 7 Hz reference is 0.34 nat
   (−98.261 to −98.600), so this is well determined: roughly 2.2 ± 0.2 nat.
3. **That 2.16 nat is not a normalising constant**, because the remaining fuel model carries no
   Gaussian term. What enforces it is a hard constraint — at least one engine must still be
   running at the 00:11 transmission (`require_power_until = m0011`) — together with the
   endurance-aware proposal, which is exactly importance-corrected and was validated to change
   ln Z by only 0.054 nat. A hard constraint changes the evidence by the log of the probability,
   under the unconstrained model, that a trajectory satisfies it. So:

   > **e^−2.16 ≈ 0.12.** On this reading, only about one in eight of the trajectories that Davey's
   > infinite-fuel model finds consistent with the satellite data could actually have flown them
   > on the fuel aboard.

   That is a substantive result about the 2016 method, not a penalty on ours: Davey's Assumption 4
   (infinite fuel, with the Mach floor standing in for endurance) admits mostly trajectories that
   run dry before 00:11. It points the same way as the earlier measurement that under a wide Mach prior 69% of the
   posterior weight sat on paths whose tanks ran dry before 00:10:59 — though that was on the
   defective tables and a wider prior, so it is corroboration of direction only.

## What this is not, and the one check that would make it firm

The one-in-eight reading assumes the fuel model acts on the posterior only through the 00:11
constraint. It also carries a sampled calibration factor and mass bookkeeping, which do not alter
Davey's dynamics but are not literally an indicator function. **The direct test is cheap**: evaluate
fuel feasibility at 00:11 over the stored final states of the `davey2016` posterior and compare the
weighted fraction with 0.12. That needs the engine to fly the fuel model over stored trajectories,
so it is a core-session task, not one this session can run.

Two further caveats. The current production fuel model is newer again — internal-v1 with a
temperature term and κ = N(1.0004, 0.0196) — and runs from run C onward also carry radar terms and
the early-flight families, so their ln Z is not comparable with Davey's; the 2.16 nat is the cost on
Davey's own priors and observations, which is the comparison the paper needs. And whether
`no-exhaustion-prior` also had the vertical-rate BFO term switched on is not recorded here; that term
was measured to be nearly inert on the posterior.

## The sentence for the paper

> Adding an aircraft fuel model to the reproduction of Davey et al. (2016) costs about 2.2 nat of
> log evidence. The cost is a constraint term rather than a misfit: it corresponds to only about one
> in eight of the trajectories admitted under the original infinite-fuel assumption remaining
> flyable on the fuel aboard to the 00:11 transmission.

(Conditional on the direct check above.)
