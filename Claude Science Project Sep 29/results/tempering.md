# Annealed SMC at the bottleneck epochs

Four interventions were measured against the 19:41 degeneracy and failed: an auxiliary
look-ahead, resample-move rejuvenation, an arc-bridge turn proposal, and Davey's own branching
resampler. This is the fifth, and it works.

## The construction

Behind `[sampler] temper_epochs` and `temper_stages`. At a named epoch the log-likelihood
increment is not applied at once. It is paid out as L^β over equal stages, and between stages
the population is resampled and then moved by the same invariant kernel the rejuvenation step
uses — re-simulating the segment from the parent's pre-epoch state with fresh manoeuvre
randomness — accepted against the *tempered* ratio, so each intermediate distribution is left
invariant exactly. The exponents sum to one, so the epoch's contribution to the weight and to
the evidence is unchanged; what changes is that the population meets a sharp likelihood in
several steps with its diversity restored between them, rather than all at once.

The reason to expect this to work where the others did not is specific. Look-ahead,
rejuvenation and branching all act on *which particles get copied*. Resampling redistributes a
population; it cannot narrow the spread of incremental weights that the leg's own manoeuvre
draws generate, and that spread is what the 19:41 effective sample size measures. The
arc-bridge did act on the proposal, and failed for a measured reason: the dead-reckoned
forecast it steers by is wrong for the 83 % of particles that manoeuvre during the leg, 7.6
times on average. Tempering needs no forecast at all. Its guide is the likelihood itself, which
is the one thing in this problem that is exactly computable.

## Results

Five modes, two seeds, 200,000 particles per mode, tempering both 18:39 and 19:41. Effective
sample sizes are absolute, summed over modes and averaged over seeds.

| stages | 18:39 ESS | 19:41 ESS | distinct prior draws | move accepted | runtime | log evidence |
|---|---|---|---|---|---|---|
| off | 21,356 | 10,122 | 461 | — | 37 s | −95.006 |
| 4 | 35,883 | 23,866 | 588 | 18.2 % | 56 s | −94.903 |
| 8 | 116,409 | 37,069 | 784 | 19.4 % | 67 s | −94.950 |
| 16 | 309,903 | 60,355 | 890 | 30.9 % | 67 s | −94.809 |
| 32 | 404,762 | 100,309 | 952 | 26.4 % | 77 s | −94.806 |

19:41 improves by a factor of **9.9**, 18:39 by **19**, and the number of distinct prior draws
surviving to the end — the quantity that decides whether the posterior is a distribution or a
handful of paths — by a little over **2**, for 2.1× the runtime. The three sample-size columns
are each monotonic in the stage count.

The other two are not, and should not be read as if they were. Move acceptance peaks at 30.9 %
at sixteen stages and falls back to 26.4 % at thirty-two; it is a property of the kernel at a
given temperature, not a convergence measure. The log evidence wanders non-monotonically
(−94.903, −94.950, −94.809, −94.806) within 0.2 nats of the untempered −95.006, which is what
an unbiased estimator should do — a monotone trend there would mean the target was moving with
the stage count, which is precisely what must not happen.

Tempering 19:41 alone leaves 18:39 at exactly its untempered 21,356 and moves nothing
downstream, so the effect is local to the epoch it is applied at and the two can be reasoned
about separately.

## A diagnostic trap, recorded because the first measurement was wrong

Tempering resamples *inside* the epoch. Reading the effective sample size at the usual place —
after the epoch's update — therefore reads it after a resample, and reports the population
size. The first run of this experiment showed a 19:41 ESS of 963,783 out of 1,000,000
particles, which is not a convergence result; it is a measurement of n.

The honest number is the worst per-stage ESS, taken after each stage's weight update and before
that stage's resample, which is the same point in the cycle the untempered diagnostic is taken
at. Everything above is that. Anyone adding a within-epoch move to this filter should expect
the same trap.

## At full scale, on the base reproduction

`config/davey2016.toml` plus `config/sensitivity/tempered-1839-1941.toml`: identical in every
respect except the sampler flag — 7,000,000 particles per replicate, eight seeds, both
bottleneck epochs tempered over sixteen stages.

| epoch | systematic | tempered | |
|---|---|---|---|
| 18:25 | 36.240 % | 36.240 % | — |
| 18:28a | 72.787 % | 72.787 % | — |
| 18:28b | 58.929 % | 58.929 % | — |
| **18:39** | **2.152 %** | **31.029 %** | **14.4×** |
| **19:41** | **1.021 %** | **6.037 %** | **5.9×** |
| 20:41 | 8.885 % | 8.817 % | — |
| 21:41 | 19.265 % | 19.341 % | — |
| 22:41 | 12.258 % | 12.190 % | — |
| 23:15 | 81.982 % | 82.013 % | — |
| 00:11 | 4.645 % | 4.596 % | — |
| 00:19a | 76.186 % | 76.377 % | — |
| 00:19b | 54.537 % | 54.802 % | — |

The effect is surgical: the two tempered epochs move by factors of 14 and 6, and the other ten
sit within 1 % of their untempered values — three of them identical to five decimal places,
because tempering 18:39 and 19:41 cannot change anything that happened before them.

**The convergence criterion moves.**

| | systematic | tempered |
|---|---|---|
| split-half overlap | 0.9340 | **0.9416** |
| replicate pairwise overlap | 0.853–0.925 | **0.873–0.941** |
| replicate median span | 0.3121° | **0.2288°** |
| tightest epoch | 19:41, at 1.02 % | **00:11, at 4.60 %** |

The replicate median span — how far apart eight independent replicates put the posterior median
— tightens by 27 %, which is the most direct statement of the gain: the same model, the same
evidence, and the eight answers agree more closely. And the binding constraint is no longer
19:41. After four failed attempts the bottleneck has moved to 00:11, which is a different
problem with a different cause.

**The posterior does not move**, which is the control that matters:

| | systematic | tempered |
|---|---|---|
| median | −38.1595° | −38.1124° |
| mode | −38.35° | −38.05° |
| 95 % interval | [−39.533, −35.880] | [−39.538, −35.861] |
| overlap with Davey Fig. 10.3 | 0.7172 | 0.7211 |
| log evidence | −96.2635 | −96.2860 |

The median shifts by 0.047°, a fifth of the replicate span, and the 95 % bounds agree to 0.02°.
The log evidence agrees to 0.023 nats. Tempering made the estimate of the posterior better
without making it a different posterior.

Runtime is not quoted here: the two runs were recorded at different times on different code
revisions and the wall-clock figures are not comparable. The matched measurement is the
small-scale sweep above, where sixteen stages cost about 1.8× the untempered runtime.

## Tempering 00:11 as well: it lifts the epoch and buys nothing

`tempered-three` adds 00:11 to the schedule, otherwise identical. Everything before 00:11 is
reproduced to five decimal places, as it must be — tempering an epoch cannot reach backwards.

| | base | tempered 18:39 + 19:41 | + 00:11 |
|---|---|---|---|
| 18:39 ESS | 2.152 % | 31.029 % | 31.029 % |
| 19:41 ESS | 1.021 % | 6.037 % | 6.037 % |
| **00:11 ESS** | 4.645 % | 4.596 % | **19.846 %** |
| split-half overlap | 0.9340 | 0.9416 | 0.9422 |
| replicate median span | 0.3121° | 0.2288° | 0.2336° |
| overlap with Fig. 10.3 | 0.7172 | 0.7211 | 0.7186 |
| log evidence | −96.264 | −96.286 | −96.286 |

00:11 rises by a factor of 4.3, and **none of the convergence measures move**. Split-half gains
0.0006, the replicate median span gets 0.005° *worse*, and both changes are far inside the
replicate noise. The tightest epoch simply reverts to 19:41 at 6.04 %.

This is worth stating plainly because it corrects a natural assumption, including one implied by
the previous section of this note. The epoch with the smallest effective sample is not
automatically the thing limiting the posterior. 00:11 had the lowest ESS after the first
tempering run, and fixing it changed nothing measurable: its low effective sample was a
consequence of how narrow the posterior already is by 00:11, not a cause of disagreement between
replicates. Per-epoch ESS and replicate agreement are different quantities, and chasing the
former is only worthwhile where the two are linked — as they were at 18:39 and 19:41, where the
degeneracy was a caustic in the likelihood rather than a narrow posterior.

The practical recommendation is therefore `tempered-1839-1941`, not `tempered-three`: the same
convergence for less work.

## A secondary mode, visible only at 99 %

Drawing the position maps at 50/90/99 rather than 50/90/95 exposes a feature the 95 % contour
hides completely: a **detached second region on the arc near 28–30°S**, separated from the main
body by a gap around 31.5–34.5°S that carries 0.38 % of the mass.

It is small. At 00:19 the region between 26 and 31°S holds **0.49 % of posterior mass**, resolved
by 88,782 particles, so it is a real feature of the model's posterior and not a sampling
artefact. At 00:11 the same region holds 0.53 %, but there it rests on only 85 of the 16,000
stored route samples, which is too thin to characterise on its own — it is believable mainly
because the 00:19 state, which is stored exactly and in bulk, agrees.

This is the northern shoulder seen in two dimensions rather than as a bump on the latitude
marginal. Being just under half a percent of mass it sits right at the edge of a 99 % region, so
its *appearance* in a figure is sensitive to the level chosen — which is a reason to quote the
enclosed mass directly, as the companion `mass-*.pdf` curves do, rather than relying on which
contours happen to be drawn.

## Honest limits

The absolute numbers are still small. Nine hundred and fifty distinct surviving prior draws out
of a million particles is twice as many as before and still an impoverished sample; tempering
improves the bottleneck substantially without making it comfortable.

At full scale 19:41 goes from 1.02 % to 6.04 %, which is a real gain and still the second-worst
epoch in the flight. The split-half overlap moves from 0.9340 to 0.9416 against a floor
calibrated at 0.924 for eight replicates (`split-half-threshold.md`) — so the base run already
passed and the tempered run passes by more. The honest summary is that tempering did not turn a
failing filter into a passing one; it tightened a filter that was marginally passing, and it
removed the specific pathology that had made the margin untrustworthy.

What it does settle is the diagnosis. Five interventions, one of which works, and the one that
works is the only one that does not depend on predicting where a particle will be. That is a
result about the problem, not just about the sampler, and it is worth a section in the paper.

The next constraint is 00:11 at 4.60 %, which tempering leaves untouched because it is not the
same pathology: 00:11 is well-conditioned geometrically — the track crosses the arc at 48°, the
most favourable angle of any epoch — and its low effective sample reflects the accumulated
narrowing of the posterior by then rather than a caustic in the likelihood. Whether tempering
helps there is an open question and cheap to test.