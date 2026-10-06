# The fuel exhaustion-time prior is nearly inert, and that changes three conclusions

Smoke pair, 1,000,000 particles × 2 replicates, one case, `6temper-realloc`'s allocation scaled
down, everything identical except the presence of `exhaustion_target_utc = 00:17:30` with
`exhaustion_sd_s = 300`.

| | split-half (1 partition) | median | Fig. 10.3 overlap | shoulder | wall |
|---|---|---|---|---|---|
| term present | 0.6599 | −37.842 | 0.6810 | 0.0664 | 1,297 s |
| term removed | 0.6553 | −37.851 | 0.6759 | 0.0639 | 1,279 s |

Nothing moves. The median shifts 0.009°, the overlap 0.005, the shoulder 0.0025, and split-half
0.005 in the direction that would favour keeping the term. Tightest-epoch ESS is 5.663% in both,
to three decimal places.

## Why: the term is worth 0.09 nats

The exhaustion likelihood scores `fuel_exhausted_unix_s` when the tank ran dry, and the time of
the **last step** when it did not — a lower bound, chosen so that a path still holding fuel is
penalised smoothly rather than by a cliff. The last step is 00:19:37. The target is 00:17:30.
The gap is **127 seconds against a 300-second standard deviation, which is 0.42 σ**, so the
log-penalty for a path that never runs dry at all, relative to one that exhausts exactly on
target, is

> −½ (127/300)² = **−0.0896 nats**, a weight ratio of 0.91.

A term that can discount the worst-case path by 9% is not shaping the posterior and is not
shocking the sampler. It is doing almost nothing.

## Three conclusions that change

**1. The posterior does not depend on the fuel-exhaustion hypothesis.** This is the sensitivity
result, and it is the comfortable one: whether or not the 00:19 log-on is attributed to fuel
exhaustion, the arc-latitude PDF is the same to within 0.01°. The methodological worry about
conditioning the ensemble on a disputed cause is real in principle and empirically negligible
here. Both arms can be reported and they agree.

**2. `results/fuel-path-degeneracy.md` identified the wrong term.** That note argued the terminal
exhaustion likelihood was the path-degeneracy shock — a sharp window on a whole-path functional,
arriving after every epoch had been resampled against. The sharpness was asserted from the
300-second figure without comparing it to the 127-second lever arm it actually acts over. It is
not sharp. **The proposed fuel look-ahead would therefore be solving a problem that does not
exist**, and it should not be built. The diagnosis of *where* the fuel degeneracy lives has to
start again.

**3. The fuel model independently supports the 00:17:30 hypothesis.** With the term removed, so
the filter is told nothing about when the engines should stop, the predicted exhaustion time of
the paths that do run dry falls as:

| | with the term | **without it** |
|---|---|---|
| P(exhaustion within 00:17:30 ± 5 min) | 96.6% | **93.0%** |
| P(exhaustion between 00:11 and 00:19:29) | 100.0% | **98.5%** |
| median exhaustion time | 00:14:56 | 00:14:56 |

An unconditioned filter, constrained only by the arcs, the Boeing tables and the requirement that
the aircraft still had fuel at 00:11, puts 98.5% of its exhausting mass between the 6th and 7th
arcs and 93% within five minutes of 00:17:30. That is the diagnostic the removal was meant to
buy, and it comes out in favour of the hypothesis rather than against it.

## Two things the same measurement exposes

**Most of the posterior still has fuel at the last step.** At smoke scale, 1M × 2 replicates with
equal weights across replicates, 53% still holds fuel with a mass-weighted mean of 3,836 kg. On
the full-scale `6temper-realloc` run — 7M × 8 replicates with the correct per-replicate,
per-stratum pooling factors applied — the figures are **63.2% still holding fuel and a mean of
6,462 kg across the whole posterior**, about 68 minutes of cruise. The full-scale pair is the one
to quote; the smoke pair understates the effect because the two replicates were pooled with equal
weights rather than by evidence share. Either way the conclusion is the same and the full-scale
version is stronger.
If the flame-out hypothesis is right, that half of the posterior is inconsistent with it, and the
reason it survives is precisely the 0.09-nat penalty computed above. So the hypothesis is *not*
being imposed on the ensemble; if anything it is barely being expressed. A term that actually
tested it would have to discriminate at 2–3 nats, not 0.09 — which argues for reshaping rather
than removing it, as a one-sided constraint anchored on the APU-start and SDU-boot interval
before 00:19:29 rather than a wide symmetric Gaussian.

**`fuel_exhausted_unix_s` is saved at 128-second resolution.** `final.npy` is `float32`, and the
unit-in-last-place of a `float32` at 1.394 × 10⁹ is exactly 2⁷ = 128 s. The column takes 19
distinct values across two million particles, spaced 128 s apart. The filter's internal
arithmetic is `f64` and unaffected, but **no exhaustion-time analysis read from the saved output
can resolve better than ±128 s**, which is a quarter of the σ the prior uses. Every exhaustion
figure in this note inherits that quantisation. The fix is to store the column as an offset in
seconds from a run-level reference epoch, which is three digits instead of ten and fits `f32`
comfortably; it affects no other column, since latitudes and fuel masses are nowhere near that
exponent.

## Where the fuel degeneracy diagnosis goes next

The ledger fact stands: 0 of 14 fuel-bearing runs pass split-half, 13 of 14 fuel-free runs at the
same Mach prior do, and the ranges do not overlap. What has changed is that the terminal term is
ruled out as the cause.

The surviving candidate is **lineage collapse**, and it is the one the reallocation result points
at. Per million particles, fuel lowers the number of distinct surviving prior draws in every
mode: true heading 1136 → 821, magnetic heading 796 → 726, true track 911 → 495, magnetic track
646 → 577, lateral navigation 824 → 569. Fuel kills whole lineages early — by design, since
`fuel_doomed` is charged as soon as the deadline is unreachable — so the survivors descend from
fewer independent prior draws at the same per-epoch ESS. That explains the ESS decoupling, the
ledger, and why reallocation worked by moving roots into the modes that carry the mass.

The engine already contains the standard remedy and this project has never used it.
`sampler.rejuvenate_epochs` applies a Metropolis move that re-simulates the segment with the
model's own transition, so the acceptance ratio is the likelihood ratio and the target is left
invariant exactly; the config documents its purpose as buying "path diversity among the children
that a resample has just made identical". That is lineage collapse by name.

One limit to state before testing it: rejuvenation re-simulates from the parent's pre-epoch state,
so it diversifies paths *downstream* of a resample but does not create new draws of the initial
position, track and Mach. It should raise effective path diversity at fixed root count. Whether
that is enough is the smoke test.
