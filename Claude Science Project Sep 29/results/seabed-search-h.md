# Searched areas on end of flight's run H: the routes stratum, against run D-he's

12 October 2026, Searched Areas module. Architecture's overnight plan of 00:05Z, step 4, second half.

**Run H is ONE STRATUM, not a run.** It is the routes stratum recomputed (`next-h-routes`, 8 seeds,
3,137,792 rows). Its Z is the routes-stratum value and must not be read beside a four-stratum mixture. In run
D-he's mixture routes carries weight 0.019, so substituting run H's routes moves the mixture by less than this
module can resolve. The comparison that means something is routes against routes, which is what follows.

Primary arm (survival factor applied), +alive, rho = 0.05, point target, Ocean Infinity excluded.

| 00:19 option | Z, run H routes | Z, run D-he routes | difference | on Phase 2 before, H / D-he | ESS after, H / D-he | estimable, H / D-he |
|---|---|---|---|---|---|---|
| 00:19 Held Out | 0.6405 | 0.6790 | -0.0385 | 0.400 / 0.358 | 727,884 / 2,380,748 | yes / yes |
| R600 BTO Only | 0.6644 | 0.6984 | -0.0340 | 0.374 / 0.336 | 550,280 / 3,009,995 | yes / yes |
| R600 BTO + Raw BFO | 0.4153 | 0.4671 | -0.0519 | 0.651 / 0.594 | 10,540 / 37,254 | yes / yes |
| Holland H1 | 0.2385 | 0.2895 | -0.0510 | 0.848 / 0.791 | 288 / 1,206 | NO / yes |
| Holland H2 | 0.2961 | 0.3398 | -0.0437 | 0.784 / 0.735 | 221 / 826 | NO / NO |

**Readings.**
1. **Run H's routes puts more probability on ground the ATSB searched than run D-he's does**, in every option
   (0.400 against 0.358 for Held Out; 0.848 against 0.791 for H1). The searches therefore take more away, and Z
   is lower by 0.034 to 0.052 throughout. That is a consistent shift, not noise, and it is the only thing this
   module can say about the difference between the two routes computations.
2. **Holland H1 and H2 are NOT estimable within this stratum alone** - effective sample size after the searches
   288 and 221, against the floor of 1,000. They are estimable in the **four-stratum** run D-he set (4,537 and
   3,307). This is not a regression: run H carries 3.14 M rows against run D-he routes' 12.8 M, about a quarter
   of the sample, and H1/H2 need a large sample precisely because so few simulated flights can produce them.
   **No single stratum has ever made them estimable; only the pooled set does.**
3. Within run D-he's own routes stratum H1 is marginal (ESS 1,206, just over the floor) and H2 is below it (826).
   Both are reported, H2 as not estimable.

## The wreckage field on run H

Settling posted `settling/run-h` after the first pass here, so the field check ran on all five primary "all"
products at step 1 (every outcome). **Note that run H's product indexing is NOT run D-he's** - settling adds
per-route products, so the "all" arms are P00, P10, P20, P30, P40 rather than P00, P06, P12, P18, P24. A first
pass here used run D-he's indices and was discarded.

| 00:19 option | outcomes | Z impact point | Z field mean | Z any piece | field - point | any - point | impact off, field on | impact on, field off |
|---|---|---|---|---|---|---|---|---|
| 00:19 Held Out | 40,000 | 0.6426 | 0.6420 | 0.6094 | -0.0006 | -0.0332 | 0.0368 | 0.0000 |
| R600 BTO Only | 40,000 | 0.6671 | 0.6663 | 0.6358 | -0.0008 | -0.0313 | 0.0326 | 0.0000 |
| R600 BTO + Raw BFO | 40,000 | 0.4147 | 0.4136 | 0.3761 | -0.0011 | -0.0386 | 0.0434 | 0.0000 |
| Holland H1 **(NOT ESTIMABLE)** | 40,000 | 0.2331 | 0.2331 | 0.1878 | +0.0000 | -0.0453 | 0.0502 | 0.0000 |
| Holland H2 **(NOT ESTIMABLE)** | 40,000 | 0.2954 | 0.2960 | 0.2386 | +0.0006 | -0.0568 | 0.0549 | 0.0000 |

1. **Shape of the field: -0.0011 to +0.0006. Fifth run, same answer.**
2. **What counts as a detection: -0.0313 to -0.0568**, again largest under Holland's readings.
3. **The asymmetry holds a fifth time: impact on searched ground with the field entirely off it is 0.0000**, in
   every option of every run this module has done.
4. The point arm reproduces this module's own run H sweep to 0.0054 or better in every option, by settling's
   resampling route rather than direct weighting.
5. H1 and H2 remain **not estimable** on run H: settling's own row effective sample sizes are 111 and 386.

## Published

`mh370-exchange/searched-areas/run-h/` (READY, 48 MB, SHA256SUMS, README.md): `seabed-lnL.npy` plus the two raw
coverage columns, 8 seeds, row-aligned with `impacts32.npy`, 3,137,792 rows. Not-computed weight **0.000**.

## COVERAGE

**(a) Feasible set** and **(b) model's reach** are run D-he's, unchanged - end of flight's labels for run H are
identical to run D-he's (same recipe, binary mh370-eof-he6 against he5).
**(c) Proposal's coverage:** 3,137,792 impacts in one stratum. **GAP: Holland H1 and H2 are not estimable in this
stratum alone (ESS 288 and 221).** Any run-H product naming H1 or H2 must say so; the estimable H1/H2 result is
the four-stratum one in `results/seabed-search-d-he.md`. Wreckage field not applied to run H: settling has posted
no run H samples, so this is a point-target result. rho a single value at the base, swept in the table above's
source JSON. ATSB Figure 73's three percentages (A-8) still unverified in primary form.

- Searched Areas Module
