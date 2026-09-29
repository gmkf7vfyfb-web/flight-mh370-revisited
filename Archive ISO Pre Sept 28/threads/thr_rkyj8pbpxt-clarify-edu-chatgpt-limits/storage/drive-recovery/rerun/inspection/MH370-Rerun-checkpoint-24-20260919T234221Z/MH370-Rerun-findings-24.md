# Checkpoint 24 — exact population replay and factor attribution

Completed 19 September 2026 UTC. Stable code remains checkpoint 20; bridge research
remains checkpoint 22; the latest ensemble is checkpoint 23. This checkpoint adds
diagnostics, not a new calibrated posterior or a replacement physical model.

## What was executed

The unchanged stable executable reran checkpoint-23 seeds 37230001 and 37230002,
5,000 initial particles each, with its existing opt-in factor export enabled for
the 18:39/19:41 block. Both posterior CSVs and filter-checkpoint files are
byte-identical to their archived originals. Every saved particle field matches
exactly except the operational elapsed_seconds field. These are authenticated
replays, not 10,000 additional independent samples.

The exporter checked 10,000 replayed child states and 10,000 weight identities,
and saved 20,000 contact-factor rows. All 10,000 block proposals remained within
model support. The two proposal banks contain 2,235 and 2,227 distinct initial
physical states/ancestors, respectively. Support rejection therefore does not
explain the weighting collapse in these two banks.

## The bottleneck is not simply a tight observation

Effective initial ancestry after each cumulative term on the same proposal bank:

| Factor stage | Seed 37230001 | Seed 37230002 |
|---|---:|---:|
| Incoming at 18:28:14 | 1,614.51 | 1,587.79 |
| Add 18:39 proposal correction | 175.00 | 155.31 |
| Add 18:39 BFO | 14.56 | 66.28 |
| Add 19:41 proposal correction | 27.80 | 2.23 |
| Add 19:41 BTO | 6.24 | 113.10 |
| Add 19:41 BFO | 6.31 | 181.34 |

The same observation can decrease concentration in one sampled bank and increase
it in another. The full correction-only stress weights have ancestry ESS 5.49
and 9.52. Observation-only stress weights have ESS 731.46 and 723.47. Removing
proposal corrections is **not a valid fix**: those ratios are required to target
the declared prior rather than the guided proposal.

This is direct evidence of large proposal-correction effects in the current core
run. Together with seed sensitivity, it supports improving proposal overlap and
checking rare high-weight paths; it does not prove a unique causal percentage or
establish that an observation should be weakened or discarded.

We also evaluated all 32 subsets of the two proposal corrections and three
measurement factors, allocating changes in negative log ancestry ESS symmetrically
over factor orderings. Proposal terms dominate the positive loss contributions
in both banks. Some measurement contributions are negative (they make weights
more even). Full subset results are in factor-attribution.json. These allocations
describe the realized bank only, not information-theoretic fractions or posterior
probabilities of competing causes.

## BFO ablations must refit the shared bias

For a retained subset of BFO contacts, centered residuals d have covariance
C = 49 I + V 11', where V is the incoming calibration-bias variance in Hz squared.
The joint log likelihood uses the full determinant and quadratic form of C.
Core block comparisons use each incoming particle's bias distribution. Waypoint
comparisons start at the declared 150 Hz mean and 625 Hz-squared variance.

This matters: deleting the stored 18:39 BFO factor without recomputing the later
bias prediction is not equivalent to leaving that observation out. Correctly
refitted leave-18:39-out stress weights give root ESS 2.12 and 4.34, worse than the
full factors in both banks. No observation is removed from the actual estimator.

Independent joint-Gaussian reconstruction matches the core saved BFO factors to
better than 1e-9 log units and waypoint SATCOM sums to better than 1e-8. Eight new
tests pass, including dense-covariance comparisons for every subset, every
sequential ordering of a four-contact example, and a demonstration that naive
factor deletion gives a different result. These are arithmetic tests, not
scientific calibration tests.

## The four core seeds disagree materially

At 19:41, ancestry ESS spans 3.33–181.34 across the four checkpoint-23 seeds.
At fuel exhaustion it is approximately 11.71–12.29. Similar final ESS does not
show that the distributions agree.

The largest pairwise cumulative-distribution differences at fuel exhaustion are:

| Marginal | Maximum CDF difference | Seeds | Wasserstein distance for that pair |
|---|---:|---|---:|
| Latitude | 0.62576 (62.6 percentage points) | 37230002 / 37230003 | 0.9434 degrees |
| Longitude | 0.70147 (70.1 percentage points) | 37230002 / 37230003 | 1.4210 degrees |

These are empirical weighted CDF distances, not KS p-values. Row dependence,
small effective ancestry and the common continuation RNG invalidate a naive
i.i.d. significance interpretation. The corrected log-evidence estimates span
approximately -91.10 to -90.05; their relative proximity does not certify marginal
convergence. No coverage claim is possible without a known-truth recovery study.

## Waypoint failure starts early and is not driven by fuel alone

The two 5,000-proposal waypoint banks preserve 538 and 535 complete route/fuel-
supported paths. On those saved paths:

| Diagnostic | Seed 37231002 ESS | Seed 37231003 ESS |
|---|---:|---:|
| Fuel factor only | 497.17 | 493.36 |
| All BFO factors, joint shared bias | 14.66 | 30.89 |
| All BTO factors only | 1.00 | 1.00 |
| SATCOM prefix through 18:28:14 | 6.74 | 11.91 |
| SATCOM prefix through 19:41 | 1.34 | 4.11 |
| Full target | 1.00 | 1.00 |

These prefix calculations are hindsight-conditioned on eventual route and fuel
support. They are **not** an online staged-filter experiment. Contact traces were
not retained for rejected paths, so this checkpoint does not infer their prefix
distribution. The BTO-only collapse identifies an important failure of coverage
in the saved waypoint bank; it neither validates nor excludes the route hypothesis.

## Unchanged scientific boundaries

Gaussian SATCOM likelihoods, recorded contact times, no jettison, Mach 0.73–0.84,
altitude 25,000–43,000 ft, and exhaustion 00:16–00:19 remain as in checkpoint 23.
No noise inflation, 2-sigma rejection, timing optimization or endpoint observation
was introduced. Historical 18:01:49 source, conditional 18:22:12 airway boundary,
and 18:28:05.9 fuel anchor remain distinct. MEKAR timing is still conditional, not
an authenticated radar constraint. 00:19/post-exhaustion observations and
hydroacoustics remain excluded. Resolution files and automations were untouched.

## Next executable work

1. Run larger independent core populations (suggested four 20,000-root seeds),
   retaining block-3 factor diagnostics. Compare CDF distances, root ESS, evidence
   variability and initial physical diversity rather than only row count.
2. Investigate the two proposal-correction tails with bounded, same-target
   alternatives and exact p/q corrections; use matched budgets and keep rejected
   variants. Do not remove corrections or loosen observation errors to improve ESS.
3. For waypoint sampling, first retain prefix/failure contact traces and reconcile
   the MEKAR/radar source law. Then implement staged proposals with a logged
   normalized route-selection law and exact correction. Test known-truth recovery
   before treating concentration as a location PDF.
4. Continue checkpoint-22 physical bridge work separately. Do not add 00:19 or
   hydroacoustic evidence until the relevant core/EoF gates are met.

The task is not blocked and remains unfinished. Frozen released files have not
been changed. Validation-wrapper false alarms and their resolutions are retained
in failed-trials.md.
