# Ocean settling on end of flight's run J — seabed wreckage per stratum

Settling `hypothesis/settling` 9330d4c (real ocean; unchanged since run I). End-of-flight tools 4605cc21 (`smoke/option_table_0019.py` as 31bb6211, which adds only the thinned-file normaliser), binary mh370-eof-rj1. Samples: `mh370-exchange/settling/run-j/<stratum>/` (README.txt with labels and COVERAGE, SHA256SUMS, READY); mixture weights `settling/run-j/stratum-mixture-weights.json`; top-level README and READY written last. Driver: `scripts/wf_runj.py` (from run I's `wf_runi.py`; diff in §Method).

**Labels (carry on every result):** core run J split-half **accepted as a pass by project ruling, 16 Oct 2026** (free flight 0.840 single split, 0.873 all-partition mean; waypoints 0.934 all-partition); the thin northern detail north of 33 S is a tail-shape limitation (core prediction 5), not non-convergence. Piloted rapid descent to 40,000 ft/min with unloading; piloted-turn model and INTERIM pitch-down PROVISIONAL; in-flight structural outcome PROVISIONAL (no transonic drag rise); breakup rows settled from the intact impact point (gap G-bf); P(left) = 0.8 PROVISIONAL; D4/D5 "Holland transient bias added". **D0 is D0'**: 00:19 values held out, transmission imposed (every cell carries +alive: impact after 00:19:37.443). Each stratum is CONDITIONAL on itself.

**Method.** As run I. Row mass = end of flight's 00:19 two-factor table (`seed_terms`): hand-off weight / (unthinned) weight total / K × (1 − P(breakup by 00:19:37)) × L(D) × L(cause). Primary cell: both log-on causes, q = 1/3 = prior odds C2:C1 (P(C1) = 0.75), C2 silent (W = 00:10:58–01:15:56). Each product is a systematic resample over all rows of all seeds of the stratum (24 / 18 / 16 / 16 seeds), one settling draw each: 40,000 per total, 10,000 per family, 20,000 per cause (same N as run I). Changes from `wf_runi.py`: run J labels; normaliser `thinning.weight_sum_in` (option_table_0019 31bb6211; identical for unthinned files); an assertion that no positive-mass row impacts at or before 00:19:37.443; optional D subset (`WF_DS`) used only for the both-burst folder.

**Run.** Mac, under `lockf -k /tmp/.mh370-heavy.lock`; four strata in parallel (prep 1 thread each; settling 2 threads, one stratum at a time; at most 5 workers), then the both-burst folder (settling 6 threads). Wall time: validation 05:21–05:25Z; four strata 05:26–05:55Z (29 min); both-burst 05:55–05:59Z; 18 Oct 2026. Disk added: 9.6 GiB on the exchange (`settling/run-j/`) + 4.6 GiB work directory (`/Users/pete/Downloads/mh370-settling-work-j`, of which 2.0 GiB is the validation set) = 14.2 GiB (du). Free space on the volume fell from 67 to 49 GiB over the same period (df); the other ~4 GiB is not in settling's folders (other sessions or the system). The 25 GiB floor was never approached.

## Checks

- Per-seed ln Z of every cell (D0–D5 × total / C1 / C2 silent) equals end of flight's `option_table_0019.seed_terms` (asserted in code) and its published `run-j/summary/table-0019-run-j-<stratum>.json` seed_ln_Z: max |difference| 1.8e-15 (waypoints, 432 values), 7.1e-15 (free 324, descent-climb 288, repro-radar 288). Both-burst: 7.1e-15 against `run-j-both-burst/summary/table-0019-supplementary-8.json` (144 values), which also confirms the hand-off mapping (both-burst seed k uses core run J waypoints seed k).
- The core shares (0.9982 / 0.0013 / 0.0003 / 0.0002, from `run_j_maps_pass.STRATA`) with the per-seed ln Z reproduce end of flight's `table-0019-mixture.json` ln Z for all 18 cells to 7e-15.
- +alive: no positive-mass row impacts at or before 00:19:37.443 in any seed of any product (asserted); every resampled impact time is after it.
- Elements: every (row, draw) outcome of every product is present; draws per row match the impact table; all columns finite (settled latitude/longitude finite); element masses sum to the impact mass for every outcome (ratio 1 ± 2e-15); fates 0 (settled) and 1 (afloat) only; 0 outcomes not computed or refused by the ocean window (all impacts 11.5–44.0 S, 83.7–109.9 E, inside 75–115 E, 45–10 S).
- SHA256SUMS re-verified after publication in all five folders (0 mismatches).
- Validation first on run-j-free seed 1 alone (155,387 rows, 386,724 draws; ln Z equal to the published table exactly; elements checked as above; figure rendered) before the full run. Reproduction of a run I seed result was NOT possible: run I's end-of-flight impacts (`end-of-flight/run-i/`) and settling's run I exchange folder are no longer on the Mac. The settling engine is the same commit (9330d4c) as run I.

## 1. 90 % seabed area (thousand km²), primary cell (both causes), by stratum

| 00:19 data treatment | waypoints | free | descent-climb | repro-radar | mixture weights (wp / free / d-c / r-r) | run I waypoints (for reference) |
|---|---|---|---|---|---|---|
| 00:19 Held Out | 160.2 (ESS 1,941,487) | 268.4 (ESS 384,629) | 214.7 (ESS 397,767) | 293.9 (ESS 330,094) | 0.9987 / 0.0009 / 0.0002 / 0.0002 | 151.2 |
| 00:19 R600 BTO Only | 116.6 (ESS 2,140,205) | 185.8 (ESS 463,068) | 155.0 (ESS 476,479) | 193.2 (ESS 429,946) | 0.9989 / 0.0008 / 0.0001 / 0.0002 | 115.8 |
| 00:19 R600 BTO + Raw BFO | 103.4 (ESS 91,999) | 161.0 (ESS 14,876) | 133.7 (ESS 21,574) | 161.1 (ESS 20,393) | 0.9988 / 0.0008 / 0.0001 / 0.0002 | 107.9 |
| 00:19 R600 BTO + both BFOs as recorded | 63.5 (ESS 4,696) | 100.1 (ESS 1,198) | 80.5 (ESS 1,528) | 99.4 (ESS 1,379) | 0.9989 / 0.0008 / 0.0001 / 0.0002 | 62.8 |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | 59.5 (ESS 21,169) | 107.0 (ESS 4,362) | 82.7 (ESS 2,147) | 105.6 (ESS 3,814) | 0.9989 / 0.0008 / 0.0001 / 0.0002 | 65.7 |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | 59.8 (ESS 25,885) | 98.8 (ESS 6,572) | 79.6 (ESS 6,931) | 97.3 (ESS 5,913) | 0.9989 / 0.0008 / 0.0001 / 0.0002 | 64.8 |

Both-burst supplement (`run-j-both-burst-waypoints`, waypoints only, 8 thinned seeds, D2–D5 only; use beside, not pooled with, run-j-waypoints, as searched areas did):

| 00:19 data treatment | both-burst 90 % area (row ESS) | run-j-waypoints 90 % area (row ESS) |
|---|---|---|
| 00:19 R600 BTO + Raw BFO | 97.9 (ESS 111,753) | 103.4 (ESS 91,999) |
| 00:19 R600 BTO + both BFOs as recorded | 58.4 (ESS 6,334) | 63.5 (ESS 4,696) |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | 52.2 (ESS 44,325) | 59.5 (ESS 21,169) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | 54.7 (ESS 27,323) | 59.8 (ESS 25,885) |

Settling adds 0.1–1.7 % to the 90 % area in every estimable product (0.5–1.9 % in products below the gate); mass-weighted settled-offset p90 1.8–4.6 km (README tables). Afloat elements (excluded from the seabed products) are 14.2–14.5 % of elements in every folder.
n.e. = not estimable (row Kish ESS < 1,000). Mixture weights = core share × Z_s(cell), normalised (core shares: waypoints 0.9982, free 0.0013, repro-radar 0.0003, descent-climb 0.0002).

## 2. Log-on cause (posterior share within the treatment = prior p × Z ratio; 90 % area)

| 00:19 data treatment | stratum | C1 fuel-exhaustion share | C1 area | C2 silent share | C2 silent area |
|---|---|---|---|---|---|
| 00:19 Held Out | waypoints | 99.1 % | 159.1 | 0.9 % (ESS 3,276,234) | 303.9 |
| 00:19 Held Out | free | 98.4 % | 263.9 | 1.6 % (ESS 1,416,578) | 355.4 |
| 00:19 Held Out | descent-climb | 98.4 % | 207.8 | 1.6 % (ESS 1,409,503) | 356.5 |
| 00:19 Held Out | repro-radar | 98.5 % | 284.8 | 1.5 % (ESS 1,087,058) | 456.5 |
| 00:19 R600 BTO Only | waypoints | 99.1 % | 115.5 | 0.9 % (ESS 4,020,010) | 206.5 |
| 00:19 R600 BTO Only | free | 98.4 % | 183.6 | 1.6 % (ESS 1,867,214) | 242.2 |
| 00:19 R600 BTO Only | descent-climb | 98.5 % | 150.0 | 1.5 % (ESS 1,817,443) | 257.4 |
| 00:19 R600 BTO Only | repro-radar | 98.6 % | 187.6 | 1.4 % (ESS 1,461,731) | 306.3 |
| 00:19 R600 BTO + Raw BFO | waypoints | 99.8 % | 104.5 | 0.2 % (ESS 62,717) | 65.5 |
| 00:19 R600 BTO + Raw BFO | free | 99.7 % | 161.1 | 0.3 % (ESS 15,340) | 93.6 |
| 00:19 R600 BTO + Raw BFO | descent-climb | 99.7 % | 132.2 | 0.3 % (ESS 16,585) | 80.7 |
| 00:19 R600 BTO + Raw BFO | repro-radar | 99.8 % | 164.0 | 0.2 % (ESS 10,921) | 103.2 |
| 00:19 R600 BTO + Raw BFO | both-burst (waypoints) | 99.8 % | 97.7 | 0.2 % (ESS 99,266) | 52.3 |
| 00:19 R600 BTO + both BFOs as recorded | waypoints | 99.6 % | 63.8 | 0.4 % (ESS 4,624) | 50.4 |
| 00:19 R600 BTO + both BFOs as recorded | free | 99.4 % | 99.7 | 0.6 % (ESS 1,949) | 64.5 |
| 00:19 R600 BTO + both BFOs as recorded | descent-climb | 99.5 % | 80.6 | 0.5 % (ESS 1,441) | 60.5 |
| 00:19 R600 BTO + both BFOs as recorded | repro-radar | 99.5 % | 99.6 | 0.5 % (ESS 1,176) | 67.6 |
| 00:19 R600 BTO + both BFOs as recorded | both-burst (waypoints) | 99.6 % | 58.4 | 0.4 % (ESS 5,914) | 43.3 |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | waypoints | 99.5 % | 60.5 | 0.5 % (ESS 4,390) | 54.7 |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | free | 99.0 % | 106.9 | 1.0 % (ESS 1,053) | 65.1 |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | descent-climb | 99.3 % | 82.9 | 0.7 % (ESS 1,008) | 65.2 |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | repro-radar | 99.3 % | 106.5 | 0.7 % (ESS 893) | 71.3 (n.e.) |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | both-burst (waypoints) | 99.5 % | 53.1 | 0.5 % (ESS 3,299) | 50.1 |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | waypoints | 99.6 % | 59.1 | 0.4 % (ESS 18,773) | 47.1 |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | free | 99.4 % | 99.5 | 0.6 % (ESS 6,780) | 63.3 |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | descent-climb | 99.5 % | 78.7 | 0.5 % (ESS 6,237) | 59.1 |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | repro-radar | 99.5 % | 97.2 | 0.5 % (ESS 6,060) | 66.4 |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | both-burst (waypoints) | 99.6 % | 54.3 | 0.4 % (ESS 19,234) | 39.3 |

## 3. Flight-end family (share within the treatment; 90 % area)

| 00:19 data treatment | stratum | A1 | A2 | B |
|---|---|---|---|---|
| 00:19 Held Out | waypoints | 17.2 %, 34.0 (ESS 997,405) | 34.3 %, 150.5 (ESS 742,682) | 48.4 %, 177.5 (ESS 716,892) |
| 00:19 Held Out | free | 11.6 %, 137.6 (ESS 125,885) | 28.7 %, 274.4 (ESS 130,775) | 59.7 %, 261.6 (ESS 191,012) |
| 00:19 Held Out | descent-climb | 13.1 %, 81.5 (ESS 167,230) | 30.3 %, 203.4 (ESS 148,468) | 56.5 %, 221.9 (ESS 178,203) |
| 00:19 Held Out | repro-radar | 12.6 %, 127.2 (ESS 117,172) | 32.0 %, 276.2 (ESS 120,994) | 55.4 %, 294.7 (ESS 149,808) |
| 00:19 R600 BTO Only | waypoints | 19.9 %, 20.9 (ESS 1,244,077) | 34.6 %, 122.6 (ESS 879,548) | 45.4 %, 132.8 (ESS 688,706) |
| 00:19 R600 BTO Only | free | 13.1 %, 56.8 (ESS 193,815) | 29.0 %, 196.9 (ESS 188,071) | 57.8 %, 192.0 (ESS 206,090) |
| 00:19 R600 BTO Only | descent-climb | 15.1 %, 39.2 (ESS 233,004) | 31.1 %, 152.8 (ESS 198,097) | 53.7 %, 161.7 (ESS 190,910) |
| 00:19 R600 BTO Only | repro-radar | 14.5 %, 51.3 (ESS 181,766) | 32.3 %, 203.2 (ESS 191,830) | 53.2 %, 199.1 (ESS 169,508) |
| 00:19 R600 BTO + Raw BFO | waypoints | 23.8 %, 18.8 (ESS 48,477) | 23.4 %, 129.0 (ESS 27,700) | 52.7 %, 115.7 (ESS 35,949) |
| 00:19 R600 BTO + Raw BFO | free | 15.6 %, 42.2 (ESS 7,129) | 25.7 %, 167.8 (ESS 6,775) | 58.7 %, 166.7 (ESS 6,363) |
| 00:19 R600 BTO + Raw BFO | descent-climb | 17.2 %, 32.3 (ESS 7,341) | 25.7 %, 146.4 (ESS 8,246) | 57.0 %, 140.4 (ESS 9,476) |
| 00:19 R600 BTO + Raw BFO | repro-radar | 18.7 %, 39.0 (ESS 6,159) | 25.7 %, 174.9 (ESS 6,452) | 55.4 %, 172.1 (ESS 9,292) |
| 00:19 R600 BTO + Raw BFO | both-burst (waypoints) | 20.6 %, 18.4 (ESS 54,655) | 22.2 %, 117.8 (ESS 33,346) | 57.1 %, 107.0 (ESS 48,684) |
| 00:19 R600 BTO + both BFOs as recorded | waypoints | 9.5 %, 16.6 (n.e.) (ESS 368) | 40.5 %, 57.3 (ESS 4,010) | 49.9 %, 69.6 (ESS 1,688) |
| 00:19 R600 BTO + both BFOs as recorded | free | 6.8 %, 26.0 (n.e.) (ESS 51) | 32.9 %, 98.9 (n.e.) (ESS 843) | 60.3 %, 97.2 (n.e.) (ESS 591) |
| 00:19 R600 BTO + both BFOs as recorded | descent-climb | 6.6 %, 25.1 (n.e.) (ESS 62) | 35.7 %, 75.6 (ESS 1,226) | 57.6 %, 79.6 (n.e.) (ESS 693) |
| 00:19 R600 BTO + both BFOs as recorded | repro-radar | 7.7 %, 29.7 (n.e.) (ESS 73) | 36.9 %, 99.7 (ESS 1,038) | 55.4 %, 89.5 (n.e.) (ESS 597) |
| 00:19 R600 BTO + both BFOs as recorded | both-burst (waypoints) | 8.0 %, 15.9 (n.e.) (ESS 409) | 37.0 %, 55.3 (ESS 5,302) | 55.0 %, 60.1 (ESS 2,595) |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | waypoints | 25.0 %, 25.2 (ESS 1,912) | 34.9 %, 56.0 (ESS 32,187) | 39.9 %, 64.7 (ESS 14,768) |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | free | 21.4 %, 52.9 (n.e.) (ESS 271) | 29.0 %, 110.7 (ESS 4,152) | 49.5 %, 93.8 (ESS 6,040) |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | descent-climb | 19.0 %, 39.5 (n.e.) (ESS 321) | 31.9 %, 81.9 (ESS 3,113) | 49.0 %, 79.9 (n.e.) (ESS 749) |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | repro-radar | 26.3 %, 48.0 (n.e.) (ESS 357) | 30.2 %, 111.8 (ESS 3,122) | 43.3 %, 95.0 (ESS 4,850) |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | both-burst (waypoints) | 24.9 %, 20.1 (ESS 4,584) | 32.0 %, 51.8 (ESS 42,580) | 42.9 %, 57.2 (ESS 28,109) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | waypoints | 6.0 %, 17.7 (ESS 2,178) | 42.2 %, 54.5 (ESS 20,864) | 51.7 %, 65.0 (ESS 9,401) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | free | 3.7 %, 40.8 (n.e.) (ESS 279) | 34.3 %, 108.3 (ESS 4,187) | 62.0 %, 93.6 (ESS 3,223) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | descent-climb | 4.1 %, 29.9 (n.e.) (ESS 366) | 37.9 %, 74.3 (ESS 4,366) | 57.9 %, 81.8 (ESS 3,144) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | repro-radar | 4.5 %, 36.8 (n.e.) (ESS 335) | 38.9 %, 97.1 (ESS 3,996) | 56.5 %, 94.8 (ESS 2,554) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | both-burst (waypoints) | 4.9 %, 17.9 (ESS 1,754) | 37.6 %, 54.2 (ESS 15,799) | 57.5 %, 56.3 (ESS 12,566) |

## COVERAGE

**(a) Feasible set.** As end of flight's run J note: piloted dives to about 40,000 ft/min with unloading to −1.0 g, speeds past VMO/MMO, piloted turns, in-flight structural damage or breakup; four strata (waypoint routes, free flight, descent-climb, Davey dynamics with radar). Core shares: waypoints 0.9982, free 0.0013, repro-radar 0.0003, descent-climb 0.0002.

**(b) Settling's reach.** Every row that reaches the water is settled as an intact impact through the real ocean (GLORYS12V1 75–115 E, 45–10 S; TEOS-10; AusSeabed then GEBCO_2026); settling bounds and sources as `results/settling-run-c/README.md` §COVERAGE (unchanged in 9330d4c). Reach gaps: **G-bf** (in-flight breakup rows are settled from the intact impact point; the fragment field along the descent is not modelled); attitude-dependent breakup (declared); impact pitch is not used (flight-path angle stand-in, gap G6). No impact was refused by the ocean window in any folder (column 'not computed' = 0).

**(c) Proposal coverage.** Row Kish ESS per product in each stratum README; gate 1,000. Products below the gate (stamped 'Not yet estimable' in the figures; NOT ASSESSED at this depth):

- waypoints: 00:19 R600 BTO + both BFOs as recorded × total × A1 (row ESS 368)
- free: 00:19 R600 BTO + both BFOs as recorded × total × A1 (row ESS 51)
- free: 00:19 R600 BTO + both BFOs as recorded × total × A2 (row ESS 843)
- free: 00:19 R600 BTO + both BFOs as recorded × total × B (row ESS 591)
- free: 00:19 R600 BTO + both BFOs, Holland transient bias added × total × A1 (row ESS 271)
- free: 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added × total × A1 (row ESS 279)
- descent-climb: 00:19 R600 BTO + both BFOs as recorded × total × A1 (row ESS 62)
- descent-climb: 00:19 R600 BTO + both BFOs as recorded × total × B (row ESS 693)
- descent-climb: 00:19 R600 BTO + both BFOs, Holland transient bias added × total × A1 (row ESS 321)
- descent-climb: 00:19 R600 BTO + both BFOs, Holland transient bias added × total × B (row ESS 749)
- descent-climb: 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added × total × A1 (row ESS 366)
- repro-radar: 00:19 R600 BTO + both BFOs as recorded × total × A1 (row ESS 73)
- repro-radar: 00:19 R600 BTO + both BFOs as recorded × total × B (row ESS 597)
- repro-radar: 00:19 R600 BTO + both BFOs, Holland transient bias added × total × A1 (row ESS 357)
- repro-radar: 00:19 R600 BTO + both BFOs, Holland transient bias added × C2 silent × all (row ESS 893)
- repro-radar: 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added × total × A1 (row ESS 335)
- both-burst (waypoints): 00:19 R600 BTO + both BFOs as recorded × total × A1 (row ESS 409)

Status: the primary cell (both causes) and both single-cause cells of every 00:19 treatment are estimable in every stratum, with one exception: repro-radar D4 × C2 silent (row ESS 893). Waypoints (core share 0.9982) has a single gap, A1 under both BFOs as recorded (D3, row ESS 368; 409 on the both-burst set). In free, descent-climb and repro-radar, A1 falls below the gate under D3, D4 and D5, and B under D3 (also A2 under D3 in free, and B under D4 in descent-climb). Compared with run I, the C2-silent gaps under D3 and D5 are closed in all four strata and the waypoints D3 B and D5 A1 gaps are closed. These are proposal-coverage gaps of end of flight (thin A1 mass under the two-BFO likelihoods); settling cannot close them. They are reported, not dropped. The both-burst set raises D3/D4 row ESS on waypoints only modestly (see §1) and does not close the D3 × A1 gap.

**Route to close the A1 × D3 gap.** End of flight's A1-branch conditional pass (`end-of-flight/run-j-a1branch`, commit 4605cc21, A1 under D3 ESS 5,282, stratified estimator) is the natural input; settling can settle it with the same driver once its row-mass recipe (stratified weights) is confirmed. Not done in this pass (not in this work order).

**Settling's parameter bounds.** Unchanged from run I (9330d4c); element classes, sink rates and breakup table with sources in `results/settling-run-c/README.md` §COVERAGE. Breakup table PROVISIONAL.

## Figures

- `waypoints`: `settling-seabed-wreckage-run-j-waypoints-{core,cause,family}.png`
- `free`: `settling-seabed-wreckage-run-j-free-{core,cause,family}.png`
- `descent-climb`: `settling-seabed-wreckage-run-j-descent-climb-{core,cause,family}.png`
- `repro-radar`: `settling-seabed-wreckage-run-j-repro-radar-{core,cause,family}.png`
- `both-burst (waypoints)`: `settling-seabed-wreckage-run-j-both-burst-waypoints-{core,cause,family}.png`

## Deviations

- Run I seed reproduction not done (run I end-of-flight inputs no longer on disk); replaced by the exact ln Z reproduction against end of flight's published run J tables and the element checks above.
- Both-burst supplement: D2–D5 products only (the thinning keeps rows for the burst likelihoods, so D0/D1 are not represented with useful ESS there); emitted as its own folder, used beside run-j-waypoints and not pooled with it (as searched areas did). EoF's 24 + 8 pooled table was not used for resampling.
- Sample sizes as run I (N = 40,000 per total, 10,000 per family, 20,000 per cause), not scaled with the larger seed counts; row ESS is reported per product.
- Validation files (tag rjv_free, 2.0 GB) remain in the work directory /Users/pete/Downloads/mh370-settling-work-j (nothing under /Users/pete is deleted by this module).

- Ocean Settling, 2026-10-18 06:20Z
