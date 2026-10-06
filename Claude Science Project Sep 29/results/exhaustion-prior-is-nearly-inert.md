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

## The one-sided constraint, evaluated exactly without a new run

"The tank ran dry by the last step" is a deterministic function of the particle state, so
conditioning the posterior on it is exact: keep the subset, keep the weights, renormalise. The PDF
of the 36.8% that ran dry **is** the posterior under a hard one-sided flame-out constraint. No
approximation and no re-run. Computed on all eight replicates of `6temper-realloc`
(`results/realloc-conditioned-on-exhaustion.pdf`):

| | unconditioned | **conditioned on flame-out** | conditioned, σ=300 tilt divided out |
|---|---|---|---|
| share of mass | 100% | 36.8% | 36.8% |
| median | −37.64° | **−37.45°** | −37.47° |
| mode | −37.75° | −37.70° | −37.70° |
| 50% HDI | [−38.15, −37.05], width 1.10° | **[−37.85, −37.15], width 0.70°** | [−37.90, −37.20], width 0.70° |
| 90% HDI | [−39.60, −35.90], width 3.70° | **[−38.45, −36.20], width 2.25°** | [−38.50, −36.25], width 2.25° |
| shoulder, −36.5..−34.5 | 0.1042 | **0.0843** | 0.0794 |
| split-half, mean over 35 partitions | 0.9109 | **0.9053** | 0.9072 |
| overlap with Davey Fig. 10.3 | 0.7934 | **0.6043** | 0.6107 |
| distinct surviving roots, 8 replicates | 40,759 | **31,937 (78%)** | 31,937 |

Five things to read off it.

1. **It sharpens the posterior substantially.** The 50% interval narrows by 36% and the 90%
   interval by 39%. That is a large gain in precision from a constraint that adds no new data —
   it only removes trajectories inconsistent with the aircraft having been out of fuel.
2. **It costs almost nothing in replicate agreement**, 0.9109 → 0.9053, and it keeps **78% of the
   distinct surviving roots while carrying 36.8% of the mass**. The subset is far better resolved
   than its mass share suggests, because the never-dry paths are concentrated in fewer lineages.
3. **The median moves north by 0.18°**, from −37.64° to −37.45°, slightly *towards* Davey's
   Fig. 10.3 median of −37.532° — 0.081° away instead of 0.104°. (All medians in this note are
   read off the 0.05° grid with the cumulative taken at each bin's upper edge. An earlier version
   interpolated against the bin centres, which biased every absolute median 0.025° south —
   exactly half a grid step — and no difference was affected. The corrected estimator reproduces
   the engine's raw-particle medians exactly and returns Davey's as −37.5323.)
4. **Overlap with Fig. 10.3 nevertheless falls hard, 0.793 → 0.604, and that is not a
   deterioration.** Overlap rewards agreement in *shape*, and the conditioned posterior is much
   narrower than Davey's. Davey has no fuel model — Assumption 4 substitutes a Mach floor for the
   endurance constraint — so his PDF is necessarily broader than one that knows the aircraft ran
   out of fuel. A lower overlap here means information has been added, not that the answer got
   worse. **Overlap with Fig. 10.3 must stop being used as a figure of merit once a constraint
   Davey did not have is imposed.**
5. **The residual σ=300 s tilt is doing nothing**, which is the same 0.09-nat conclusion from the
   other direction: dividing it out moves the median from −37.452° to −37.472°, two hundredths of
   a degree, and leaves both intervals identical.

The shoulder drops from 0.1042 to 0.0843, which is 35.0% of Davey's 0.2406 against 43.3%
unconditioned. So the flame-out constraint takes the project *further* from reproducing the
northern shoulder. That is consistent with the shoulder being carried by the magnetic modes and by
slower, shorter paths — the ones most likely to still hold fuel at 00:19.

What this does not settle: the fully specified one-sided term would also carry a soft upper tail
on how long *before* 00:19:29 the tank emptied, anchored on APU auto-start and SDU boot. The hard
constraint evaluated here admits exhaustion at 00:11 as readily as at 00:19:12. Section 2d of
`results/6temper-realloc-datasheet.md` shows the exhaustion time is quantised to 128 s in storage,
so the surviving mass sits in five slots between 00:10:40 and 00:19:12 and the earliest of them
carries 1.7%. Adding the upper tail would mostly reweight within those five slots.

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
