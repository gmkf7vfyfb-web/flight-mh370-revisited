# A1 coverage fix for Holland H1/H2: aimed pitch-down, smoke (12 Oct 2026)

**SMOKE, PROVISIONAL, not evidence.** Core run D `next-d-free` seed 1, N = 8 x 4, the H1/H2 recipe (arm C) with and without
`full/a1-aimed-pitchdown.toml` (binary he7, a8a8a5cc; he7 = he6 + the option; the run without aim is the H1/H2 sweep's own seed 1,
he5, byte-identical physics). Ran under the heavy lock 01:05-01:15Z (12 threads). Constraint unpowered, survival factor PRIMARY.

**Diagnosis.** In the full sweep the A1 rows that reach the H1/H2 burst states pitch down 70-140 s before 00:19:29 and arrive
through the phugoid, outside the burst window, so they carried the x5 out-of-window correction (A1 effective impacts 136 / 59).
**Change.** The pitch-down start is drawn 0.5 uniform in [-150, -40] s, 0.3 in [-15, +6] s of 00:19:29.416, 0.2 from the prior
(exact ln(prior/proposal); prior unchanged; push-over targeting unchanged).

| Option (primary) | ln Z without / with aim | Effective impacts without / with | A1 effective impacts without / with | A1 share without / with |
|---|---|---|---|---|
| Holland H1 | -28.76 / -28.73 | 700 / 837 | 21 / 52 | 0.10 / 0.13 |
| Holland H2 | -22.60 / -22.60 | 339 / 472 | 11 / 83 | 0.10 / 0.11 |
| Held Out | -0.217 / -0.216 | 705 k / 718 k | 85.9 k / 93.7 k | 0.14 / 0.14 |
| R600 BTO Only | -5.865 / -5.865 | 952 k / 967 k | 114 k / 124 k | 0.12 / 0.12 |

ln Z unchanged within Monte Carlo noise: the proposal correction is exact. A1 effective impacts x2.5 (H1) and x7.5 (H2).
Projected for 4 strata x 4 seeds: A1 about 340 (H1) and 440 (H2), still below 1,000: more parents are needed (size in architecture.md).
