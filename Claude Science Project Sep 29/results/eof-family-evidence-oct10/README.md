# End of flight: the 00:19 evidence factor per core family, and the re-weighted family mixture (core (b) `next-run`, 10 Oct 2026)

Architecture ruling C (~19:10 UTC): P(family | all data, option) ∝ P_core(family) × Ẑ_00:19(family, option).

**Inputs and labels:**
- Inputs: `mh370-exchange/end-of-flight/next-run/<stratum>/seed-1..4` (the accepted stand-in sweep); code `smoke/family_evidence.py`.
- Labels: core (b), split-half NOT converged; two-tank bookkeeping only; descent idle floor ON; dive class (b) PROVISIONAL.
- P_core(family) is held as core published it: free 0.6948, Davey dynamics + radar 0.1527, descent-climb 0.1376, routes 0.0149.

**Definitions.**
- For each seed: ln Ẑ_k = ln Σ_rows w·L·c − ln Σ_rows w, with:
  - w the impact-row prior weight (hand-off weight, exact within-parent correction);
  - L the 00:19 likelihood of the option (with the fuel-exhaustion lag density for H1);
  - c the existence constraint.
- The factor is the mean of Ẑ_k over the 4 seeds.
- **The ± is the seed-to-seed standard error of that mean, in log units.** It includes core (b)'s non-convergence. It is not a parent-level
  bootstrap.
- Ẑ is an absolute density (the BTO and BFO normal constants are included). Only its **ratio between families** enters the re-weighting.
- Mixture quantiles come from 0.001° weighted histograms, with seeds equal-weighted inside each stratum. The fixed-weight values reproduce
  the stand-in's `mixture.json`: held out −37.03, and R600 BTO Only −37.93 (the stand-in's `r600-bto__other`).

| 00:19 option | ln Ẑ free | ln Ẑ Davey dynamics + radar | ln Ẑ descent-climb | ln Ẑ routes | P(family) re-weighted (free / Davey+radar / descent-climb / routes) | mixture median lat, fixed P (5-95 %) | mixture median lat, re-weighted (5-95 %) |
|---|---|---|---|---|---|---|---|
| 00:19 Held Out | -0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.695 / 0.153 / 0.138 / 0.015 | -37.03 (-39.92 to -29.70) | -37.03 (-39.92 to -29.70) |
| 00:19 Held Out +alive | -0.11 ± 0.01 | -0.11 ± 0.00 | -0.10 ± 0.00 | -0.11 ± 0.00 | 0.695 / 0.152 / 0.138 / 0.015 | -37.24 (-40.00 to -29.63) | -37.24 (-40.00 to -29.63) |
| 00:19 R600 BTO Only +alive | -5.80 ± 0.07 | -5.90 ± 0.02 | -5.73 ± 0.04 | -5.71 ± 0.01 | 0.697 / 0.139 / 0.148 / 0.016 | -37.93 (-40.22 to -29.46) | -37.94 (-40.22 to -29.50) |
| 00:19 R600 BTO + Raw BFO +alive | -12.56 ± 0.02 | -12.57 ± 0.05 | -12.08 ± 0.21 | -12.31 ± 0.15 | 0.639 / 0.140 / 0.204 / 0.018 | -37.42 (-39.37 to -28.88) | -37.46 (-39.43 to -29.01) |
| 00:19 Holland H1 +alive | -31.34 ± 0.06 | -31.76 ± 0.20 | -29.97 ± 0.80 | -31.40 ± 0.22 | 0.512 / 0.075 / 0.403 / 0.010 | -37.13 (-39.05 to -27.80) | -37.36 (-39.08 to -27.80) |
| 00:19 Holland H2 +alive | -23.91 ± 0.11 | -24.02 ± 0.20 | -23.60 ± 0.07 | -23.90 ± 0.14 | 0.671 / 0.133 / 0.181 / 0.015 | -37.14 (-39.04 to -27.90) | -37.14 (-39.07 to -27.90) |

**Reading.**
- **The re-weighting barely moves the estimable options.**
  - **00:19 R600 BTO Only:** families within ±0.1 nat of each other, so P(family) changes by ≤ 0.014 and the median by 0.01°.
  - **00:19 R600 BTO + Raw BFO:** descent-climb is favoured by 0.48 ± 0.21 nat against free. Its weight rises 0.138 → 0.204, and the median
    moves 0.04° south (−37.42 → −37.46).
  - **00:19 Held Out:** the factor is 1 by definition. With `+alive` it is P(airborne at 00:19:37 | family) = 0.90 in every family, so
    nothing moves.
- **00:19 Holland H1 and H2 are NOT re-weighted for use.** They are **not yet estimable (targeted sampler in progress)**: diagnostic smoke 2
  showed their evidence is heavy-tailed within parents. The 4-seed s.e. shown understates it. Their rows are given only so that the column
  exists.
- **Display, until core converges:** show the fixed-weight mixture beside the re-weighted one, both labelled (ruling C).

`family-evidence-next-run-b.json` holds every per-seed ln Z, effective parents and impacts per seed, and both mixtures with their quantiles.

- End of flight
