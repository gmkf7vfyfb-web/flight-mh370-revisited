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

## Cause: few ancestral lineages, not few rows
- Each seed has 3.2M impact rows. In the 00:11 hand-off, waypoints has 2,445–5,312 distinct filter particles north of 33 S per seed (905–2,941 north of 30 S), with within-seed Kish 942–2,002 (336–1,069).
- By the ancestor index recorded in the hand-off (`origin`), the northern mass of each seed rests on 332–401 distinct lineages but only **22–78 effective lineages north of 33 S** (10–83 north of 30 S). The largest single lineage carries 4–31% of the northern mass. Free flight is similar (27–70).
- So each seed is a few independent draws of "how much goes north". This is why the seed scatter is so large.

## What it means for run J
1. **More seeds help only linearly.** B″ gives waypoints 12 seeds (1.5×): implied effective sample north of 33 S about 100. To reach 1,000 would need about 15× the seeds (about 120 waypoint seeds), which is not practical.
2. **Correction to my run-J note §4.4.** Giving free flight its seeds first does not fix the combined product: free flight carries 0.2–0.3% of it, and its northern lineage count is no better.
3. **Aiming the 00:11 hand-off cannot fix it either.** It only re-allocates rows among lineages that already exist (the same ceiling as request 20). The aim must act inside the filter early enough to keep more lineages alive, for example an evidence-aimed look-ahead at 22:41 (horizon 00:11, where the look-ahead did work), with g from the downstream evidence at each particle's predicted end region, the exact correction and a defensive share. No latitude band is named.
4. **Run J can still go tonight.** Its main-mode results (the publication convergence) are not affected. The northern result must be labelled with this effective sample size. An aimed supplement (run K) samples the same target and can be pooled with run J afterwards by standard combination of independent importance-sampling estimates, so run J is not wasted.
