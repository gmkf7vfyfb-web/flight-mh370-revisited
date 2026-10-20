# End of flight on core run D, "make H1/H2 estimable" recipe: full sweep (11 Oct 2026, 21:51-23:14 UTC)

**PROVISIONAL. Not converged at the core stage** (core run D split-half below its 4-seed floor 0.896 in three of four strata, and
the routes stratum has an incomplete route exploration: core's README). Architecture GO 20:55Z 11 Oct. Run under the heavy lock,
12 threads; binary /tmp/mh370-eof-he5 (sha256 262ffeb7), script `full/sweep_holland.sh`, recipe = smoke arm C
(`results/eof-holland-estimable-oct11`). Core run D m0011 look-ahead hand-offs (read with `handoff::read_corrected`), 4 strata x 4
seeds, N = 8 children x 4 descents per parent. Output on the exchange: `end-of-flight/next-run-d-he/` (compact float32, every seed
verified by `check`; 18 GB); summary `summary/holland-sweep-summary.json` (= `holland-sweep-summary.json` here; tool
`smoke/holland_sweep_summary.py`). This sweep carries physics items 2-4 and SUPERSEDES the items 2-4 sweep, which was not run.

Labels (carry into every product): constraint `unpowered` (reference); **primary** = with the survival factor (no in-flight
breakup before 00:19:37, adopted by architecture 20:55Z as part of the 00:19 data model), **sensitivity** = without it;
piloted rapid descent to 40,000 ft/min with unloading to -1.0 g; INTERIM parametric pitch-down in free flight; piloted load-factor
ceiling U[1.5, 5.0] g; targeted burst proposal (exact weights, unnormalised within-parent); in-flight structural outcome
PROVISIONAL (VD 380 KEAS, MD 0.95 declared; no transonic drag rise, so P(breakup) in dives is an upper-side estimate); residual
roll direction P(left) = 0.8 PROVISIONAL; families by ruling 6 as amended. Mixture over strata with core's P(family) (free 0.594,
Davey dynamics + radar 0.235, descent-climb 0.153, routes 0.019) times the end-of-flight evidence.

## Results

| 00:19 option | Version | ln Z (mixture) | Effective impacts | A1 share / eff. | A2 share / eff. | B share / eff. | P(in-flight breakup) | Contact speed <= 212 m/s | Latitude q05 / q50 / q95 |
|---|---|---|---|---|---|---|---|---|---|
| 00:19 Held Out | primary | -0.22 | 6,378,686 | 0.13 / 784,077 | 0.33 / 2,840,019 | 0.53 / 2,986,827 | 0.243 | 0.891 | -39.72 / -37.39 / -29.17 |
| 00:19 Held Out | without survival factor | -0.06 | 6,918,708 | 0.12 / 796,266 | 0.32 / 2,923,815 | 0.56 / 3,404,714 | 0.349 | 0.897 | -39.62 / -37.33 / -29.24 |
| 00:19 R600 BTO Only | primary | -5.89 | 8,377,630 | 0.12 / 982,984 | 0.33 / 3,751,788 | 0.56 / 4,014,416 | 0.261 | 0.887 | -39.93 / -37.93 / -29.21 |
| 00:19 R600 BTO Only | without survival factor | -5.74 | 8,796,714 | 0.10 / 982,147 | 0.32 / 3,713,036 | 0.58 / 4,414,471 | 0.357 | 0.895 | -39.85 / -37.82 / -29.31 |
| 00:19 R600 BTO + Raw BFO | primary | -12.81 | 190,237 | 0.15 / 21,623 | 0.26 / 80,257 | 0.59 / 102,661 | 0.255 | 0.847 | -39.11 / -37.38 / -28.95 |
| 00:19 R600 BTO + Raw BFO | without survival factor | -12.71 | 196,447 | 0.13 / 21,622 | 0.27 / 75,905 | 0.60 / 107,528 | 0.323 | 0.844 | -39.07 / -37.38 / -29.08 |
| 00:19 Holland H1 | primary | -28.72 | 4,690 | 0.12 / 136 | 0.37 / 4,981 | 0.51 / 3,520 | 0.932 | 0.860 | -38.94 / -37.55 / -29.67 |
| 00:19 Holland H1 | without survival factor | -28.70 | 4,338 | 0.13 / 131 | 0.37 / 4,711 | 0.51 / 3,365 | 0.932 | 0.856 | -38.94 / -37.52 / -29.80 |
| 00:19 Holland H2 | primary | -22.56 | 2,234 | 0.12 / 59 | 0.33 / 2,186 | 0.55 / 1,920 | 0.879 | 0.854 | -38.92 / -37.49 / -29.94 |
| 00:19 Holland H2 | without survival factor | -21.65 | 1,599 | 0.05 / 58 | 0.33 / 482 | 0.62 / 1,075 | 0.937 | 0.935 | -38.75 / -37.46 / -30.31 |

| Version | ln BF H1:H2 at W = 60 / 300 / 900 / 1,775 / 3,600 s | Break-even W (s) |
|---|---|---|
| primary | -2.07 / -0.46 / +0.64 / +1.32 / +2.03 | 474 |
| without survival factor | -2.96 / -1.35 / -0.25 / +0.43 / +1.14 | 1157 |

| Stratum (core P) | Held Out | R600 BTO Only | R600 BTO + Raw BFO | Holland H1 | Holland H2 |
|---|---|---|---|---|---|
| next-d-free (0.594) | -0.22 ± 0.01 | -5.89 ± 0.04 | -12.79 ± 0.05 | -28.74 ± 0.09 | -22.55 ± 0.04 |
| next-d-repro-radar (0.235) | -0.23 ± 0.01 | -5.96 ± 0.03 | -12.96 ± 0.07 | -28.87 ± 0.12 | -22.66 ± 0.07 |
| next-d-descent-climb (0.153) | -0.21 ± 0.02 | -5.81 ± 0.05 | -12.71 ± 0.20 | -28.54 ± 0.38 | -22.49 ± 0.28 |
| next-d-routes (0.019) | -0.24 ± 0.00 | -5.80 ± 0.02 | -12.97 ± 0.02 | -28.65 ± 0.07 | -22.52 ± 0.09 |

(Third table: per stratum, mean of the four seed ln Z values ± seed standard deviation, primary version.)

Readings:
1. **H1 and H2 are now estimable.** Effective impacts (mixture, primary): H1 4,690, H2 2,234 (sensitivity: 4,338 and 1,599). The
   1,000 gate is met by both, in both versions. Seed standard deviation of ln Z in the free stratum: H1 0.09, H2 0.04; largest in
   descent-climb (0.38 and 0.28).
2. **H1:H2** depends on the declared log-on window W ("other" has no log-on-time density). Primary: break-even W = 474 s; ln BF
   H1:H2 = -0.46 at W = 300 s and +1.32 at W = 1,775 s. Without the survival factor the break-even is 1,157 s (-1.35 and +0.43).
   The survival factor lowers H2 by 0.91 nat and H1 by 0.02 nat: 61-65% of the H2 posterior without it sits on descents whose
   structure would probably have failed before 00:19:37.
3. **Impact latitude is insensitive to the 00:19 option**: medians -37.39 (Held Out), -37.93 (R600 BTO Only), -37.38 (Raw BFO),
   -37.55 (H1), -37.49 (H2), primary.
4. **In-flight breakup** (PROVISIONAL): Held Out 0.24 (0.35 without the survival factor), R600 BTO Only 0.26, H1 0.93, H2 0.88.
   Under H1/H2 the descent that matches the bursts almost always exceeds the design dive speed later in the descent.
5. **Families under H1/H2** (primary): H1 A1 0.12 / A2 0.37 / B 0.51; H2 A1 0.12 / A2 0.33 / B 0.55.
6. **A against B by B-onset window** cannot be read from this 00:11 sweep (every B onset here is after the 00:11 hand-off, share
   1.0 by construction); it is in `results/eof-a-vs-b-2241-late-onset-oct11.md` (22:41 hand-off, N = 1 smoke): ln BF of A against
   B before 23:15 / 23:15-00:11 / after 00:11 = +6.15 / -0.68 / -1.27.

## COVERAGE

- (a) FEASIBLE set: cruise to fuel exhaustion with uncontrolled or controlled descents (A1, A2) and deliberate descents to a
  ditching (B), including piloted dives to about 39,000 ft/min with unloading to -1.0 g (NTSB AAB-02/01, CS-25.337(c)), speeds to
  and past VMO/MMO, uncontrolled pitch-downs (SIR App. 1.6E), pull-outs past the 2.5 g limit (NTSB AAR-86/03), and in-flight
  structural damage or breakup.
- (b) MODEL'S REACH: all of the above in parametric form. GAPS: stepped shapes have no push-over (G-st, conditional); the pitch-down
  is INTERIM (not the 6-DOF); no transonic drag rise above the crest Mach (drag calibration 1(B) pending), so dive speeds and
  P(breakup) are upper-side; partial damage flown with undamaged dynamics (G-pd) and breakup rows keep the intact impact point
  (G-bf; the fragment field waits for 1(B) and the consumers' answers).
- (c) PROPOSAL COVERAGE (effective impacts, primary): Held Out 6.38 M, R600 BTO Only 8.38 M, Raw BFO 190 k, **H1 4,690, H2 2,234
  (gate 1,000: MET)**. Per family: A1 under H1 136 and under H2 59 - **COVERAGE GAP** (A1 reaches the H1/H2 states only through
  the interim pitch-down; fix: the 6-DOF free dynamics, or a pitch-down window aimed at the free phase of A1, plus more parents);
  A2 4,981 / 2,186; B 3,520 / 1,920. Held Out A1 784 k.
- Bounds and sources: as in `results/eof-holland-estimable-oct11/README.md` (rate, floor, hold, VMO, pitch-down, ceiling,
  structural fragility).
