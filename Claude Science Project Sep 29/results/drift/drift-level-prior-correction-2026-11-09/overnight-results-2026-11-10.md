# Overnight runs: higher-windage scenario, ocean-error length scale, particle noise (10 Nov 2026)

Status: working record. Windage classes are provisional (my choices; Pete asked for a higher range as a minimum sensitivity). Companion to `wide-windage-results-2026-11-10.md`.

## 1. Summary

- Higher-windage scenario (exterior class log-normal, median 2.4 %, σ(log) 0.35, truncated 0.8 to 6 %): drift alone median 34.6° S, 30 % north of 33° S. Tension with the ruled core: ln S +0.34, d 1.07, p 0.566 (0.6σ); bootstrap range of p 0.49 to 0.65.
- The three windage priors give p = 0.109 (production), 0.320 (wide) and 0.566 (higher). The tension falls as the windage prior moves up.
- Combined with the core (one dimension): median 36.1° S, mean 35.98° S, 3.8 % north of 33° S. Core alone: 36.4° S, 35.95° S, 8.1 %.
- The data prefer the higher windage prior. The core-weighted marginal likelihood (rough, from the 84 release points) is +2.2 ln units for the wide prior and +5.2 for the higher prior, against production. The higher prior is preferred over the wide one by 3.0 ln units.
- Timing: the mean probability of a find date as early as observed, over eight exterior finds, is 0.32 (production), 0.36 (wide) and 0.48 (higher). A calibrated model gives about 0.5.
- Ocean-error length scale (wide class, 42 southern points): 50 km changes nothing within the noise; 200 km raises the early Mossel Bay arrival fraction from 9.7 % to 13.9 % (+4.2 ± 1.7 percentage points).
- Particle noise (master seed 23): -0.26 ± 0.31 percentage points. Negligible.
- Run 3 (extra ocean samples, three classes) is still running: 2 of 6 legs done at 16:19 UTC; expected end about 17:45 UTC. Free disk space then is about 3 GB; the guard stops the chain at 3 GB.
- Reading: the drift latitude and the tension depend mainly on one provisional parameter, the windage of the exterior class. Drift data alone do not fix the latitude unless the windage is constrained.

## 2. Drift alone and tension (`windage-classes-smoothed-summary.csv`)

Production / wide / higher windage prior. Same method as before (16 seeds × 16,384 draws, Gaussian-process smoothing, bootstrap 400).

| Case | Median ° S | North of 33° S % | p |
|---|---|---|---|
| Two ocean models | 30.0 / 33.2 / 34.6 | 74 / 48 / 30 | 0.109 / 0.320 / 0.566 |
| GlobCurrent only | 30.0 / 33.3 / 34.6 | 73 / 47 / 29 | 0.112 / 0.328 / 0.549 |
| GLORYS12 only | 29.4 / 31.1 / 34.1 | 89 / 69 / 39 | 0.061 / 0.122 / 0.505 |
| No finds on Australian coasts (0.25) | 29.5 / 32.2 / 33.4 | 80 / 59 / 45 | 0.078 / 0.167 / 0.272 |
| Without Mossel Bay | 32.9 / 34.2 / 35.3 | 51 / 37 / 24 | 0.407 / 0.601 / 0.699 |
| No finds on Australian coasts (0.25), without Mossel Bay | 31.4 / 33.1 / 33.7 | 63 / 50 / 41 | 0.154 / 0.302 / 0.362 |
| Mossel Bay at the ATSB find date (21-23 Mar 2016) | 30.8 / 33.6 / 34.8 | 66 / 44 / 28 | 0.151 / 0.400 / 0.594 |
| Mossel Bay arrival within 10 days of 23 Dec 2015 | 30.8 / 33.8 / 34.9 | 67 / 41 / 26 | 0.151 / 0.451 / 0.624 |
| Identity weights all 1 | 30.0 / 33.2 / 34.6 | 74 / 48 / 30 | 0.110 / 0.310 / 0.549 |
| Identity weights 1 / 0.9 / 0.7 | 30.1 / 33.2 / 34.7 | 72 / 48 / 30 | 0.118 / 0.341 / 0.622 |

Combined with the core (`windage-classes-combined-with-core.csv`), two ocean models: production 35.7° S, 34.79° S, 18.0 %; wide 35.9° S, 35.58° S, 7.7 %; higher 36.1° S, 35.98° S, 3.8 %.

## 3. Which windage do the data prefer? (`windage-classes-core-weighted-likelihood.csv`)

ln of the core-weighted mean likelihood at the 84 release points, with the 16-seed level marginalisation and the two ocean models at equal weight (rough: no smoothing, one set of ocean samples):

| Windage prior | ln Z | against production |
|---|---|---|
| production: normal 1.2 % ± 0.3 %, truncated 0.5 to 2 % | -182.74 | 0 |
| wide: log-normal median 1.2 %, σ(log) 0.5, truncated 0.3 to 5 % | -180.58 | +2.16 |
| higher: log-normal median 2.4 %, σ(log) 0.35, truncated 0.8 to 6 % | -177.54 | +5.20 |

A ln difference of 5 is a factor of about 180. The estimate has noise from the finite ocean samples (not quantified), and it is for the whole exterior class, not for one find. The CSIRO replica trial of the cowling (about 1.2 %, one attitude) speaks against a high value for that item alone; the other early finds (Paindane, Vilanculos) point the same way as Mossel Bay.

## 4. Timing (`windage-classes-timing-pit.csv`)

Core-weighted probability that the model find date is as early as observed (ramp prior, delay 60 days). Mpame is excluded (window-end artefact).

| Item | Production | Wide | Higher |
|---|---|---|---|
| mossel-bay-engine-cowling-roy | 0.020 | 0.039 | 0.078 |
| paindane-right-flap-fairing | 0.028 | 0.054 | 0.128 |
| vilanculos-horizontal-stabilizer-panel | 0.091 | 0.136 | 0.255 |
| mauritius-left-outboard-flap | 0.411 | 0.435 | 0.637 |
| chidenguele-right-fan-cowling | 0.169 | 0.225 | 0.337 |
| pemba-right-outboard-flap | 0.439 | 0.562 | 0.817 |
| linga-linga-vertical-stabilizer | 0.618 | 0.661 | 0.752 |
| nautilus-bay-right-aileron | 0.763 | 0.792 | 0.837 |

At the higher prior the early finds move to the middle of the distribution and the later finds (Pemba 0.82, Nautilus Bay 0.84) move to the upper tail. The PIT values are not independent, and the ramp is provisional.

## 5. Ocean-error length scale and particle noise (`overnight-variants-vs-base.csv`)

Wide class, southern release points, ocean samples 217 to 232, paired with the 100 km run; core-weighted; two models at equal weight; bootstrap over ocean samples (60 draws).

| Variant | Release points | Early fraction by day 655: base → variant | Difference ± bootstrap sd | PIT of Mossel Bay: base → variant |
|---|---|---|---|---|
| length scale 50 km | 42 | 9.7 % → 10.3 % | +0.7 ± 0.9 points | 0.027 → 0.028 |
| length scale 200 km | 42 | 9.7 % → 13.9 % | +4.2 ± 1.7 points | 0.027 → 0.043 |
| master seed 23 | 28 | 10.1 % → 9.9 % | -0.3 ± 0.3 points | 0.029 → 0.028 |

- A shorter length scale does not matter. A longer one (200 km) raises early arrivals by about 40 % in relative terms, which is real but smaller than the windage effect (a factor 2 to 3 between the production and wide priors).
- The length scale was assumed (100 km); the replay of drifters measured the error amplitude and time scale only. Measuring it from the drifter data is the next step for this question.
- Particle noise is small against the other effects, so the early-tail results are not a sampling artefact of the importance splitting.
- The 200 km and 50 km runs were not carried through smoothing and tension; only the Mossel Bay arrival metrics are compared.

## 6. Checks

- All rescorings and arrival tables reproduce the module's own coefficients: higher windage 24,187 comparisons, length scale 8,025 and 7,972, particle noise 5,370; maximum relative difference 2.2e-8; zero/non-zero mismatches 0.
- Hybrid coefficients: classes 0 and 2 from the production rescoring, class 1 from the new run (252 nodes, 48,384 class-1 entries replaced); the builder's self-test reproduces its input exactly.
- Smoothing: same scripts as the headline with only the variant name and output folder changed.

## 7. Key assumptions and modelling choices

| Item | Value | Status |
|---|---|---|
| Core | final 7 Nov end-of-flight model, D0 | Pete's ruling |
| Windage classes | production, wide, higher (as above) | provisional; wide design approved by Pete; higher requested by Pete as a minimum sensitivity; numbers mine |
| Evidence estimate | core-weighted mean likelihood at 84 release points | my choice; rough |
| Flaperon and interior classes | from the production run | my choice |
| Length scales 50 and 200 km; master seed 23 | as above | my choices |
| Detection prior (0.1/0.5/1/1), identity weights, delay 60 d, kernel 50 km | as in README | provisional / my choices |

## 8. Next steps (my recommendation)

1. Infer the windage distribution from the data instead of choosing it: reweight the stored particles over a grid of medians and widths inside the sampled range (0.3 to 5 % and 0.8 to 6 % cover most of it) and report the posterior. The stored arrivals contain the windage of every particle.
2. Report the tension for all three priors in the paper, with the physical argument for each (README sections 11 and 12).
3. Rescore run 3 when it ends, then repeat the smoothing with 48 ocean samples in the south.
4. Measure the ocean-error length scale from the drifter data.
