Ocean settling - seabed wreckage samples on end of flight's run J northern supplement, full rule-B set, 2026-10-20 10:26Z.
CONDITIONAL on the waypoints stratum (core share 0.9982). Work order threads/work-orders/overnight-2026-10-20.md B1.
Settling hypothesis/settling 9330d4c (real ocean, 75-115 E, 45-10 S; unchanged since run I). Results note:
Claude Science Project Sep 29/results/settling-run-j-supplement/README.md.
Core run J split-half accepted as a pass by project ruling, 16 Oct 2026. D0 = D0' (impact after 00:19:37.443 imposed; checked).
CAVEAT (end of flight, verbatim): the uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all three rounds.

INPUT: end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz (2,408,038 rows; the file end of flight names for
downstream modules): run J production + all supplement rows + extra descents (D2-D5), rule B with core's r_hat, one
Horvitz-Thompson thinning. ROW MASS = exp(lnw:comb/<d>) as stored (no re-weighting here). Products: per D0'-D5 total (N 40,000),
A1 / A2 / B (N 10,000; family4_code 1 / 2 / 3; code 6 'other', 0.1-0.2 %, is in the totals only), impacts north of 33 S
(N 10,000, CONDITIONAL; share in the table); per D3s-D5s ('other log-on cause only', C2-silent arm) total (N 40,000).
Each product is a systematic resample, one settling draw each: AVERAGE over outcomes (equal weight 1/N).
A1 under D3 here rests on the unconditional rule-B rows (row ESS below the gate): for A1 under D3-D5 use the stratified A1
products in settling/run-j-a1branch/ (run J paths) or this folder's a1-stratified/ subfolder if present (see its README).

Products (j indexes rjs_draws.npz rows_<j>, draws_<j>); 90 % areas thousand km2 (resampled impacts -> seabed):
| j | 00:19 treatment | subset | N | row ESS | share within the treatment | 90 % area | settled offset p50/p90/p99 km | not computed | estimable |
|---|---|---|---|---|---|---|---|---|---|
| P00 | 00:19 Held Out | all | 40,000 | 233,461 | 100.00 % | 164.7 -> 165.1 | 0.36 / 3.78 / 21.14 | 0 | yes |
| P01 | 00:19 Held Out | A1 | 10,000 | 41,685 | 17.00 % | 35.7 -> 36.0 | 0.30 / 1.89 / 21.74 | 0 | yes |
| P02 | 00:19 Held Out | A2 | 10,000 | 77,395 | 34.15 % | 165.9 -> 166.4 | 0.35 / 3.70 / 20.94 | 0 | yes |
| P03 | 00:19 Held Out | B | 10,000 | 114,317 | 48.76 % | 187.1 -> 187.7 | 0.40 / 4.39 / 20.78 | 0 | yes |
| P04 | 00:19 Held Out | north33 | 10,000 | 97,492 | 3.49 % | 363.7 -> 365.1 | 0.42 / 4.01 / 23.28 | 0 | yes |
| P05 | 00:19 R600 BTO Only | all | 40,000 | 200,631 | 100.00 % | 118.8 -> 119.1 | 0.35 / 3.71 / 21.51 | 0 | yes |
| P06 | 00:19 R600 BTO Only | A1 | 10,000 | 38,454 | 19.62 % | 21.0 -> 21.3 | 0.30 / 1.89 / 21.54 | 0 | yes |
| P07 | 00:19 R600 BTO Only | A2 | 10,000 | 68,349 | 34.50 % | 124.8 -> 125.2 | 0.35 / 3.65 / 21.29 | 0 | yes |
| P08 | 00:19 R600 BTO Only | B | 10,000 | 93,685 | 45.78 % | 133.6 -> 133.9 | 0.40 / 4.31 / 21.34 | 0 | yes |
| P09 | 00:19 R600 BTO Only | north33 | 10,000 | 93,035 | 2.09 % | 248.4 -> 249.7 | 0.41 / 3.92 / 24.10 | 0 | yes |
| P10 | 00:19 R600 BTO + Raw BFO | all | 40,000 | 84,627 | 100.00 % | 106.5 -> 106.8 | 0.37 / 3.91 / 21.09 | 0 | yes |
| P11 | 00:19 R600 BTO + Raw BFO | A1 | 10,000 | 33,250 | 23.59 % | 19.6 -> 19.8 | 0.30 / 1.92 / 21.64 | 0 | yes |
| P12 | 00:19 R600 BTO + Raw BFO | A2 | 10,000 | 24,099 | 23.33 % | 129.6 -> 130.0 | 0.37 / 3.89 / 20.75 | 0 | yes |
| P13 | 00:19 R600 BTO + Raw BFO | B | 10,000 | 35,611 | 52.97 % | 115.3 -> 115.5 | 0.41 / 4.48 / 20.96 | 0 | yes |
| P14 | 00:19 R600 BTO + Raw BFO | north33 | 10,000 | 39,114 | 2.56 % | 226.6 -> 228.1 | 0.42 / 4.08 / 23.49 | 0 | yes |
| P15 | 00:19 R600 BTO + both BFOs as recorded | all | 40,000 | 5,393 | 100.00 % | 63.7 -> 64.0 | 0.33 / 3.07 / 21.68 | 0 | yes |
| P16 | 00:19 R600 BTO + both BFOs as recorded | A1 | 10,000 | 408 | 9.35 % | 17.6 -> 17.9 | 0.30 / 1.94 / 21.83 | 0 | NO |
| P17 | 00:19 R600 BTO + both BFOs as recorded | A2 | 10,000 | 4,451 | 40.56 % | 58.9 -> 59.2 | 0.33 / 3.11 / 21.89 | 0 | yes |
| P18 | 00:19 R600 BTO + both BFOs as recorded | B | 10,000 | 1,968 | 49.98 % | 69.1 -> 69.4 | 0.34 / 3.23 / 21.48 | 0 | yes |
| P19 | 00:19 R600 BTO + both BFOs as recorded | north33 | 10,000 | 2,947 | 2.18 % | 145.8 -> 147.5 | 0.39 / 3.12 / 24.01 | 0 | yes |
| P20 | 00:19 R600 BTO + both BFOs, Holland transient bias added | all | 40,000 | 28,559 | 100.00 % | 61.6 -> 61.9 | 0.32 / 2.83 / 21.66 | 0 | yes |
| P21 | 00:19 R600 BTO + both BFOs, Holland transient bias added | A1 | 10,000 | 2,913 | 24.65 % | 27.1 -> 27.4 | 0.30 / 1.91 / 21.66 | 0 | yes |
| P22 | 00:19 R600 BTO + both BFOs, Holland transient bias added | A2 | 10,000 | 30,460 | 34.77 % | 58.6 -> 58.8 | 0.33 / 3.06 / 21.86 | 0 | yes |
| P23 | 00:19 R600 BTO + both BFOs, Holland transient bias added | B | 10,000 | 16,069 | 40.39 % | 66.1 -> 66.4 | 0.34 / 3.17 / 21.63 | 0 | yes |
| P24 | 00:19 R600 BTO + both BFOs, Holland transient bias added | north33 | 10,000 | 4,082 | 2.80 % | 132.0 -> 134.2 | 0.37 / 2.62 / 24.59 | 0 | yes |
| P25 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | all | 40,000 | 18,910 | 100.00 % | 60.4 -> 60.7 | 0.33 / 3.03 / 21.60 | 0 | yes |
| P26 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | A1 | 10,000 | 1,455 | 5.81 % | 17.9 -> 18.1 | 0.32 / 1.94 / 22.15 | 0 | yes |
| P27 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | A2 | 10,000 | 14,195 | 41.72 % | 56.5 -> 56.8 | 0.33 / 2.94 / 21.81 | 0 | yes |
| P28 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | B | 10,000 | 7,173 | 52.40 % | 64.1 -> 64.4 | 0.33 / 3.16 / 21.70 | 0 | yes |
| P29 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | north33 | 10,000 | 7,843 | 2.20 % | 137.3 -> 138.8 | 0.38 / 2.98 / 23.96 | 0 | yes |
| P30 | 00:19 R600 BTO + both BFOs as recorded, other log-on cause only | all | 40,000 | 5,631 | 100.00 % | 49.8 -> 50.1 | 0.31 / 1.90 / 21.40 | 0 | yes |
| P31 | 00:19 R600 BTO + both BFOs, Holland transient bias added, other log-on cause only | all | 40,000 | 4,889 | 100.00 % | 52.3 -> 52.8 | 0.33 / 1.95 / 21.77 | 0 | yes |
| P32 | 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added, other log-on cause only | all | 40,000 | 13,906 | 100.00 % | 45.5 -> 45.9 | 0.31 / 1.91 / 21.46 | 0 | yes |

COVERAGE
(a) Feasible set: as end of flight's run J and supplement notes (piloted dives to about 40,000 ft/min, unloading, speeds past
    VMO/MMO, piloted turns, in-flight structural damage or breakup; overbank above 90 deg a declared reach gap there).
(b) Settling's reach: every row reaching the water, settled as an intact impact. Reach gaps: G-bf (in-flight breakup rows settled
    from the intact impact point); attitude-dependent breakup (declared); impact pitch not used (G6).
(c) Proposal coverage (row Kish ESS on the reduced table per product above; gate 1,000). Products below the gate:
    - 00:19 R600 BTO + both BFOs as recorded x A1: row ESS 408
    End of flight's distinct-state band ESS (full set) is the authoritative northern coverage figure: results/eof-run-j-supplement-oct20.

Files: rjs_impacts.f64 (f64, 14 columns: unix_s, lat, lon, v_east, v_north, v_up, flight-path angle, mass, KE, vertical KE,
parent (= handoff_row), debris_class, draws, 0*10+1); rjs_source.npy (int64: 0, 1, ROW INDEX into reduced/impacts-ruleB.npz);
rjs_elements.f64 (8 columns: table row, draw, breakup family, class, fate (0 settled, 1 afloat), lat, lon, mass kg);
rjs_draws.npz; rjs_info.json (products, impact-level band masses and ESS, comb and alone); figures settling-seabed-wreckage-run-j-supplement-waypoints-{core,family,north,other}.{png,pdf,json}.
