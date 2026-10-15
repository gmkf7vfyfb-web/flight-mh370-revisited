# Is run I's sampling adequate north of the searched areas? Measured 15 October 2026

**Answer: no.** After the drift and searched-area evidence, a large share of the composed posterior lies north of the searched areas, but it rests on a few tens of effective samples.

## Method
- Source: composer pass 2b on run I (`mh370-exchange/composer/run-i-ruling-oct15/work/`). The composer stores, per family and seed, the normalised latitude curve of each product and its downstream log-evidence. It does not store per-sample weights.
- Families are combined per seed with weight exp(core ln Z + downstream ln M); core ln Z is read from each seed's `diagnostics.json`. Waypoints carries 0.995–0.997 of every product.
- **Monte Carlo error** = the scatter of the northern mass across the 8 independent seeds. **Implied effective sample size** = 8 × p(1 − p)/var_seed × p, the number of independent samples that would give the same scatter. This counts all sources of noise, including shared ancestry from resampling, which a single-time Kish value does not see. With 8 seeds the implied value is itself uncertain by about ±50%.
- "North of the searched areas" = north of 33 S, also shown for 30 S. Ocean Infinity areas are excluded in this composer pass.

## Result (combined product; D0 = 00:19 values held out; T = cause model; ocean mixture)
| Evidence | North of | Mass | Seed range | Relative MC error of the 8-seed mean | Implied effective sample |
|---|---|---|---|---|---|
| flight data only (P1) | 33 S | 0.030 | 0.011–0.062 | 20% | 25 |
| flight data only (P1) | 30 S | 0.015 | 0.005–0.037 | 24% | 17 |
| + drift + searches (DrS), D0 | 33 S | **0.177** | 0.096–0.268 | 11% | **66** |
| + drift + searches (DrS), D0 | 30 S | **0.085** | 0.038–0.150 | 14% | **45** |
| + drift + searches, D2 (R600 BTO+BFO) | 33 S | 0.178 | 0.078–0.323 | 16% | 32 |
| + drift + searches, D4 (both BFOs, Holland transient bias added) | 33 S | 0.151 | 0.077–0.242 | 17% | 30 |
| + drift + searches, D4 | 30 S | 0.098 | 0.038–0.202 | 24% | 16 |
| + Pléiades + searches (HS), D0 | 33 S | 0.004 | 0.003–0.009 | 16% | 38 |

Full table, all families: `composer_north_ess_run_i.csv`.

## Cause (corrected the same evening)
**My first diagnosis, "few ancestral lineages", was wrong.** The `origin` index is the particle's 18:01 index. The whole population collapses to about 21 effective 18:01 lineages per seed (waypoints; 13 south of 36 S, 37 north of 33 S), so this is ordinary SMC genealogy and is not specific to the north.

**The measured cause is noise in the mode probabilities.** Waypoints, 00:11 hand-off, 8 seeds:

| Mode | P(mode), median [range] | P(north of 33 S given mode) | Particles per seed | ln Z seed sd |
|---|---|---|---|---|
| true track | 0.600 [0.464–0.749] | 0.006 | 2.5M | 0.373 |
| lateral navigation | 0.190 [0.126–0.333] | 0.010 | 2.5M | 0.294 |
| true heading | 0.096 [0.068–0.143] | 0.077 | 1.0M | 0.157 |
| magnetic track | 0.049 [0.028–0.123] | 0.251 | 0.5M | 0.245 |
| magnetic heading | 0.024 [0.016–0.031] | 0.538 | 0.5M | 0.202 |

- The north is carried by the magnetic modes, about 65% of the northern mass in waypoints. These modes get the fewest particles (0.5M each, 7%).
- **Variance split.** Holding the mode probabilities at their 8-seed means cuts the seed sd of the northern mass from 0.0107 to 0.0049 (waypoints) and from 0.0159 to 0.0033 (free). Holding the within-mode shares fixed leaves it almost unchanged (0.0104; 0.0138). So about 80% of the variance is mode-probability noise.
- **Where that noise enters.** Almost all the seed-to-seed variance of each mode's ln Z comes from the 00:11 increment: true track 0.382 of 0.373 total (waypoints) and 0.665 of 0.804 (free); lateral navigation 0.288 of 0.294 and 0.494 of 0.504. Effective sample after the 00:11 update: true track about 100k of 2.5M; magnetic modes 2.5k–6.9k of 0.5M.
- **Not the usual importance-sampling error.** With N = 2.5M and an ESS of 100k, the textbook ln Z sd at that epoch would be about 0.003. The observed 0.38 means the 00:11 increment depends on where each seed's population stands when it reaches 00:11. That is earlier path-space noise expressed at 00:11, consistent with the core finding of 12 Oct that free-flight convergence is limited by which 18:01–22:41 lineages survive 00:11.
- **Earlier tests do not settle it.** The tempering, adaptive-tempering, look-ahead, resample-move and arc-bridge tests were judged on the latitude split-half of the main mode, not on mode-probability noise.

## What it means for run J
1. **More seeds help only linearly.** B″ gives waypoints 12 seeds (1.5×): implied effective sample north of 33 S about 100. To reach 1,000 would need about 15× the seeds (about 120 waypoint seeds), which is not practical.
2. **Correction to my run-J note §4.4.** Giving free flight its seeds first does not fix the combined product: free flight carries 0.2–0.3% of it, and its northern lineage count is no better.
3. **Aiming the 00:11 hand-off cannot fix it.** The noise is in the filter's per-mode evidence, before any hand-off.
4. **Candidate fix for run J (exact, no latitude choice): re-allocate particles across modes.** Each mode is its own filter and the mixture is weighted by evidence, so the per-mode particle count changes only noise, not the target. Give the magnetic modes more (they carry the north), and test whether the 00:11 ln Z noise falls with more particles in a mode. A one-hour test on the repro stratum decides it (`threads/work-orders/mode-allocation-test-2026-10-15.md`).
5. **Seed budget.** The composed product is 99.7% waypoints, so the definitive northern answer is limited by waypoint seeds. B″ gives waypoints the fewest (12).
