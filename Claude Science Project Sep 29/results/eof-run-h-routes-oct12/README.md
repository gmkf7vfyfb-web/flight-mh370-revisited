# Run H routes (fly-by turns + leg tracking) carried to impact (12 Oct 2026)

**PROVISIONAL; per route, conditional on the route.** Core's caveat applies: the 6-route family is a data-selected subset
(the pilot's leaders), not a fair family comparison with free flight; do not use it as a family-level weight. Architecture GO
21:30Z 11 Oct; run outside the lock at 4 threads 01:06-01:30Z 12 Oct (architecture 01:05Z). Input: core run H
(`core/run-h/`, job 644a5bff, 8 seeds x about 1,530 rows, uniform hand-off rows; gzipped files checked against core's SHA256SUMS,
27/27). Recipe = the H1/H2 sweep (arm C), binary he6 (954621fc; impacts byte-identical to he5 on the run D smoke), except
N = 64 children x 4 descents per parent (sampling only, declared: the hand-off is 1.5% of run D's per-seed size). Survival
factor PRIMARY (the table); results without it in `run-h-per-route.json`. Constraint unpowered. Output
`end-of-flight/run-h/next-h-routes/seed-1..8` (compact, verified), summary `summary/run-h-per-route.json`; tool
`smoke/run_h_summary.py`. Routes 10 and 2 (BULVA ends) have no hand-off rows (core: log evidence below -470).

**First attempt failed** (23:17-00:24Z): binary he5 predated core's `fly_by` field in the run H config and stopped at config
parsing on every seed. Fixed by rebuilding on the merged tree (he6); see architecture.md ~01:15 UTC.

"Core 00:19 latitude" is core's own number, labelled **"core, Davey both-BTO no-BFO 00:19 treatment"** (Pete's label, 21:20Z);
the other latitudes are end-of-flight impact latitudes under the named 00:19 option.

| 00:19 option | Route | Posterior route share | ln Z | Effective impacts / parents | P(A1 / A2 / B) | P(in-flight breakup) | Impact latitude q05 / q50 / q95 (90% region) | Core 00:19 latitude q05 / q50 / q95 |
|---|---|---|---|---|---|---|---|---|
| 00:19 Held Out | pooled | 1.000 | -0.25 | 937,479 / 8,270 | 0.14 / 0.34 / 0.52 | 0.23 | -39.74 / -38.17 / -35.50 | - |
| 00:19 Held Out | MEKAR-SAMAK-ISBIX | 0.841 | -0.42 | 772,809 / 6,822 | 0.14 / 0.34 / 0.52 | 0.23 | -39.72 / -38.19 / -35.81 | -37.42 / -37.17 / -36.96 |
| 00:19 Held Out | NILAM-IGOGU-ISBIX | 0.104 | -2.51 | 116,332 / 997 | 0.13 / 0.33 / 0.53 | 0.24 | -39.91 / -38.00 / -32.13 | -37.55 / -37.30 / -35.04 |
| 00:19 Held Out | NILAM-SAMAK-ISBIX | 0.044 | -3.37 | 40,484 / 380 | 0.14 / 0.35 / 0.51 | 0.22 | -39.50 / -38.05 / -34.55 | -37.40 / -37.16 / -36.40 |
| 00:19 Held Out | NILAM-ANOKO-ISBIX | 0.010 | -4.88 | 11,751 / 95 | 0.13 / 0.33 / 0.54 | 0.23 | -40.07 / -38.10 / -33.17 | -37.71 / -37.44 / -34.99 |
| 00:19 R600 BTO Only | pooled | 1.000 | -5.73 | 705,866 / 6,770 | 0.12 / 0.33 / 0.55 | 0.25 | -39.85 / -38.36 / -36.53 | - |
| 00:19 R600 BTO Only | MEKAR-SAMAK-ISBIX | 0.852 | -5.89 | 591,827 / 5,700 | 0.12 / 0.33 / 0.55 | 0.25 | -39.83 / -38.37 / -36.65 | -37.42 / -37.17 / -36.96 |
| 00:19 R600 BTO Only | NILAM-IGOGU-ISBIX | 0.095 | -8.08 | 77,212 / 704 | 0.12 / 0.32 / 0.56 | 0.26 | -40.09 / -38.35 / -35.42 | -37.55 / -37.30 / -35.04 |
| 00:19 R600 BTO Only | NILAM-SAMAK-ISBIX | 0.043 | -8.88 | 30,655 / 303 | 0.11 / 0.34 / 0.55 | 0.25 | -39.63 / -38.27 / -36.30 | -37.40 / -37.16 / -36.40 |
| 00:19 R600 BTO Only | NILAM-ANOKO-ISBIX | 0.009 | -10.44 | 7,892 / 70 | 0.11 / 0.32 / 0.56 | 0.25 | -40.20 / -38.44 / -35.44 | -37.71 / -37.44 / -34.99 |
| 00:19 R600 BTO + Raw BFO | pooled | 1.000 | -12.48 | 21,452 / 3,367 | 0.15 / 0.25 / 0.60 | 0.25 | -39.12 / -37.91 / -36.37 | - |
| 00:19 R600 BTO + Raw BFO | MEKAR-SAMAK-ISBIX | 0.862 | -12.63 | 18,372 / 2,906 | 0.15 / 0.25 / 0.60 | 0.24 | -39.11 / -37.91 / -36.53 | -37.42 / -37.17 / -36.96 |
| 00:19 R600 BTO + Raw BFO | NILAM-IGOGU-ISBIX | 0.088 | -14.91 | 1,949 / 264 | 0.16 / 0.29 / 0.54 | 0.28 | -39.15 / -37.90 / -35.23 | -37.55 / -37.30 / -35.04 |
| 00:19 R600 BTO + Raw BFO | NILAM-SAMAK-ISBIX | 0.044 | -15.61 | 1,079 / 175 | 0.12 / 0.24 / 0.64 | 0.22 | -39.12 / -37.87 / -36.03 | -37.40 / -37.16 / -36.40 |
| 00:19 R600 BTO + Raw BFO | NILAM-ANOKO-ISBIX | 0.006 | -17.56 | 91 / 35 NOT ESTIMABLE | 0.15 / 0.16 / 0.69 | 0.31 | -39.41 / -38.21 / -35.34 | -37.71 / -37.44 / -34.99 |
| 00:19 Holland H1 | pooled | 1.000 | -28.37 | 111 / 105 NOT ESTIMABLE | 0.17 / 0.38 / 0.45 | 0.87 | -38.38 / -37.95 / -36.85 | - |
| 00:19 Holland H1 | MEKAR-SAMAK-ISBIX | 0.776 | -28.62 | 684 / 488 NOT ESTIMABLE | 0.09 / 0.42 / 0.48 | 0.95 | -38.38 / -37.99 / -36.87 | -37.42 / -37.17 / -36.96 |
| 00:19 Holland H1 | NILAM-IGOGU-ISBIX | 0.179 | -30.09 | 4 / 4 NOT ESTIMABLE | 0.52 / 0.16 / 0.32 | 0.49 | -38.47 / -37.13 / -36.90 | -37.55 / -37.30 / -35.04 |
| 00:19 Holland H1 | NILAM-SAMAK-ISBIX | 0.039 | -31.63 | 43 / 35 NOT ESTIMABLE | 0.05 / 0.45 / 0.50 | 0.97 | -38.45 / -37.99 / -36.77 | -37.40 / -37.16 / -36.40 |
| 00:19 Holland H1 | NILAM-ANOKO-ISBIX | 0.006 | -33.43 | 11 / 5 NOT ESTIMABLE | 0.15 / 0.67 / 0.19 | 0.91 | -38.84 / -37.98 / -36.12 | -37.71 / -37.44 / -34.99 |
| 00:19 Holland H2 | pooled | 1.000 | -22.35 | 386 / 358 NOT ESTIMABLE | 0.09 / 0.37 / 0.54 | 0.91 | -38.46 / -37.99 / -36.38 | - |
| 00:19 Holland H2 | MEKAR-SAMAK-ISBIX | 0.845 | -22.52 | 328 / 302 NOT ESTIMABLE | 0.09 / 0.37 / 0.53 | 0.92 | -38.45 / -37.99 / -36.71 | -37.42 / -37.17 / -36.96 |
| 00:19 Holland H2 | NILAM-IGOGU-ISBIX | 0.117 | -24.50 | 38 / 37 NOT ESTIMABLE | 0.08 / 0.29 / 0.63 | 0.89 | -38.47 / -38.04 / -33.53 | -37.55 / -37.30 / -35.04 |
| 00:19 Holland H2 | NILAM-SAMAK-ISBIX | 0.024 | -26.07 | 25 / 24 NOT ESTIMABLE | 0.12 / 0.54 / 0.35 | 0.88 | -38.28 / -37.63 / -34.63 | -37.40 / -37.16 / -36.40 |
| 00:19 Holland H2 | NILAM-ANOKO-ISBIX | 0.014 | -26.61 | 6 / 5 NOT ESTIMABLE | 0.00 / 0.60 / 0.39 | 0.99 | -38.57 / -38.40 / -35.78 | -37.71 / -37.44 / -34.99 |

Readings:
1. Impact latitude medians per route under Held Out are -38.0 to -38.2 (pooled -38.17); under R600 BTO Only -38.3 to -38.4
   (pooled -38.36). Against the same options in the free-flight H1/H2 sweep (Held Out -37.39, R600 BTO Only -37.93) they are
   south by 0.6-0.8 deg under Held Out (pooled 0.78) and by 0.3-0.5 deg under R600 BTO Only (pooled 0.43). (Core's own 00:19
   medians, -37.2 to -37.4, are 00:19 positions, not impact points, and are not differenced here.)
2. Families do not depend on the route (A1 0.12-0.14, A2 0.33-0.35, B 0.51-0.55 under Held Out).
3. The route shares hardly move from core's 00:11 shares (MEKAR-SAMAK-ISBIX 0.84-0.86 against core's 0.856).

## COVERAGE
- (a) Feasible / (b) reach: as in `results/eof-holland-sweep-run-d-oct11/README.md` (same recipe, same gaps: G-st, interim
  pitch-down, no transonic drag rise, G-pd, G-bf, A1 under H1/H2).
- (c) Proposal coverage, primary: Held Out, R600 BTO Only and R600 BTO + Raw BFO are estimable for the pooled set and for
  MEKAR-SAMAK-ISBIX, NILAM-IGOGU-ISBIX and NILAM-SAMAK-ISBIX (effective impacts 1,079 or more); NILAM-ANOKO-ISBIX (share about
  0.01) is estimable for Held Out and BTO Only (11,751 / 7,892) but **not for Raw BFO (91)**. **Holland H1 and H2 are NOT
  ESTIMABLE** for the pooled set (111 / 386 effective impacts) and for every route (H1 at most 684 on MEKAR-SAMAK-ISBIX; H2 at
  most 328). Cause: 1,530 parents per seed (8 seeds, 12,240 in all) against 100,000 per seed in run D. Fix: more run H hand-off
  rows from core (about 10x for H2 at the pooled level), not more children.
