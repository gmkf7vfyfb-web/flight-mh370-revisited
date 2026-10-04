# Davey's branching resampler, built and measured

Obtaining the book (`davey-2016-reference.md`) revealed that this engine's resampler is not the
published one. Both are SIR particle filters — p. 16 is explicit that "the filter used in this
book is a form of SIR particle filter", drawing from the dynamics and weighting by the
likelihood, which is what this engine does too. What differs is how the *resampling step* of
that SIR filter is implemented. Davey does not resample a fixed population by multinomial or
systematic selection; Sect. 8 describes branching with pruning over independently propagated
trajectories, and the book presents it explicitly as a way of resampling rather than as an
alternative to it: "thus resampling can also be implemented through a randomised branching
procedure, recursively adapting the number of particles" (p. 56). That made it both a fidelity gap and the
one candidate remedy for the 19:41 bottleneck carrying the original authors' endorsement, so it
was built first, ahead of tempering.

It reproduces the published evidence and it does **not** fix 19:41.

## The scheme, and one interpretive decision

Behind `[sampler.branching]`. A particle whose weight is at or above a threshold is duplicated
into `branch_factor` children each carrying its parent's weight divided by that factor; one
below the threshold is kept with probability equal to its weight, at weight one, and is
otherwise pruned. Both arms preserve the weighted sum in expectation (Davey Eq. 8.5), the
weights are left unnormalised until the end, and the population size floats. Table 8.2 gives
n̄ in 3–10 and η at e⁻²⁵ or e⁻³⁰.

One thing the book leaves undetermined. It states η as an absolute threshold on a weight whose
scale it never fixes. Read literally against unnormalised Gaussian densities, a path that
matched every measurement perfectly would still fall through an e⁻²⁵ floor after a handful of
epochs, purely from the repeated division by n̄ — the tabulated constants are then mutually
inconsistent. Here the population is rescaled every epoch so its best member sits at weight
one, with the shift banked exactly into the evidence, which makes η read as "this many nats
behind the best surviving path". That is the only reading on which Davey's own n̄ and η work
together, and it is scale-free.

The population ceiling is a departure, forced by memory: Davey's population is bounded only by
pruning. Overflow is resolved at the parent level rather than by building the oversized child
set and thinning it — every child of a parent is an identical copy at the same weight, so
drawing the capped population from the parents weighted by the mass each one's block would have
carried is the same draw, and it avoids a transient peak of n̄ times the live count. That change
alone took peak memory from 26.5 GB to 7.5 GB with results identical to the digit.

## Results

Five modes, two seeds, 200,000 particles per mode at the start, population ceiling 1,500,000.
Effective sample sizes are absolute, summed over modes and averaged over seeds.

| run | peak live | 19:41 ESS | 00:11 ESS | runtime | peak memory | log evidence |
|---|---|---|---|---|---|---|
| baseline, 200k/mode | 200,000 | 10,122 | 33,713 | 51 s | 1.3 GB | −95.006 |
| baseline, 1.5M/mode | 1,500,000 | **76,727** | 316,487 | 365 s | 4.9 GB | −94.703 |
| branching n̄=3, η=e⁻²⁵ | 1,500,000 | **76,207** | 2,677 | 76 s | 7.5 GB | −94.880 |
| branching n̄=10, η=e⁻³⁰ | 1,500,000 | **75,833** | 465,152 | 292 s | 7.2 GB | −94.725 |

**The evidence agrees.** Across five branching configurations spanning both tabulated
thresholds and branch factors 3, 5 and 10, the log evidence lands between **−94.880 and
−94.659** — n̄=3 at e⁻²⁵ −94.880, n̄=3 at e⁻³⁰ −94.659, n̄=5 at e⁻³⁰ −94.729, n̄=10 at e⁻²⁵
−94.689, n̄=10 at e⁻³⁰ −94.725 — against −94.703 for the 1.5M baseline, which sits inside that
range. The spread is 0.22 nats and the baseline is not an outlier in it. The scheme is
unbiased, as Eq. 8.5 says it should be, and that is the check that matters for using it at all.

**19:41 is unmoved.** At equal peak population every scheme delivers the same effective sample
at the bottleneck: 76,727, 76,207, 75,833 — a spread of 1.2 %. The large differences in ESS
*fraction* between these runs (1.02 %, 6.16 %, 1.62 %) are entirely an artefact of how many
particles happen to be live at that moment, and reporting them without the population would
have been misleading.

**The branch factor trades the bottleneck against the end of the flight.** At n̄=3 the
population collapses after 19:41 — 247k, 90k, 74k, 57k — and by 00:11 there are 2,677 effective
particles against the baseline's 316,487. That is a worse filter, badly. At n̄=10 the population
holds at the ceiling and 00:11 improves on the baseline by a factor of 1.47, at 80 % of its
runtime. So within the published range the useful setting is the top of it, and the gain is at
the end of the flight rather than at 19:41.

**Where it does win is time.** n̄=3 reaches the same 19:41 effective sample as the 1.5M baseline
in 76 seconds against 365 — 4.8× faster — because it carries the large population only through
the epochs that need it and prunes hard afterwards. That is exactly the adaptive allocation
Davey describes, and it works; it simply does not buy accuracy at the epoch we care about.

## What this settles

Four interventions have now been measured against the 19:41 degeneracy: auxiliary look-ahead,
resample-move rejuvenation, the arc-bridge proposal, and Davey's branching. The first, second
and fourth all act on **which particles get copied**, and all three leave the effective sample
at 19:41 unchanged at matched cost. The third acted on the proposal and failed for a measured
reason — the dead-reckoned prediction it steers by is wrong for the 83 % of particles that
manoeuvre during the leg, 7.6 times on average.

Resampling redistributes a population; it cannot narrow the spread of incremental weights that
the leg's own manoeuvre draws generate. That spread is what the 19:41 ESS measures, and it is
why the published method does no better here than ours. It also means the remaining lever is
not a better way of choosing particles but a different way of applying the likelihood —
tempering, which stages the 19:41 likelihood as L^β with an invariant move between stages and
needs no prediction across the leg at all. That is next.

## Fidelity

Independently of convergence, the engine should be able to run the published sampler, and now
can. The default remains systematic resampling so every existing result stays byte-reproducible;
`[sampler.branching]` selects Davey's. The comparison above is the first direct measurement of
what that choice costs, and the answer — same posterior, same evidence, different efficiency
profile — is worth stating in the paper.