# Prior heading A/B: 289.7 (corrected) vs 295.66 (earlier), full scale, seeds 1-4

`runs/reference-289` (10 Oct 2026, binary `5aee2bb`, 13:48Z, 8.7 h) against seeds 1-4 of
`runs/reference-snapshots`. Identical configuration except the prior track (Davey Fig. 4.2,
digitised at 18:02: 289.7 deg). 7M particles per seed. Hand-offs at 22:41 and 00:11.

## Result (mean +/- seed s.d., 4 seeds each)

| quantity | 295.66 | 289.7 | shift |
|---|---|---|---|
| log Z | -98.369 +/- 0.108 | -99.429 +/- 0.085 | -1.06 |
| 00:19 latitude 5% | -38.115 +/- 0.094 | -37.973 +/- 0.112 | +0.14 |
| 00:19 latitude 25% | -37.619 +/- 0.175 | -37.337 +/- 0.068 | +0.28 |
| **00:19 latitude median** | **-37.273 +/- 0.148** | **-36.421 +/- 0.081** | **+0.85** |
| 00:19 latitude 75% | -36.716 +/- 0.070 | -35.680 +/- 0.090 | +1.04 |
| 00:19 latitude 95% | -34.987 +/- 0.038 | -29.795 +/- 0.747 | +5.2 |
| 00:11 latitude median (posterior routes) | -36.378 +/- 0.242 | -35.477 +/- 0.109 | +0.90 |
| 18:22 cross-track from N571 (NM, + north) | 18.55 +/- 0.19 | 3.40 +/- 1.16 | -15.2 |

- Pooled over seeds 1-4, at 00:19:
  - 295.66: 5/25/50/75/95% = -38.13 / -37.66 / -37.27 / -36.78 / -35.24.
  - 289.7: -37.99 / -37.34 / -36.43 / -35.65 / -29.14.
- P(latitude > -34 S): 3.0% to 7.6%.
- Per-epoch evidence (mode mixture), 289.7 minus 295.66:
  - m1825 +0.44 (better), m1828a+b -0.20, m1839 -0.18, m1941 +0.18.
  - The rest of the -1.06 comes from the later arcs.
- **The heading fix is not a minor sensitivity.** The median moves 0.85 deg north, 6-10 times the seed
  s.d. The PDF becomes bimodal (modes near 37.5 S and 36.1 S), and a northern tail opens.
- The earlier heading fitted the SATCOM data about 1 nat better. Its error kept paths 15-22 NM north of
  N571 at 18:22, which suits the 18:25-18:28 arcs at cruise speed. The radar evidence is in the
  family strata (`runs/families-*`) of the same launch.

## Hand-offs (ruling E2)

- 100,000 rows per seed per epoch (99,999 in two cases).
- P(mode) snapshot = evidence-to-date within 1.4e-14 for all 8 seed-epochs
  (`report/check_snapshots.py`).
