Checks: production rows 153,599,936 (24 seeds), pass rows 13,398,857 (8 seeds); impact-point ln L against the published run J column: max |Δ| 3.6e-15 (float64), 2.4e-07 (float32 columns); per-seed ln Z against option_table_0019 max |Δ| 3.6e-15; SCALE 0.141077 (settling 0.141077); P_D0'(branch) 0.093481. Settled point arm against the impact-point columns max |Δ ln L| 2.2e-15; 16,248,867 settled elements, 287,137 outcomes, 0 carried.

**Table 1. The gate: A1 (cruise to fuel exhaustion, then no control) after the searches, run J against the A1-branch stratified estimate.**

| 00:19 treatment | run J impact point: row ESS after (source) | stratified impact point: row ESS before / after | parents after | settled: row ESS before (settling) | settled: distinct-row ESS after | gate 500 / 1,000 |
|---|---|---|---|---|---|---|
| D0' 00:19 held out | 199,190 (production) | 658,188 / **141,664** | 29,601 | 658,188 | 4,251 | met / met |
| D1 R600 BTO only | 1,287,554 (production) | 823,034 / **905,822** | 197,143 | 823,034 | 6,584 | met / met |
| D2 R600 BTO + BFO as recorded | 45,373 (production) | 41,988 / **40,990** | 28,545 | 41,988 | 8,820 | met / met |
| D3 both BFOs as recorded | 401 (both-burst) | 5,283 / **4,763** | 4,367 | 5,283 | 4,260 | met / met |
| D4 both BFOs, Holland transient bias added | 2,902 (both-burst) | 11,395 / **7,178** | 5,730 | 11,395 | 4,620 | met / met |
| D5 R600 BFO + R1200 BFO, Holland transient bias added | 1,838 (production) | 2,920 / **2,690** | 2,558 | 2,920 | 2,508 | met / met |

**Table 2. Impact point, waypoints stratum, base, rho 0.05: Z and the share on searched ground, run J against the stratified estimate.**

| 00:19 treatment | family | Z run J | Z stratified (seed SE) | Z, EoF normalisation | on searched ground before → after, run J | before → after, stratified | share before → after, stratified |
|---|---|---|---|---|---|---|---|
| D0' 00:19 held out | all | 0.3101 | 0.3105 | 0.3105 | 0.771 → 0.284 | 0.770 → 0.284 | 1 → 1 |
|  | A1 | 0.1328 | 0.1357 (0.0031) | same | 0.967 → 0.775 | 0.964 → 0.756 | 0.1722 → 0.0752 (EoF 0.1722 → 0.0752) |
|  | A2 | 0.3430 | 0.3430 | same | 0.734 → 0.244 | 0.734 → 0.244 | 0.3427 → 0.3785 (EoF 0.3427 → 0.3785) |
|  | B | 0.3497 | 0.3497 | same | 0.727 → 0.246 | 0.727 → 0.246 | 0.4851 → 0.5462 (EoF 0.4851 → 0.5462) |
| D1 R600 BTO only | all | 0.2744 | 0.2753 | 0.2754 | 0.810 → 0.329 | 0.809 → 0.328 | 1 → 1 |
|  | A1 | 0.1112 | 0.1133 (0.0015) | same | 0.991 → 0.929 | 0.988 → 0.910 | 0.1968 → 0.0810 (EoF 0.1962 → 0.0807) |
|  | A2 | 0.3236 | 0.3236 | same | 0.755 → 0.262 | 0.755 → 0.262 | 0.3472 → 0.4081 (EoF 0.3474 → 0.4082) |
|  | B | 0.3084 | 0.3084 | same | 0.772 → 0.289 | 0.772 → 0.289 | 0.4560 → 0.5109 (EoF 0.4563 → 0.5111) |
| D2 R600 BTO + BFO as recorded | all | 0.2110 | 0.2113 | 0.2115 | 0.881 → 0.467 | 0.880 → 0.466 | 1 → 1 |
|  | A1 | 0.1050 | 0.1049 (0.0006) | same | 0.997 → 0.987 | 0.998 → 0.988 | 0.2354 → 0.1169 (EoF 0.2346 → 0.1164) |
|  | A2 | 0.2465 | 0.2465 | same | 0.842 → 0.397 | 0.842 → 0.397 | 0.2347 → 0.2737 (EoF 0.2349 → 0.2739) |
|  | B | 0.2430 | 0.2430 | same | 0.845 → 0.398 | 0.845 → 0.398 | 0.5299 → 0.6094 (EoF 0.5305 → 0.6097) |
| D3 both BFOs as recorded | all | 0.1506 | 0.1506 | 0.1507 | 0.948 → 0.685 | 0.948 → 0.689 | 1 → 1 |
|  | A1 | 0.1054 | 0.1052 (0.0010) | same | 0.997 → 0.988 | 0.997 → 0.986 | 0.0860 → 0.0600 (EoF 0.0851 → 0.0594) |
|  | A2 | 0.1454 | 0.1439 | same | 0.953 → 0.709 | 0.955 → 0.721 | 0.4093 → 0.3909 (EoF 0.4097 → 0.3911) |
|  | B | 0.1607 | 0.1639 | same | 0.936 → 0.641 | 0.933 → 0.634 | 0.5047 → 0.5491 (EoF 0.5052 → 0.5495) |
| D4 both BFOs, Holland transient bias added | all | 0.1366 | 0.1378 | 0.1376 | 0.963 → 0.761 | 0.962 → 0.758 | 1 → 1 |
|  | A1 | 0.1097 | 0.1100 (0.0021) | same | 0.993 → 0.960 | 0.993 → 0.964 | 0.2595 → 0.2073 (EoF 0.2629 → 0.2102) |
|  | A2 | 0.1396 | 0.1409 | same | 0.960 → 0.739 | 0.958 → 0.733 | 0.3444 → 0.3523 (EoF 0.3428 → 0.3510) |
|  | B | 0.1499 | 0.1532 | same | 0.948 → 0.692 | 0.945 → 0.682 | 0.3961 → 0.4404 (EoF 0.3943 → 0.4388) |
| D5 R600 BFO + R1200 BFO, Holland transient bias added | all | 0.1436 | 0.1438 | 0.1438 | 0.955 → 0.727 | 0.955 → 0.727 | 1 → 1 |
|  | A1 | 0.1068 | 0.1051 (0.0010) | same | 0.996 → 0.975 | 0.997 → 0.989 | 0.0551 → 0.0403 (EoF 0.0548 → 0.0400) |
|  | A2 | 0.1396 | 0.1396 | same | 0.960 → 0.742 | 0.960 → 0.742 | 0.4246 → 0.4125 (EoF 0.4247 → 0.4126) |
|  | B | 0.1512 | 0.1512 | same | 0.947 → 0.696 | 0.947 → 0.696 | 0.5203 → 0.5473 (EoF 0.5205 → 0.5474) |

**Table 3. The two normalisations: end of flight's (production Z(d) in the denominator, A2/B rescaled) minus settling's single measure.**

| 00:19 treatment | A1 share before: single measure / EoF | Δ Z (all families) | Δ on searched ground after |
|---|---|---|---|
| D0' 00:19 held out | 0.1722 / 0.1722 | +0.00000 | -0.0000 |
| D1 R600 BTO only | 0.1968 / 0.1962 | +0.00011 | -0.0002 |
| D2 R600 BTO + BFO as recorded | 0.2354 / 0.2346 | +0.00012 | -0.0003 |
| D3 both BFOs as recorded | 0.0860 / 0.0851 | +0.00004 | -0.0002 |
| D4 both BFOs, Holland transient bias added | 0.2595 / 0.2629 | -0.00013 | +0.0008 |
| D5 R600 BFO + R1200 BFO, Holland transient bias added | 0.0551 / 0.0548 | +0.00001 | -0.0001 |

**Table 4. Validation: the search factor on the branch rows, production (24 seeds, branch rows only) against the pass (8 seeds).**

| 00:19 treatment | Z(branch) production (seed SE) | Z(branch) pass (seed SE) | difference / combined SE |
|---|---|---|---|
| D0' 00:19 held out | 0.1335 (0.0033) | 0.1387 (0.0050) | +0.88 |
| D1 R600 BTO only | 0.1111 (0.0012) | 0.1150 (0.0026) | +1.34 |
| D2 R600 BTO + BFO as recorded | 0.1053 (0.0005) | 0.1051 (0.0010) | -0.17 |
| D3 both BFOs as recorded | 0.1045 (0.0009) | 0.1052 (0.0010) | +0.50 |
| D4 both BFOs, Holland transient bias added | 0.1090 (0.0024) | 0.1087 (0.0025) | -0.09 |
| D5 R600 BFO + R1200 BFO, Holland transient bias added | 0.1068 (0.0010) | 0.1051 (0.0010) | -1.21 |

**Table 5. Settled seabed positions (settling run-j-a1branch products), base, rho 0.05.**

| 00:19 treatment | family | Z settled (Δ settled − point ± SE) | Z settled, run J | on searched ground after: point → settled | run J settled | settled outcomes N / distinct rows |
|---|---|---|---|---|---|---|
| D0' 00:19 held out | all | **0.3117** (+0.0012 ± 0.0001) | 0.3112 | 0.284 → 0.292 | 0.298 | 40,000 / 39,999 |
|  | A1 | **0.1364** (+0.0007 ± 0.0001) | 0.1335 | 0.759 → 0.760 | 0.768 | 10,000 / 10,000 |
| D1 R600 BTO only | all | **0.2761** (+0.0008 ± 0.0001) | 0.2751 | 0.330 → 0.338 | 0.335 | 40,000 / 40,000 |
|  | A1 | **0.1137** (+0.0004 ± 0.0000) | 0.1115 | 0.926 → 0.925 | 0.933 | 10,000 / 10,000 |
| D2 R600 BTO + BFO as recorded | all | **0.2123** (+0.0010 ± 0.0001) | 0.2122 | 0.473 → 0.483 | 0.478 | 40,000 / 38,085 |
|  | A1 | **0.1054** (+0.0004 ± 0.0000) | 0.1054 | 0.987 → 0.986 | 0.985 | 10,000 / 9,849 |
| D3 both BFOs as recorded | all | **0.1513** (+0.0006 ± 0.0001) | 0.1513 | 0.692 → 0.700 | 0.697 | 40,000 / 24,686 |
|  | A1 | **0.1055** (+0.0003 ± 0.0000) | 0.1058 | 0.986 → 0.985 | 0.987 | 10,000 / 6,795 |
| D4 both BFOs, Holland transient bias added | all | **0.1383** (+0.0006 ± 0.0001) | 0.1372 | 0.751 → 0.757 | 0.769 | 40,000 / 37,196 |
|  | A1 | **0.1106** (+0.0006 ± 0.0001) | 0.1102 | 0.963 → 0.962 | 0.962 | 10,000 / 8,950 |
| D5 R600 BFO + R1200 BFO, Holland transient bias added | all | **0.1444** (+0.0007 ± 0.0001) | 0.1441 | 0.734 → 0.741 | 0.734 | 40,000 / 32,498 |
|  | A1 | **0.1054** (+0.0003 ± 0.0000) | 0.1070 | 0.991 → 0.990 | 0.978 | 10,000 / 6,280 |

**Table 6. Per-cell detection field at the settled positions (V0 base, V1 central, V2 pessimistic, V3 optimistic): Z and on searched ground after.**

| 00:19 treatment | family | V0 | V1 central (Δ vs V0 ± SE) | V2 | V3 | on searched after V0 / V1 / V2 / V3 | run J spatial (mixture) V1 Z / on searched after |
|---|---|---|---|---|---|---|---|
| D0' 00:19 held out | all | 0.3117 | 0.3097 (-0.0020 ± 0.0002) | 0.4902 | 0.2554 | 0.292 / 0.282 / 0.542 / 0.131 | 0.3091 / 0.287 |
|  | A1 | 0.1364 | 0.1362 (-0.0002 ± 0.0004) | 0.3559 | 0.0679 | 0.760 / 0.749 / 0.902 / 0.498 | 0.1342 / 0.755 |
| D1 R600 BTO only | all | 0.2761 | 0.2730 (-0.0032 ± 0.0002) | 0.4599 | 0.2161 | 0.338 / 0.328 / 0.598 / 0.153 | 0.2723 / 0.325 |
|  | A1 | 0.1137 | 0.1128 (-0.0009 ± 0.0004) | 0.3338 | 0.0433 | 0.925 / 0.917 / 0.971 / 0.783 | 0.1113 / 0.926 |
| D2 R600 BTO + BFO as recorded | all | 0.2123 | 0.2091 (-0.0033 ± 0.0002) | 0.4123 | 0.1473 | 0.483 / 0.469 / 0.727 / 0.245 | 0.2087 / 0.465 |
|  | A1 | 0.1054 | 0.1039 (-0.0014 ± 0.0003) | 0.3267 | 0.0338 | 0.986 / 0.986 / 0.995 / 0.958 | 0.1044 / 0.981 |
| D3 both BFOs as recorded | all | 0.1513 | 0.1473 (-0.0039 ± 0.0002) | 0.3657 | 0.0812 | 0.700 / 0.689 / 0.871 / 0.438 | 0.1477 / 0.689 |
|  | A1 | 0.1055 | 0.1057 (+0.0002 ± 0.0004) | 0.3312 | 0.0349 | 0.985 / 0.981 / 0.993 / 0.944 | 0.1072 / 0.971 |
| D4 both BFOs, Holland transient bias added | all | 0.1383 | 0.1366 (-0.0017 ± 0.0002) | 0.3599 | 0.0688 | 0.757 / 0.747 / 0.899 / 0.507 | 0.1358 / 0.760 |
|  | A1 | 0.1106 | 0.1129 (+0.0023 ± 0.0005) | 0.3396 | 0.0420 | 0.962 / 0.938 / 0.976 / 0.842 | 0.1135 / 0.941 |
| D5 R600 BFO + R1200 BFO, Holland transient bias added | all | 0.1444 | 0.1408 (-0.0036 ± 0.0002) | 0.3617 | 0.0741 | 0.741 / 0.730 / 0.891 / 0.489 | 0.1409 / 0.723 |
|  | A1 | 0.1054 | 0.1049 (-0.0005 ± 0.0004) | 0.3308 | 0.0343 | 0.990 / 0.988 / 0.995 / 0.964 | 0.1065 / 0.971 |

**Table 7. A1 under the both-frequency treatments: rho sweep and the sensitivity without Ocean Infinity (stratified).**

| 00:19 treatment | case | Z impact point | row ESS after | Z settled | on searched ground after, settled |
|---|---|---|---|---|---|
| D3 both BFOs as recorded | base, rho 0.05 | 0.1052 | 4,763 | 0.1055 | 0.985 |
|  | base, rho 0 | 0.0581 | 3,788 | 0.0584 | 0.975 |
|  | base, rho 0.25 | 0.2936 | 5,236 | 0.2938 | 0.994 |
|  | base, rho 0.5 | 0.5290 | 5,276 | 0.5292 | 0.996 |
|  | sensitivity: without Ocean Infinity | 0.1144 | 2,866 | 0.1146 | 0.978 |
| D4 both BFOs, Holland transient bias added | base, rho 0.05 | 0.1100 | 7,178 | 0.1106 | 0.962 |
|  | base, rho 0 | 0.0632 | 4,287 | 0.0638 | 0.937 |
|  | base, rho 0.25 | 0.2974 | 10,427 | 0.2979 | 0.983 |
|  | base, rho 0.5 | 0.5316 | 11,095 | 0.5319 | 0.989 |
|  | sensitivity: without Ocean Infinity | 0.1367 | 1,654 | 0.1371 | 0.947 |
| D5 R600 BFO + R1200 BFO, Holland transient bias added | base, rho 0.05 | 0.1051 | 2,690 | 0.1054 | 0.990 |
|  | base, rho 0 | 0.0580 | 2,303 | 0.0583 | 0.984 |
|  | base, rho 0.25 | 0.2935 | 2,886 | 0.2938 | 0.995 |
|  | base, rho 0.5 | 0.5290 | 2,911 | 0.5292 | 0.997 |
|  | sensitivity: without Ocean Infinity | 0.1165 | 1,012 | 0.1167 | 0.980 |

**Table 8. The other families under the both-frequency treatments (impact point, stratified measure; unchanged rows from production).**

| 00:19 treatment | A2 row ESS after | B row ESS after | all families row ESS after | run J (both-burst for D3/D4) A2 / B / all |
|---|---|---|---|---|
| D3 both BFOs as recorded | 2,083 | 773 | 2,154 | 2,581 / 499 / 1,336 |
| D4 both BFOs, Holland transient bias added | 12,482 | 6,895 | 22,695 | 19,336 / 10,418 / 24,504 |
| D5 R600 BFO + R1200 BFO, Holland transient bias added | 7,637 | 3,462 | 9,142 | 7,637 / 3,462 / 9,188 |
