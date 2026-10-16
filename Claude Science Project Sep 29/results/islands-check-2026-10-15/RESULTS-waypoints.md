# Islands check, waypoints: result (16 Oct 2026 00:40Z)

Job 3474b49b (bin-4ec7c95, engine source = 03d51db). Run I's waypoints chain without the hand-off
look-ahead and server-sampler files. Northern effective lineages L_eff = (sum W)^2 / sum W^2 over distinct
(mode, 18:25 origin) groups, W = weight x mode probability / mode sum x r(lat at 00:19:37), r = DrS (D0) / P1
evidence ratio (evidence-ratio-waypoints-D0-DrS-over-P1.csv). Seeds pooled with equal weight.

| Configuration (7M in total per row) | L_eff per seed, north of 33 S | Pooled, north of 33 S | Pooled, north of 30 S | ln Z | Split-half |
|---|---|---|---|---|---|
| 1 seed x 7M (run I, 8 seeds) | 11.0–76.5 (mean 38.5) | — | — | −128.998 (8 seeds) | 0.869 |
| 4 seeds x 1.75M | 6.9, 18.3, 28.5, 25.1 | 46.3 | 66.6 | −129.188 | 0.895 |
| 8 seeds x 0.875M | 7.8–17.7 | 84.9 | 62.4 | −129.430 | 0.734 |

Northern mass north of 33 S, equal-seed pooling, before / after the r tilt: 7M 0.0152 / 0.102;
4 x 1.75M 0.016 / 0.100; 8 x 0.875M 0.017 / 0.107. **No particle-count bias in the northern mass.**
Seed-to-seed sd of the tilted mass at 7M: 0.024 (relative SE 8.3% with 8 seeds).

**Decision rule (set before the test):** islands are the fix if 4 islands give about 4x one 7M seed.
Result: 1.2x (4 islands) and 2.2x (8 islands), and the main posterior gets worse (ln Z lower, split-half
0.73 at 8 islands). **Islands are not the fix.**

Projection, run I's 8 seeds resampled (2,000 bootstrap draws), 7M per seed:

| Waypoint seeds | Pooled L_eff north of 33 S (median, IQR) | Relative SE of tilted northern mass | Deskstar time (23.4 min/seed) |
|---|---|---|---|
| 8 | 152 (132–183) | 8.3% | 3.1 h |
| 12 (run J plan) | 225 (201–260) | 6.8% | 4.7 h |
| 16 | 302 (274–344) | 5.9% | 6.2 h |
| 24 | 452 (417–497) | 4.8% | 9.4 h |
| 32 | 602 (559–652) | 4.2% | 12.5 h |

L_eff grows linearly with seeds (about 19 per 7M seed). The other remedy is the evidence-tilted
proposal (exact correction), which takes about a day to build and validate.

STE100 note: splitting the particles into more, smaller runs did not give more northern endings. More
full-size runs give more, in proportion. The northern share of the answer is stable; only its detail is thin.
