# Held-out level tests and level correction, version 2 (Indian Ocean primary)

3 Nov 2026. Hydroacoustics, source-grid method (X18). EXPLORATORY and UNCHECKED. Nothing is committed to GitHub.
Version 1 (all-ocean, pre-registered, FAILED): report artifact e49c9098 version b3e7a677. It is kept unchanged.
Pre-registration: artifact bba2e3a7 version a8543449.

## What changed from version 1

1. Royer 2016 station differences are now added. The Royer sound-model table (148 paths) arrived after version 1.
2. The PRIMARY model is now an Indian Ocean fit. The lead chose this (Pete delegated the call) AFTER the pre-registered all-ocean test failed. It is POST HOC.
3. Atlantic sources (ship shock trials, San Juan charge, San Juan loss event) are removed from the primary fit. The F-35A crash (Pacific) is kept as a check only.
4. The model part of the predictive spread is multiplied by 1.98. This is the smallest factor that gives held-out 90 % coverage of 80 % or more (POST HOC, as the lead directed).
5. Royer station set: the primary uses only stations where Royer reports an arrival (set A2, POST HOC). The pre-registered rule (set A1) also let in SSEIR on predicted times. Royer reports no arrival at SSEIR for events A, B, 5 and 10, and SSEIR carries seismic survey shots. The three largest Royer residuals (+22, +19, -14 dB) all use SSEIR. This rule was chosen AFTER those residuals were seen. Set A1 is reported as a sensitivity.
6. level_correction.json version 2 carries the Indian Ocean values. It keeps two alternatives: zero bias with a wide spread, and the failed all-ocean class fit.

## 1. Result in short

1. Indian Ocean primary, held out (91 bands): before inflation, mean z -0.11, SD z 1.59, coverage 73 % (P2 and P3 fail). With the spread x 1.98: mean z -0.09, SD z 1.21, coverage 80 % (all three pass, by construction of the factor).
2. The Indian Ocean correction beats no correction, but only a little: CRPS 4.76 against 4.96 dB before inflation, and 5.90 against 6.14 dB after.
3. The SUS deep charges are the ONLY Indian Ocean source with a known level. When they are held out, the training set has no absolute level. Their prediction then comes from the weak prior (sd 30 dB), so the SUS fold (100 % coverage, SD z 0.13) is not a real test of the bias. The absolute bias is therefore untested out of source.
4. The inflation is driven by the airgun rows (fold SD z 1.46, coverage 71 % after inflation). The main cause is the over-blocked path air7 to Cape Leeuwin (about 20 dB).
5. The predictive spread is large. sd_db at 10 Hz is 21-22 dB after inflation. At 25 Hz, where the data lie, it is about 20 dB. The 10 Hz bias is extrapolated from SUS bands at 16-40 Hz.
6. Royer adds little: 2 station differences in the primary set (5 in set A1). Both A2 differences lie inside their 90 % intervals.
7. With Royer added, the pre-registered all-ocean model still fails (set A1: mean z 0.60, coverage 75 %; set A2: mean z 0.88, coverage 47 %).
8. Checks: F-35A (Pacific, station difference, 8 bands) mean z -0.13, all bands inside 90 %. Airgun detection floors: log score -0.64 corrected against -0.70 uncorrected (information only).

## 2. Model choices and parameters (primary)

| Item | Value |
|---|---|
| Sound model | frozen chain tl-chain-2026-10-27, RAM, L1 seabed (GlobSed v3 over 3500 m/s basement), GEBCO 2026, WOA23 March; same as the 7th-arc dense grid and the Royer run |
| Sources | SUS 2003 route B (absolute anchor); airgun 2001 Fig. 23 shapes (level free per site); Royer 2016 differences (set A2) |
| Excluded from primary | Atlantic (ship shock trials, San Juan charge and loss event); Pacific F-35A (check only); Wake and Juan Fernandez 2008 (no paths); glass spheres |
| Correction | bias + slope x log2(f / 10 Hz); own values for a class with >= 3 Indian Ocean source events, else pooled |
| Class events (Indian Ocean) | clear deep path 8, ridge near the axis 6, ridge above the axis 1, blocked 0 |
| Variance terms (REML, all Indian Ocean units) | path offset tau 7.25 dB; band term 3.25 dB |
| Inflation | model part of the spread x 1.98 (smallest factor for coverage >= 80 %); set A1 needs x 1.18 |
| Royer energies | 5-40 Hz arrival energy, block-mean noise (amendment A1); calibration +2.9 dB Cape Leeuwin, +0.86 dB OHASISBIO; flat source energy per Hz; source depth 10 m |

Final correction (Indian Ocean primary; bias at 10 Hz):

| Class | Bias (dB) | Slope (dB/oct) | sd before inflation, 10 Hz (dB) | sd_db in JSON, 10 Hz (dB) | sd after inflation, 25 Hz (dB) | Source events | Basis |
|---|---|---|---|---|---|---|---|
| global | -8.49 ± 7.17 | 3.51 ± 1.79 | 10.70 | 21.19 | 19.59 | 15 | own fit |
| clear deep path | -14.01 ± 7.81 | 4.98 ± 2.65 | 11.14 | 22.06 | 19.78 | 8 | own fit |
| ridge near the channel axis | -1.42 ± 7.46 | 2.26 ± 2.06 | 10.90 | 21.58 | 19.95 | 6 | own fit |
| ridge above the channel axis | -8.49 ± 7.17 | 3.51 ± 1.79 | 10.70 | 21.19 | 19.59 | 1 | pooled value |
| blocked | -8.49 ± 7.17 | 3.51 ± 1.79 | 10.70 | 21.19 | 19.59 | 0 | pooled value |

Values at 25 Hz (bias + 1.32 x slope): global -3.9 dB; clear deep path -7.4 dB; ridge near the axis 1.6 dB.

Alternatives in the JSON:
- zero_bias_wide: bias 0, slope 0, sd 12.58 dB per path (POST HOC; all-ocean held-out z SD 1.0 with Royer set A1; coverage 91% over 212 rows).
- all_ocean_class_fit: version 1 values, marked FAILED.

## 3. Held-out results

| Set | Bands | Mean z | SD z | 90 % cover | CRPS corrected | CRPS uncorrected | P1 / P2 / P3 |
|---|---|---|---|---|---|---|---|
| Indian Ocean primary, before inflation | 91 | -0.11 | 1.59 | 73% | 4.76 | 4.96 | PASS / FAIL / FAIL |
| Indian Ocean primary, spread x 1.98 | 91 | -0.09 | 1.21 | 80% | 5.90 | 6.14 | PASS / PASS / PASS |
| Indian Ocean, Royer A1 set, before inflation | 94 | -0.09 | 1.32 | 78% | 4.60 | 4.93 | PASS / PASS / FAIL |
| Indian Ocean, Royer A1 set, spread x 1.18 | 94 | -0.08 | 1.25 | 81% | 4.74 | 5.08 | PASS / PASS / PASS |
| All oceans (pre-registered) + Royer A1 | 280 | 0.60 | 1.28 | 75% | 8.50 | 7.20 | FAIL / PASS / FAIL |
| All oceans (pre-registered) + Royer A2 | 277 | 0.88 | 1.54 | 47% | 10.19 | 7.28 | FAIL / FAIL / FAIL |

Indian Ocean primary by hold-out unit and by path class (spread x 1.98):

| Set | Bands | Mean z | SD z | 90 % cover | CRPS corrected | CRPS uncorrected | P1 / P2 / P3 |
|---|---|---|---|---|---|---|---|
| SUS 2003 | 26 | -0.09 | 0.13 | 100% | 10.23 | 10.01 | PASS / FAIL / FAIL |
| Airguns 2001 | 63 | -0.09 | 1.46 | 71% | 4.11 | 4.54 | PASS / FAIL / FAIL |
| Royer event A | 1 | -0.36 | nan | 100% | 6.10 | 6.11 | INFORMATION / INFORMATION / INFORMATION |
| Royer event 10 | 1 | 0.37 | nan | 100% | 6.23 | 6.17 | INFORMATION / INFORMATION / INFORMATION |
| clear deep path | 41 | -0.34 | 0.84 | 93% | 5.55 | 5.72 | PASS / PASS / PASS |
| clear deep path | clear deep path | 1 | 0.37 | nan | 100% | 6.23 | 6.17 | INFORMATION / INFORMATION / INFORMATION |
| ridge above the channel axis | clear deep path | 1 | -0.36 | nan | 100% | 6.10 | 6.11 | INFORMATION / INFORMATION / INFORMATION |
| ridge near the channel axis | 48 | 0.13 | 1.45 | 69% | 6.19 | 6.50 | PASS / FAIL / FAIL |

## 4. Royer 2016 station differences

| Event | Difference | Path classes | Observed (dB) | Predicted (dB) | Residual (dB) | In primary set A2 |
|---|---|---|---|---|---|---|
| Royer A | SWAMS3 minus SSEIR | clear deep path / clear deep path | -4.26 dB | 2.00 dB | -6.3 | no (Royer reports no arrival at SSEIR) |
| Royer A | MAD minus SSEIR | ridge above the channel axis / clear deep path | -15.87 dB | -1.89 dB | -14.0 | no (Royer reports no arrival at SSEIR) |
| Royer B | SSEIR minus H01W2 | ridge above the channel axis / clear deep path | 5.05 dB | -17.01 dB | 22.1 | no (Royer reports no arrival at SSEIR) |
| Royer 5 | SSEIR minus H01W2 | ridge near the channel axis / clear deep path | 0.96 dB | -18.32 dB | 19.3 | no (Royer reports no arrival at SSEIR) |
| Royer 10 | SWAMS3 minus H01W2 | clear deep path / clear deep path | 10.00 dB | 2.20 dB | 7.8 | yes |

- The event A difference to WKER is not available: that path crosses land and was not run.
- Large positive residuals on paths to SSEIR would mean that the model over-blocks the ridge paths, as for air7 to Cape Leeuwin. But Royer reports no arrival at SSEIR for these events, so those energies may be survey shots or noise. They are not used in the primary.

## 5. Open issues

1. The Indian Ocean absolute bias rests on one source family (SUS) with a 4-17 dB source-route spread. It cannot be tested out of source.
2. The spread inflation is a blunt fix. It over-covers SUS and under-covers airguns. A path-specific term for ridge-crossing paths would be better, but there are too few such paths to fit it.
3. sd_db is defined at 10 Hz, where the bias is extrapolated. Users of the JSON should note the smaller spread at 20-40 Hz (see the 25 Hz column).
4. The Indian Ocean restriction, the Royer set A2 and the inflation factor are all POST HOC.
5. Not independently verified.

## 6. Files

Residual table, held-out results, summary, Indian Ocean floor check, chart, JSON and code: see the artifact list returned with this task.
