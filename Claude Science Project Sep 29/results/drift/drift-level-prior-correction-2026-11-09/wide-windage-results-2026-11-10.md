# Wide-windage run: results (10 Nov 2026, morning)

Status: working record. Windage prior for the exterior class widened from N(1.2 %, 0.3 %) truncated 0.5 to 2 % to log-normal (median 1.2 %, σ(log) 0.5, truncated 0.3 to 5 %). Provisional; my choice, approved as a design by Pete. Everything else as the headline (README section 6 and 9).

## 1. Summary

- The run finished at 05:00 UTC on 10 Nov: 18 legs, all exit code 0, 14 nodes each, 5.26 h, peak memory 17.5 GB.
- Rescoring (module rescorer) reproduces the module's own coefficients to 2.2e-8 (4,022 comparisons; zero/non-zero mismatches 0). The arrival-time tables reproduce them to 2.2e-8 over 24,104 comparisons.
- Headline, two ocean models, drift alone: median 33.2° S (was 30.0° S), 48 % north of 33° S (was 74 %).
- Tension with the ruled core: ln S +0.03 (was -0.70), d 0.83, p 0.320 (was 0.109), 1.0σ (was 1.6σ). The bootstrap range of p is 0.24 to 0.41.
- Combined with the core (one dimension): median 35.9° S, mean 35.58° S, 7.7 % north of 33° S. The core alone gives 36.4° S, 35.95° S and 8.1 %. The earlier headline gave 35.7° S, 34.79° S and 18.0 %.
- The early Mossel Bay arrivals now come from windage near 2.5 % (GLORYS12 leg): mass-weighted mean 2.63 %, median 2.50 %, 90th percentile 4.15 %, 70 % of the mass above 2 %. In the old run the range stopped at 2 %.
- Reading: with a windage prior that includes literature-supported values above 2 %, the drift data and the core agree. The result depends on this prior. It is not a finding that the true windage is wide.

## 2. Drift alone and tension (`wide-vs-production-smoothed-summary.csv`)

| Case | Median ° S (production → wide) | North of 33° S % | ln S | p |
|---|---|---|---|---|
| Two ocean models | 30.0 → 33.2 | 74 → 48 | -0.70 → +0.03 | 0.109 → 0.320 |
| GlobCurrent only | 30.0 → 33.3 | 73 → 47 | -0.63 → +0.04 | 0.112 → 0.328 |
| GLORYS12 only | 29.4 → 31.1 | 89 → 69 | -1.86 → -0.60 | 0.061 → 0.122 |
| No finds on Australian coasts (0.25) | 29.5 → 32.2 | 80 → 59 | -1.17 → -0.37 | 0.078 → 0.167 |
| Without Mossel Bay | 32.9 → 34.2 | 51 → 37 | +0.16 → +0.33 | 0.407 → 0.601 |
| No finds on Australian coasts (0.25), without Mossel Bay | 31.4 → 33.1 | 63 → 50 | -0.32 → -0.02 | 0.154 → 0.302 |
| Mossel Bay at the ATSB find date (21-23 Mar 2016) | 30.8 → 33.6 | 66 → 44 | -0.34 → +0.15 | 0.151 → 0.400 |
| Mossel Bay arrival within 10 days of 23 Dec 2015 | 30.8 → 33.8 | 67 → 41 | -0.39 → +0.21 | 0.151 → 0.451 |
| Identity weights all 1 | 30.0 → 33.2 | 74 → 48 | -0.71 → +0.01 | 0.110 → 0.310 |
| Identity weights 1 / 0.9 / 0.7 | 30.1 → 33.2 | 72 → 48 | -0.60 → +0.08 | 0.118 → 0.341 |

Same method as before: 16 seeds × 16,384 level draws, Gaussian-process smoothing, bootstrap over ocean samples (400), 0.1° bins. The windage class is the only change. GLORYS12 alone stays the most tense (p 0.122); GlobCurrent alone is not (p 0.328).

## 3. Combined with the ruled core (`wide-vs-production-combined-with-core.csv`)

One-dimensional product of the core posterior and the smoothed drift likelihood on 0.1° bins. The production row reproduces the earlier numbers (35.7° S, 34.79° S, 18.0 %).

## 4. Timing (`wide-vs-production-timing-pit.csv`, `wide-vs-production-mossel-bay-early-fraction-by-band.csv`)

- Core-weighted probability that the model find date is as early as observed (provisional ramp): Mossel Bay 0.020 → 0.039, Paindane 0.028 → 0.054, Vilanculos 0.091 → 0.136. The two earliest finds remain in the lower tail.
- Fraction of the kernel arrivals at Mossel Bay by day 655 from 36–40.25° S (core weight 0.544): 2.6 % → 7.5 %; from 33–36° S (0.372): 6.4 % → 14.1 %.
- Windage of the early arrivals: `wide-early-arrival-windage-glorys12.csv`. The GlobCurrent kernel-arrival file (120 MB) stayed on deskstar; its windage table is not done.

## 5. Caveats

- Widening a prior generally lowers a tension unless the data favour the narrow range. The result shows that the tension depends on the windage prior. It does not show which prior is right.
- The effective dimension d is below 1 (0.83). The χ² reference is then anti-conservative (README section 11, calibration smoke test), so the nominal p is, if anything, too small. The change from 0.109 to 0.320 is therefore not an artefact of that.
- The run uses one symmetric prior. The higher-windage scenario (median 2.4 %), the ocean-error length scale (50 and 200 km), the particle-noise check and the extra ocean samples are running overnight (job 6496b915).
- Not yet done with the wide class: figures A to G, the evidence ledger, and the second independent review of the new rescored inputs.

## 6. Key assumptions and modelling choices

| Item | Value | Status |
|---|---|---|
| Core | final 7 Nov end-of-flight model with fuel, D0 | Pete's ruling |
| Wide exterior class | log-normal, median 1.2 %, σ(log) 0.5, truncated 0.3 to 5 % | design approved by Pete; numbers mine; provisional |
| Flaperon and interior classes | from the production run (same nodes and ocean samples) | my choice |
| Detection prior in time (0.1/0.5/1/1), identity weights, delay 60 d, kernel 50 km, Australia off | as in README | provisional / my choices; not Pete's rulings |
| Smoothing | Matérn 3/2 Gaussian process, 16 seeds × 16,384 draws, bootstrap 400 | as before |
