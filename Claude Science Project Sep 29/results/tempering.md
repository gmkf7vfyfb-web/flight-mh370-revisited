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

## Honest limits

The absolute numbers are still small. Nine hundred and fifty distinct surviving prior draws out
of a million particles is twice as many as before and still an impoverished sample; tempering
improves the bottleneck substantially without making it comfortable. Whether that is enough to
move the project's convergence criterion — the split-half overlap between replicate posteriors
— is a separate question from the per-epoch effective sample size, and is measured at full
scale separately.