# Ocean settling on end of flight's run I — seabed wreckage per stratum (PROVISIONAL, NOT CONVERGED)

Settling `hypothesis/settling` 9330d4c (real ocean). End-of-flight tools f7f54dd0 (`smoke/option_table_0019.py`), binary mh370-eof-ri1. Samples: `mh370-exchange/settling/run-i/<stratum>/` (README.txt with COVERAGE, SHA256SUMS, READY); mixture weights `settling/run-i/stratum-mixture-weights.json`.

**Labels (carry on every result):** core run I split-half NOT converged (waypoints 0.916 against floor 0.924); piloted-turn model and INTERIM pitch-down PROVISIONAL; in-flight structural outcome PROVISIONAL; breakup rows settled from the intact impact point (gap G-bf); P(left) = 0.8 PROVISIONAL; D4/D5 "Holland transient bias added". Each stratum is CONDITIONAL on itself.

**Method.** Row mass = end of flight's 00:19 two-factor table (`seed_terms`): hand-off weight / sum / K × (1 − P(breakup by 00:19:37)) × L(D) × L(cause). Primary cell: both log-on causes, q = 1/3 = prior odds C2:C1, so P(C1) = 0.75, P(C2) = 0.25, C2 silent (W = 00:10:58–01:15:56). Per-cell per-seed ln Z equals `seed_terms` to ≤ 7e-15 in every seed of every stratum. Each product is a systematic resample over all rows of 8 seeds, one settling draw each (40,000 per total, 10,000 per family, 20,000 per cause).

## 1. 90 % seabed area (thousand km²), primary cell, by stratum

| 00:19 data treatment | next-i-waypoints | next-i-free | next-i-descent-climb | next-i-repro-radar | core-share mixture weights (wp / free / d-c / r-r) |
|---|---|---|---|---|---|
| 00:19 Held Out | 151.2 (ESS 820,912) | 228.0 (ESS 743,901) | 250.3 (ESS 532,835) | 370.1 (ESS 466,331) | 0.9984 / 0.0011 / 0.0001 / 0.0003 |
| 00:19 R600 BTO Only | 115.8 (ESS 830,734) | 160.7 (ESS 814,396) | 182.9 (ESS 581,741) | 246.8 (ESS 555,722) | 0.9985 / 0.0011 / 0.0001 / 0.0003 |
| 00:19 R600 BTO + Raw BFO | 107.9 (ESS 63,543) | 133.0 (ESS 73,370) | 171.8 (ESS 37,516) | 227.2 (ESS 40,033) | 0.9982 / 0.0015 / 0.0001 / 0.0003 |
| 00:19 R600 BTO + both BFOs as recorded | 62.8 (ESS 2,169) | 98.1 (ESS 2,430) | 109.2 (ESS 1,538) | 137.2 (ESS 1,276) | 0.9983 / 0.0013 / 0.0001 / 0.0003 |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | 65.7 (ESS 10,839) | 94.3 (ESS 10,710) | 114.0 (ESS 7,403) | 152.0 (ESS 6,622) | 0.9985 / 0.0011 / 0.0001 / 0.0003 |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | 64.8 (ESS 4,055) | 88.9 (ESS 7,031) | 110.4 (ESS 3,772) | 138.2 (ESS 2,772) | 0.9982 / 0.0014 / 0.0001 / 0.0003 |

Settling adds 0.1–1.5 % to the 90 % area in every estimable product (up to 1.9 % in products below the gate); settled-offset p90 1.9–4.7 km (README tables). n.e. = not estimable (row Kish ESS < 1,000). Mixture weights = core share × Z_s(cell), normalised; core shares are themselves NOT converged.

## 2. Log-on cause (posterior share within the treatment = prior p × Z ratio; 90 % area)

| 00:19 data treatment | stratum | C1 fuel-exhaustion share | C1 area | C2 silent share | C2 silent area |
|---|---|---|---|---|---|
| 00:19 Held Out | next-i-waypoints | 99.7 % | 150.5 | 0.3 % (ESS 341,686) | 229.7 |
| 00:19 Held Out | next-i-free | 99.6 % | 231.3 | 0.4 % (ESS 329,188) | 357.4 |
| 00:19 Held Out | next-i-descent-climb | 99.3 % | 245.5 | 0.7 % (ESS 365,770) | 404.4 |
| 00:19 Held Out | next-i-repro-radar | 99.5 % | 360.8 | 0.5 % (ESS 278,856) | 438.6 |
| 00:19 R600 BTO Only | next-i-waypoints | 99.7 % | 114.3 | 0.3 % (ESS 349,136) | 155.9 |
| 00:19 R600 BTO Only | next-i-free | 99.7 % | 163.3 | 0.3 % (ESS 358,062) | 240.2 |
| 00:19 R600 BTO Only | next-i-descent-climb | 99.4 % | 183.8 | 0.6 % (ESS 414,822) | 290.3 |
| 00:19 R600 BTO Only | next-i-repro-radar | 99.5 % | 241.6 | 0.5 % (ESS 314,505) | 283.4 |
| 00:19 R600 BTO + Raw BFO | next-i-waypoints | 99.8 % | 106.9 | 0.1 % (ESS 10,222) | 90.2 |
| 00:19 R600 BTO + Raw BFO | next-i-free | 99.9 % | 133.4 | 0.1 % (ESS 11,119) | 146.5 |
| 00:19 R600 BTO + Raw BFO | next-i-descent-climb | 99.8 % | 168.6 | 0.2 % (ESS 7,092) | 163.1 |
| 00:19 R600 BTO + Raw BFO | next-i-repro-radar | 99.8 % | 227.0 | 0.2 % (ESS 7,071) | 158.5 |
| 00:19 R600 BTO + both BFOs as recorded | next-i-waypoints | 99.9 % | 62.1 | 0.1 % (ESS 275) | 55.1 (n.e.) |
| 00:19 R600 BTO + both BFOs as recorded | next-i-free | 99.9 % | 98.2 | 0.1 % (ESS 259) | 96.6 (n.e.) |
| 00:19 R600 BTO + both BFOs as recorded | next-i-descent-climb | 99.8 % | 108.8 | 0.2 % (ESS 354) | 91.8 (n.e.) |
| 00:19 R600 BTO + both BFOs as recorded | next-i-repro-radar | 99.9 % | 136.3 | 0.1 % (ESS 312) | 93.4 (n.e.) |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | next-i-waypoints | 99.9 % | 65.6 | 0.1 % (ESS 1,422) | 62.9 |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | next-i-free | 99.9 % | 94.5 | 0.1 % (ESS 1,260) | 100.7 |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | next-i-descent-climb | 99.8 % | 113.5 | 0.2 % (ESS 1,659) | 107.0 |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | next-i-repro-radar | 99.8 % | 151.8 | 0.2 % (ESS 1,239) | 110.7 |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | next-i-waypoints | 99.9 % | 64.8 | 0.1 % (ESS 831) | 59.6 (n.e.) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | next-i-free | 99.9 % | 88.6 | 0.1 % (ESS 774) | 93.0 (n.e.) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | next-i-descent-climb | 99.8 % | 110.4 | 0.2 % (ESS 942) | 104.7 (n.e.) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | next-i-repro-radar | 99.9 % | 137.8 | 0.1 % (ESS 720) | 103.7 (n.e.) |

## 3. Flight-end family (share within the treatment; 90 % area)

| 00:19 data treatment | stratum | A1 | A2 | B |
|---|---|---|---|---|
| 00:19 Held Out | next-i-waypoints | 18.9 %, 63.0 (ESS 170,184) | 41.0 %, 148.3 (ESS 443,379) | 40.0 %, 159.9 (ESS 254,298) |
| 00:19 Held Out | next-i-free | 19.4 %, 101.7 (ESS 162,226) | 41.8 %, 208.3 (ESS 408,541) | 38.6 %, 258.4 (ESS 218,436) |
| 00:19 Held Out | next-i-descent-climb | 17.0 %, 121.9 (ESS 106,118) | 37.0 %, 242.8 (ESS 286,656) | 45.8 %, 267.4 (ESS 186,801) |
| 00:19 Held Out | next-i-repro-radar | 16.8 %, 197.0 (ESS 84,981) | 37.7 %, 378.1 (ESS 247,832) | 45.4 %, 351.5 (ESS 166,417) |
| 00:19 R600 BTO Only | next-i-waypoints | 16.7 %, 36.4 (ESS 164,832) | 41.7 %, 113.8 (ESS 498,038) | 41.4 %, 119.6 (ESS 251,024) |
| 00:19 R600 BTO Only | next-i-free | 18.4 %, 50.7 (ESS 153,300) | 44.8 %, 159.7 (ESS 434,948) | 36.7 %, 176.2 (ESS 246,985) |
| 00:19 R600 BTO Only | next-i-descent-climb | 15.9 %, 61.8 (ESS 105,250) | 39.0 %, 184.5 (ESS 327,332) | 45.0 %, 191.9 (ESS 199,633) |
| 00:19 R600 BTO Only | next-i-repro-radar | 14.5 %, 104.8 (ESS 86,607) | 37.8 %, 255.3 (ESS 324,209) | 47.6 %, 227.2 (ESS 203,054) |
| 00:19 R600 BTO + Raw BFO | next-i-waypoints | 25.3 %, 28.7 (ESS 15,700) | 31.5 %, 122.8 (ESS 31,791) | 43.0 %, 109.4 (ESS 21,711) |
| 00:19 R600 BTO + Raw BFO | next-i-free | 24.1 %, 34.2 (ESS 17,296) | 47.8 %, 128.5 (ESS 35,412) | 27.9 %, 161.9 (ESS 20,527) |
| 00:19 R600 BTO + Raw BFO | next-i-descent-climb | 20.5 %, 54.9 (ESS 8,045) | 30.4 %, 187.6 (ESS 17,454) | 49.0 %, 175.0 (ESS 14,868) |
| 00:19 R600 BTO + Raw BFO | next-i-repro-radar | 20.4 %, 82.5 (ESS 7,559) | 32.4 %, 251.0 (ESS 18,059) | 47.1 %, 216.4 (ESS 16,223) |
| 00:19 R600 BTO + both BFOs as recorded | next-i-waypoints | 16.3 %, 26.3 (n.e.) (ESS 352) | 40.2 %, 58.6 (ESS 1,392) | 43.3 %, 59.8 (n.e.) (ESS 698) |
| 00:19 R600 BTO + both BFOs as recorded | next-i-free | 16.4 %, 44.5 (n.e.) (ESS 290) | 50.2 %, 80.7 (ESS 1,532) | 33.2 %, 104.7 (n.e.) (ESS 718) |
| 00:19 R600 BTO + both BFOs as recorded | next-i-descent-climb | 13.8 %, 42.5 (n.e.) (ESS 279) | 37.5 %, 100.1 (n.e.) (ESS 889) | 48.6 %, 107.9 (n.e.) (ESS 557) |
| 00:19 R600 BTO + both BFOs as recorded | next-i-repro-radar | 12.6 %, 52.7 (n.e.) (ESS 267) | 37.6 %, 125.2 (n.e.) (ESS 796) | 49.6 %, 128.2 (n.e.) (ESS 450) |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | next-i-waypoints | 15.1 %, 34.1 (ESS 1,362) | 41.3 %, 56.2 (ESS 6,895) | 43.6 %, 63.9 (ESS 3,731) |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | next-i-free | 16.8 %, 40.5 (ESS 1,483) | 44.0 %, 84.9 (ESS 6,172) | 39.1 %, 100.2 (ESS 3,554) |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | next-i-descent-climb | 12.4 %, 53.0 (n.e.) (ESS 816) | 39.8 %, 104.2 (ESS 4,615) | 47.7 %, 119.2 (ESS 2,780) |
| 00:19 R600 BTO + both BFOs, Holland transient bias added | next-i-repro-radar | 13.1 %, 81.6 (n.e.) (ESS 577) | 37.0 %, 150.5 (ESS 4,642) | 49.8 %, 132.2 (ESS 2,700) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | next-i-waypoints | 14.6 %, 28.8 (n.e.) (ESS 253) | 38.6 %, 57.4 (ESS 3,170) | 46.7 %, 59.9 (ESS 1,887) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | next-i-free | 13.1 %, 40.8 (n.e.) (ESS 926) | 54.7 %, 75.3 (ESS 4,104) | 32.1 %, 108.5 (ESS 2,031) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | next-i-descent-climb | 12.1 %, 47.7 (n.e.) (ESS 482) | 38.1 %, 102.8 (ESS 2,185) | 49.7 %, 110.3 (ESS 1,469) |
| 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | next-i-repro-radar | 11.5 %, 84.3 (n.e.) (ESS 542) | 37.3 %, 130.3 (ESS 2,351) | 51.0 %, 123.7 (n.e.) (ESS 940) |

## COVERAGE

**(a) Feasible set.** As end of flight's run I note: piloted dives to about 40,000 ft/min, unloading, speeds past VMO/MMO, piloted turns, in-flight structural damage or breakup; four strata (waypoint routes, free flight, descent-climb, Davey dynamics with radar). Core shares (equal prior): waypoints 0.9982, free 0.0011, descent-climb 0.0002, repro-radar 0.0004.

**(b) Settling's reach.** Every row that reaches the water is settled as an intact impact through the real ocean (GLORYS12V1 75–115 E, 45–10 S; TEOS-10; AusSeabed then GEBCO_2026); settling bounds and sources as `results/settling-run-c/README.md` §COVERAGE (unchanged in 9330d4c). Reach gaps: **G-bf** (in-flight breakup rows are settled from the intact impact point; the fragment field along the descent is not modelled; waits for end of flight's 1(B) columns); attitude-dependent breakup (declared). No impact was refused by the ocean window in any stratum (column 'not computed' = 0).

**(c) Proposal coverage.** Row Kish ESS per product in each stratum README; gate 1,000. Products below the gate (stamped 'Not yet estimable' in the figures; NOT ASSESSED at this depth):

- next-i-waypoints: 00:19 R600 BTO + both BFOs as recorded × total × A1 (row ESS 352)
- next-i-waypoints: 00:19 R600 BTO + both BFOs as recorded × total × B (row ESS 698)
- next-i-waypoints: 00:19 R600 BTO + both BFOs as recorded × C2 silent × all (row ESS 275)
- next-i-waypoints: 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added × total × A1 (row ESS 253)
- next-i-waypoints: 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added × C2 silent × all (row ESS 831)
- next-i-free: 00:19 R600 BTO + both BFOs as recorded × total × A1 (row ESS 290)
- next-i-free: 00:19 R600 BTO + both BFOs as recorded × total × B (row ESS 718)
- next-i-free: 00:19 R600 BTO + both BFOs as recorded × C2 silent × all (row ESS 259)
- next-i-free: 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added × total × A1 (row ESS 926)
- next-i-free: 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added × C2 silent × all (row ESS 774)
- next-i-descent-climb: 00:19 R600 BTO + both BFOs as recorded × total × A1 (row ESS 279)
- next-i-descent-climb: 00:19 R600 BTO + both BFOs as recorded × total × A2 (row ESS 889)
- next-i-descent-climb: 00:19 R600 BTO + both BFOs as recorded × total × B (row ESS 557)
- next-i-descent-climb: 00:19 R600 BTO + both BFOs as recorded × C2 silent × all (row ESS 354)
- next-i-descent-climb: 00:19 R600 BTO + both BFOs, Holland transient bias added × total × A1 (row ESS 816)
- next-i-descent-climb: 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added × total × A1 (row ESS 482)
- next-i-descent-climb: 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added × C2 silent × all (row ESS 942)
- next-i-repro-radar: 00:19 R600 BTO + both BFOs as recorded × total × A1 (row ESS 267)
- next-i-repro-radar: 00:19 R600 BTO + both BFOs as recorded × total × A2 (row ESS 796)
- next-i-repro-radar: 00:19 R600 BTO + both BFOs as recorded × total × B (row ESS 450)
- next-i-repro-radar: 00:19 R600 BTO + both BFOs as recorded × C2 silent × all (row ESS 312)
- next-i-repro-radar: 00:19 R600 BTO + both BFOs, Holland transient bias added × total × A1 (row ESS 577)
- next-i-repro-radar: 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added × total × A1 (row ESS 542)
- next-i-repro-radar: 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added × total × B (row ESS 940)
- next-i-repro-radar: 00:19 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added × C2 silent × all (row ESS 720)

Status: the primary cell (both causes) of every 00:19 treatment is estimable in every stratum (lowest row ESS 1,276: R600 BTO + both BFOs as recorded, repro-radar). The gaps sit in the two-BFO treatments: under both BFOs as recorded (Holland H2 data) the C2-silent cell and the A1 and B families fall below the gate in all four strata, and A2 also in descent-climb and repro-radar; under D5 the A1 family and the C2-silent cell fall below it in all four strata (and B in repro-radar); under both BFOs with Holland transient bias added (Holland H1 data) A1 falls below it in descent-climb and repro-radar. These are proposal-coverage gaps of end of flight (more A1 / C2-silent mass under the two-BFO likelihoods); settling cannot close them. They are reported, not dropped.

## Figures

- `next-i-waypoints`: `settling-seabed-wreckage-run-i-waypoints-{core,cause,family}.png`
- `next-i-free`: `settling-seabed-wreckage-run-i-free-{core,cause,family}.png`
- `next-i-descent-climb`: `settling-seabed-wreckage-run-i-descent-climb-{core,cause,family}.png`
- `next-i-repro-radar`: `settling-seabed-wreckage-run-i-repro-radar-{core,cause,family}.png`

- Ocean Settling, 2026-10-12 19:55Z
