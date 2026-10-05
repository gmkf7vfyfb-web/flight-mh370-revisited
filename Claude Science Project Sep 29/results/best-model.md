# The best model: fuel evidence inside a tempered filter

`config/davey2016.toml` + `config/sensitivity/best-model.toml`, eight replicates of 7,000,000
particles (1,400,000 per autopilot mode), 6.88 h wall on 18 threads, 7.2 GB peak. This is the
first run to combine the in-filter fuel model with the annealed-SMC sampler that fixed the 19:41
bottleneck, and it is the configuration the project had been building toward: fuel as evidence,
on Davey's own priors, with a sampler that converges on the fuel-free problem.

**It gets closest to Davey of anything we have run, and it does not converge.** Both halves of
that sentence are the result.

## Agreement with Davey Fig. 10.3

| quantity | this run | Davey Fig. 10.3 | fuel-free tempered |
|---|---|---|---|
| median latitude at 00:19 | **−37.583°** | −37.532° | −38.112° |
| mode | −37.50° | −37.9° | −38.05° |
| 95% interval | −39.561 to −34.481 | −39.378 to −34.903 | — |
| density overlap with Fig. 10.3 | **0.7825** | 1 | 0.7211 |
| shoulder mass, 34.5–36.5°S | **0.1047** | 0.2406 | 0.0355 |
| log evidence | −104.734 | — | −96.286 |

The median lands **0.05° from Davey's**, against 0.58° for the fuel-free run. Overlap improves
from 0.7211 to 0.7825. The northern shoulder, which no configuration has reproduced, reaches
**43.5% of Davey's** — the largest share any *full-evidence* run has achieved (the previous best
was 35%, `endurance-4`; `endurance-3` reached 48% but scored evidence only to 00:11).

Fuel costs 8.45 nats of log evidence. That is not a verdict against it: adding a likelihood
factor can only lower the evidence, and the comparison is between two different models of what
the data are, not two hypotheses about the path.

### The mechanism is mode reweighting

| autopilot mode | fuel + tempering | fuel-free tempered |
|---|---|---|
| true track | 59.2% | 56.4% |
| lateral navigation | 24.6% | 35.8% |
| true heading | 10.2% | 5.9% |
| magnetic track | 4.8% | 1.6% |
| magnetic heading | 1.2% | 0.3% |

Endurance moves weight out of lateral navigation and into the three heading-and-magnetic modes,
which between them go from 7.8% to 16.2%. Those are the modes that carry the shoulder, which is
why fuel and the shoulder move together. This corroborates, on a converged-sampler baseline, what
the narrow-Mach fuel runs showed earlier: Davey's Assumption 4 — substituting a 0.73 Mach floor
for a fuel constraint — is not equivalent to modelling endurance, because endurance admits a
different and more northern set of trajectories than a speed floor does.

## Convergence: it fails, and by how much

Split-half overlap over **all 35 balanced partitions** of the eight replicates
(`report/model_comparison.py`, which is the honest statistic — `convergence.py` reports the
runner's single first-half-against-second-half value, 0.8604 here, one arbitrary choice among 35):

| | mean | min | max | floor at 8 replicates | verdict |
|---|---|---|---|---|---|
| fuel + tempering | **0.8798** | 0.8260 | 0.9368 | 0.924 | **fails** |
| fuel-free tempered | 0.9545 | 0.9321 | 0.9746 | 0.924 | passes |

Replicate median span is 0.3915° against 0.229° fuel-free; the eight replicate medians run
−37.8182 to −37.4267. The per-replicate curves in `best-model-8seed-density-m0019a.pdf` show it
directly: peak heights span roughly 0.35 to 1.35 per degree, a factor of four.

Doubling the replicates from four to eight narrowed the gap but did not close it. At four
replicates the statistic was 0.8083 against a 0.896 floor, short by 0.088; at eight it is 0.8798
against 0.924, short by 0.044. The floor rises with replicate count because the statistic itself
does, so halving the shortfall by doubling the replicates is real progress on the same scale —
but extrapolating it would need something like 32 replicates, which is not the fix.

## What actually limits it — and this is new

The bottleneck has **moved off the tempered epochs**. Per-epoch effective sample size, mean
fraction over replicates and modes:

| epoch | fuel + tempering | fuel-free tempered | change |
|---|---|---|---|
| 18:25 | 13.30% | 36.24% | ↓ 2.7× |
| 18:28:05 | 67.52% | 72.79% | — |
| 18:28:14 | 54.53% | 58.93% | — |
| 18:39 *(tempered)* | 31.25% | 31.03% | unchanged |
| 19:41 *(tempered)* | 5.67% | 6.04% | unchanged |
| **20:41** | **2.50%** | 8.82% | **↓ 3.5×** |
| 21:41 | 7.63% | 19.34% | ↓ 2.5× |
| 22:41 | 5.54% | 12.19% | ↓ 2.2× |
| 23:15 | 58.17% | 82.01% | ↓ 1.4× |
| 00:11 *(tempered)* | 11.62% | 4.60% | ↑ 2.5× |
| 00:19:29 | 75.68% | 76.38% | — |
| 00:19:37 | 53.62% | 54.80% | — |

Tempering holds its two epochs exactly where it put them, and the three tempered epochs are no
longer the constraint. Fuel instead depresses the **untempered mid-flight stretch**, and 20:41 is
now the tightest epoch in the run at 2.50% — below where 19:41 ever was after tempering. The
pattern is consistent: `require_power_until = "m0011"` discards trajectories whose tanks run dry
early, and whether a trajectory will run dry is largely decided by how it flew between 20:41 and
22:41, so that is where the fuel factor concentrates its weight variance.

That points to a targeted and much cheaper fix than more particles: **temper 20:41, 21:41 and
22:41 as well.** Tempering is the one intervention of five that worked, it costs roughly 1.8×
runtime per tempered epoch at 16 stages, and it is already implemented and config-gated. The
2.8M-particle-per-mode run remains the fallback, but it is now the second choice rather than the
first.

A correction to a claim made from the four-replicate partial: I reported there that fuel cuts the
distinct surviving prior draws hardest in magnetic heading and magnetic track. At eight
replicates that is wrong in direction. Minimum distinct origins across replicates:

| mode | fuel + tempering | fuel-free tempered |
|---|---|---|
| true heading | 1150 | 1136 |
| magnetic heading | 1016 | 398 |
| true track | 693 | 2277 |
| magnetic track | 808 | 323 |
| lateral navigation | 797 | 2061 |

Fuel *raises* surviving draws in the two magnetic modes, by 2.6× and 2.5×, and *lowers* them in
true track and lateral navigation by about 3×. That is the same reweighting the mode mixture
shows, seen from the sampler's side: the modes fuel favours get more of the population and
therefore retain more diversity. Static-parameter collapse is not the problem in any mode — the
smallest figure, 693, is well clear of the ~100 the engine's README cites as the bootstrap-filter
failure case.

## How to quote this run

The posterior summaries are usable with the caveat stated: the **direction** of every fuel effect
is robust (the median moves north, overlap and shoulder both rise, every replicate agrees on
that), the **magnitudes** are not converged estimates. In particular do not quote the shoulder to
three figures; "about 43% of Davey's, direction robust, magnitude unconverged" is what the data
support. The 99% upper bound of −26.15° is the detached northern loitering mode appearing at the
edge of the credible region, not a plausible terminus in its own right; at 90% the interval closes
to −35.85°.

Files: `best-model-8seed-position-m0011.pdf`, `best-model-8seed-position-m0019a.pdf`,
`best-model-8seed-density-m0011.pdf`, `best-model-8seed-density-m0019a.pdf`,
`best-model-report.pdf` (8 pages), `model-comparison.csv`.
