# The 19:41 bottleneck: tangential geometry, and why a look-ahead does not fix it

Every unconverged run in this project loses its effective sample at the same epoch. In the
evidence-ladder runs the m1941 ESS fraction is 0.080 % (BTO only), 0.127 % (BTO and BFO), against
2–8 % at the neighbouring arcs. This note establishes what is geometrically special about that
epoch, and reports a sampler change aimed at it that **failed**.

## 19:41 is the closest approach, so the track is tangential to the arc

The observations alone show it. BTO over the flight runs 12,600 → 12,500 → 12,480 → **11,500** →
11,740 → 12,780 → 14,540 → 18,040 µs: the 19:41 arc is the innermost. A parabola through
m1828b, m1941 and m2041 puts closest approach at **19:55:50**, fifteen minutes after the epoch,
and the range rate at m1941 is **−0.0139 km/s** against +0.098 at 00:11.

On a nominal 470 kt arc-crossing path — constructed by placing the aircraft on each successive
arc at the distance a constant ground speed allows, which lands at 37.2°S at 00:11 and 38.3°S at
00:19 and so agrees with the posterior — the angle between the track and the BTO gradient is:

| epoch | track-to-gradient angle | along-track NM per BTO σ | cross-track NM per σ | anisotropy |
|---|---|---|---|---|
| 18:28 | 112° | 10.3 | 4.2 | 2.4 |
| **19:41** | **92.0°** | **121.8** | **4.2** | **29.2** |
| 20:41 | 76° | 17.3 | 4.2 | 4.1 |
| 21:41 | 62° | 8.2 | 4.3 | 1.9 |
| 22:41 | 55° | 6.1 | 4.2 | 1.4 |
| 00:11 | 48° | 4.6 | 4.1 | 1.1 |

At 19:41 the track is within 2° of tangential. One measurement standard deviation admits about
122 NM of along-track displacement against 4.2 NM across it. Two independent routes agree on that
figure: the horizontal BTO gradient gives 121.8 NM, and the curvature of the BTO parabola
(473 µs/h², i.e. 0.00214 µs/NM²) gives 116 NM.

## The mechanism is a fold, not dilution of precision

The GPS analogy is close but needs one correction. Weak conditioning on its own flattens the
likelihood, which would *raise* effective sample size, not collapse it. What actually happens is
that near closest approach the map from along-track position to range is quadratic rather than
linear:

    rho(s) ~ rho_min + s^2 / 2R

`rho_min` is set by the path's cross-track offset, and cross-track sensitivity is undiminished at
6.95 µs/NM. So the likelihood is flat in one direction and has a **hard edge** in the other: a
particle whose closest approach is farther than the observed range is excluded whatever its
timing. That is a caustic, and importance weights degenerate at boundaries rather than at peaks.

This matches the earlier work in the archive. The 19:41 BTO log factors across twenty declared
histories span **−1704.03 to −4.34** — a cliff, not a peak — while the BFO term at the same epoch
spans only −58.60 to −3.03. The archive is also explicit that it is **not** support rejection: all
twenty declared histories, and 200 independently generated ones, retained support at both 18:39
and 19:41. The recorded diagnosis was a likelihood/proposal overlap failure, with proposal
corrections spanning **11.675 log units** among histories within two log-likelihood units of the
best 19:41 fit.

### One honest caveat on the geometry

Across all eight BTO epochs the rank correlation between anisotropy and measured ESS is **−0.05**:
nil. 00:11 is the best-conditioned epoch and carries the second-lowest ESS. So tangency is an
extreme and specific feature of 19:41, which happens to be the ESS minimum; it is not a general
predictor of where this filter degenerates, and it should not be presented as one.

## What was tried: an auxiliary look-ahead, and why it failed

Implemented as Pitt & Shephard's auxiliary particle filter and gated behind
`[sampler] lookahead_bto_sd_us`. Before propagating into a BTO epoch, each particle is scored by
where a dead-reckoned continuation of its present ground velocity would place it on that epoch's
arc; that factor enters the resampling weights and is divided out again after the real
propagation and the real likelihood. The division is exact and the factor only needs to be
positive, so the dead-reckoning approximation cannot bias the posterior.

Measured at 1M particles per mode, one seed, on the base configuration:

| run | log evidence | m1941 ESS | m2041 ESS | final ESS | distinct draws |
|---|---|---|---|---|---|
| look-ahead off | −96.661 | 0.989 % | 10.04 % | 69.62 % | 90 |
| σ_extra 2000 µs | −96.661 | 0.989 % | 10.04 % | 69.62 % | 90 |
| σ_extra 600 µs | −96.679 | **0.077 %** | 9.76 % | 70.11 % | 103 |
| σ_extra 200 µs | −96.726 | 0.954 % | 13.74 % | 69.94 % | 89 |

The exactness bookkeeping checks out: at 2000 µs the auxiliary weight never triggers a resample,
the factor is added and subtracted, and the log evidence is bit-identical to the off case. When a
resample does fire, the log evidence moves by 0.018–0.065 nats, inside the replicate spread.

But the intervention does not work. At 600 µs the single firing lands on m1941 and makes it **an
order of magnitude worse**, 0.989 % → 0.077 %.

The reason is the horizon, and the per-epoch gaps make it plain. The gap before m1941 is **4,267
seconds** — 71 minutes. Over that interval the particle's arrival point is dominated by turns and
speed changes drawn *during* the propagation, so a dead-reckoned prediction from the velocity at
18:28 is nearly independent of where the particle actually lands. Resampling on an uninformative
weight discards good particles, and then dividing that weight out re-inflates the survivors'
weights. The net effect is added variance, which is Pitt & Shephard's own stated failure mode for
a poor auxiliary density.

The epochs where dead reckoning *would* be accurate are m1828b and m0019b, 9 and 8 seconds after
their predecessors — and those already sit at 60–70 % ESS, so there is nothing there to fix. The
MH370 epoch spacing puts every epoch that needs help in the regime where this construction cannot
provide it.

## What was tried second: resample-move rejuvenation, which is invariant and does not help either

The archive records what is missing — "no active backward simulation or full-history
rejuvenation" — so the second intervention supplies the rejuvenation half, as Gilks & Berzuini's
resample-move, behind `[sampler] rejuvenate_epochs`. After the ordinary resample at a named
epoch, every child re-simulates its segment from its parent's pre-epoch state with fresh
manoeuvre randomness, and the candidate is accepted on the Metropolis ratio of the two
incremental weights. Because the proposal is the model's own transition, that ratio is the
likelihood ratio and the move is invariant for the current target.

To let both the move and the likelihood use one code path rather than two, the epoch update was
first factored into a closure. The refactor is byte-exact: seed 1 of the base configuration
returns log evidence −96.66146918417472 before and after, to every digit.

Measured at 2M particles, four seeds, base configuration:

| variant | log evidence | median | P(shoulder) | split-half | distinct draws (TT) | acceptance | wall |
|---|---|---|---|---|---|---|---|
| off | −96.341 | −38.111 | 0.0365 | 0.818 | 181.0 | — | 299 s |
| 18:39 and 19:41 | −96.362 | −38.096 | 0.0379 | **0.828** | 221.2 | 14.4 % | 1,615 s |
| all ten epochs | −96.344 | −38.151 | 0.0365 | **0.817** | 233.8 | 35.9 % | 570 s |

The move does what it claims. The posterior does not shift — log evidence within 0.021 nats,
median within 0.055°, shoulder 0.0365 to 0.0379 — so invariance holds at scale as well as in
principle. And it genuinely diversifies the genealogy: surviving distinct prior draws rise from
181 to 221 and 234, a gain of 22 % and 29 %.

**But split-half does not move**: 0.818 → 0.828 → 0.817, all inside replicate noise. The
two-epoch variant costs 5.4× the runtime for that nothing.

(The timing is counter-intuitive — rejuvenating at two epochs cost more than at ten — because
the move only fires where a resample fires, and rejuvenating early changes which later epochs
degenerate enough to trigger one. The 19:41 segment is 71 minutes and is by far the most
expensive to re-simulate, so a variant that skips it is cheaper regardless of how many other
epochs it treats.)

## What was tried third: an arc-bridge turn proposal, which also fails

The two-ended construction, behind `[sampler] bridge_prior_mix`. During the leg into a BTO
epoch, a turn is drawn from a mixture of the prior and the turns whose dead-reckoned
continuation reaches that epoch's arc, with the exact prior-to-proposal ratio carried into the
weight — structurally identical to the fuel endurance proposal, which does work. The filter
converts the epoch's BTO into an aircraft-to-satellite range and hands the dynamics pure
geometry, so the measurement model stays in one place.

| run | log evidence | m1941 ESS | m2041 ESS | distinct draws |
|---|---|---|---|---|
| bridge off | −96.66 | **0.989 %** | 10.04 % | 90 |
| prior mix 0.50 | −96.02 | 0.304 % | 6.51 % | 96 |
| prior mix 0.25 | −96.69 | 0.334 % | 7.62 % | 109 |
| prior mix 0.10 | −95.84 | 0.210 % | 1.38 % | 114 |

Worse at every mixture, by a factor of three to five.

## One cause behind all three failures

Each construction assumes the leg into 19:41 is predictable from its start. It is not. Under the
prior, with the manoeuvre time constant log-uniform on 1–20 h and three clocks running (turn,
speed, altitude):

| leg | duration | P(at least one manoeuvre) |
|---|---|---|
| 18:28:05 → 18:28:14 | 9 s | 0.2 % |
| 18:28 → 18:39 | 701 s | 16.0 % |
| **18:39 → 19:41** | **4,267 s** | **56.2 %** |
| 19:41 → 20:41 | 3,602 s | 51.6 % |
| 00:19:29 → 00:19:37 | 8 s | 0.2 % |

**More than half the particles manoeuvre during the leg into 19:41.** A dead-reckoned prediction
from the start of that leg is therefore wrong for the majority of them, and each construction
fails in the way that follows from its own use of that prediction:

- the **look-ahead** resamples on an auxiliary weight that is nearly independent of where the
  particle lands, then divides it out, which is pure added variance;
- the **bridge** steers a turn so the dead-reckoned arrival hits the arc, but the 56 % that
  manoeuvre again afterwards do not arrive there, so they pay the importance correction without
  the likelihood gain that was supposed to offset it;
- **rejuvenation** re-simulates the segment from the same transition, so its candidates miss the
  sliver at the same rate the originals did — which is why it buys genealogical diversity and no
  convergence.

The symmetry is exact: the only epochs where dead reckoning is reliable are the 9- and 8-second
pairs, at 0.2 % manoeuvre probability, and those already sit at 60–70 % ESS. Every epoch that
needs help is in the regime where none of these three can give it.

## Conclusion: this degeneracy is not reachable by reweighting or by local diversity

Two interventions, both correct, neither useful:

- An auxiliary look-ahead **harms** the epoch it targets, because over 71 minutes a dead-reckoned
  predictive density carries no information about where the particle lands.
- Resample-move rejuvenation adds a fifth more genealogical diversity and buys no convergence.

Taken together these rule out two of the three available classes of fix. Reweighting cannot help
because the weights are already correct and the problem is which states exist, not how they are
scored. Blind re-simulation cannot help because the transition it draws from is the same one that
failed to reach the sliver the first time. What is left is the class neither attempt belongs to: a
proposal that uses the **next** arc to steer the segment, so the intervening manoeuvre draws are
conditioned on both endpoints rather than on the first alone.

That was the construction the archive's checkpoints reached for under the name "two-ended
guidance". It has now been built and it fails, for the reason above.

### What the three failures jointly point at

All three try to *predict across* the leg. The measurement that follows is the same in each case:
you cannot, because the model puts a manoeuvre in that leg for 56 % of particles. So the remedy
has to be one that needs no prediction at all.

That is **tempering**: apply the 19:41 likelihood in stages, L^β for β rising from 0 to 1, with a
resample and an invariant MCMC move between stages, so the population migrates into the sliver
gradually instead of being hit with the whole cliff at one instant. Annealed SMC is the textbook
answer to a likelihood that is sharp relative to the proposal, and it is the only one of the four
that does not depend on knowing where a particle will end up — it uses the likelihood itself as
the guide, which is the one thing here that is exactly computable.

Both halves already exist. The likelihood is factored into `step_update`, so raising it to a power
is a one-line change, and the rejuvenation move built above is precisely the invariant kernel
tempering needs between stages. Neither helped alone; the literature says the combination is what
works, and this project now has the measurement to explain why the alternatives did not.
