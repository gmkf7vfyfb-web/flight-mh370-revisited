# 2026–27 season decision table — preliminary pipeline test on composer views v3.2 (20 Oct 2026)

Status: **pipeline test, before calibration, not for release.** Pete ruled on 20 Oct 2026 that the decision table (gap analysis §6 item 3) waits for the full end-to-end calibration run. This folder builds and tests the pipeline on the current posterior so that, when the calibration run lands, the table is a re-run with one column added. Nothing here is an evidence term; the planned Ocean Infinity block is never used as non-detection evidence.

Written by the decision-table thread (general session, default profile). Inputs: `mh370-exchange/composer/run-j-views-v3.2/` (maps-v3.npz, products-v3.csv, READY), `mh370-exchange/searched-areas/spatial-fields-v2/fields.npz`, and the search-footprint tracing `outputs/mh370_search_evidence/search_footprints.geojson` (feature `oi2024_proposed_inboard_northwest`, grade C). Repository HEAD 3de9525.

## What was computed

1. Davey eq. 11.2, P(success | search B) = P_D × (posterior mass in B after all searches to date), with the planning detection probability P_D = 0.9, on the composer's 769 km² equal-area cells and on 2 × 2-cell blocks (about 3,100 km²; the project's stand-in for Davey's 0.5° blocks), for six 00:19 treatments and ten products (core; core + drift; all evidence; all + Australian non-recovery; detection field ×0, ×10; detection variants V0, V2, V3).
2. The cumulative probability of a find against area searched, best cells first, for all cells and for unsearched cells only (existing coverage below 0.1).
3. The planned Ocean Infinity block (inboard band tracing, 6,122 km² on the cell grid; the official residual is 7,428.54 km²) against the best unsearched cells of equal area.
4. Each block tagged with its existing coverage, 1 − Π(1 − c_i) over ATSB Phase 2 (per cell), Ocean Infinity 2018 (0.889) and 2025–26 (0.7808).
5. A widening response curve: the same quantities after the all-evidence posterior is tempered (p^β, β = 1 to 0.5), which is the form a calibration-adjusted column would take.
6. Rank stability over a 30-cell grid (six treatments × five detection/evidence variants).
7. A table of the smoke calibration statistics as they stand (9 case runs; mechanics only).

## Headline numbers (all evidence, P_D = 0.9)

| 00:19 treatment | planned block: mass | ± approx. SD | P(success) | best unsearched equal area: P(success) | ratio | mass on searched ground |
|---|---|---|---|---|---|---|
| D0' held out | 0.0285 | 0.0055 | 0.026 | 0.065 | 2.6 | 0.30 |
| D3 both BFOs | 0.0042 | 0.0026 | 0.004 | 0.043 | 11.4 | 0.63 |
| D4 both BFOs, Holland offset | 0.0028 | 0.0023 | 0.003 | 0.037 | 14.6 | 0.68 |

Planned-block mass is the composer's exact outcome-level value (`p_in_next_oi_area_not_evidence`); the cell-grid value under-reads it by up to 21 % under D0' (0.0226 against 0.0285) because the post-search posterior is a strip narrower than a cell. The best-unsearched comparator is on the cell grid and is a set of top cells, not a contiguous block, so it is an upper bound. The full table in `next-area-summary.csv` covers all six treatments and ten products; `ranked-blocks-top15.csv` lists the fifteen best blocks per product with coverage tags.

## What the test shows

- **The best blocks after the searches are on searched ground.** Under D3 the top block (37.27 S, 89.75 E, coverage 1.00) holds 0.127 of the all-evidence mass; no block in the D3 top ten is unsearched: seven are searched (coverage 0.83–1.00) and three are partly searched (0.16–0.46). Under D0' the top block (38.53 S, 89.75 E) is unsearched, with 0.039 of the mass, and the next three are searched or partly searched. Across the 30-cell grid, the two blocks most often in the top five (-37.27 S 89.75 E, 23/30; -37.9 S 89.75 E, 22/30) are both fully searched. A ranked table that does not carry a coverage tag would therefore read as a recommendation to re-search the 37 S strip; that reading rests entirely on the level of the detection model (ρ, q), as the composer's views already flag.
- **The planned block ranks low in every cell of the grid.** Its probability of success is 0.026 under D0' and 0.003–0.004 under D3/D4; the best unsearched cells of equal area give 0.065 and 0.037–0.043. The ratio is 2.5 under D0' and 11–15 under D3/D4, and it stays above 1 at every ρ scale, every detection variant and with the Australian term (where the best unsearched cells move to 26–31 S).
- **Widening does not change the ordering.** Tempering the D3 all-evidence posterior from β = 1 to β = 0.5 raises the planned block from 0.006 to 0.009 (cell grid) and lowers the ratio from 7 to 3; under D0' it lowers the planned block from 0.020 to 0.013 and the ratio from 3.2 to 1.8. The calibration result will set the magnitudes, not the direction (`widening-response.csv`).
- **Monte Carlo error at block level is large.** Design effects (seed bootstrap against multinomial, from the composer's own north-of-33 S statistics) are 4–34, so a block holding 2–4 % of the mass carries an approximate SD of 0.5–0.6 percentage points. Neighbouring blocks in the top ten are often within 2 SD of each other and must be reported as ties in the released table.

## Smoke calibration statistics (mechanics only)

`smoke-case-statistics-D0.csv` tabulates, for the nine smoke case runs, the map level at the truth, the latitude and cross-arc ranks and P(true cause) for core, core + searches and all evidence under D0. Map level at truth for 'all' runs from 0.22 to 0.998 across cases. Five truths cannot test coverage; every value is "not assessed at this depth". The case maps were deleted for disk, so no widening factor can be fitted to the smoke.

## What the released table needs (requests)

1. **Composer:** emit block masses and named-polygon masses per bootstrap replicate (the bootstrap already forms `MPb = M @ MP`; the block sum and the polygon sum are two more lines), so the released table has exact Monte Carlo SDs and exact polygon masses rather than the design-effect approximation and the cell-grid under-read used here.
2. **Calibration run (protocol amendment, proposed as A6):** report, per case and per stack, the map level at the truth under tempering β ∈ {1, 0.9, 0.8, 0.7, 0.6, 0.5}. The calibration-adjusted column of the decision table is then the β at which nominal 90 % coverage is met, read from the response curve in `widening-response.csv`.
3. **Searched areas:** the official residual is 7,428.54 km²; the tracing used here is 6,122 km². The gap (about 1,300 km²) needs a stated treatment (scale the tracing, or add the uncompleted part of the outboard band).
4. **Still to add:** the three-way split table (on searched ground / glide tail beyond 25 NM / north of 25 S), the other named public proposals as polygons (ATSB 2017 First Principles Review 25,000 km² area; CSIRO 35.6 S; UWA 33.17 S), and blocks north of 30 S gated on the composed-outcome ESS (D3/D4 25–20 S are below the gate in v3.2).

## Files

`next-area-summary.csv`, `ranked-blocks-top15.csv`, `rank-stability-top5.csv`, `kendall-tau.csv`, `widening-response.csv`, `smoke-case-statistics-D0.csv`, `fig1-find-probability-vs-area.(png|pdf)`, `fig2-ranked-blocks-map.(png|pdf)`, `make_prelim.py` (this pipeline).

---
Footnote, STE100: this is a test of the method on the current result. The numbers can change when the calibration run is done. The planned search block has a low probability of success in every case we tried. The best blocks after the searches are mostly on ground that was already searched; that result depends on how good we think the earlier searches were.
Technical: composer views v3.2 (run J, settled seabed, per-cell detection V1 central, OI 2018/2025–26 grade C coverage 0.889/0.7808, drift finds only, Pléiades conditional, hydroacoustics zero weight); Davey eq. 11.2 with P_D = 0.9; cells 769 km² equal-area (0.25° lon × authalic rows); blocks 2 × 2 cells; SD ≈ sqrt(deff · m(1−m)/ESS_Kish) with deff from the composer's north-of-33 S seed bootstrap; widening p^β renormalised; 'unsearched' = coverage < 0.1.

> **Superseded for interpretation by `results/decision-2026-27-prelim-v2/` (21 Oct 2026).** This version used product DS only (no Australian non-recovery term); calling it "all evidence" was a labelling error.
