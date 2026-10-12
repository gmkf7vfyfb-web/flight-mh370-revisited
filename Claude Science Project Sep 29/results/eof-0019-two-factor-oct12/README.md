# 00:19 two-factor table: data treatment D0-D5 x log-on cause (12 Oct 2026)

**TEST on the run D-he summary only (no new descents; architecture 01:45Z, 02:05Z, 02:15Z).** PROVISIONAL; core run D not
converged. Input: `end-of-flight/next-run-d-he/` (4 strata x 4 seeds; strata mixed with core's P(family)); tool
`smoke/option_table_0019.py`; data `table-run-d-he.json`. Survival factor applied throughout.

- **C1** fuel exhaustion + APU start: Erlang(8, 14.875 s) lag density from the realised flame-out to 00:19:29.416; constraint
  unpowered (silent and unpowered coincide under this cause).
- **C2** other: uniform 1/W over the data-defined window W = 00:10:58-01:15:56 (3,898 s); constraint **silent primary**
  (no second APU log-on after a later flame-out), unpowered beside it.
- **Total per D:** per-row competing causes L_logon = f_lag + q/W, i.e. p f_lag + (1 - p)/W with p = 1/(1 + q); q = 1/3 (p = 0.75)
  primary, q = 1 (p = 0.5) sensitivity.
- **D5** (R600 BFO as recorded, R1200 BFO with a start-up offset U[17, 130] Hz, one shared bias) is computed in closed form from
  stored columns (R600 BTO residual, both BFO innovations) and the hand-off bias variance (column 9 of handoff.npy). The same
  method reproduces the stored D2, D3 and D4 columns to within 7e-4 nat (float32 storage). **No D option uses the R1200 BTO.**
- Named cells: **D4xC1 (Holland's Hypothesis 1)**, **D3xC2 (Holland's Hypothesis 2)**. Bayes factors only between the same data.

| D (00:19 data) | C1 fuel exhaustion: ln Z / ESS | C2 other, silent: ln Z / ESS | C2 other, unpowered: ln Z / ESS | Total q = 1/3 (silent): ln Z / ESS | Total q = 1 (silent): ln Z / ESS | Total q = 1/3, latitude q05 / q50 / q95 |
|---|---|---|---|---|---|---|
| D0: held out | -7.21 / 547,294 | -11.36 / 428,027 | -8.49 / 6,378,686 | -7.49 / 552,983 | -7.89 / 564,328 | -39.31 / -37.17 / -29.47 |
| D1: R600 BTO | -12.83 / 740,696 | -17.01 / 568,040 | -14.16 / 8,377,630 | -13.12 / 748,245 | -13.51 / 763,298 | -39.46 / -37.67 / -30.08 |
| D2: R600 BTO + R600 BFO | -18.86 / 50,534 | -23.94 / 13,326 | -21.08 / 190,237 | -19.14 / 50,734 | -19.54 / 51,131 | -39.04 / -37.28 / -28.77 |
| D3: R600 BTO + both BFOs (Holland H2 data) | -28.48 / 443 | -33.96 / 233 | -30.83 / 2,234 | -28.77 / 443 | -29.17 / 444 | -38.91 / -37.48 / -31.57 |
| D4: R600 BTO + both BFOs, shared start-up offset (Holland H1 data) | -28.72 / 4,690 | -33.81 / 59 | -31.00 / 4,594 | -29.00 / 4,706 | -29.41 / 4,730 | -38.94 / -37.54 / -29.67 |
| D5: R600 BTO + R600 BFO + R1200 BFO with offset | -29.14 / 2,402 | -34.55 / 887 | -31.40 / 7,543 | -29.42 / 2,409 | -29.83 / 2,423 | -38.85 / -37.50 / -29.70 |

| Same-data ln Bayes factor | D0 | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|---|
| C1:C2 within D (C2 silent) | +4.15 | +4.17 | +5.09 | +5.48 | +5.09 | +5.41 |
| C1:C2 within D (C2 unpowered) | +1.28 | +1.32 | +2.23 | +2.35 | +2.28 | +2.26 |

| Same-data ln Bayes factor | C1 | C2 silent | C2 unpowered | Total q = 1/3 (silent) |
|---|---|---|---|---|
| D3:D4 | +0.24 | -0.15 | +0.17 | +0.24 |
| D5:D3 | -0.66 | -0.59 | -0.57 | -0.66 |
| D5:D4 | -0.42 | -0.74 | -0.40 | -0.42 |

Readings (test only):
1. **The cause favours fuel exhaustion in every D**: ln BF C1:C2 = +4.2 to +5.5 with C2 silent, +1.3 to +2.3 with C2 unpowered.
   So the total at q = 1/3 sits within 0.3 nat of C1 (0.29 nat = ln p).
2. **D3:D4 (Holland's warm-up offset test):** +0.24 under C1, -0.15 under C2 silent, +0.17 under C2 unpowered: no preference.
   **D5 is weakly disfavoured** against both: D5:D3 -0.57 to -0.66, D5:D4 -0.40 to -0.74.
3. **Holland's Hypothesis 1 (D4xC1):** ln Z -28.72, ESS 4,690 (as in the H1/H2 sweep). **Holland's Hypothesis 2 (D3xC2):**
   ln Z -33.96, ESS 233 with silent (primary); -30.83, ESS 2,234 with unpowered. Silent removes 3.1 nat under "other".
4. Impact latitude medians (totals, q = 1/3) are -37.2 to -37.7 for every D.

## COVERAGE
- Cells that the run D-he proposal did not aim at fall below 1,000 effective impacts: **D3xC1 443, D3xC2 silent 233
  (Holland's H2 under the primary constraint), D4xC2 silent 59, D5xC2 silent 887**; so do the D3 totals (443-502). These are
  COVERAGE GAPS on run D-he. For run I: aim the burst proposal at every D x C cell (both causes), and give the C2 silent cells
  their own proposal component (the burst-state targets are the same; the silent factor needs a later flame-out to be absent
  or after impact).
- A1 inside the D3/D4/D5 cells: 6-442 effective impacts (gap, as before; aimed pitch-down built, run I).
