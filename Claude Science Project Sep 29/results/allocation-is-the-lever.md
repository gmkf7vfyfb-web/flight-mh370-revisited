# Particle allocation moved replicate agreement three times further than tempering, and cost less

`6temper-realloc` is `best-model-6temper` with one variable changed: the 7,000,000 particles per
replicate are divided 1.0M / 0.5M / 2.5M / 0.5M / 2.5M across true heading, magnetic heading, true
track, magnetic track and lateral navigation, instead of 1.4M each. That is the allocation the
fuel-free runs converge under. Eight replicates, one measurement case, everything else identical.

| run | split-half, mean over all 35 partitions | floor | median | replicate span | Fig. 10.3 overlap | shoulder | wall |
|---|---|---|---|---|---|---|---|
| `best-model` (3 tempered, equal) | 0.8798 [0.8260–0.9368] | 0.924 | −37.583 | 0.391° | 0.7825 | 0.1047 | 6.88 h |
| `best-model-6temper` (6 tempered, equal) | 0.8869 [0.8415–0.9379] | 0.924 | −37.586 | 0.306° | 0.7822 | 0.1060 | 11.3 h |
| **`6temper-realloc`** (6 tempered, by mass) | **0.9109** [0.8738–0.9398] | 0.924 | −37.643 | **0.216°** | **0.7879** | 0.1018 | **9.42 h** |
| `tempered-1839-1941` (no fuel, reference) | 0.9545 [0.9321–0.9746] | 0.924 | −38.112 | 0.229° | 0.7211 | 0.0355 | 0.45 h |

Reallocation is worth **+0.0240** of split-half. Three extra tempered epochs were worth +0.0071
and cost 1.64× the compute. Reallocation cost **less**: 9.42 h against 11.3 h, a 17% saving at the
same particle total.

The saving is not the point but it is worth recording a likely cause, because it affects how
future allocations should be costed. The two magnetic modes went from 1.4M to 0.5M each — 1.8M
particles moved out of modes that need an IGRF declination lookup at every step and into modes
that do not. That would make the declination grid, not the fuel tables, the marginal cost of a
magnetic-mode particle. It is a hypothesis from the arithmetic, not a measurement; a per-mode
timing breakdown would settle it and does not exist.

## The decisive diagnostic

**Per-epoch effective sample size is identical between the two runs.**

| epoch | 6temper | realloc |
|---|---|---|
| 18:25 | 13.30% | 12.92% |
| 19:41 | 5.67% | 5.67% |
| 20:41 | 25.86% | 25.88% |
| 21:41 | 45.12% | 45.55% |
| 22:41 | 38.13% | 38.52% |
| 00:11 | 11.65% | 11.64% |
| 00:19:29 | 75.49% | 75.75% |

Every epoch agrees to within 0.4 percentage points, and the tightest epoch is 5.67% in both. Same
ESS everywhere, +0.024 of replicate agreement. This is the third and cleanest demonstration that
per-epoch ESS is not what limits replicate agreement in this filter — the first two were the 00:11
tempering (4.3× ESS, no change) and the six-epoch run (10.3× at 20:41, +0.0071). Here the two
statistics are fully decoupled: one is constant while the other moves.

## Where the disagreement went

Mean absolute difference between pooled halves, over all 35 balanced partitions, by latitude band:

| band | 6temper | realloc | change |
|---|---|---|---|
| −45..−40 | 0.0006 | 0.0013 | +117% |
| −40..−38.5 | 0.0681 | 0.0561 | −18% |
| **−38.5..−37 (main peak)** | **0.1341** | **0.0900** | **−33%** |
| −37..−36.5 | 0.0067 | 0.0096 | +43% |
| −36.5..−34.5 (shoulder) | 0.0083 | 0.0103 | +24% |
| −34.5..−32 | 0.0010 | 0.0010 | 0% |
| −32..−25 | 0.0016 | 0.0022 | +38% |
| **total** | **0.2261** | **0.1782** | **−21%** |

The reduction is concentrated in the band the reallocation was aimed at. The shoulder and the
northern tail got noisier, which is the expected cost of taking the magnetic modes from 1.4M to
0.5M, and they carry 5.8% and 1.2% of the disagreement respectively. The trade is strongly net
positive.

## The mechanism, corrected

An interim read at four replicates, computed on the stride-10 backups, suggested that what had
improved was mode-mixture stability in both dominant modes. On the full eight-replicate data that
is only half right, and the half that is wrong should be stated plainly.

| mode | particles | mean probability | relative spread across replicates | distinct surviving draws |
|---|---|---|---|---|
| true track | 1.4M → 2.5M | 0.5809 → 0.5890 | 33.2% → **29.2%** | 880–988 → **1562–1754** |
| lateral navigation | 1.4M → 2.5M | 0.2530 → 0.2515 | 53.6% → 58.1% | 929–1017 → **1673–1835** |
| true heading | 1.4M → 1.0M | 0.1050 → 0.1030 | 40.0% → 65.1% | 1286–1399 → 922–985 |
| magnetic heading | 1.4M → 0.5M | 0.0118 → 0.0114 | 33.9% → 62.1% | 1087–1191 → 359–429 |
| magnetic track | 1.4M → 0.5M | 0.0492 → 0.0452 | 30.5% → 59.5% | 816–908 → 298–356 |

By that measure only true track's *mixing weight* steadied. But the min–max range across
individual replicates is not the measure tied to split-half, which compares two *pooled* halves.
Recomputed as the mean absolute difference between pooled halves over all 35 partitions
(`report/quantity_convergence.py`), the picture is worse still and the correction should be
stated plainly:

| mode probability | best-model | 6temper | realloc |
|---|---|---|---|
| true heading | 8.3% | 7.1% | 12.7% |
| magnetic heading | 6.2% | 6.8% | 12.7% |
| true track | 5.3% | 6.0% | 6.8% |
| magnetic track | 6.8% | 6.9% | 12.9% |
| lateral navigation | 8.3% | 9.6% | 12.0% |

**Every mode's mixing weight is less stable under reallocation, true track included.** So the
improvement is not mixing-weight stability by either measure; the earlier reading that it was,
taken from a four-replicate interim on thinned backups, was wrong.

What did improve, in both dominant modes and by about 80%, is the number of distinct surviving
prior draws — the resolution at which each mode's own conditional posterior is estimated. True
track and lateral navigation carry 84% of the mass between them. Estimating those two conditional
densities better tightens the mixture even where the weights multiplying them are no steadier
than before. The posterior median span across replicates falling 0.306° → 0.216°, the best any
fuel-bearing run has achieved, is the same fact seen from the other side.

This also sharpens what to expect from further reallocation. Pushing more particles into true
track and lateral navigation should keep paying until their conditional densities stop sharpening;
it will not stabilise the mixing weights, and the minor modes will keep degrading. There is a
floor under how far that can go, set by needing the shoulder to remain estimable at all — and the
mixing weights are now the quantity closest to that floor, so the next allocation step should be
smaller than this one.

## What is actually converged, quantity by quantity

A single overlap gate answers one question for the whole posterior and answers it badly in both
directions. `report/quantity_convergence.py` evaluates every reported number on each pooled half
over all 35 partitions. Mean absolute half-to-half difference:

| quantity | best-model | 6temper | **realloc** | no-fuel reference |
|---|---|---|---|---|
| median | 0.066° | 0.058° | **0.043°** | 0.046° |
| 50% HDI, northern bound | 0.089° | 0.084° | **0.064°** | 0.130° |
| 50% HDI, southern bound | 0.564° | 0.489° | **0.124°** | 0.127° |
| 90% HDI, northern bound | 0.139° | 0.151° | **0.107°** | 0.059° |
| 90% HDI, southern bound | 0.323° | 0.310° | **0.251°** | 0.026° |
| peak mass, −38.5..−37 | 8.5% | 7.5% | **4.8%** | 2.4% |
| shoulder mass, −36.5..−34.5 | 7.8% | 6.7% | **9.2%** | 2.8% |
| mode probabilities | 5.3–8.3% | 6.0–9.6% | **6.8–12.9%** | 4.7–7.7% |

Read down the realloc column and the verdict is not one verdict:

- **The location of the posterior is converged.** The median agrees between halves to 0.043°,
  about 2.6 nautical miles on the 7th arc, and it has been stable to 0.06° across three
  successive models. Quoting it to 0.1° is safe.
- **The 50% credible interval is converged**, and this is where reallocation paid most: the
  southern bound went from 0.564° between halves to 0.124°, a factor of 4.5. That single number
  is the largest improvement anywhere in the table.
- **The peak mass is nearly converged**, 4.8% against the no-fuel reference's 2.4%.
- **The shoulder is not converged**, at 9.2% mean and 23% worst case, and it got worse rather
  than better. No fuel-bearing run has it under 6.7%.
- **The mode probabilities are not converged in any run**, not even the one that passes the gate:
  the no-fuel reference still swings lateral navigation by 7.7% between halves.

That is the honest basis on which to relax a single pass/fail bar: not by lowering 0.924, but by
retiring it as the sole gate and reporting each quantity against the precision the paper quotes
it at. The median and the 50% interval are publishable now. The shoulder is direction-robust and
magnitude-unconverged, and saying so is a stronger paper than quoting it to three figures behind
a threshold it does not meet.

## Where this leaves the convergence programme

0.9109 against 0.924 is a shortfall of 0.013, down from 0.044. Posterior summary at 00:19:29,
pooled over eight replicates: median −37.643, mode −37.80, 50% HDI [−38.15, −37.10], 90% HDI
[−39.60, −35.90] with a 0.15° gap near −39.4, 99% HDI [−40.15, −33.35] plus the detached northern
loitering region [−29.85, −26.75]. Log evidence −104.678, unmoved from −104.748. Overlap with
Davey Fig. 10.3 is 0.7879, the highest any full-evidence run in this project has reached, and the
shoulder is 0.1018, which is 42.3% of Davey's 0.2406.

Both remaining candidates are now worth running and they are independent of each other:

1. **Remove the fuel exhaustion-time prior** (`config/sensitivity/no-exhaustion-prior.toml`).
   `results/fuel-path-degeneracy.md` traces the residual degeneracy to that term, and it is a
   conditional hypothesis about the cause of the 00:19 log-on rather than an observation. Smoke
   gate first.
2. **Push the allocation further** toward true track and lateral navigation, now that the
   direction is measured rather than argued.

Report the shoulder as direction-robust and magnitude-unconverged until one of them closes the
remaining 0.013.
