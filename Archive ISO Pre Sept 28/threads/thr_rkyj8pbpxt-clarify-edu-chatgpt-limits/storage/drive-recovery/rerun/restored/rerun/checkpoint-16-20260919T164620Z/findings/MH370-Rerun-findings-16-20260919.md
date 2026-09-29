# MH370 Rerun checkpoint 16 findings

Created: 2026-09-19T16:46:20Z

## Question tested

Can an exact defensive ancestor proposal prevent the 18:28:05 genealogical loss identified in checkpoint 15 and improve end-to-end estimator stability?

The proposal operates within each scientific stratum. If root `r` has current normalized target mass `P_r` among `R` positive-mass roots, it proposes the root from

`Q_r = (1 - epsilon) P_r + epsilon / R`,

then chooses a row within that root proportional to its target mass. Each selected descendant retains the exact `p_i / q_i` correction. The policy changes only the resampling proposal; it adds no observation and does not change the target distribution.

## Implementation and controls

The existing, tested `WithinStratumResamplingPolicy` was exposed in an isolated cruise-runner candidate. The configuration defaults to epsilon zero and is validated in `[0,1]`. The selected policy is written to provenance and is forwarded through both ordinary and retained-parent execution paths.

- Particle-filter tests: 74 passed.
- Invalid epsilon 1.1: rejected before sampling.
- Epsilon-zero historical control: 40 scientific-file comparisons across eight seeds were byte-identical to checkpoint 15, including every posterior and filter-checkpoint file.
- Release binary SHA-256: `cae587fd7078efdc681e7eee22fe01e68f6dcf70fd817127e4e00e39e8548f3b`.
- Physical matrix: six epsilon values by eight common seeds, 48 completed runs.

The first launch failure was a non-scientific orchestration error: generated configs initially retained paths relative to the source config directory. It failed before sampling and is preserved. Paths were resolved to exact inputs before the successful matrix.

## Results

| Epsilon | Roots at 18:28:14 | Root ESS at 18:28:14 | Root ESS at 19:41 | Final positive roots | Final root ESS | Final max-root weight | Evidence SD | Median latitude CDF distance |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.00 | 45.50 | 33.10 | 7.02 | 4.88 | 1.49 | 0.792 | 2.92 | 0.772 |
| 0.02 | 46.75 | 33.08 | 7.08 | 4.75 | 1.33 | 0.864 | 2.77 | 0.959 |
| 0.05 | 48.00 | 33.19 | 7.12 | 5.62 | 1.36 | 0.858 | 3.30 | 0.955 |
| 0.10 | 51.12 | 33.04 | 6.77 | 7.62 | 1.43 | 0.826 | 3.88 | 0.905 |
| 0.20 | 55.62 | 32.51 | 6.87 | 14.25 | 1.56 | 0.803 | 3.50 | 0.841 |
| 0.50 | 72.75 | 32.31 | 7.22 | 32.50 | 1.38 | 0.836 | 4.82 | 0.897 |

Positive epsilon does what it is designed to do mechanically: it retains more distinct root labels. At epsilon 0.50, mean positive roots at the final contact rise from 4.88 to 32.50. But those roots carry extremely unequal corrected weights. Mean final root ESS falls from 1.49 to 1.38, mean maximum-root weight rises from 0.792 to 0.836, and evidence standard deviation rises from 2.92 to 4.82.

The same distinction appears immediately after the early resampling. Epsilon 0.50 retains 72.75 roots rather than 45.50, but root ESS is slightly lower, 32.31 rather than 33.10. The extra roots therefore have negligible effective mass. At 19:41, root ESS remains near seven for every epsilon.

No positive epsilon materially stabilizes the location marginals. Median between-seed latitude CDF distances range from 0.841 to 0.959 for positive epsilon, versus 0.772 at epsilon zero. Same-seed epsilon-versus-zero CDF differences are also large, indicating that these 100-root ensembles remain dominated by Monte Carlo path selection.

Mean log-evidence declines as epsilon increases. Because the exact proposal correction preserves the target, this is not evidence for a different physical model and must not be interpreted as a Bayes factor. With only eight high-variance estimates, it is evidence that aggressive defensive mixing increases finite-sample weight variance and downward log-estimate bias.

## Estimator decision

Reject a fixed, all-resampling defensive root mixture as the replacement estimator. It converts genealogical extinction into a larger collection of nominally alive, near-zero-mass roots but does not solve effective ancestry collapse, evidence instability, or marginal instability.

Retain the implementation because it is exact, opt-in, epsilon-zero compatible, and may be useful as a small component of a better targeted proposal. Do not use distinct-root count alone as an acceptance metric; require root ESS, maximum-root weight, evidence behavior, marginal agreement, and synthetic coverage.

## Updated diagnosis

The concentration is not explained by hard physical rejection. Checkpoint 15 found all 3,200 critical-block candidates physically supported. It is also not fixed by resampling more uniformly over existing roots. The main missing ingredient is proposal coverage in trajectory space before the selective 18:39/19:41 likelihood, followed by later genealogical amplification. Real early SATCOM information contributes, but the present forward proposal does not explore enough of the trajectories that remain compatible with later observations.

The next candidate should therefore change trajectory construction, not merely ancestor selection. The most direct route is the already validated two-ended proposal measure: generate uncertain terminal/exhaustion states under explicit 00:15–00:17 and 00:15–00:19 hypotheses, propagate toward the separately sourced 18:22 radar boundary with exact path, endpoint, time, and fuel proposal/prior ratios, and evaluate every SATCOM observation once at its actual time. A prior-predictive mixture must preserve support.

## Scope and limitations

- These are bounded physical diagnostics with 100 initial roots, not convergence runs.
- The physical source remains the broad historical 18:01:49 state at 5.624829 N, 99.048157 E, with fuel anchored at 18:28:05.9.
- The separate bridge target around 18:22:12 at 6.578 N, 96.340 E is not substituted into these runs.
- No backward/full-aircraft fuel-exhaustion bridge is run here.
- No calibrated location probability or solved location is claimed.
- Hydroacoustic evidence remains excluded.

