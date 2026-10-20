# End of flight on the run J northern supplement, combined with run J production by rule B (19 Oct 2026)

End of Flight Module, overnight order A (`threads/work-orders/overnight-2026-10-19.md`, Pete approved 19 Oct ~03:45Z; disk cap
40 GB and pause floor 5 GB per coordination 04:15Z). Core run J convergence is a PASS by project ruling (16 Oct 2026); this pass adds
northern detail and does not reopen it. Waypoints stratum only (core prior share 0.998).

**Caveat (verbatim).** The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all three rounds.
Impact energy, attitude, flight-path angle and energy-transfer duration from this arm are a labelled sensitivity on uncalibrated
dynamics, not a physical prediction.

## Declared reductions and substitutions (read first)

1. **Every 2nd supplement row (k = 2), not all rows.** Measured on seed 1001: 1.42 GB of compact output per seed at k = 2, so all
   rows would need 45.5 GB against the 40 GB cap. Fixed subset: rows 0, 2, 4, ... of each `handoff-m0011-supplement` (50,000 or
   50,001 of 100,000 or 100,001 rows per seed; 800,004 rows in all). Rule B multiplies u2 by k = 2. The other half of the rows is
   not flown.
2. **Config tree at a517deeb, not branch head.** The production pass ran from that tree with binary `mh370-eof-rj1` (sha256
   19031f41748ecb0c, built from 16f2eb1); later overlays (e.g. new fields in `smoke/terminal.toml`) would not parse in that binary.
   Check: the merged configuration of supplement seed 1001 is identical to run J production seed 1 except `seeds`, and all 48 input
   files listed in `results/run-j/MANIFEST-waypoints.txt` match their sha256 (including `internal-v1.json` and the weather grids).
   The supplement's own core overlays (`size-north`, `supplement`) set only filter sizes, seeds and the supplement flag, which the
   terminal stage does not read; the run J waypoints chain was used.
3. **D5 is scored with a 4.3177 Hz 00:19 BFO error** (run J's observation table), not the 7 Hz of the base table that
   `option_table_0019.py` uses (coordination 19 Oct, calibration-smoke fault F1). Production-alone D5 therefore reads
   ln Z −29.186 here against −29.169 in `results/eof-run-j-waypoints-oct16`; D0'–D4 reproduce that table to 0.001 nat and to the
   third decimal of every family share.
   `smoke/option_table_0019.py` itself is now fixed the same way (`run_obs` reads the run's own `[inputs] observations`).
4. **Extra descents (step 4) only for the both-burst treatments D2–D5 and only for supplement paths north of 35.5 S at 00:11**
   (93 % of the k = 2 subset; 742,244 paths), 256 more per path, Poisson-thinned to 250,000 rows per group. D0' and D1 use the first
   64 descents only.
5. **Optional step 5 (16 new 22:41 hand-offs) not run.** The joined-V2 recipe writes about 4.9 GB per seed (39 GB for 8 run J seeds
   in `run-j-joined-v2/J2241`), so 16 seeds need about 78 GB: beyond the cap. Planned descent before 00:11 under D2/D4 is therefore
   **not assessed at this depth** on the supplement; a thinned J2241 pass (both-burst cells only, about 0.5 GB per seed) is the costed fix.
6. **Run outside the heavy lock**, 12 threads (11 during the A1-branch add-on, with 1 for analysis): Pete retired the Mac heavy-lock
   requirement on 16 Oct (bc6c54cd) and the order allots order A 12 threads.
7. The driver deletes its own transient full impact files after the compact copy is verified (the production recipe); these were
   scratch files this run created in the session workspace. Nothing else was deleted.
8. `validate/seed-1` (a possible 17th supplement replicate) was not used.

## 1. What was run

| Pass | Paths (00:11 hand-off rows) | Descents per path | Rows | Output (exchange `end-of-flight/run-j-supplement/`) | Time |
|---|---|---|---|---|---|
| A, production recipe | 16 seeds x every 2nd row = 800,004 | 64 | 51.2M | `north-k2/` 16 x 1.42 GB, verified compact | 04:11-05:30Z |
| A4, extra descents (D2-D5) | the same paths north of 35.5 S, 4 groups per seed | +256 (terminal seeds 20010-20163) | 190M, thinned to 16.0M | `north-k2-xd256/` 64 x 0.11 GB | 05:31-09:27Z |
| add-on, A1-branch conditional | the same 800,004 paths | 64, D3-aimed selection K = 8 | thinned to 0.5M per seed | `north-k2-a1branch/` | 09:41Z- (section 7) |

Recipe of pass A = `run_j_production.sh` for run-j-waypoints exactly (round-3 laws, bank limit U[52, 90] deg, dive p = 0.5,
C2-silent aim, children 16 x 4, the same scored columns). Pass A4 is that recipe with `full/children-64.toml`. Each extra group
has its own terminal seed, because the descent streams are keyed by (seed, purpose, child, row): reusing the hand-off seed would
repeat the first 64 descents (see the correction in section 6). Pooling: for every selected path, the first pass's rows carry
64/320 and the extra rows 256/320 of the path's mass; the selection depends only on the 00:11 state, so the pool is exact.
Drivers: `engine/hypotheses/end-of-flight/full/run_j_supplement.sh`, `run_j_supplement_xd.sh`, `run_j_supplement_a1.sh`;
analysis: `smoke/supplement_combine.py` (per-seed parts), `supplement_summary.py`, `supplement_tables.py`, `supplement_figures.py`,
`supplement_reduced.py`; hand-off subsets: `smoke/handoff_stride.py`, `smoke/handoff_select.py`.

**Rule B, as applied** (core `results/run-j-supplement/README.md` section 5). Row mass under treatment d =
u_t x beta_t(lat_0011) x exp(survival + D_d + log-on total), with u1 = w/24 (run J rows), u2 = 2 w/16 (supplement rows), w the
stored impact weight (hand-off weight x exp(log_correction) x within-path weight), n1 = 2,399,999 and n2 = 800,004 hand-off rows,
r = r_hat(00:11 latitude) from `r_hat.csv` (0.1 outside its bins). Two-factor totals, q = 1/3, 'other cause' silent, as in
`option_table_0019.py`. Bootstrap: 2,000 draws, the 24 production and 16 supplement seeds resampled separately with replacement.

## 2. Result in one paragraph

Rule B reproduces production in every check: ln Z moves by 0.003-0.008 nat, family shares by at most 0.002, the 5 / 50 / 95 %
impact latitudes by at most 0.1 deg (one 0.1 deg bin), and 29 of the 30 northern band masses (6 treatments x 35-30, 30-25,
25-20 S, north of 33 S, north of 30 S) lie inside production's own 95 % seed-bootstrap interval. The exception is D4 in 25-20 S:
0.0037 [0.0026, 0.0050] combined against 0.0021 [0.0015, 0.0029] from production alone, Production rests on 87 distinct states there and
the combined value on 272: **this band mass is unconverged in both**, and is reported as not assessed at adequate depth. The supplement raises the northern effective sample sizes by 1.4-19 times (D0' 30-25 S: 3,459 -> 19,201 distinct
00:11 states; D3 30-25 S: 83 -> 1,494). After the extra descents, D0', D1, D2 are above 1,000 in all three northern bands; D4 and D5 are
above 1,000 in 35-30 and 30-25 S; **D3 35-30 S (855), D3 25-20 S (281), D4 25-20 S (272) and D5 25-20 S (890) stay short**. By
family, A1 (cruise to fuel exhaustion then no control) under D3, D4 and D5 stays short in every northern band (23-310); the A1-branch
add-on (section 7) addresses that. The seed-bootstrap intervals of the northern masses do not narrow when the supplement is added
(D0' north of 33 S: 0.0321 [0.0271, 0.0381] -> 0.0345 [0.0285, 0.0412]), as core predicted: the northern mass rests on the mode
probabilities of the 16 supplement replicates, so more end-of-flight sampling cannot narrow it.

## 3. Tables

**Band ESS by impact latitude: rows / parents / distinct 00:11 states** (target 1,000; production alone -> + supplement, 64 descents -> + extra descents)

| treatment | 35-30 S | 30-25 S | 25-20 S |
|---|---|---|---|
| D0' 00:19 data not used | 108.8k/30.0k/30.0k -> 154.1k/46.2k/45.8k | 15.7k/3,459/3,459 -> 94.4k/23.4k/19.2k | 6,443/1,451/1,451 -> 29.3k/7,149/5,754 |
| D1 R600 BTO | 125.7k/40.9k/40.9k -> 171.7k/58.5k/57.7k | 20.1k/5,549/5,549 -> 128.1k/36.6k/27.5k | 6,596/2,273/2,273 -> 38.7k/10.7k/9,694 |
| D2 R600 BTO + BFO | 6,010/5,180/5,180 -> 9,317/7,959/7,940 -> **12.6k/10.4k/10.4k** | 1,075/901/901 -> 8,909/7,233/6,681 -> **25.8k/15.6k/13.2k** | 184/167/167 -> 2,111/1,841/1,796 -> **4,469/3,365/3,199** |
| D3 both BFOs as recorded | 307/305/305 -> 598/593/593 -> **869/856/855** | 83/83/83 -> 483/480/479 -> **1,546/1,509/1,494** | 22/22/22 -> 152/150/149 -> **291/282/281** |
| D4 both BFOs, Holland transient bias added | 367/363/363 -> 1,840/1,772/1,767 -> **2,426/2,307/2,303** | 166/154/154 -> 641/623/618 -> **1,513/1,377/1,314** | 104/87/87 -> 108/101/101 -> **351/274/272** |
| D5 R600 + R1200 BFO with start-up offset | 548/542/542 -> 1,004/993/993 -> **1,213/1,194/1,193** | 256/245/245 -> 1,006/955/948 -> **3,821/3,511/3,357** | 63/63/63 -> 342/339/337 -> **949/904/890** |

**Band ESS by 00:11 latitude: rows / parents / distinct 00:11 states** (target 1,000; production alone -> + supplement, 64 descents -> + extra descents)

| treatment | 35-30 S | 30-25 S | 25-20 S |
|---|---|---|---|
| D0' 00:19 data not used | 212.2k/53.4k/53.4k -> 269.0k/71.2k/70.9k | 18.7k/3,859/3,859 -> 111.4k/23.5k/20.0k | 3,468/693/693 -> 18.6k/4,072/3,089 |
| D1 R600 BTO | 268.2k/77.9k/77.9k -> 329.7k/97.2k/96.7k | 23.6k/6,129/6,129 -> 133.4k/28.9k/24.9k | 3,369/1,111/1,111 -> 24.6k/6,329/5,615 |
| D2 R600 BTO + BFO | 12.4k/10.5k/10.5k -> 16.2k/13.7k/13.7k -> **19.5k/16.0k/16.0k** | 1,298/1,062/1,062 -> 7,470/4,625/4,481 -> **26.2k/12.6k/11.5k** | 90/84/84 -> 1,555/1,351/1,305 -> **3,527/2,578/2,398** |
| D3 both BFOs as recorded | 652/646/646 -> 875/868/868 -> **996/985/985** | 96/96/96 -> 477/459/458 -> **1,665/1,588/1,578** | 11/11/11 -> 99/98/98 -> **257/246/244** |
| D4 both BFOs, Holland transient bias added | 1,336/1,309/1,309 -> 4,877/4,600/4,592 -> **5,883/5,489/5,484** | 200/183/183 -> 648/617/614 -> **1,972/1,697/1,639** | 69/66/66 -> 63/59/59 -> **221/183/182** |
| D5 R600 + R1200 BFO with start-up offset | 1,658/1,629/1,629 -> 2,543/2,496/2,496 -> **2,940/2,868/2,867** | 290/279/279 -> 882/833/830 -> **4,454/3,898/3,789** | 36/36/36 -> 358/352/347 -> **735/688/670** |

**Family ESS by impact band (distinct 00:11 states), final combined set** (A1 = cruise to fuel exhaustion then no control; A2 = cruise to fuel exhaustion then controlled descent; B = planned descent begun before fuel exhaustion)

| treatment | 35-30 S A1 / A2 / B | 30-25 S A1 / A2 / B | 25-20 S A1 / A2 / B |
|---|---|---|---|
| D0' 00:19 data not used | 10.6k / 17.2k / 45.3k | 4,552 / 8,259 / 22.2k | 1,206 / 2,205 / 7,265 |
| D1 R600 BTO | 16.7k / 25.2k / 45.5k | 7,030 / 13.0k / 28.5k | 2,025 / 4,027 / 10.2k |
| D2 R600 BTO + BFO | 2,746 / 4,694 / 4,586 | 1,843 / 3,893 / 10.6k | 685 / 1,576 / 1,745 |
| D3 both BFOs as recorded | 23 / 687 / 514 | 89 / 769 / 698 | 35 / 192 / 132 |
| D4 both BFOs, Holland transient bias added | 251 / 1,283 / 3,459 | 310 / 1,242 / 1,697 | 60 / 378 / 743 |
| D5 R600 + R1200 BFO with start-up offset | 165 / 1,497 / 516 | 151 / 2,312 / 1,494 | 32 / 510 / 440 |

**P5, prediction by prediction** (impact band; distinct-state ESS, the most conservative measure; rows ESS in brackets)

| prediction | first pass (64 descents) | with extra descents | verdict (first pass, as P5 was stated) | verdict with extra descents |
|---|---|---|---|---|
| D2 35-30 S: >= 1,000 | 7,940 (9,317) | 10,356 (12,614) | inside | inside (>= 1,000: yes) |
| D2 30-25 S: >= 1,000 | 6,681 (8,909) | 13,217 (25,763) | inside | inside (>= 1,000: yes) |
| D2 25-20 S: >= 1,000 | 1,796 (2,111) | 3,199 (4,469) | inside | inside (>= 1,000: yes) |
| D4 30-25 S: 0.8k-2.5k | 618 (641) | 1,314 (1,513) | below | inside (>= 1,000: yes) |
| D4 35-30 S: 0.6k-1.5k | 1,767 (1,840) | 2,303 (2,426) | above | above (>= 1,000: yes) |
| D3 35-30 S: 0.5k-1.5k | 593 (598) | 855 (869) | inside | inside (>= 1,000: no) |
| D3 30-25 S: 0.5k-1.5k | 479 (483) | 1,494 (1,546) | below | inside (>= 1,000: yes) |

**Band masses (impact latitude), production alone vs combined, with 95 % seed-bootstrap intervals**

| treatment | 35-30 S | 30-25 S | 25-20 S | north of 33 S | north of 30 S |
|---|---|---|---|---|---|
| D0' 00:19 data not used | 0.0925 [0.0794, 0.1077] -> 0.0955 [0.0825, 0.1097] | 0.0131 [0.0113, 0.0153] -> 0.0127 [0.0107, 0.0150] | 0.0025 [0.0020, 0.0031] -> 0.0030 [0.0025, 0.0035] | 0.0321 [0.0271, 0.0381] -> 0.0345 [0.0285, 0.0412] | 0.0157 [0.0134, 0.0186] -> 0.0157 [0.0133, 0.0186] |
| D1 R600 BTO | 0.0597 [0.0500, 0.0707] -> 0.0616 [0.0520, 0.0726] | 0.0085 [0.0073, 0.0102] -> 0.0084 [0.0069, 0.0102] | 0.0022 [0.0017, 0.0027] -> 0.0025 [0.0020, 0.0030] | 0.0184 [0.0150, 0.0224] -> 0.0205 [0.0163, 0.0256] | 0.0107 [0.0091, 0.0129] -> 0.0109 [0.0090, 0.0131] |
| D2 R600 BTO + BFO | 0.0680 [0.0572, 0.0805] -> 0.0693 [0.0594, 0.0804] | 0.0113 [0.0097, 0.0134] -> 0.0108 [0.0091, 0.0129] | 0.0034 [0.0028, 0.0041] -> 0.0036 [0.0031, 0.0042] | 0.0235 [0.0193, 0.0286] -> 0.0252 [0.0202, 0.0307] | 0.0148 [0.0128, 0.0172] -> 0.0145 [0.0124, 0.0170] |
| D3 both BFOs as recorded | 0.0638 [0.0514, 0.0776] -> 0.0639 [0.0535, 0.0745] | 0.0100 [0.0077, 0.0124] -> 0.0088 [0.0073, 0.0105] | 0.0020 [0.0013, 0.0030] -> 0.0027 [0.0022, 0.0034] | 0.0213 [0.0163, 0.0272] -> 0.0218 [0.0174, 0.0269] | 0.0120 [0.0094, 0.0149] -> 0.0115 [0.0096, 0.0139] |
| D4 both BFOs, Holland transient bias added | 0.0649 [0.0528, 0.0796] -> 0.0657 [0.0541, 0.0794] | 0.0122 [0.0098, 0.0156] -> 0.0122 [0.0095, 0.0155] | 0.0021 [0.0015, 0.0029] -> 0.0037 [0.0026, 0.0050] | 0.0253 [0.0191, 0.0336] -> 0.0276 [0.0215, 0.0353] | 0.0144 [0.0117, 0.0183] -> 0.0159 [0.0123, 0.0205] |
| D5 R600 + R1200 BFO with start-up offset | 0.0668 [0.0553, 0.0795] -> 0.0671 [0.0562, 0.0787] | 0.0092 [0.0078, 0.0112] -> 0.0090 [0.0075, 0.0110] | 0.0022 [0.0016, 0.0029] -> 0.0026 [0.0022, 0.0031] | 0.0202 [0.0161, 0.0251] -> 0.0219 [0.0173, 0.0270] | 0.0115 [0.0098, 0.0137] -> 0.0116 [0.0098, 0.0140] |

**Whole-posterior summaries, production alone -> combined**

| treatment | ln Z | A1 / A2 / B | impact latitude 5 / 50 / 95 % | 00:11 latitude 50 % |
|---|---|---|---|---|
| D0' 00:19 data not used | -7.525 -> -7.528 | 0.172 / 0.343 / 0.484 -> 0.171 / 0.342 / 0.486 | -38.45 / -37.15 / -33.85 -> -38.45 / -37.15 / -33.75 | -36.15 -> -36.15 |
| D1 R600 BTO | -12.935 -> -12.940 | 0.199 / 0.346 / 0.454 -> 0.198 / 0.346 / 0.455 | -38.45 / -37.25 / -34.55 -> -38.45 / -37.25 / -34.55 | -36.15 -> -36.15 |
| D2 R600 BTO + BFO | -19.121 -> -19.126 | 0.238 / 0.234 / 0.527 -> 0.237 / 0.233 / 0.528 | -38.15 / -37.15 / -34.35 -> -38.15 / -37.15 / -34.35 | -36.15 -> -36.15 |
| D3 both BFOs as recorded | -28.582 -> -28.590 | 0.095 / 0.405 / 0.499 -> 0.094 / 0.407 / 0.498 | -38.05 / -37.25 / -34.45 -> -38.05 / -37.25 / -34.45 | -36.15 -> -36.15 |
| D4 both BFOs, Holland transient bias added | -28.513 -> -28.520 | 0.250 / 0.349 / 0.400 -> 0.248 / 0.350 / 0.401 | -37.95 / -37.25 / -34.35 -> -37.95 / -37.25 / -34.35 | -36.15 -> -36.15 |
| D5 R600 + R1200 BFO with start-up offset | -29.186 -> -29.190 | 0.059 / 0.418 / 0.522 -> 0.058 / 0.418 / 0.524 | -37.95 / -37.25 / -34.45 -> -38.05 / -37.25 / -34.45 | -36.15 -> -36.15 |

## 4. Reading of P5 and of step 4

1. **D2 >= 1,000 in all three bands: confirmed** already with the first 64 descents (7,940 / 6,681 / 1,796 distinct states).
2. **D4.** 35-30 S came out above core's range (1,767 at 64 descents against 0.6k-1.5k); 30-25 S came out below it (618 against
   0.8k-2.5k). With the extra descents 30-25 S reaches 1,314.
3. **D3.** 35-30 S was inside the range (593); 30-25 S was below it (479). With the extra descents: 855 and 1,494.
4. **"Linear in descents" holds on average but not path by path.** Same-path test on extra group 0 (about 11,600 paths per seed x 16): four
   times the descents gave x1.8-x4.9 the rows ESS for D2, D4 and D5 in most bands, but x0.6-x2.4 for D3 and x1.0 for D4 in 30-25 S.
   With about 30-260 effective rows in those cells the ESS is itself noisy, and a few heavy descents dominate. Over all four groups the
   pooled gain was close to linear for D3 and D4 in 30-25 S (x3.1 and x2.1 over the first pass) and much less in 35-30 S (x1.4, x1.3),
   where the production paths carry a large part of the weight (beta1 = 0.75 at r = 1, near 34 S at 00:11) and received no extra descents.
5. **Remaining shortfall (distinct 00:11 states, impact bands, against 1,000):** D3 35-30 S 855 (-145), D3 25-20 S 281 (-719), D4
   25-20 S 272 (-728), D5 25-20 S 890 (-110). By family: A1 under D3/D4/D5 23-310 in every northern band; A2 and B under D3 132-769;
   D4 A1 251-310; D5 A1 32-165. **Fix, costed:** 25-20 S is limited by the paths there (supplement 14 % of rows in 25.5-21 S at
   00:11); flying the other half of the supplement rows (k = 1) doubles those paths at about 23 GB and 1.3 h (first pass) plus about
   7 GB and 4 h for their extra descents; extra descents on the 24 production seeds' paths north of 35.5 S at 00:11 (706,180
   paths, 29 % of production rows) would help 35-30 S at about 7 GB thinned and about 4 h at 12 threads (tonight's rate).
   Neither was in tonight's cap.

## 5. Reduced impact table for downstream modules

`mh370-exchange/end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz` (+ `.json`): 1,781,905 rows, 0.25 GB. One unbiased
Horvitz-Thompson thinning of every row of all three passes (production, supplement first pass, extra descents), inclusion
pi = min(1, 150,000 x max_d m_d / Z_{d, band}) per 5 deg impact band, so each band keeps its effective rows. Columns: technique,
seed, hand-off row (original numbering), family4_code, 00:11 latitude, impact position, time, velocity, flight-path angle, mass,
impact heading / bank / energy, breakup probabilities, debris class, bank limit, push-over flag, and **ln weight per treatment**:
`lnw:comb/D0..D5` (rule B, normalised; sums 0.997-1.001) and `lnw:alone/D0..D5` (production alone; supplement rows -inf).
Check against the full set: every band mass within 0.0004; band rows ESS kept for D2-D5 (e.g. D3 35-30 / 30-25 / 25-20 S:
868 / 1,544 / 291 against 869 / 1,546 / 291); D0' and D1 keep 28k-114k per northern band (of 29k-172k). A downstream module
scores its likelihood per row and multiplies `exp(lnw:comb/<d>)`; no further combination step is needed.
**Not in it:** the A1-branch rows (a conditional pass; use the stratified estimator of `results/eof-a1-branch-oct18`).

## 6. Correction to an earlier note (17 Oct both-burst supplementary pass)

`results/eof-run-j-waypoints-oct16` section 3b called the children-64 pass and production "independent sets of descent draws". They
are not fully independent: the pass reused production's terminal seeds 1-8 and the descent streams are keyed by (seed, purpose,
child, row), so its children 0-15 repeat production's descents. Measured on seed 1 (paths 0-1,999): 3,733 of 14,949 rows (0.250)
are identical to a production row. The pass is still unbiased; only the "two independent passes agree" check is overstated (a
quarter of the draws are shared). Tonight's passes use their own terminal seeds (20010-20163, 30001-30016). The 18 Oct A1-branch
pass also reused seeds 1-8, under a conditioned prior; its overlap with production was not measured.

## 7. Add-on: A1-branch conditional pass on the supplement paths (coordination request 19 Oct ~04:20Z)

Recipe = the 18 Oct A1-branch pass exactly (`results/eof-a1-branch-oct18`: production recipe + `smoke/score-select-0019-raw.toml`
+ `smoke/a1-branch.toml`, i.e. onset flame-out-associated, no intervention, D3-aimed scored selection K = 8); merged config identical to
that pass's seed 1 except `seeds`. Paths: the same k = 2 supplement subset (800,004). Terminal seeds 30001-30016. Thinned to 0.5M rows
per seed (cells none, R600, both raw, both start-up offset). 09:41-11:14Z, 11 threads. Combined with the 18 Oct branch pass (run J
seeds 1-8, n1 = 799,999 rows, u1 = w/8) by rule B. Estimator: Z(d, branch, band) = Z(D0') P_D0'(branch) E_D0'[L_d 1_band | branch],
P_D0'(branch) = 0.0935 (production, 24 seeds; the supplement moves D0' family shares by at most 0.001). Check: the 8-seed branch
pass alone reproduces the 18 Oct ln E[L_d | branch] (D2 -11.299, D3 -21.151, D4 -20.210; D5 -22.214 with the 4.3177 Hz error).
`a1-branch.json`.

**A1 (flame-out, no-intervention branch) by impact band: branch share of Z(d) / ESS rows / paths / distinct 00:11 states;
18 Oct branch pass alone -> + supplement branch pass.**

| treatment | 35-30 S | 30-25 S | 25-20 S | branch share of Z(d) |
|---|---|---|---|---|
| D0' 00:19 data not used | 0.0076, 10,958/2,283/2,283 -> 0.0084, 27,092/5,845/5,818 | 0.0011, 1,345/286/286 -> 0.0011, 16,250/4,709/3,872 | 0.0002, 287/39/39 -> 0.0003, 4,382/1,280/1,040 | 0.0935 |
| D2 R600 BTO + BFO | 0.0076, 924/650/650 -> 0.0082, 2,245/1,574/1,570 | 0.0006, 147/85/85 -> 0.0008, 1,425/1,088/912 | 0.0001, 64/26/26 -> 0.0002, 686/478/468 | 0.1260 -> 0.1252 |
| D3 both BFOs as recorded | 0.0048, 335/320/320 -> 0.0052, 843/770/**768** | 0.0005, 32/32/32 -> 0.0005, 396/366/**360** | 0.0001, 7/6/6 -> 0.0002, 121/111/**111** | 0.0856 -> 0.0847 |
| D4 both BFOs, Holland transient bias added | 0.0127, 1,361/717/717 -> 0.0147, 3,290/1,949/**1,908** | 0.0035, 54/39/39 -> 0.0039, 1,594/924/**745** | 0.0006, 35/20/20 -> 0.0009, 501/298/**294** | 0.2042 -> 0.2016 |
| D5 R600 + R1200 BFO with start-up offset | 0.0032, 94/87/87 -> 0.0032, 684/636/**636** | 0.0003, 37/37/37 -> 0.0004, 211/208/**200** | 0.0000, 10/10/10 -> 0.0001, 43/43/**43** | 0.0538 -> 0.0533 |

**Reading.**
1. Under D3-D5 the supplement branch pass raises A1's northern distinct-state ESS by 2.4-19 times. **D4 x A1 in 35-30 S now meets 1,000
   (1,908)**, where Pléiades places A1 under H (median 35.3 S). D3 x A1 35-30 S (768) and D5 x A1 35-30 S (636) pass the 500 figure
   but not 1,000; every A1 cell in 30-25 and 25-20 S under D3-D5 stays below 1,000 (43-745).
2. The branch shares and ln E[L_d | branch] are unchanged within 0.013 nat: the supplement improves the northern shape, not the A1 share.
3. Under D3 and D5, rows ESS is about paths ESS in the north: one descent per path dominates. The branch is limited by northern paths, as Pléiades
   found; more descents per path will help little. The next step is the other half of the supplement rows under the branch recipe
   (k = 1: about 1.7 h and 3.5 GB thinned) or an H-aimed defensive component (Pléiades request 2).
4. For the Pléiades module: these supplement branch rows are at `north-k2-a1branch/seed-*` (compact, thinned; `handoff-subset.npy`
   and `stride.json` give the 00:11 path), to be combined with `run-j-a1branch/` by rule B with u1 = w/8, n1 = 799,999, n2 = 800,004,
   u2 = 2 w/16 (the code is `smoke/supplement_combine.py` with SUP_S1 = 8).

## 8. A1 outside the branch (Pléiades B2 second finding): not run tonight

A1 outside the flame-out / no-intervention branch is the undemonstrated-recovery part of family A1 (`compact_impacts.family_labels`:
control realised "maintained-then-lost" with recovery attempted, onset at exhaustion). A second conditional pass would condition the
control prior on the upset-then-recovery option (`control_weights = [0, 0, 0, 1]`, `onset.mechanism_weights = [0, 0, 1]`), keep the
D3-aimed selection, and use the same stratified estimator with P_D0'(that branch) from production. It should close the gap in the
same way the first branch pass did (D3 x A1 89 -> 5,282), because the limit is the prior dilution of that branch, not the paths;
but only the A1 outcome of a realised upset counts, so the gain is smaller by P(undemonstrated | upset). **Cost:** run J seeds 1-8
x 100,000 paths, about 12 min per seed at 12 threads (1.6 h) and 3.5 GB thinned; on the supplement paths a further 1.7 h and 3.5 GB.
It needs no core change.

## COVERAGE

**(a) Feasible set (777-200ER, unchanged from `results/eof-run-j-waypoints-oct16` section 5).** Uncontrolled spirals with bank up
to 90 deg and beyond (overbank physically possible); dives and level-offs after a push-over; piloted rapid descents to 40,000 ft/min;
planned descents and ditching approaches begun at any time before exhaustion, including before 00:11; impacts after the 00:19:37
transmission; the whole 7th-arc span the 00:11 posterior reaches (about 40-20 S).

**(b) Model's reach.** As the production pass: bank limit U[52, 90] deg (overbank above 90 deg is a declared reach gap); round-3
laws (Boeing leave-one-out gate failed: uncalibrated); planned descent before 00:11 only through the joined-V2 recipe, which this
pass does not use. This pass adds no reach; it changes only where the samples land.

**(c) Proposal's coverage (this pass).** 00:11 paths: 2.4M production rows (8 % north of 34.5 S) plus 0.8M supplement rows (92 % north
of 34.5 S). Effective distinct 00:11 states by impact band, after the supplement and the extra descents: see section 3. Per 00:19
option (all families): D0', D1, D2 >= 3,199 in every northern band; D4 and D5 >= 1,193 in 35-30 and 30-25 S; **gaps below 1,000:**
D3 35-30 S (855), D3 25-20 S (281), D4 25-20 S (272), D5 25-20 S (890). Per family (section 3, family table): **A1 under D3, D4
and D5 is below 1,000 in every northern band (23-310)** (section 7 for the A1-branch pass); A2 and B under D3 132-769; B under D5
35-30 S 516; all D0', D1 family cells >= 1,206. In 40-35 S every option holds >= 4,477 distinct states (D3, whose A1 part, 367, is the
gap the 18 Oct A1-branch pass closed) and >= 15.9k for the others.

**Gaps and status.**
1. D3 35-30 S, and D3 / D4 / D5 in 25-20 S, below 1,000: OPEN, costed fixes in section 4 item 5. The band masses there rest on few
   states and are reported as not assessed at adequate depth (D4 25-20 S is the one band where production alone and the combined
   value disagree).
2. A1 under D3-D5 in the north: OPEN for the unconditional sample; the A1-branch pass is the fix (section 7).
3. A1 outside the flame-out / no-intervention branch (undemonstrated recoveries; Pléiades B2 finding): OPEN, not run tonight
   (section 8).
4. Planned descent begun before 00:11, on the supplement paths: NOT ASSESSED at this depth (declared reduction 5).
5. Half of the supplement rows not flown (k = 2): a declared reduction, exact by rule B; it lowers the northern ESS, not the bias.
6. Free, descent-climb and repro strata: no supplement exists (core); their production values stand.

**Parameter bounds and sources.** Bank limit U[52, 90] deg (Boeing traces 53-60 deg rounded outward; knife-edge limit; Pete 16 Oct);
dive probability 0.5 (Decision 4); log-on cause q = 1/3, 'other cause' silent (12 Oct rulings); BFO error 4.3177 Hz at 00:19 (run J);
D5 offset U[17, 130] Hz (Pete); r_hat from core `r_hat.csv` (efficiency only; rule B is exact for any r_hat).

## Files

- Repository `results/eof-run-j-supplement-oct19/`: this note; `summary-final.json` (all treatments, both weightings, bands,
  bootstrap, PDFs), `summary-pass1.json` (64 descents only), `a1-branch.json`, `tables.md`; figures `eof-run-j-supplement-latitude-pdf`,
  `-band-ess`, `-band-mass` (PNG + PDF).
- Exchange `mh370-exchange/end-of-flight/run-j-supplement/`: `north-k2/` (16 verified compact seeds + hand-off subsets and
  stride.json), `north-k2-xd256/` (64 thinned groups + select.json), `north-k2-a1branch/` (16 thinned seeds), `reduced/`
  (impacts-ruleB.npz/.json), `summary/` (the JSON above), README.md, SHA256SUMS, READY.
- Order disk use: see the exchange README (cap 40 GB).
