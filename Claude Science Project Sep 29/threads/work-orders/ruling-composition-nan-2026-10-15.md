
# Ruling for approval — the composition convention for not-computed rows, and the split-half tolerance

Item 4. Drafted 15 October 2026 by the coordinating session. **Needs Pete's approval before the
composer runs.**

## The problem, measured

Impact modules return a log-likelihood per impact sample, and some samples get no value. Drift
leaves 16–25 per cent of the weight not computed; the imagery module 1–3 per cent. Carrying
those rows at their (replicate, mode) mean likelihood ratio, which is composition ruling 1,
against excluding them, which is the convention the drift and imagery modules themselves use,
changes the imagery hypothesis's 90 per cent region from **254,000 to 62,000 km²** — a factor of
four on a headline number. The library's default tolerance of 1e-3 nat refuses drift outright.

## Why the rows are missing

A not-computed row means the module could not evaluate that sample: the impact fell outside its
ocean domain, or the acoustic path was blocked, or a transform returned an error. **It does not
mean the sample is impossible**, and the project has already ruled that NaN is not zero.

## The ruling proposed

**1. Carry at the mean. Never exclude.** A module that cannot evaluate a sample has no
information about it, and a factor with no information must contribute a constant — the module
abstains on that row. Carrying at the mean implements exactly that. Excluding instead
renormalises the posterior onto the subset the module happened to be able to compute, which is a
different posterior and is informative selection whenever computability correlates with
location. It does correlate: drift cannot compute for impacts outside its domain, which are the
northern tail, so excluding silently removes the northern tail. That is the whole of the
254,000-to-62,000 difference, and the smaller number is the wrong one.

**2. The not-computed share is a reported statistic, not a footnote.** Every composed table
carries it per module per option. A reader cannot interpret a factor without knowing on how much
of the weight it was silent.

**3. A factor abstaining on more than 10 per cent of the weight is a labelled sensitivity, not a
headline.** Carrying at the mean is honest but it is not free: a factor silent on a quarter of
the weight is a weak factor, and presenting it beside factors that scored everything overstates
it. On run I this puts **drift in the sensitivity column** (16–25 per cent) and leaves the
imagery module in the headline (1–3 per cent). The threshold is a declared convention, like the
split-half floor, and should be stated as ours.

**4. Fix the domain rather than the convention, where that is cheap.** Carrying at the mean is
the correct treatment of missing information, not a licence to leave information missing. Drift's
16–25 per cent is largely its ocean-domain edge, which is a configuration bound rather than a
physical one.

## The split-half tolerance

The library requires every factor's half-to-half log-evidence increment to agree within a fixed
tolerance, default 0.1 nat, provisional; the default 1e-3 refuses drift, and the imagery factor
fails at 0.21–0.36 nat in the free-flight and routes strata.

**Proposed: set the tolerance from the factor's own measured seed-to-seed spread, not a
constant.** A factor cannot be required to agree between halves more tightly than its own Monte
Carlo noise, and a fixed constant either refuses sound factors or passes noisy ones depending
only on how noisy the factor happens to be. Report the tolerance used and the measured spread
side by side, so the test can be audited. Where a factor fails against its own noise, that is a
real failure and the factor is reported as unconverged.

## What changes if this is approved

Every composed number that depended on the unruled convention is replaced by one composition
pass, about an hour. The imagery hypothesis's region is reported at the carry-at-mean value, the
drift factor moves to the sensitivity column on run I, and the composed tables gain a
not-computed column.

## What I need from Pete

Approval, or a different ruling on points 1 and 3 — the 10 per cent threshold in particular is a
judgement call and is the one number here that is mine rather than measured.

---

## Addendum, 15 October 2026 06:30Z — the ruling's measured premise was from the wrong run

The ruling stands as the convention. Its stated consequence for run I does not.

The figures quoted above — drift leaving 16–25 per cent of the weight not computed, the imagery
module 1–3 per cent, and the 254,000-against-62,000 km² swing — were measured in **composer pass 0
on core run (b)**, not on run I. The coordination session quoted them as if they were run I.

Composer pass 2b (`results/composer-pass2b-run-i-ruling.md`, commits 2431bf4, 0bdf91b, 628dbde)
measured the run I shares directly: drift leaves at most **0.092 per cent** of the equal-prior core
weight not computed (GLORYS12; 0.080 per cent GlobCurrent; worst single stratum-seed 4.95 per cent),
the imagery module under 1e-6 per cent, hydroacoustics and searches zero. Pass 2 already carried
not-computed rows at the mean, so applying the ruling changes **no impact-level headline number**:
780 product values and 342 evidence values match pass 2 to the stored rounding, and the largest move
anywhere is +99 km² (+0.16 per cent) on one seabed 50 per cent area, from carrying the seabed step per
seed rather than pooled. **The 10 per cent sensitivity column is empty on run I; drift stays in the
headline.**

Under point 4 (tolerance from each factor's own seed spread), drift passes the split-half check in
1 of 6 options, searches after drift 1 of 6, the imagery factor 3 of 6, searches after the imagery
factor 6 of 6. Under the old fixed 0.1 nat all of the first three failed in all six. The failures are
narrow and share one seed pattern, the non-convergence of core run I.
