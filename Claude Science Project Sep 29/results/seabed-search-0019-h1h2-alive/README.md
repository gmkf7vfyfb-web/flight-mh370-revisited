# The standard result under end of flight's `+alive` reference

10 October 2026, searched-areas module, **PROVISIONAL-OVERNIGHT**.
`impact-map-0019-h1h2-alive.{pdf,png,json}`, from
`engine/hypotheses/seabed-search/impact_map_options.py --constraints alive` on `runs/eof-289-full`
(4 seeds x 3.2 x 10^6 impacts; prior track 289.7 deg at 18:01:49 UTC, base config
`config/davey2016.toml`, resolved `bfo_bias` 150 +/- 25 Hz; arcs from `runs/fixture-8/run.json`).

End of flight's 04:05 UTC entry made `+alive` the provisional reference for downstream modules: the
aircraft was airborne at 00:19:37.443, so that the log-on acknowledge could be sent at all. That is a
datum about the burst's existence, separate from its BTO and BFO values, and it binds on the held-out
arm, which otherwise puts 10.2% of its weight before that burst. This is the same four-panel
comparison as `results/seabed-search-0019-h1h2/` run under it.

| # | arm | Z plain → +alive | 1 − Z, +alive | mass on Phase 2, +alive | median before → after, +alive | 90 % area before → after, +alive (km²) | ESS +alive | estimable |
|---|---|---|---|---|---|---|---|---|
| 1 | Held out: no 00:19 observation | 0.7335 → 0.7206 | 0.2794 | 0.311 → 0.047 | 36.95°S → 36.90°S | 540,301 → 653,222 | 11,042,105 → 8,322,034 | yes |
| 1a | R600 BTO arc only | 0.7078 → 0.7081 | 0.2919 | 0.325 → 0.050 | 37.71°S → 38.09°S | 339,182 → 413,533 | 6,465,333 → 4,764,030 | yes |
| 2 | R600 BTO + BFO as observed | 0.5249 → 0.5249 | 0.4751 | 0.529 → 0.108 | 37.25°S → 37.30°S | 211,616 → 286,719 | 197,539 → 117,404 | yes |
| 3 | **Holland H1** | 0.3287 → 0.3287 | 0.6713 | 0.748 → 0.300 | 36.38°S → 37.29°S | 36,787 → 40,035 | 36 → 26 | **NO** |
| 4 | **Holland H2** | 0.2772 → 0.2772 | 0.7228 | 0.805 → 0.313 | 36.24°S → 36.28°S | 51,462 → 65,033 | 82 → 40 | **NO** |
|  | R1200 only, Holland offset | 0.3425 → 0.3425 | 0.6575 | 0.732 → 0.224 | 36.42°S → 35.21°S | 139,146 → 237,525 | 10,065 → 4,675 | yes |

Areas are 90 % highest-posterior-density on a 0.02 deg grid smoothed at 0.1 deg, on the authalic
sphere. ESS is the Kish effective sample size pooled over four seeds (12.8 x 10^6 impacts); anything
under 1,000 is reported as unconverged, never as a result.

## What changes, and what does not

1. **Only the held-out arm moves.** `+alive` costs it about 10% of its weight and takes the evidence
   from **Z = 0.7335 to 0.7206**, so the searches now remove 27.9% of its probability rather than
   26.7%. Mass on Phase 2 coverage rises from 0.297 to 0.311: the trajectories the constraint removes
   are short ones that impact before 00:19:37, and they sit off searched ground.
2. **Every arm that scores a 00:19 burst is unchanged to four decimals**, because scoring a burst
   already requires the aircraft to have a state at it. The BTO-arc-only arm moves in the fourth
   decimal (0.7078 to 0.7081) and `none__fuel-exhaustion` in the third (0.5865 to 0.5911).
3. **A finding of mine weakens under the constraint, and it should be reported that way.** On the plain
   held-out arm the seabed searches move the median 0.20 deg NORTH, -36.78 to -36.58. Under `+alive`
   the same shift is **0.05 deg**, -36.95 to -36.90. The direction survives; the magnitude does not.
   The earlier statement that the full-scale shift "reverses to the north" should therefore be read as
   "the southward shift seen at smoke scale does not survive full scale, and what replaces it is a
   shift of between 0.05 and 0.20 deg north depending on whether the 00:19:37 burst is required to
   exist". The widening is the robust part: the 90 % region grows in every estimable arm.

## Which to quote

The plain arms stay published; `+alive` is the provisional reference and is labelled as such wherever
it is quoted, pending Pete's choice between plain, `+alive` and `+silent`. `+silent` is not run here:
it keeps only 14% of the held-out weight and moves the median 1.2 deg, so it is a materially different
posterior rather than a refinement, and it is end of flight's to recommend before this module spends a
run on it.

## Two definitions that are now end of flight's rather than mine

Their `option_posteriors` reads every `loglik:` column from the run itself and derives the BTO-only
arms, so this script no longer widens their option list or derives `r600-bto` locally. One definition
of each, and it is theirs. The `+alive` factor is likewise theirs, passed straight through.
