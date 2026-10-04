# Is the 0.90 split-half floor rigorous?

Short answer: **its origin is arbitrary, the statistic it gates is noisier and more
replicate-dependent than a single number suggests, and a calibrated floor turns out to sit at
0.896 for four replicates — so the verdicts do not change, but the margins are much smaller than
"0.864 against 0.90" implies and the statistic should never be quoted as a bare number again.**

## Where 0.90 came from

Nowhere defensible. `report/convergence.py` states that the threshold has "a criterion stated
elsewhere in the project rather than chosen here", and points at `report/build_report.py`. That
file simply asserts it, in a sentence that switches wording at `split >= 0.9`. There is no
derivation and no external source. It is a round number.

**What Davey et al. used is not established here.** The book PDF is gitignored and absent from
the restored workspace, so this note cannot check it, and I am not going to assert a criterion I
have not read. That remains an open item.

## The statistic is replicate-count dependent

Split-half overlap compares two pooled halves, so it inherits the Monte Carlo noise of whatever
sample each half contains. Fewer replicates per half means noisier halves and systematically
*lower* overlap — for the same posterior and the same sampler.

Measured on the base run, which is the project's converged reference, by re-computing the
statistic over every balanced partition of every subset of its eight replicates:

| replicates | mean | 5th percentile | range | partitions |
|---|---|---|---|---|
| 4 | 0.919 | **0.896** | 0.885–0.955 | 210 |
| 6 | 0.934 | 0.914 | 0.906–0.965 | 280 |
| 8 | 0.943 | **0.924** | 0.920–0.964 | 35 |

The same converged posterior scores 0.943 at eight replicates and 0.919 at four. A fixed floor
therefore judges a four-replicate run about 0.025 more harshly than an eight-replicate one, for
no reason connected to the sampler.

## The statistic is also noisy in itself

The engine reports one split — first half against second half. That choice is arbitrary, and with
four replicates there are only three balanced partitions to choose from. They disagree
substantially:

| run | stored (first/second) | mean over partitions | range |
|---|---|---|---|
| davey2016 (8 seeds) | 0.934 | 0.943 | 0.920–0.964 |
| endurance-1-fuel-only | 0.996 | 0.997 | 0.996–0.997 |
| endurance-2-bto-0011 | 0.766 | 0.784 | 0.764–**0.822** |
| endurance-3-btobfo-0011 | 0.857 | 0.837 | 0.786–0.868 |
| endurance-4-btobfo-0019 | 0.864 | 0.837 | 0.780–**0.878** |
| reject-4-btobfo-0019 | 0.829 | 0.838 | 0.828–0.846 |

Rung 4 spans 0.780 to 0.878 across the three available splits — a range of 0.099, wider than its
distance from the floor. Rung 2 reads 0.766 or 0.822 depending only on which half you call first.

## A calibrated floor, and what it changes

The principled replacement is to ask what a *converged* run of this engine scores at the same
replicate count, and fail anything below that distribution's lower tail. Taking the base run as
that reference and its 5th percentile as the floor:

| run | seeds | mean | calibrated floor | verdict |
|---|---|---|---|---|
| davey2016 | 8 | 0.943 | 0.924 | pass |
| endurance-1-fuel-only | 4 | 0.997 | 0.896 | pass |
| endurance-2-bto-0011 | 4 | 0.784 | 0.896 | fail |
| endurance-3-btobfo-0011 | 4 | 0.837 | 0.896 | fail |
| endurance-4-btobfo-0019 | 4 | 0.837 | 0.896 | fail |
| reject-4-btobfo-0019 | 4 | 0.838 | 0.896 | fail |

**No verdict changes.** The calibrated four-replicate floor, 0.896, lands within 0.004 of the
round number that was there by assertion — so 0.90 happens to be about right for four replicates,
and is too lenient for eight, where the calibrated floor is 0.924 and the base run's stored 0.934
is a narrower pass than it looked.

The fuel runs remain distinguishable from converged: at matched four-replicate resolution the
converged reference spans 0.885–0.955 while rungs 3 and 4 span 0.780–0.878, and the two ranges do
not overlap. The user's intuition that 0.86 "is not totally degenerate" is right in spirit — these
runs are far from the 0.5-ish overlap a genuinely degenerate sampler would give — but they are
still outside what this engine produces when it has converged.

## What should change in practice

1. Quote the split-half as **mean and range over all balanced partitions**, never as the single
   first-against-second value. For four replicates that single value can be off by 0.05.
2. Make the floor a function of replicate count, calibrated against a converged reference run,
   rather than a constant. The three values measured here are 0.896, 0.914 and 0.924 for four,
   six and eight replicates.
3. Treat the floor as a screening device rather than a proof. It compares a run against one
   reference posterior; it is not a statement about absolute error, and nothing in it bounds the
   bias of a quantity like the shoulder probability — for that, the half-to-half spread of the
   quantity itself is the honest diagnostic, and for the fuel runs that spread is ±19 %.
