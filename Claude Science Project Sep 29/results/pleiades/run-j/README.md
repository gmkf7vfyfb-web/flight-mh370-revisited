# Pléiades module on core run J: H-conditional 00:19 two-factor table (D0′-D5 x C1 / C2 silent / total q = 1/3), tension, close-ups, western residual

Pléiades module, 18 Oct 2026 (overnight; Pete offline). Brief: `threads/master-prompts/pleiades.md` v2 (adopted 00:41Z), section 8 items 1, 2 and 5 (in part).
Scripts (all in `engine/hypotheses/pleiades/prepare/`): `score_runj.py` (per seed: columns + sums), `aggregate_runj.py`, `score_runj_joined.py`,
`aggregate_runj_joined.py`, `runj_closeups.py`, `runj_tables.py` (every number in the tables below is read from the JSON files here by that script),
`finalize_runj.py`. Builder `build_columns.py` (parser amended for `run-j-*`, commit 18a00f78; output byte-identical to the previous version).

**Labels (carry them into every product):**
- **conditional on H** (at least one imaged object came from 9M-MRO); no identity likelihood; no absolute Bayes factor or P(H | data) (not interpretable until the Poisson and footprint term exists);
- core run J: split-half accepted as a pass by project ruling, 16 Oct 2026 (all four families; free flight 0.840 single split);
- end-of-flight physics PROVISIONAL (end of flight's run J label list applies in full: piloted-turn model, INTERIM pitch-down, push-over and Boeing sequence, residual roll P(left) = 0.8, in-flight structural outcome);
- Pléiades rating 5 (12 objects, 6 clusters at 3 km, equal weight) + all four COSMO-SkyMed contacts F1-F4, pass-marginal, one debris field;
- headline: ρ 0.25, GLORYS12 + ERA5 and GlobCurrent + ERA5 (product-relative windage), equal prior; GLORYS12 only shown beside; ρ 0 / 0.5 as sensitivity;
- **before any seabed search** (searched areas' run J columns are not used tonight; "after all searches" is out of scope);
- D0′ = 00:19 values held out, transmission imposed (the log-on cause factor and the survival factor apply; end of flight's D0 cell of `option_table_0019`).

## Inputs and seed sets
- End of flight run J (`mh370-exchange/end-of-flight/run-j/`): waypoints 24 seeds, free 18, descent-climb 16, repro-radar 16; strata mixed by core run J P(family) from core `summary.json` log evidence: waypoints 0.99817, free 0.00126, descent-climb 0.00024, repro-radar 0.00033.
- D3 and D4, waypoints stratum: end of flight's both-burst supplementary set (`run-j-both-burst/run-j-waypoints/`, seeds 1-8, thinned; normalised by `thinning.weight_sum_in` inside `seed_terms`), as the composer uses it. Production-only D3/D4 are reported as a check.
- Joined V2 (`run-j-joined-v2/`): seed pairs 1-23 (J2241 seed 24 was still running at 01:20Z and is not used; J0011 seed 24 is complete but has no partner).
- Surfaces: the module's wide-grid hook as in `pleiades/run-i/surfaces` (78-115 E, 45-5 S, 0.05 deg; sha256 identical to `pleiades/next-run-d-he/surfaces`).
- Rows scored: 321,601,217 impact rows (74 production seeds + 8 both-burst seeds) and 147.2 M joined rows (23 seed pairs x 2 arms).

## Method
Row mass per D x C cell is end of flight's `option_table_0019.seed_terms`, executed from its own source up to its final reduction (as `composer-views-run-j/reduce_seed_views.py`).
Only the q = 1 and C2-unpowered totals, which this note does not report, are skipped (memory). Under H the row factor is an exact cell lookup on the surface;
a row outside the computed support has zero likelihood under H (module convention); its share of the flight-only mass is at most 1.3e-06 in any cell.
Seeds pooled by evidence within a stratum (ln(P_s/K_s) + seed scale); tension is the module's measure (`rerun_reference.tension`: ln S with the Handley-Lemos p, two-way 90 % overlap, mean shift) on the wide grid.
The joined V2 weights are end of flight's `joined_v2.py` main(), reproduced line by line from its own functions; seeds combined as `joined_v2_summary.py` does (medians; Z-weighted pools; ESS summed, never pooled).

## Checks
1. **Flight-only reproduction:** the pooled ln Z and family shares without H equal end of flight's `run-j/summary/table-0019-mixture.json` (D0 −7.5251, D2 −19.1209, D3 −28.5819, D4 −28.5126 production; A1/A2/B shares to 4 decimals); ESS agrees to 5e-5 relative.
2. **Joined V2 reproduction:** ln Z without H equals end of flight's `joined-s<k>.json` for seed pairs 1-21 (max |difference| 0.0e+00); pairs 22-23 have no end-of-flight summary yet.
3. **Builder:** amended `build_columns.py` writes byte-identical columns and SHA256SUMS to the previous version (both-burst seed 3).
4. **Columns:** every column file re-hashed at finalisation against the hash taken at write time (`finalize_runj.py`).
5. **Not computed under H:** at most 1.3e-06 of the flight-only mass in any cell (land and grid edge); no row is outside the grid.

## Reading
1. **Under H every D x C cell moves to 35.38-35.60 S, 92.20-92.62 E** (headline setting), 85-134 NM north-east of the flight-only PDF (flight-only means 36.72-36.96 S in the primary column). This is the same place as on run I (35.5-35.6 S, 92.0-92.4 E).
2. **The tension is moderate and is reported with the conditional.** Primary column: ln S -1.57 to -1.04, p 0.15-0.22; the flight-only PDF has only 27-39 % of its mass inside H's 90 % region. Over all 18 cells ln S is -1.58 to -0.18 (p 0.15-0.38). The narrower 90 % regions under H are partly a symptom of this tension, not only of precision.
3. **H does not separate the 00:19 treatments.** In the primary column ln E[L_H] is within -0.19 to +0.00 of D0′; the waypoints seed-to-seed SD of the same quantity is 0.33-0.57, so every difference is inside the Monte Carlo noise. H does not pick D3, D4 or D5 (Holland's H2 and H1 data and the offset variant).
4. **ESS gate (1,000, effective impacts under H):** D3 fails under every cause (headline both-burst set 615 / 972 / 621 for C1 / C2 silent / total); D4 x C2 silent fails (710); A1 fails under D3, D4 and D5 in every cause; A2 and B fail under D3; A2 fails under D2 x C2 silent and D4 x C2 silent. D0′, D1 and D2 pass in every cause; D4 and D5 pass in total. The full list is the last table. Production-only D3 (no both-burst set) is 570: the supplementary set adds little under H, because it targets the 00:19 data, not the Pléiades-compatible end states.
5. **Families under H (D0′):** B (planned descent) rises from 0.484 to 0.560, A2 falls from 0.343 to 0.289, A1 0.172 to 0.150: H prefers end states that reach further north-east along and inside the arc, which planned descents supply.
6. **Western residual on run J impacts (brief 8.2, replaces the declared-reach sweep):** under H and D0′, 12.4 % of the mass is ≥ 30 NM inside the 00:19 arc and 5.0 % ≥ 50 NM (flight-only 7.7 / 3.5 %); inside H's own 90 % region (the 8-9 Oct definition of the lobe) 8.0 % and 2.0 %. The 9 Oct values (4-5 % and about 2 %, on the 295.66 reference with a declared reach) are therefore of the right size at 50 NM and about 1.6-2 times larger at 30 NM on run J. The western mass comes from A2 and B, not A1 (A1 ≥ 30 NM inside: 3.9 %). With any 00:19 BTO (D1-D5) it falls to ≤ 4.2 % (≥ 30 NM, whole grid) and ≤ 1.2 % inside H's 90 % region: the 00:19:29 BTO, not the Pléiades data, controls the western residual. Run J reach: descents to impact are end of flight's (Boeing-calibrated glide, rapid descents to 40,000 ft/min); the column is the signed BTO-arc distance at impact (positive beyond the arc).
7. **Planned descents before 00:11 (joined V2), under H:** the B share under D0′ rises from a seed median of 0.204 to 0.313, and the pre-00:11 B share from 0.145 to 0.255. **Provisional:** B ESS under H is 1,320 summed over 23 seeds but only 28 in the poorest seed; under D1, D3 and D4 the summed B ESS is below the gate (GAP). D5 is not in end of flight's joined estimate.


### Primary: competing-causes total q = 1/3 (C2 silent), headline setting (ρ 0.25, two ocean models, GlobCurrent product-relative)

| D | cause | ESS under H (without H) | A1 / A2 / B ESS under H | mean under H | shift NM | ln S (p) | 90 % km² under H (without H) | PDF without H inside H 90 % | ln E[L_H] − D0′ (seed SD) |
|---|---|---|---|---|---|---|---|---|---|
| D0′ held out, transmission imposed | total q=1/3 (C2 silent) | 141,104 (1,946,710) | 56,354 / 46,717 / 64,026 | 35.44 S 92.20 E | 109 | -1.04 (0.22) | 63,129 (158,530) | 33 % | +0.00 (0.33) |
| D1 R600 BTO | total q=1/3 (C2 silent) | 191,410 (2,145,061) | 82,269 / 71,721 / 76,664 | 35.54 S 92.33 E | 125 | -1.30 (0.18) | 49,575 (113,459) | 33 % | -0.19 (0.38) |
| D2 R600 BTO + R600 BFO | total q=1/3 (C2 silent) | 9,953 (92,216) | 3,311 / 2,527 / 4,613 | 35.52 S 92.34 E | 116 | -1.23 (0.20) | 39,188 (93,612) | 34 % | -0.07 (0.34) |
| D3 R600 BTO + both BFOs (H2 data) | total q=1/3 (C2 silent) | 621 (6,348) **GAP** | 42 / 328 / 309 | 35.51 S 92.44 E | 134 | -1.13 (0.15) | 18,702 (37,660) | 27 % | -0.05 (0.43) |
| D4 R600 BTO + both BFOs, Holland transient bias (H1 data) | total q=1/3 (C2 silent) | 3,985 (44,422) | 354 / 1,517 / 3,526 | 35.48 S 92.41 E | 131 | -1.57 (0.15) | 22,772 (42,492) | 39 % | -0.11 (0.57) |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | total q=1/3 (C2 silent) | 2,517 (25,943) | 121 / 1,504 / 1,177 | 35.50 S 92.42 E | 128 | -1.28 (0.17) | 21,970 (45,583) | 31 % | -0.06 (0.40) |

### Beside it: GLORYS12 only, ρ 0.25, total q = 1/3 (C2 silent)

| D | cause | ESS under H (without H) | A1 / A2 / B ESS under H | mean under H | shift NM | ln S (p) | 90 % km² under H (without H) | PDF without H inside H 90 % | ln E[L_H] − D0′ (seed SD) |
|---|---|---|---|---|---|---|---|---|---|
| D0′ held out, transmission imposed | total q=1/3 (C2 silent) | 139,493 (1,946,710) | 53,342 / 47,495 / 63,909 | 35.44 S 92.25 E | 110 | -1.02 (0.23) | 56,633 (158,530) | 15 % | +0.00 (0.35) |
| D1 R600 BTO | total q=1/3 (C2 silent) | 183,631 (2,145,061) | 73,467 / 70,638 / 75,416 | 35.52 S 92.38 E | 127 | -1.29 (0.19) | 44,577 (113,459) | 14 % | -0.18 (0.40) |
| D2 R600 BTO + R600 BFO | total q=1/3 (C2 silent) | 9,645 (92,216) | 2,957 / 2,711 / 4,433 | 35.49 S 92.40 E | 119 | -1.22 (0.20) | 35,978 (93,612) | 17 % | -0.06 (0.36) |
| D3 R600 BTO + both BFOs (H2 data) | total q=1/3 (C2 silent) | 548 (6,348) **GAP** | 37 / 347 / 263 | 35.50 S 92.48 E | 136 | -1.14 (0.15) | 16,970 (37,660) | 10 % | -0.04 (0.45) |
| D4 R600 BTO + both BFOs, Holland transient bias (H1 data) | total q=1/3 (C2 silent) | 3,926 (44,422) | 315 / 1,570 / 3,759 | 35.45 S 92.47 E | 135 | -1.63 (0.15) | 21,250 (42,492) | 9 % | -0.12 (0.59) |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | total q=1/3 (C2 silent) | 2,537 (25,943) | 114 / 1,405 / 1,232 | 35.48 S 92.47 E | 131 | -1.31 (0.17) | 19,941 (45,583) | 9 % | -0.06 (0.41) |

### Each cause separately, headline setting

| D | cause | ESS under H (without H) | A1 / A2 / B ESS under H | mean under H | shift NM | ln S (p) | 90 % km² under H (without H) | PDF without H inside H 90 % | ln E[L_H] − D0′ (seed SD) |
|---|---|---|---|---|---|---|---|---|---|
| D0′ held out, transmission imposed | C1 | 137,850 (1,912,219) | 52,845 / 46,360 / 62,745 | 35.44 S 92.20 E | 109 | -1.05 (0.22) | 62,952 (156,976) | 33 % | -0.00 (0.33) |
| D0′ held out, transmission imposed | C2 silent | 420,157 (3,291,642) | 377,246 / 30,098 / 145,758 | 35.48 S 92.44 E | 85 | -0.18 (0.38) | 62,852 (303,446) | 20 % | +0.26 (0.33) |
| D1 R600 BTO | C1 | 186,985 (2,109,081) | 77,317 / 71,158 / 75,264 | 35.54 S 92.32 E | 125 | -1.32 (0.18) | 49,500 (112,465) | 33 % | -0.20 (0.38) |
| D1 R600 BTO | C2 silent | 543,826 (4,036,956) | 573,571 / 46,452 / 142,396 | 35.60 S 92.62 E | 107 | -0.32 (0.35) | 43,160 (205,955) | 18 % | +0.13 (0.40) |
| D2 R600 BTO + R600 BFO | C1 | 9,890 (91,868) | 3,245 / 2,524 / 4,599 | 35.52 S 92.34 E | 116 | -1.23 (0.19) | 39,214 (93,636) | 34 % | -0.07 (0.34) |
| D2 R600 BTO + R600 BFO | C2 silent | 8,473 (62,912) | 5,962 / 653 / 1,936 | 35.41 S 92.49 E | 97 | -0.86 (0.27) | 18,281 (51,114) | 31 % | +0.42 (0.35) |
| D3 R600 BTO + both BFOs (H2 data) | C1 | 615 (6,304) **GAP** | 42 / 326 / 306 | 35.51 S 92.44 E | 134 | -1.13 (0.15) | 18,702 (37,611) | 27 % | -0.05 (0.43) |
| D3 R600 BTO + both BFOs (H2 data) | C2 silent | 972 (5,932) **GAP** | 45 / 444 / 647 | 35.50 S 92.55 E | 126 | -0.86 (0.24) | 10,372 (25,545) | 14 % | +0.33 (0.52) |
| D4 R600 BTO + both BFOs, Holland transient bias (H1 data) | C1 | 3,920 (44,091) | 341 / 1,506 / 3,477 | 35.48 S 92.41 E | 131 | -1.58 (0.15) | 22,773 (42,364) | 39 % | -0.11 (0.57) |
| D4 R600 BTO + both BFOs, Holland transient bias (H1 data) | C2 silent | 710 (3,311) **GAP** | 155 / 383 / 3,206 | 35.38 S 92.48 E | 112 | -0.66 (0.27) | 13,258 (32,228) | 19 % | +0.48 (0.48) |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | C1 | 2,491 (25,776) | 120 / 1,493 / 1,163 | 35.50 S 92.42 E | 128 | -1.29 (0.17) | 21,995 (45,558) | 31 % | -0.07 (0.40) |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | C2 silent | 3,235 (18,834) | 176 / 1,215 / 1,931 | 35.48 S 92.53 E | 115 | -0.82 (0.26) | 12,232 (32,271) | 19 % | +0.37 (0.40) |

### Check: D3 and D4 with the production waypoints seeds only (no both-burst set), headline setting

| D | cause | ESS under H (without H) | A1 / A2 / B ESS under H | mean under H | shift NM | ln S (p) | 90 % km² under H (without H) | PDF without H inside H 90 % | ln E[L_H] − D0′ (seed SD) |
|---|---|---|---|---|---|---|---|---|---|
| D3 R600 BTO + both BFOs (H2 data) | C1 | 565 (4,678) **GAP** | 31 / 249 / 302 | 35.51 S 92.40 E | 127 | -1.06 (0.16) | 18,371 (39,010) | 27 % | -0.05 (0.43) |
| D3 R600 BTO + both BFOs (H2 data) | C2 silent | 682 (4,640) **GAP** | 35 / 360 / 402 | 35.49 S 92.55 E | 116 | -0.64 (0.26) | 10,523 (28,165) | 15 % | +0.38 (0.43) |
| D3 R600 BTO + both BFOs (H2 data) | total q=1/3 (C2 silent) | 570 (4,707) **GAP** | 31 / 251 / 306 | 35.51 S 92.41 E | 127 | -1.06 (0.16) | 18,396 (39,086) | 27 % | -0.04 (0.42) |
| D4 R600 BTO + both BFOs, Holland transient bias (H1 data) | C1 | 3,061 (21,062) | 264 / 1,233 / 2,817 | 35.49 S 92.39 E | 124 | -1.46 (0.16) | 23,220 (46,941) | 38 % | -0.11 (0.44) |
| D4 R600 BTO + both BFOs, Holland transient bias (H1 data) | C2 silent | 542 (4,407) **GAP** | 156 / 534 / 872 | 35.37 S 92.45 E | 102 | -0.25 (0.34) | 12,201 (34,689) | 18 % | +0.64 (0.47) |
| D4 R600 BTO + both BFOs, Holland transient bias (H1 data) | total q=1/3 (C2 silent) | 3,116 (21,216) | 277 / 1,243 / 2,855 | 35.49 S 92.39 E | 124 | -1.45 (0.16) | 23,222 (47,044) | 38 % | -0.10 (0.44) |

### Transport-error correlation ρ, total q = 1/3 (C2 silent), two ocean models

| D | ρ 0: mean, ESS, ln S | ρ 0.25: mean, ESS, ln S | ρ 0.5: mean, ESS, ln S |
|---|---|---|---|
| D0′ held out, transmission imposed | 35.39 S 92.25 E, 117,758, -1.02 | 35.44 S 92.20 E, 141,104, -1.04 | 35.49 S 92.15 E, 166,032, -1.03 |
| D1 R600 BTO | 35.48 S 92.39 E, 162,956, -1.29 | 35.54 S 92.33 E, 191,410, -1.30 | 35.60 S 92.26 E, 221,299, -1.29 |
| D2 R600 BTO + R600 BFO | 35.46 S 92.41 E, 8,670, -1.21 | 35.52 S 92.34 E, 9,953, -1.23 | 35.58 S 92.27 E, 11,318, -1.21 |
| D3 R600 BTO + both BFOs (H2 data) | 35.47 S 92.49 E, 568, -1.11 | 35.51 S 92.44 E, 621, -1.13 | 35.56 S 92.38 E, 679, -1.14 |
| D4 R600 BTO + both BFOs, Holland transient bias (H1 data) | 35.43 S 92.47 E, 3,501, -1.55 | 35.48 S 92.41 E, 3,985, -1.57 | 35.54 S 92.33 E, 4,519, -1.57 |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | 35.45 S 92.48 E, 2,232, -1.25 | 35.50 S 92.42 E, 2,517, -1.28 | 35.55 S 92.36 E, 2,847, -1.29 |

### Family shares, total q = 1/3 (C2 silent): without H → under H (headline setting)

| D | A1 | A2 | B | code 6 (deliberate onset, ditching attempt) |
|---|---|---|---|---|
| D0′ held out, transmission imposed | 0.172 → 0.150 | 0.343 → 0.289 | 0.484 → 0.560 | 0.001 → 0.001 |
| D1 R600 BTO | 0.199 → 0.180 | 0.346 → 0.289 | 0.454 → 0.530 | 0.001 → 0.001 |
| D2 R600 BTO + R600 BFO | 0.238 → 0.211 | 0.234 → 0.266 | 0.527 → 0.521 | 0.001 → 0.001 |
| D3 R600 BTO + both BFOs (H2 data) | 0.080 → 0.083 | 0.370 → 0.328 | 0.550 → 0.588 | 0.000 → 0.001 |
| D4 R600 BTO + both BFOs, Holland transient bias (H1 data) | 0.249 → 0.210 | 0.320 → 0.293 | 0.429 → 0.496 | 0.002 → 0.001 |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | 0.060 → 0.045 | 0.422 → 0.372 | 0.517 → 0.583 | 0.001 → 0.000 |

### Western residual (brief 8.2) on run J impacts, total q = 1/3 (C2 silent): share of mass at ≥ 30 / ≥ 50 NM inside the 00:19 arc (arc_distance_nm)

| D | without H: ≥ 30 / ≥ 50 NM | under H, whole grid: ≥ 30 / ≥ 50 NM | under H, inside H's 90 % region: ≥ 30 / ≥ 50 NM | same, west of 91.5 E | GLORYS12 only, inside H 90 %: ≥ 30 / ≥ 50 | A1 / A2 / B under H, share of family ≥ 30 NM | ESS under H |
|---|---|---|---|---|---|---|---|
| D0′ held out, transmission imposed | 7.7 / 3.5 % | 12.4 / 5.0 % | 8.0 / 2.0 % | 5.8 / 2.0 % | 7.0 / 1.3 % | 3.9 / 12.9 / 14.5 % | 141,104 |
| D1 R600 BTO | 2.9 / 1.0 % | 4.2 / 1.4 % | 1.2 / 0.0 % | 0.8 / 0.0 % | 1.1 / 0.0 % | 0.0 / 6.5 / 4.3 % | 191,410 |
| D2 R600 BTO + R600 BFO | 2.3 / 0.6 % | 3.2 / 0.8 % | 1.1 / 0.1 % | 0.6 / 0.1 % | 1.0 / 0.0 % | 0.0 / 5.0 / 3.6 % | 9,953 |
| D3 R600 BTO + both BFOs (H2 data) | 0.8 / 0.0 % | 0.6 / 0.0 % | 0.2 / 0.0 % | 0.1 / 0.0 % | 0.1 / 0.0 % | 0.0 / 0.7 / 0.6 % | 621 **GAP** |
| D4 R600 BTO + both BFOs, Holland transient bias (H1 data) | 0.6 / 0.1 % | 0.7 / 0.1 % | 0.2 / 0.0 % | 0.1 / 0.0 % | 0.2 / 0.0 % | 0.0 / 0.9 / 0.8 % | 3,985 |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | 0.6 / 0.0 % | 1.0 / 0.0 % | 0.5 / 0.0 % | 0.1 / 0.0 % | 0.6 / 0.0 % | 0.0 / 0.7 / 1.3 % | 2,517 |

### Planned descents before 00:11 (end of flight's joined V2, run J waypoints, seed pairs 1-23), total q = 1/3 (C2 silent), headline setting

| D | B share, median of seeds (range): without H → under H | B share pooled (Z-weighted): without H → under H | pre-00:11 B, median: without H → under H | B ESS under H, sum (min per seed) | all-family ESS under H, sum | mean under H | ln E[L_H] − its D0′, seed median (SD) |
|---|---|---|---|---|---|---|---|
| D0′ held out, transmission imposed | 0.204 (0.076-0.316) → 0.313 (0.204-0.434) | 0.160 → 0.315 | 0.145 → 0.255 | 1,320 (28) | 11,673 | 35.33 S 92.25 E | +0.00 (0.41) |
| D1 R600 BTO | 0.108 (0.040-0.185) → 0.220 (0.115-0.317) | 0.084 → 0.210 | 0.047 → 0.149 | 986 (13) **GAP** | 19,500 | 35.51 S 92.29 E | -0.19 (0.48) |
| D2 R600 BTO + R600 BFO | 0.098 (0.041-0.175) → 0.104 (0.064-0.367) | 0.079 → 0.112 | 0.000 → 0.000 | 1,375 (1) | 3,278 | 35.50 S 92.25 E | -0.08 (0.46) |
| D3 R600 BTO + both BFOs (H2 data) | 0.061 (0.021-0.113) → 0.064 (0.025-0.214) | 0.049 → 0.070 | 0.000 → 0.000 | 263 (2) **GAP** | 415 | 35.54 S 92.33 E | -0.58 (0.64) |
| D4 R600 BTO + both BFOs, Holland transient bias (H1 data) | 0.049 (0.017-0.098) → 0.060 (0.036-0.203) | 0.041 → 0.068 | 0.000 → 0.000 | 700 (2) **GAP** | 1,186 | 35.50 S 92.28 E | -0.24 (0.55) |

### Cells and families below the 1,000 gate under H (headline setting)

D2 x C2 silent, A2 (653); D3 x C1 (615); D3 x C1, A1 (42); D3 x C1, A2 (326); D3 x C1, B (306); D3 x C2 silent (972); D3 x C2 silent, A1 (45); D3 x C2 silent, A2 (444); D3 x C2 silent, B (647); D3 x total q=1/3 (C2 silent) (621); D3 x total q=1/3 (C2 silent), A1 (42); D3 x total q=1/3 (C2 silent), A2 (328); D3 x total q=1/3 (C2 silent), B (309); D4 x C1, A1 (341); D4 x C2 silent (710); D4 x C2 silent, A1 (155); D4 x C2 silent, A2 (383); D4 x total q=1/3 (C2 silent), A1 (354); D5 x C1, A1 (120); D5 x C2 silent, A1 (176); D5 x total q=1/3 (C2 silent), A1 (121).


## Close-ups (colour and seabed, D0′-D5, total q = 1/3, C2 silent, before any seabed search)
`closeups/closeup-runj-D<d>-{colour,seabed}.{png,pdf}`; statistics in `closeups/closeup-runj-stats.csv`. D3 is labelled NOT ESTIMABLE on its charts (D4 and D5 pass in total; their A1 is a GAP and is stated in each footnote).
Flight-only maps (0.05 deg, normalised) are in the exchange: `mh370-exchange/pleiades/run-j/maps/map-D<d>.npz` (pre = post: no search).

## COVERAGE
- **(a) Feasible set, (b) model reach:** end of flight's run J README and COVERAGE apply unchanged; this module adds no sampling. Carried gaps from there: stepped descent shapes not eligible for push-over; INTERIM pitch-down; thin northern detail north of 33 S (few distinct 00:11 parents; core run J prediction 5; the northern supplement is approved and not yet run).
- **(c) Proposal coverage under H:** effective impacts per D x C cell and per family A1 / A2 / B are in the tables. **GAPs (below 1,000 under H, headline setting):** see the last table; in short D3 (all causes, all families), D4 x C2 silent, A1 under D3-D5, A2 under D2 x C2 silent and D4 x C2 silent, B under D3; joined V2 B under D1, D3, D4.
- Why: end of flight's proposal targets the 00:19 data, not the Pléiades-compatible end states near 35.5 S 92.3 E; under H the importance weights concentrate on few rows (ESS falls by about 10-14x in every cell). Fix (end of flight's to choose): a defensive-mixture component aimed at those end states with exact re-weighting (the L_H surface is available as a proposal density), or more seeds; the run J northern supplement may help D3-D5 because H mass lies north of the flight-only peak.
- Declared regions: the conditional under H lies 34-37 S, inside the surfaces' computed support (45-5 S, 78-115 E); not computed ≤ 1.3e-06.
- Parameter bounds (sources as the brief): windage 0-5 % U10; transport error about 95-120 km per component at 15 d (drifter-calibrated); ρ 0.25 headline (measured 0.07-0.41), 0 / 0.5 beside; GlobCurrent product-relative windage offset 0.60-0.75 % U10 (drift audit F1).
- Every 00:19 option (D0′-D5) and every family (A1, A2, B) is estimated from the same sample set; those below the gate are reported, not dropped.

## Deviations and limits (tonight)
- **Columns written for run-j-waypoints (24 seeds, 7.9 GB) and the both-burst set (8 seeds, 0.42 GB, written before the 01:13Z alert) only.** Free, descent-climb, repro-radar and joined-V2 columns are **deferred for disk** (coordination DISK ALERT 01:13Z); they carry core P 0.0018 together. Their rows are fully SCORED (the table pools all four families); only the per-impact exchange columns are not written. Rebuild later with `build_columns.py <eof run root> <surfaces> <out> run-j-free ...` (about 0.18 GB per seed).
- Joined V2: 23 of 24 seed pairs (seed 24 not complete at run time).
- `seed_terms` executed with the q = 1 and C2-unpowered totals skipped (memory); the cells reported are arithmetically unchanged (check 1).
- No seeds were dropped or subsampled; no searched-areas term; no new transport.
- Wall time: scoring 00:53-01:22Z (2 workers on waypoints, 3 on the rest, after a restart at 00:59Z to cut memory: four waypoints workers pushed the Mac into about 9 GiB of new swap); aggregation, joined V2 and close-ups 01:22-01:30Z.
