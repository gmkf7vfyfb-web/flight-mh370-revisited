# MH370 Rerun checkpoint 15 findings

Created: 2026-09-19T16:16:01Z

## Question tested

Does expanding every retained parent into four complete transition candidates at the 18:39/19:41 block reduce the estimator's ancestry collapse and improve end-to-end stability, or does it mainly inflate ordinary row ESS with correlated descendants?

## Design

Eight common seeds (`37150001`–`37150008`) were run under four scenarios:

| Scenario | Initial roots | Candidates per retained parent | Planned transition count | Critical-block candidates |
|---|---:|---:|---:|---:|
| `k1-roots100` | 100 | 1 | 800 | 100 |
| `k1-roots140` | 140 | 1 | 1,120 | 140 |
| `k1-roots400` | 400 | 1 | 3,200 | 400 |
| `k4-roots100` | 100 | 4 at 18:39/19:41 | 1,100 | 400 |

The same-root comparison isolates the pool. The 140-root comparison approximately matches total propagation work. The 400-root comparison gives both methods the same number of critical-block candidates while allocating the baseline budget to independent early roots.

All 32 runs completed. The release binary SHA-256 was `2599a10fe70b1b3c65ca432c226da4557396673d4f8e8fce71c7e188a78aca49`. Same-seed 100-root `K=1` and `K=4` checkpoint records were exactly identical through 18:28:14 in all eight pairs. All 3,200 `K=4` block candidates were positive. Candidate and realized log-evidence increments agreed within `1e-12`; output-resampling corrections were below `1e-12`.

## Main metrics

| Scenario | Evidence SD | 19:41 row ESS | 19:41 root ESS | 19:41 max root | Final row ESS | Final root ESS | Final max root |
|---|---:|---:|---:|---:|---:|---:|---:|
| `K=1`, 100 roots | 2.921 | 8.24 | 7.02 | 0.277 | 3.91 | 1.49 | 0.792 |
| `K=1`, 140 roots | 1.051 | 7.24 | 5.98 | 0.338 | 3.08 | 1.67 | 0.778 |
| `K=1`, 400 roots | 1.937 | 23.76 | 21.10 | 0.144 | 8.15 | 2.10 | 0.682 |
| `K=4`, 100 roots | 4.287 | 81.52 | 12.58 | 0.185 | 3.16 | 1.43 | 0.835 |

At equal roots, `K=4` improves 19:41 root ESS in seven of eight paired seeds and maximum-root weight in seven of eight. It improves 19:41 row ESS in all eight. By the final contact, it improves root ESS in only four of eight and maximum-root weight in only four of eight. The mean direction is slightly worse.

At approximately equal total propagation work, `K=4` improves 19:41 root ESS in seven of eight seeds but final root ESS in only two of eight. Its mean final maximum-root weight is `0.835`, compared with `0.778` for the 140-root `K=1` ensemble.

At equal critical-block candidate count, the 400-root `K=1` method is better genealogically: mean 19:41 root ESS is `21.10` versus `12.58`, final root ESS `2.10` versus `1.43`, and final maximum-root weight `0.682` versus `0.835`. This comparison favors genuine early-state coverage over multiple descendants from a smaller root set.

## Why row ESS was misleading

At 18:28:05 the 100-root filter's mean ESS is `40.01`, below the 50% threshold, so posterior resampling occurs. At 18:28:14 the mean row ESS has rebounded to `85.23`, but only `45.5` distinct prior roots remain and root ESS is `33.10`. The mean row/root ESS ratio is already `2.62`.

The `K=4` pool begins from those same surviving roots. At 19:41 it reports mean row ESS `81.52`, but root ESS is only `12.58`; the ratio is `6.90`. Its mean candidate pool contains `45.5` positive roots but the downselected output contains only `27.4` distinct roots. Thus the large row ESS is real as a weighted-row statistic but does not represent independent initial-state coverage.

The same divergence appears later. Ordinary resampling produces many rows attached to a handful of roots; consequently row ESS repeatedly looks tolerable while root ESS falls toward one.

## Location-marginal stability

Between-seed weighted CDF distances remain very large:

| Scenario | Median latitude CDF distance | Median longitude CDF distance |
|---|---:|---:|
| `K=1`, 100 roots | 0.772 | 0.772 |
| `K=1`, 140 roots | 0.853 | 0.879 |
| `K=1`, 400 roots | 0.725 | 0.703 |
| `K=4`, 100 roots | 0.976 | 0.952 |

The intersection of the eight per-run 5–95% latitude and longitude intervals is empty for every method except small nonzero overlap in the 400-root ensemble. Therefore none of these bounded ensembles supports calibrated location probabilities.

## Scientific interpretation

The results strengthen the earlier three-part diagnosis:

- real information: early SATCOM factors substantially concentrate the posterior;
- coverage failure: resampling after 18:28:05 removes initial roots before the difficult long transition;
- genealogical amplification: the 18:39/19:41 bottleneck and later resampling concentrate the remaining genealogy.

Physical support is not the primary cause. Every `K=4` candidate in this experiment is supported, but candidate/root ESS is still limited. The proposal pool accurately samples more descendants without replenishing lost early states.

## Estimator decision

Do not adopt the single-block `K=4` retained-parent pool as the replacement estimator. Keep it as a valid diagnostic and possible component of a later bridge, because it improves local root ESS and has exact weights. The next modification should act at the 18:28:05 resampling boundary itself.

The particle-filter library already contains a tested `uniform_root_mixture_epsilon` policy. It samples ancestors from a mixture that protects roots and applies an exact importance correction. The next physical candidate should expose this policy without changing the epsilon-zero path, then test epsilon sensitivity using exact solvable cases, synthetic recovery, and the present eight physical seeds.

## Scope and limitations

- These are bounded physical estimator diagnostics, not convergence runs.
- Eight seeds are enough to reject a strong `K=4` improvement claim, not to calibrate a location distribution.
- The runs use the broad historical source at 18:01:49 with its existing fuel anchor, not the distinct 18:22:12 final-radar bridge target.
- The backward fuel-exhaustion proposal is not exercised here.
- Hydroacoustic evidence is excluded.
- Evidence differences diagnose Monte Carlo behavior; they are not Bayes factors between different physical models.
