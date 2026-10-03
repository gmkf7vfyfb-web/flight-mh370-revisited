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

## What follows

An auxiliary look-ahead needs an informative predictive density. Over an hour of flight with a
manoeuvre model, that requires integrating over the intervening randomness rather than ignoring
it — which means either steering the manoeuvre draws themselves during the propagation, with the
exact prior-to-proposal correction (the construction that did work for the fuel endurance
constraint), or using later information, which is what a backward pass supplies. The fold at
19:41 leaves the along-track position genuinely ambiguous forward in time; the 20:41 arc is what
resolves it. That makes smoothing the structurally indicated remedy, and the archive notes it has
never been attempted here: "no active backward simulation or full-history rejuvenation".
