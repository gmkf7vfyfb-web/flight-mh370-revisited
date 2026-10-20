**Table 1. D0' (00:19 values held out, transmission imposed) per family folder, base, rho 0.05.**

| family | P(family), core | seeds | rows | Z | Z split-half | Z without OI (sens.) | on searched ground before → after | ATSB ground before → after | in next OI area before → after (layer) | ESS before / after |
|---|---|---|---|---|---|---|---|---|---|---|
| run-j-waypoints | 0.9982 | 24 | 153,599,936 | 0.3101 | 0.3088 / 0.3113 | 0.3501 | 0.771 → 0.284 | 0.724 → 0.245 | 0.005 → 0.016 | 1,941,487 / 860,901 |
| run-j-free | 0.0013 | 18 | 57,600,064 | 0.3744 | 0.3743 / 0.3744 | 0.4497 | 0.701 → 0.237 | 0.613 → 0.176 | 0.010 → 0.025 | 384,629 / 174,307 |
| run-j-descent-climb | 0.0002 | 16 | 51,200,064 | 0.3475 | 0.3603 / 0.3362 | 0.3998 | 0.730 → 0.251 | 0.669 → 0.204 | 0.007 → 0.020 | 397,767 / 165,088 |
| run-j-repro-radar | 0.0003 | 16 | 51,199,904 | 0.3749 | 0.3825 / 0.3682 | 0.4433 | 0.700 → 0.231 | 0.620 → 0.176 | 0.009 → 0.023 | 330,094 / 141,825 |

**Table 2. D0', four-family mixture (core P(family)): the rho sweep and the sensitivity without Ocean Infinity.**

| case | Z | ln Z | on searched ground before → after | ATSB ground before → after | in next OI area before → after (layer) | north of 33 S before → after | ESS after |
|---|---|---|---|---|---|---|---|
| base, rho 0.05 (reference) | 0.3101 | -1.171 | 0.771 → 0.284 | 0.724 → 0.245 | 0.005 → 0.016 | 0.032 → 0.068 | 863,670 |
| base, rho 0 | 0.2738 | -1.295 | 0.771 → 0.191 | 0.724 → 0.153 | 0.005 → 0.018 | 0.032 → 0.075 | 696,181 |
| base, rho 0.25 | 0.4554 | -0.787 | 0.771 → 0.509 | 0.724 → 0.466 | 0.005 → 0.011 | 0.032 → 0.051 | 1,444,729 |
| base, rho 0.5 | 0.6369 | -0.451 | 0.771 → 0.646 | 0.724 → 0.601 | 0.005 → 0.008 | 0.032 → 0.041 | 1,817,992 |
| sensitivity: without Ocean Infinity, rho 0.05 | 0.3502 | -1.049 | 0.771 → 0.350 | 0.724 → 0.217 | 0.005 → 0.014 | 0.032 → 0.091 | 791,498 |

**Table 3. D0', mixture, by hypothesis family (A1 / A2 / B), base, rho 0.05.**

| family | share before | share after | Z | on searched ground before → after | in next OI area after (layer) | ESS before / after |
|---|---|---|---|---|---|---|
| A1 | 0.172 | 0.074 | 0.1329 | 0.967 → 0.774 | 0.018 | 999,271 / 199,740 |
| A2 | 0.343 | 0.379 | 0.3431 | 0.734 → 0.244 | 0.011 | 744,403 / 426,460 |
| B | 0.485 | 0.547 | 0.3498 | 0.727 → 0.246 | 0.018 | 721,538 / 377,262 |

**Table 4. All six 00:19 options, mixture, base, rho 0.05** († D3/D4: waypoints from the both-burst supplementary set).

| option | Z | Z without OI (sens.) | on searched ground before → after | in next OI area after (layer) | ESS before / after | ESS after A1 / A2 / B |
|---|---|---|---|---|---|---|
| D0' held out | 0.3101 | 0.3502 | 0.771 → 0.284 | 0.016 | 1,946,710 / 863,670 | 199,740 / 426,460 / 377,262 |
| D1 R600 BTO | 0.2745 | 0.3048 | 0.810 → 0.329 | 0.005 | 2,145,061 / 1,176,680 | 1,289,914 / 704,141 / 429,711 |
| D2 R600 BTO + BFO | 0.2110 | 0.2469 | 0.881 → 0.467 | 0.007 | 92,216 / 35,135 | 45,450 / 12,846 / 16,560 |
| D3 both BFOs (H2 data)† | 0.1507 | 0.1770 | 0.947 → 0.685 | 0.002 | 6,348 / 1,340 | 402 / 2,587 / 500 |
| D4 shared offset (H1 data)† | 0.1366 | 0.1609 | 0.963 → 0.761 | 0.003 | 44,422 / 24,571 | 2,909 / 19,387 / 10,449 |
| D5 R1200 BFO with offset | 0.1437 | 0.1728 | 0.955 → 0.727 | 0.005 | 25,943 / 9,213 | 1,841 / 7,655 / 3,472 |

**Table 5. D0' per family folder, Z over the rho sweep (base).**

| family | rho 0 | rho 0.05 | rho 0.25 | rho 0.5 | between-seed SD of Z (rho 0.05) |
|---|---|---|---|---|---|
| run-j-waypoints | 0.2737 | 0.3101 | 0.4553 | 0.6369 | 0.0215 |
| run-j-free | 0.3414 | 0.3744 | 0.5061 | 0.6707 | 0.0217 |
| run-j-descent-climb | 0.3131 | 0.3475 | 0.4849 | 0.6566 | 0.0338 |
| run-j-repro-radar | 0.3420 | 0.3749 | 0.5065 | 0.6710 | 0.0149 |

**Table 6. D0' per family folder and hypothesis family, base, rho 0.05: Z (ESS after).**

| family | A1 | A2 | B |
|---|---|---|---|
| run-j-waypoints | 0.1328 (199,190) | 0.3430 (425,340) | 0.3497 (375,878) |
| run-j-free | 0.2015 (25,347) | 0.3945 (57,723) | 0.3982 (100,908) |
| run-j-descent-climb | 0.1697 (30,993) | 0.3679 (71,049) | 0.3777 (84,513) |
| run-j-repro-radar | 0.2006 (25,803) | 0.3907 (62,066) | 0.4053 (70,706) |
