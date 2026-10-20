# End of flight completes the run J northern supplement: all rows, extra descents, and the second A1 conditional pass (20 Oct 2026)

End of Flight Module, overnight order A (`threads/work-orders/overnight-2026-10-20.md`; Mac, 12 threads, cap 30 GB). Follows
`results/eof-run-j-supplement-oct19` (f4fa6cf0). Core run J convergence is a PASS by project ruling (16 Oct 2026). Waypoints stratum only.

**Caveat (verbatim).** The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all three rounds.
Impact energy, attitude, flight-path angle and energy-transfer duration from this arm are a labelled sensitivity on uncalibrated
dynamics, not a physical prediction.

## Declared reductions and substitutions

1. **Extra descents on the new half thinned to 180,000 rows per group** (250,000 last night) to stay inside the 30 GB cap. Checked
   per group: the thinning keeps the effective size of every scored cell unchanged (e.g. seed 1001 group 0: 762 / 35 / 15 / 59 before
   and after).
2. **The second A1 conditional pass covers run J seeds 1-8 only** (800,000 paths, as costed on 19 Oct), not the supplement paths;
   its northern tail is therefore thin (section 3).
3. **The A1-branch pass of 19 Oct stays on the first half of the supplement only** (k = 2, rule B with u2 x 2, n2 = 800,004); it was
   not extended to the new half (not in the order).
4. Config tree a517deeb and binary mh370-eof-rj1 (sha256 19031f41748ecb0c) as on 19 Oct; the merged configuration of the new half's
   seed 1001 equals run J production seed 1 except `seeds`; the 48 run J inputs re-verified after the workspace was rebuilt.
5. Analysis ran beside the 12-thread job for about 1 h in total (single-threaded; the `nice` call was not permitted in the sandbox).
6. New 'other cause only' cells D3s, D4s, D5s (log-on from another cause, silent, without the q = 1/3 mixture) are added because the
   Pléiades finding was stated for that cell; the headline cells stay the q = 1/3 totals.
7. Repository: the work-order commit 15316c85 had deleted 10,952 files; this order was worked from f4fa6cf0 and is committed on top of
   the restored tree (0915281), with no deletions.

## 1. What was run (20 Oct, 02:50-09:52Z)

| Pass | Paths | Descents per path | Output (exchange `end-of-flight/run-j-supplement/`) | Time |
|---|---|---|---|---|
| second half, production recipe | 16 seeds x rows 1, 3, 5, ... = 799,999 | 64 (terminal seeds 40001-40016) | `north-k2b/` 16 x 1.42 GB compact | 02:50-03:59Z |
| A1 outside the branch (`smoke/a1-outside.toml`) | run J seeds 1-8 x 100,000 | 64, D3-aimed selection K = 8 (seeds 60001-60008) | `run-j-a1outside/` 8 x 0.18 GB, thinned 0.4M | 03:59-05:57Z |
| extra descents, second half (D2-D5) | 743k paths north of 35.5 S, 4 groups per seed | +256 (seeds 50010-50163) | `north-k2b-xd256/` 64 x 0.08 GB, thinned | 05:57-09:52Z |

Rule B now uses all supplement rows: u2 = w/16 (no factor 2), n2 = 1,600,003, n1 = 2,399,999; each supplement seed's two halves are
one replicate (its paths kept apart, its distinct 00:11 states merged across halves). New disk: 29.93 GB (cap 30).

## 2. Result

- **Rule B still reproduces production:** ln Z within 0.015 nat, family shares within 0.003, 5 / 50 / 95 % latitudes within 0.1 deg;
  29 of 30 northern band masses inside production's 95 % seed-bootstrap interval (again the exception is D4 in 25-20 S, 0.0036
  [0.0026, 0.0048] against production 0.0021 [0.0015, 0.0029]; production rests on 87 states there, the full set on 560).
- **The northern masses do not change** between half and all of the supplement (D0' north of 33 S 0.0345 -> 0.0349; every band
  within 0.0005), and their intervals do not narrow: they are limited by the 16 replicates' mode probabilities, not by end of flight.
- **All supplement rows lift every both-burst cell** (distinct states, impact 35-30 / 30-25 / 25-20 S): D3 855 / 1,494 / 281 ->
  **1,311 / 2,377 / 424**; D4 2,303 / 1,314 / 272 -> **3,658 / 1,993 / 560**; D5 1,193 / 3,357 / 890 -> **1,856 / 5,844 / 1,720**;
  D2 -> 14.5k / 18.8k / 6,239. **Remaining below 1,000: D3 and D4 in 25-20 S only** (424, 560), plus family cells (section 2 table).
- **A1 outside the branch (second conditional pass).** Under D4 (q = 1/3 total) it is 0.27 of A1 (0.075 of Z), and the A1 share
  becomes 0.276 by the stratified estimator (main set 0.247). Its overall ESS is 15,694 rows (Pléiades measured about 127 in production under 'other cause'), but the north stays
  thin (35-30 / 30-25 / 25-20 S: 191 / 45 / 36 distinct states): run J paths only. Under D3 and D5 it carries no measurable mass in the
  total cells (< 0.0001 of Z), and under 'other cause only' 0.06 of D3's A1 and < 0.01 of D5's; there the pass itself finds only 51
  and 23 effective rows, so **D3 x A1-outside stays not estimable** (an undemonstrated recovery rarely gives the recorded pair). Under
  D4 'other cause only' it is 0.38 of A1 (Pléiades found 0.46 in production) with 6,877 effective rows.

## 3. Tables

**Band ESS by impact latitude: rows / paths / distinct 00:11 states** (target 1,000; production alone -> 19 Oct, half the supplement -> **20 Oct, all supplement rows**)

| treatment | 35-30 S | 30-25 S | 25-20 S |
|---|---|---|---|
| D0' 00:19 data not used | 108.8k/30.0k/30.0k -> 154.1k/46.2k/45.8k -> **204.2k/60.5k/59.0k** | 15.7k/3,459/3,459 -> 94.4k/23.4k/19.2k -> **179.3k/44.3k/24.9k** | 6,443/1,451/1,451 -> 29.3k/7,149/5,754 -> **48.9k/12.6k/7,897** |
| D1 R600 BTO | 125.7k/40.9k/40.9k -> 171.7k/58.5k/57.7k -> **220.3k/77.1k/74.4k** | 20.1k/5,549/5,549 -> 128.1k/36.6k/27.5k -> **246.5k/70.2k/33.6k** | 6,596/2,273/2,273 -> 38.7k/10.7k/9,694 -> **58.6k/17.5k/14.0k** |
| D2 R600 BTO + BFO | 6,010/5,180/5,180 -> 12.6k/10.4k/10.4k -> **17.8k/14.6k/14.5k** | 1,075/901/901 -> 25.8k/15.6k/13.2k -> **56.8k/31.6k/18.8k** | 184/167/167 -> 4,469/3,365/3,199 -> **10.3k/7,172/6,239** |
| D3 both BFOs as recorded | 307/305/305 -> 869/856/855 -> **1,334/1,313/1,311** | 83/83/83 -> 1,546/1,509/1,494 -> **2,533/2,467/2,377** | 22/22/22 -> 291/282/281 -> **436/427/424** |
| D4 both BFOs, Holland transient bias added | 367/363/363 -> 2,426/2,307/2,303 -> **3,922/3,681/3,658** | 166/154/154 -> 1,513/1,377/1,314 -> **2,766/2,389/1,993** | 104/87/87 -> 351/274/272 -> **706/573/560** |
| D5 R600 + R1200 BFO with start-up offset | 548/542/542 -> 1,213/1,194/1,193 -> **1,899/1,858/1,856** | 256/245/245 -> 3,821/3,511/3,357 -> **7,206/6,605/5,844** | 63/63/63 -> 949/904/890 -> **1,927/1,797/1,720** |

**Band ESS by 00:11 latitude: rows / paths / distinct 00:11 states** (target 1,000; production alone -> 19 Oct, half the supplement -> **20 Oct, all supplement rows**)

| treatment | 35-30 S | 30-25 S | 25-20 S |
|---|---|---|---|
| D0' 00:19 data not used | 212.2k/53.4k/53.4k -> 269.0k/71.2k/70.9k -> **329.3k/85.3k/84.4k** | 18.7k/3,859/3,859 -> 111.4k/23.5k/20.0k -> **208.7k/43.3k/26.8k** | 3,468/693/693 -> 18.6k/4,072/3,089 -> **34.6k/7,408/4,181** |
| D1 R600 BTO | 268.2k/77.9k/77.9k -> 329.7k/97.2k/96.7k -> **392.4k/115.0k/113.6k** | 23.6k/6,129/6,129 -> 133.4k/28.9k/24.9k -> **254.1k/54.4k/35.3k** | 3,369/1,111/1,111 -> 24.6k/6,329/5,615 -> **40.2k/10.5k/8,137** |
| D2 R600 BTO + BFO | 12.4k/10.5k/10.5k -> 19.5k/16.0k/16.0k -> **24.7k/20.0k/19.9k** | 1,298/1,062/1,062 -> 26.2k/12.6k/11.5k -> **57.6k/26.5k/19.3k** | 90/84/84 -> 3,527/2,578/2,398 -> **8,067/5,292/4,383** |
| D3 both BFOs as recorded | 652/646/646 -> 996/985/985 -> **1,201/1,190/1,190** | 96/96/96 -> 1,665/1,588/1,578 -> **2,704/2,578/2,519** | 11/11/11 -> 257/246/244 -> **518/498/489** |
| D4 both BFOs, Holland transient bias added | 1,336/1,309/1,309 -> 5,883/5,489/5,484 -> **8,247/7,599/7,572** | 200/183/183 -> 1,972/1,697/1,639 -> **3,709/3,112/2,693** | 69/66/66 -> 221/183/182 -> **432/370/359** |
| D5 R600 + R1200 BFO with start-up offset | 1,658/1,629/1,629 -> 2,940/2,868/2,867 -> **4,119/3,987/3,985** | 290/279/279 -> 4,454/3,898/3,789 -> **8,230/6,795/6,276** | 36/36/36 -> 735/688/670 -> **929/886/851** |

**Family ESS by impact band (distinct 00:11 states), 19 Oct -> 20 Oct** (A1 = cruise to fuel exhaustion then no control; A2 = cruise to fuel exhaustion then controlled descent; B = planned descent begun before fuel exhaustion)

| treatment | 35-30 S A1 / A2 / B | 30-25 S A1 / A2 / B | 25-20 S A1 / A2 / B |
|---|---|---|---|
| D0' 00:19 data not used | 10.6k -> 13.4k / 17.2k -> 21.9k / 45.3k -> 59.9k | 4,552 -> 5,785 / 8,259 -> 11.0k / 22.2k -> 33.7k | 1,206 -> 1,625 / 2,205 -> 3,172 / 7,265 -> 10.7k |
| D1 R600 BTO | 16.7k -> 21.2k / 25.2k -> 33.0k / 45.5k -> 58.2k | 7,030 -> 8,180 / 13.0k -> 15.8k / 28.5k -> 43.5k | 2,025 -> 3,108 / 4,027 -> 6,161 / 10.2k -> 14.0k |
| D2 R600 BTO + BFO | 2,746 -> 3,938 / 4,694 -> 6,839 / 4,586 -> 6,367 | 1,843 -> 2,229 / 3,893 -> 5,045 / 10.6k -> 20.3k | 685 -> 1,015 / 1,576 -> 2,596 / 1,745 -> 3,861 |
| D3 both BFOs as recorded | 23 -> 31 / 687 -> 1,068 / 514 -> 808 | 89 -> 203 / 769 -> 1,673 / 698 -> 974 | 35 -> 60 / 192 -> 307 / 132 -> 192 |
| D4 both BFOs, Holland transient bias added | 251 -> 411 / 1,283 -> 1,806 / 3,459 -> 5,268 | 310 -> 555 / 1,242 -> 829 / 1,697 -> 4,528 | 60 -> 114 / 378 -> 569 / 743 -> 1,695 |
| D5 R600 + R1200 BFO with start-up offset | 165 -> 257 / 1,497 -> 2,210 / 516 -> 804 | 151 -> 328 / 2,312 -> 3,794 / 1,494 -> 2,685 | 32 -> 65 / 510 -> 950 / 440 -> 871 |

**Band masses (impact latitude) with 95 % seed-bootstrap intervals: production alone -> 19 Oct -> 20 Oct**

| treatment | 35-30 S | 30-25 S | 25-20 S | north of 33 S | north of 30 S |
|---|---|---|---|---|---|
| D0' 00:19 data not used | 0.0925 [0.0794, 0.1077] -> 0.0955 [0.0825, 0.1097] -> **0.0959** [0.0824, 0.1117] | 0.0131 [0.0113, 0.0153] -> 0.0127 [0.0107, 0.0150] -> **0.0127** [0.0107, 0.0151] | 0.0025 [0.0020, 0.0031] -> 0.0030 [0.0025, 0.0035] -> **0.0030** [0.0025, 0.0036] | 0.0321 [0.0271, 0.0381] -> 0.0345 [0.0285, 0.0412] -> **0.0349** [0.0285, 0.0421] | 0.0157 [0.0134, 0.0186] -> 0.0157 [0.0133, 0.0186] -> **0.0159** [0.0133, 0.0188] |
| D1 R600 BTO | 0.0597 [0.0500, 0.0707] -> 0.0616 [0.0520, 0.0726] -> **0.0617** [0.0516, 0.0737] | 0.0085 [0.0073, 0.0102] -> 0.0084 [0.0069, 0.0102] -> **0.0084** [0.0069, 0.0103] | 0.0022 [0.0017, 0.0027] -> 0.0025 [0.0020, 0.0030] -> **0.0026** [0.0021, 0.0031] | 0.0184 [0.0150, 0.0224] -> 0.0205 [0.0163, 0.0256] -> **0.0208** [0.0163, 0.0263] | 0.0107 [0.0091, 0.0129] -> 0.0109 [0.0090, 0.0131] -> **0.0110** [0.0091, 0.0133] |
| D2 R600 BTO + BFO | 0.0680 [0.0572, 0.0805] -> 0.0693 [0.0594, 0.0804] -> **0.0693** [0.0590, 0.0808] | 0.0113 [0.0097, 0.0134] -> 0.0108 [0.0091, 0.0129] -> **0.0108** [0.0090, 0.0130] | 0.0034 [0.0028, 0.0041] -> 0.0036 [0.0031, 0.0042] -> **0.0037** [0.0031, 0.0042] | 0.0235 [0.0193, 0.0286] -> 0.0252 [0.0202, 0.0307] -> **0.0255** [0.0203, 0.0315] | 0.0148 [0.0128, 0.0172] -> 0.0145 [0.0124, 0.0170] -> **0.0145** [0.0123, 0.0172] |
| D3 both BFOs as recorded | 0.0638 [0.0514, 0.0776] -> 0.0639 [0.0535, 0.0745] -> **0.0633** [0.0531, 0.0749] | 0.0100 [0.0077, 0.0124] -> 0.0088 [0.0073, 0.0105] -> **0.0089** [0.0074, 0.0107] | 0.0020 [0.0013, 0.0030] -> 0.0027 [0.0022, 0.0034] -> **0.0027** [0.0021, 0.0033] | 0.0213 [0.0163, 0.0272] -> 0.0218 [0.0174, 0.0269] -> **0.0218** [0.0171, 0.0272] | 0.0120 [0.0094, 0.0149] -> 0.0115 [0.0096, 0.0139] -> **0.0116** [0.0097, 0.0140] |
| D4 both BFOs, Holland transient bias added | 0.0649 [0.0528, 0.0796] -> 0.0657 [0.0541, 0.0794] -> **0.0656** [0.0533, 0.0802] | 0.0122 [0.0098, 0.0156] -> 0.0122 [0.0095, 0.0155] -> **0.0126** [0.0097, 0.0162] | 0.0021 [0.0015, 0.0029] -> 0.0037 [0.0026, 0.0050] -> **0.0036** [0.0026, 0.0048] | 0.0253 [0.0191, 0.0336] -> 0.0276 [0.0215, 0.0353] -> **0.0280** [0.0214, 0.0361] | 0.0144 [0.0117, 0.0183] -> 0.0159 [0.0123, 0.0205] -> **0.0162** [0.0124, 0.0210] |
| D5 R600 + R1200 BFO with start-up offset | 0.0668 [0.0553, 0.0795] -> 0.0671 [0.0562, 0.0787] -> **0.0664** [0.0553, 0.0790] | 0.0092 [0.0078, 0.0112] -> 0.0090 [0.0075, 0.0110] -> **0.0089** [0.0073, 0.0109] | 0.0022 [0.0016, 0.0029] -> 0.0026 [0.0022, 0.0031] -> **0.0027** [0.0022, 0.0032] | 0.0202 [0.0161, 0.0251] -> 0.0219 [0.0173, 0.0270] -> **0.0220** [0.0172, 0.0276] | 0.0115 [0.0098, 0.0137] -> 0.0116 [0.0098, 0.0140] -> **0.0116** [0.0096, 0.0140] |

**Whole-posterior summaries: production alone -> 20 Oct combined**

| treatment | ln Z | A1 / A2 / B | impact latitude 5 / 50 / 95 % |
|---|---|---|---|
| D0' 00:19 data not used | -7.525 -> -7.534 | 0.172 / 0.343 / 0.484 -> 0.171 / 0.342 / 0.487 | -38.45 / -37.15 / -33.85 -> -38.45 / -37.15 / -33.75 |
| D1 R600 BTO | -12.935 -> -12.946 | 0.199 / 0.346 / 0.454 -> 0.197 / 0.345 / 0.457 | -38.45 / -37.25 / -34.55 -> -38.45 / -37.25 / -34.55 |
| D2 R600 BTO + BFO | -19.121 -> -19.132 | 0.238 / 0.234 / 0.527 -> 0.237 / 0.233 / 0.530 | -38.15 / -37.15 / -34.35 -> -38.15 / -37.15 / -34.25 |
| D3 both BFOs as recorded | -28.582 -> -28.597 | 0.095 / 0.405 / 0.499 -> 0.093 / 0.405 / 0.500 | -38.05 / -37.25 / -34.45 -> -38.05 / -37.25 / -34.45 |
| D4 both BFOs, Holland transient bias added | -28.513 -> -28.527 | 0.250 / 0.349 / 0.400 -> 0.247 / 0.349 / 0.403 | -37.95 / -37.25 / -34.35 -> -37.95 / -37.25 / -34.35 |
| D5 R600 + R1200 BFO with start-up offset | -29.186 -> -29.199 | 0.059 / 0.418 / 0.522 -> 0.058 / 0.417 / 0.524 | -37.95 / -37.25 / -34.45 -> -38.05 / -37.25 / -34.45 |

**A1 by the two conditional strata** (P_D0'(branch 1, no intervention) = 0.0928, P_D0'(branch 2, recovery attempted) = 0.1008 under rule B; production 0.0935 / 0.1014). Branch 2 ESS: rows / paths / distinct states per impact band, run J seeds 1-8.

| treatment | A1 share, stratified (branch 1 + branch 2) | A1 share, main set | branch 2 as fraction of A1 (stratified / main) | branch 2 ESS rows, all | branch 2, 35-30 S | 30-25 S | 25-20 S |
|---|---|---|---|---|---|---|---|
| D0' 00:19 data not used | 0.1692 (0.0928 + 0.0764) | 0.1708 | 0.45 / 0.46 | 150,055 | 9,710 / 1,893 / 1,893 | 1,427 / 298 / 298 | 247 / 86 / 86 |
| D2 R600 BTO + BFO | 0.2259 (0.1243 + 0.1016) | 0.2365 | 0.45 / 0.46 | 38,869 | 1,669 / 818 / 818 | 253 / 128 / 128 | 79 / 30 / 30 |
| D3 both BFOs as recorded | 0.0841 (0.0841 + 0.0000) | 0.0933 | 0.00 / 0.00 | 54 | 6 / 6 / 6 | 2 / 1 / 1 | 6 / 6 / 6 |
| D4 both BFOs, Holland transient bias added | 0.2755 (0.2005 + 0.0750) | 0.2467 | 0.27 / 0.24 | 15,694 | 356 / 191 / 191 | 134 / 45 / 45 | 96 / 36 / 36 |
| D5 R600 + R1200 BFO with start-up offset | 0.0530 (0.0530 + 0.0000) | 0.0580 | 0.00 / 0.00 | 3 | 1 / 1 / 1 | 1 / 1 / 1 | 8 / 8 / 8 |
| D3, other cause only | 0.1136 (0.1065 + 0.0071) | 0.0873 | 0.06 / 0.05 | 51 | 6 / 6 / 6 | 2 / 1 / 1 | 6 / 6 / 6 |
| D4, other cause only | 0.4760 (0.2953 + 0.1806) | 0.3893 | 0.38 / 0.41 | 6,877 | 1,149 / 559 / 559 | 107 / 79 / 79 | 66 / 21 / 21 |
| D5, other cause only | 0.0758 (0.0757 + 0.0002) | 0.0583 | 0.00 / 0.01 | 23 | 1 / 1 / 1 | 1 / 1 / 1 | 8 / 8 / 8 |

## 4. Reading

1. Flying the other half of the supplement rows roughly doubled the both-burst northern ESS where paths limited it (D3 25-20 S
   281 -> 424, D4 25-20 S 272 -> 560, D5 25-20 S 890 -> 1,720): the 19 Oct finding that 25-20 S is path-limited holds.
2. The per-path weight balance matters: with the new half at 64 descents only, D4 30-25 S fell to 640 (interim, not reported as a
   result) and recovered to 1,993 once the new half had its extra descents. Both halves now carry the same descents per path.
3. One family cell moved down: D4 A2 in 30-25 S, 1,242 -> 829 distinct states (a few heavy new-half rows). It is reported as is;
   the D4 total in that band is 1,993.
4. Family A1 under D3-D5 in the north stays below 1,000 in the unconditional sample (31-555); the conditional strata are the
   estimator for it (19 Oct section 7 for branch 1; section 2 above for branch 2).

## COVERAGE

**(a) Feasible set and (b) model's reach:** unchanged from `results/eof-run-j-supplement-oct19` (overbank above 90 deg a declared
reach gap; round-3 laws uncalibrated; planned descent before 00:11 only through joined-V2, not used here).

**(c) Proposal's coverage.** 00:11 paths: 2.4M production rows (8 % north of 34.5 S) plus all 1.6M supplement rows (92 % north of
34.5 S). Distinct-state ESS in section 3. **Gaps below 1,000 (all families):** D3 25-20 S (424), D4 25-20 S (560). **Family gaps:**
A1 under D3-D5 in every northern band in the unconditional sample (use the strata); D3 A1 outside the branch not estimable even
conditionally (51 effective rows; carries 0.06 of D3's A1 under 'other cause', < 0.0001 of Z under the total); D4 A1 outside the
branch north of 35 S thin (191 / 45 / 36), because that pass is on run J paths only; D3 A2 / B and D4 / D5 A1 / B cells in 25-20 S
(60-950). **Fix for the remaining A1-outside tail, costed:** the same conditional pass on the supplement paths (16 seeds x 100,000,
about 16 min per seed at 12 threads = 4.3 h, about 3 GB thinned).

**Bounds and sources:** as 19 Oct (bank limit U[52, 90] deg; dive p = 0.5; q = 1/3, 'other cause' silent; BFO error 4.3177 Hz;
D5 offset U[17, 130] Hz; r_hat from core).

## Files

- Repository: this note; `summary-full.json` (all treatments incl. D3s-D5s, both weightings, bands, bootstrap, PDFs),
  `a1-strata.json`, `tables.md`, `a1-table.md`; figures `eof-run-j-supplement-full-latitude-pdf`, `-band-ess`, `-band-mass` (PNG + PDF).
- Exchange `end-of-flight/run-j-supplement/`: new `north-k2b/`, `north-k2b-xd256/`, `run-j-a1outside/`; `reduced/impacts-ruleB.npz`
  (+ .json) **now the full set** (2,408,038 rows, 0.43 GB; ln weights `lnw:comb/D0..D5, D3s..D5s` and `lnw:alone/...`; new columns
  `supplement_half`, `latent:onset_mechanism`, `latent:control_realised`, `latent:recovery_attempted`; band masses within 0.0004 of the
  full set, D2-D5 band ESS kept within 1 %); last night's file kept as `reduced/impacts-ruleB-k2.npz`; README, SHA256SUMS, READY.
- Code (`engine/hypotheses/end-of-flight/`): `full/run_j_supplement.sh` (SUP_OFFSET, SUP_SEED_BASE), `full/run_j_supplement_xd.sh`
  (XD_OFFSET, XD_SEED_BASE), `full/run_j_a1_outside.sh`, `smoke/a1-outside.toml`, `smoke/supplement_a1_outside.py`;
  `smoke/supplement_combine.py` (`partm`: several row sets of one replicate; branch masses; D3s-D5s), `supplement_reduced.py`,
  `supplement_summary.py`, `supplement_tables.py --compare`, `supplement_figures.py make_full`.
