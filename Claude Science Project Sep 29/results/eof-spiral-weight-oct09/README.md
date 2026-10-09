# Dive-class weight sensitivity: 0.25 / 0.50 / 0.75 against glide-only

9 October 2026, End of Flight Module. **SMOKE SCALE, PROVISIONAL. Not evidence.**

- **Basis.** Pete ruled the dive class at a 50/50 weight, with 25/75 and 75/25 as sensitivity. The class
  itself is the PROVISIONAL-OVERNIGHT option (b): divergent spiral, bank cap 90°, endorsed by architecture
  (~06:45 UTC).
- **Runs.**
  - Seed 1, on the `reference-snapshots` 00:11 hand-off (295.66° prior), at 2 threads outside the lock.
  - Weights 0.25, 0.50 and 0.75 at N = 8: `runs/eof-spiralw0.25-n8-s1`, `eof-dive-n8-s1` and
    `eof-spiralw0.75-n8-s1`, using `smoke/spiral-weight-{0.25,0.75}.toml`.
  - Weight 0 (dive OFF) and weight 0.50 at N = 16 (`eof-s6-n16-s1`, `eof-dive-n16-s1`). ESS scales with N,
    so compare ESS only between rows of equal N.
- **Bayes factor.** The divergent : glide Bayes factor is the posterior odds of a divergent descent divided by
  the prior odds w / (1 − w). If the module is behaving correctly, it does not depend on w.
- **Files.**
  - `spiral-weight-sensitivity.json` holds every option and both log-on causes.
  - The generator is `engine/hypotheses/end-of-flight/smoke/spiral_sensitivity.py`. Its weights come from
    the same function as the Pléiades displacement histograms in `results/eof-displacement-oct09/`.

| option × log-on cause | divergent weight (run) | N | ESS | posterior divergent share | Bayes factor divergent : glide | median impact lat, lon (°) | displacement from 00:19:37, 50% / 90% (NM) |
|---|---|---|---|---|---|---|---|
| `r600_inflated__fuel-exhaustion` | 0.00 (w0.00-n16) | 16 | 59,377 | 0.000 | — | -37.83, 89.39 | 50 / 100 |
| `r600_inflated__fuel-exhaustion` | 0.25 (w0.25) | 8 | 29,613 | 0.247 | 1.0 | -37.82, 89.40 | 48 / 100 |
| `r600_inflated__fuel-exhaustion` | 0.50 (w0.50) | 8 | 29,213 | 0.498 | 1.0 | -37.82, 89.41 | 46 / 100 |
| `r600_inflated__fuel-exhaustion` | 0.75 (w0.75) | 8 | 28,782 | 0.744 | 1.0 | -37.81, 89.43 | 45 / 100 |
| `r600_inflated__fuel-exhaustion` | 0.50 (w0.50-n16) | 16 | 58,352 | 0.495 | 1.0 | -37.82, 89.41 | 47 / 100 |
| `r1200_inflated__other` | 0.00 (w0.00-n16) | 16 | 3,055 | 0.000 | — | -37.31, 89.47 | 18 / 97 |
| `r1200_inflated__other` | 0.25 (w0.25) | 8 | 2,947 | 0.648 | 5.5 | -37.12, 89.43 | 4 / 77 |
| `r1200_inflated__other` | 0.50 (w0.50) | 8 | 4,532 | 0.851 | 5.7 | -37.04, 89.44 | 2 / 56 |
| `r1200_inflated__other` | 0.75 (w0.75) | 8 | 6,039 | 0.948 | 6.1 | -37.03, 89.42 | 2 / 44 |
| `r1200_inflated__other` | 0.50 (w0.50-n16) | 16 | 9,061 | 0.848 | 5.6 | -37.05, 89.44 | 2 / 57 |
| `r1200_inflated__fuel-exhaustion` | 0.00 (w0.00-n16) | 16 | 994 | 0.000 | — | -37.53, 89.59 | 64 / 100 |
| `r1200_inflated__fuel-exhaustion` | 0.25 (w0.25) | 8 | 895 | 0.684 | 6.5 | -37.19, 89.57 | 3 / 87 |
| `r1200_inflated__fuel-exhaustion` | 0.50 (w0.50) | 8 | 1,375 | 0.865 | 6.4 | -37.13, 89.56 | 2 / 77 |
| `r1200_inflated__fuel-exhaustion` | 0.75 (w0.75) | 8 | 1,828 | 0.954 | 6.8 | -37.09, 89.55 | 2 / 65 |
| `r1200_inflated__fuel-exhaustion` | 0.50 (w0.50-n16) | 16 | 2,723 | 0.863 | 6.3 | -37.11, 89.57 | 2 / 77 |
| `r1200_no-offset__fuel-exhaustion` | 0.00 (w0.00-n16) | 16 | 147 | 0.000 | — | -37.35, 89.53 | 51 / 91 |
| `r1200_no-offset__fuel-exhaustion` | 0.25 (w0.25) | 8 | 159 | 0.731 | 8.1 | -37.14, 89.64 | 3 / 80 |
| `r1200_no-offset__fuel-exhaustion` | 0.50 (w0.50) | 8 | 264 | 0.870 | 6.7 | -37.18, 89.43 | 2 / 73 |
| `r1200_no-offset__fuel-exhaustion` | 0.75 (w0.75) | 8 | 365 | 0.957 | 7.3 | -37.09, 89.52 | 2 / 46 |
| `r1200_no-offset__fuel-exhaustion` | 0.50 (w0.50-n16) | 16 | 537 | 0.868 | 6.6 | -37.15, 89.50 | 2 / 70 |
| `r1200_startup-offset__fuel-exhaustion` | 0.00 (w0.00-n16) | 16 | 204 | 0.000 | — | -37.23, 89.85 | 21 / 88 |
| `r1200_startup-offset__fuel-exhaustion` | 0.25 (w0.25) | 8 | 391 | 0.846 | 16.4 | -37.03, 89.61 | 2 / 46 |
| `r1200_startup-offset__fuel-exhaustion` | 0.50 (w0.50) | 8 | 711 | 0.936 | 14.7 | -37.02, 89.59 | 2 / 13 |
| `r1200_startup-offset__fuel-exhaustion` | 0.75 (w0.75) | 8 | 1,012 | 0.986 | 23.1 | -37.04, 89.54 | 2 / 4 |
| `r1200_startup-offset__fuel-exhaustion` | 0.50 (w0.50-n16) | 16 | 1,374 | 0.940 | 15.7 | -37.02, 89.59 | 2 / 11 |
| `both_inflated__fuel-exhaustion` | 0.00 (w0.00-n16) | 16 | 191 | 0.000 | — | -37.96, 89.32 | 64 / 100 |
| `both_inflated__fuel-exhaustion` | 0.25 (w0.25) | 8 | 129 | 0.323 | 1.4 | -37.94, 89.34 | 72 / 100 |
| `both_inflated__fuel-exhaustion` | 0.50 (w0.50) | 8 | 139 | 0.596 | 1.5 | -37.61, 89.38 | 37 / 97 |
| `both_inflated__fuel-exhaustion` | 0.75 (w0.75) | 8 | 136 | 0.799 | 1.3 | -37.52, 89.37 | 29 / 96 |
| `both_inflated__fuel-exhaustion` | 0.50 (w0.50-n16) | 16 | 260 | 0.578 | 1.4 | -37.56, 89.42 | 40 / 99 |

## Reading

- **R600 inflated is indifferent to the dive class.** Only this R600 sub-option is in the table; for startup-offset see `results/eof-displacement-oct09/`. The posterior divergent share equals the prior weight, so the
  Bayes factor is about 1, and the median impact moves by 0.02° or less.
- **R1200 prefers the divergent spiral by a stable Bayes factor.** The factor is 5.5–6.1 with the other log-on
  cause, 6.3–6.8 for inflated with fuel-exhaustion, and 6.6–8.1 for no-offset. It is about the same at all three
  weights, which is the consistency check.
  - Startup-offset gives 15–23, with lower ESS.
- **The R1200 location depends on whether the class is present, not on its weight.**
  - Under inflated with fuel-exhaustion, adding the class moves the median impact from 37.53° S to 37.13° S,
    about 24 NM north.
  - Moving the weight from 0.25 to 0.75 moves it only 37.19° S to 37.09° S, about 6 NM.
  - The median displacement from 00:19:37 is 2–4 NM at every non-zero weight. The 90% radius depends on the
    weight: 87, 77 and 65 NM at 0.25, 0.50 and 0.75.
- **Caveat on tightness.** The near-zero displacement inherits the declared chord misfit: the dive ends
  1.0–2.7 NM after the 15,000 ft/min crossing, against 4.7–7.9 NM in the Boeing cases. It is probably a few NM
  too tight.
- **`both/inflated` stays concentration-limited** (ESS 129–260 at one seed). Its median moves about 0.4°
  north as the weight rises, but it is not interpretable at this scale.
- **The weight still matters for anything scored on the full impact distribution.** It changes the 90% radius by
  about 20 NM. The paper should carry Pete's 50/50 as the reference, with this table as the sensitivity.
