# Where the wreckage is on the seabed: end of flight's run H (core run H, six routes)

Ocean settling, 12 Oct 2026 (~02:05Z). Overnight plan step 4, second part: settling's scoring of `end-of-flight/run-h/`. Samples are in
`mh370-exchange/settling/run-h/` (README, SHA256SUMS, READY).

**PROVISIONAL.**
- Core run H is a data-selected subset of six routes (fly-by plus leg tracking). Four routes are populated; the BULVA routes have no rows.
  It is not a fair family comparison with free flight, and core reports no convergence test.
- End of flight's recipe is that of next-run-d-he (binary he6), and so are the labels (`results/settling-run-d-holland/README.md`).
- **No end-of-flight summary existed at run time.** Per-seed ln Z is recorded in `nrh_info.json` for end of flight to cross-check, but it
  is not checked.

## Figures

- `settling-seabed-wreckage-run-h-core`: the five options.
- `-family`.
- `-sens`.
- `-routes`: rows are routes in order of probability, columns the five options; each panel is conditional on its route.

## Areas

| product | row ESS (Kish) | share of option | 90 %: resampled impacts → seabed (thousand km²) | settled offset p50 / p90 / p99 (km) | estimable |
|---|---|---|---|---|---|
| 00:19 Held Out | 937,479 | — | 122.1 → 122.7 | 0.38 / 4.46 / 21.96 | yes |
| 00:19 Held Out · A1 | 111,798 | 14 % | 88.4 → 88.8 | 0.32 / 2.94 / 21.06 | yes |
| 00:19 Held Out · A2 | 434,093 | 34 % | 146.7 → 147.3 | 0.36 / 4.19 / 21.49 | yes |
| 00:19 Held Out · B | 430,088 | 52 % | 76.9 → 77.5 | 0.44 / 5.06 / 22.34 | yes |
| Held Out · NILAM-IGOGU-ISBIX | 116,332 | 10 % | 279.4 → 280.6 | 0.39 / 4.52 / 21.77 | yes |
| Held Out · NILAM-ANOKO-ISBIX | 11,751 | 1 % | 232.9 → 234.6 | 0.39 / 4.67 / 22.41 | yes |
| Held Out · NILAM-SAMAK-ISBIX | 40,484 | 4 % | 134.8 → 135.4 | 0.38 / 4.43 / 21.65 | yes |
| Held Out · MEKAR-SAMAK-ISBIX | 772,809 | 84 % | 97.5 → 98.0 | 0.38 / 4.46 / 21.78 | yes |
| 00:19 R600 BTO Only | 705,866 | — | 70.5 → 70.9 | 0.39 / 4.62 / 22.33 | yes |
| 00:19 R600 BTO Only · A1 | 85,921 | 12 % | 60.2 → 60.5 | 0.31 / 2.87 / 21.80 | yes |
| 00:19 R600 BTO Only · A2 | 312,534 | 33 % | 101.5 → 102.0 | 0.37 / 4.34 / 22.24 | yes |
| 00:19 R600 BTO Only · B | 335,165 | 55 % | 36.8 → 37.3 | 0.44 / 5.04 / 22.34 | yes |
| R600 BTO Only · NILAM-IGOGU-ISBIX | 77,212 | 10 % | 145.2 → 145.9 | 0.39 / 4.63 / 22.25 | yes |
| R600 BTO Only · NILAM-ANOKO-ISBIX | 7,892 | 1 % | 136.5 → 137.5 | 0.39 / 4.84 / 23.01 | yes |
| R600 BTO Only · NILAM-SAMAK-ISBIX | 30,655 | 4 % | 70.0 → 70.5 | 0.39 / 4.56 / 22.04 | yes |
| R600 BTO Only · MEKAR-SAMAK-ISBIX | 591,827 | 85 % | 57.1 → 57.6 | 0.39 / 4.58 / 22.04 | yes |
| 00:19 R600 BTO + Raw BFO | 21,452 | — | 48.3 → 48.7 | 0.39 / 4.58 / 22.16 | yes |
| 00:19 R600 BTO + Raw BFO · A1 | 2,447 | 15 % | 20.5 → 20.6 | 0.32 / 2.66 / 21.60 | yes |
| 00:19 R600 BTO + Raw BFO · A2 | 8,471 | 25 % | 77.5 → 77.8 | 0.35 / 4.24 / 21.61 | yes |
| 00:19 R600 BTO + Raw BFO · B | 11,885 | 60 % | 24.4 → 24.9 | 0.43 / 5.03 / 22.36 | yes |
| R600 BTO + Raw BFO · NILAM-IGOGU-ISBIX | 1,949 | 9 % | 95.0 → 95.5 | 0.38 / 4.39 / 21.86 | yes |
| R600 BTO + Raw BFO · NILAM-ANOKO-ISBIX | 91 | 1 % | 57.6 → 59.0 | 0.46 / 5.14 / 22.06 | **no** |
| R600 BTO + Raw BFO · NILAM-SAMAK-ISBIX | 1,079 | 4 % | 47.6 → 48.0 | 0.38 / 4.57 / 22.32 | yes |
| R600 BTO + Raw BFO · MEKAR-SAMAK-ISBIX | 18,372 | 86 % | 38.3 → 38.7 | 0.39 / 4.57 / 22.23 | yes |
| 00:19 Holland H1 | 111 | — | 13.4 → 13.7 | 0.38 / 4.73 / 22.67 | **no** |
| 00:19 Holland H1 · A1 | 3 | 17 % | 5.4 → 5.5 | 0.69 / 5.70 / 22.17 | **no** |
| 00:19 Holland H1 · A2 | 517 | 38 % | 9.7 → 10.0 | 0.32 / 4.20 / 22.84 | **no** |
| 00:19 Holland H1 · B | 304 | 45 % | 9.9 → 10.2 | 0.36 / 4.66 / 22.66 | **no** |
| 00:19 Holland H1, breakup before 00:19:37 allowed | 113 | mass ×1.02 | 13.5 → 13.8 | 0.38 / 4.70 / 22.63 | **no** |
| 00:19 Holland H1, impacts at or below 212 m/s | 93 | 91 % | 12.4 → 12.7 | 0.40 / 4.91 / 22.68 | **no** |
| Holland H1 · NILAM-IGOGU-ISBIX | 4 | 18 % | 9.8 → 10.5 | 0.72 / 5.88 / 22.68 | **no** |
| Holland H1 · NILAM-ANOKO-ISBIX | 11 | 1 % | 18.0 → 18.8 | 0.36 / 4.57 / 22.34 | **no** |
| Holland H1 · NILAM-SAMAK-ISBIX | 43 | 4 % | 12.5 → 13.0 | 0.30 / 3.81 / 22.82 | **no** |
| Holland H1 · MEKAR-SAMAK-ISBIX | 684 | 78 % | 12.6 → 12.9 | 0.34 / 4.39 / 22.67 | **no** |
| 00:19 Holland H2 | 386 | — | 21.7 → 22.3 | 0.35 / 4.52 / 22.66 | **no** |
| 00:19 Holland H2 · A1 | 52 | 9 % | 17.2 → 17.4 | 0.34 / 2.99 / 20.98 | **no** |
| 00:19 Holland H2 · A2 | 199 | 37 % | 14.0 → 14.5 | 0.35 / 4.63 / 22.67 | **no** |
| 00:19 Holland H2 · B | 166 | 54 % | 14.3 → 14.8 | 0.36 / 4.64 / 22.77 | **no** |
| 00:19 Holland H2, breakup before 00:19:37 allowed | 253 | mass ×2.36 | 17.6 → 18.0 | 0.32 / 4.28 / 22.42 | **no** |
| 00:19 Holland H2, impacts at or below 212 m/s | 335 | 85 % | 18.9 → 19.4 | 0.38 / 4.80 / 22.63 | **no** |
| Holland H2 · NILAM-IGOGU-ISBIX | 38 | 12 % | 23.9 → 25.0 | 0.35 / 4.49 / 21.92 | **no** |
| Holland H2 · NILAM-ANOKO-ISBIX | 6 | 1 % | 7.9 → 8.3 | 0.81 / 5.91 / 21.62 | **no** |
| Holland H2 · NILAM-SAMAK-ISBIX | 25 | 2 % | 17.9 → 18.4 | 0.36 / 4.22 / 22.83 | **no** |
| Holland H2 · MEKAR-SAMAK-ISBIX | 328 | 84 % | 16.9 → 17.3 | 0.35 / 4.52 / 22.69 | **no** |


## What it shows

1. **Holland H1 and H2 are NOT estimable on run H.** The row ESS is 111 (H1) and 386 (H2) against the 1,000 gate; on next-run-d-he
   they were 4,690 and 2,234. Run H has about 3.1 M rows against 51 M, and under H1 a single impact takes 8.9 % of the draws. For H1/H2,
   use next-run-d-he; run H answers the route question for the other options.
2. **MEKAR-SAMAK-ISBIX carries 84-86 % of every option.** Its seabed region is the smallest of the four routes: Held Out 98, R600 BTO
   Only 58, R600 BTO + Raw BFO 39 thousand km². The NILAM routes give wider regions (NILAM-IGOGU-ISBIX 281 / 146 / 96) that reach further
   along the arc.
3. **Over all routes the regions are small:** Held Out 123, R600 BTO Only 71, R600 BTO + Raw BFO 49 thousand km² (seabed), against 553 / 312 / 227 on
   next-run-d-he. That is the cost of the data-selected route subset. These are conditional results, not a replacement for the free strata.
4. **Settling adds under 1 % to every estimable area**, as in every earlier run.

## COVERAGE

- (a) The feasible set and (b) settling's reach are as for next-run-d-he, including gap **G-bf** (in-flight breakup rows settled from the
  intact impact point).
- (c) Proposal coverage:
  - H1 / H2 NOT estimable (111 / 386): a **GAP on run H**, closed for the free strata by next-run-d-he.
  - Per route, Raw BFO on NILAM-ANOKO-ISBIX has 91 and is not estimable.
  - Every Held Out and R600 BTO Only route panel is estimable (ESS ≥ 7,892).
  - The table above gives the ESS per option, route and family.
- The route family itself is a **conditional hypothesis** ("the aircraft flew one of core run H's six routes"), and every panel title
  names its route.

## Reproduce

    WF_STRATA=next-h-routes=1.0 WF_ROUTE_DIR=mh370-exchange/core/run-h WF_ROUTES=3,11,19,43 python3 wf_rows.py prep <EoF smoke> mh370-exchange/end-of-flight/run-h - nrh
    (settle field/nrh_impacts.f64; 19.7 min at 2 threads; prep about 4 min at 1 thread)
    WF_RUN_NAME=... WF_NSEEDS=8 python3 wf_rows.py render <EoF smoke> <reference-289 run.json> nrh run-h 9330d4c 7da43d01 core|family|sens|routes

- Ocean Settling
