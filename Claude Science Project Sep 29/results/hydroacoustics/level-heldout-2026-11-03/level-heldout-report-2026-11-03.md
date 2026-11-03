# Held-out level tests of the sound model and the path-class level correction

3 Nov 2026. Hydroacoustics, source-grid method (X18). EXPLORATORY and UNCHECKED. Nothing is committed to GitHub.
Pre-registration: level-heldout-prereg-2026-11-03.md (artifact bba2e3a7, version a8543449). It was saved before any fit. Amendment A1 (Royer energy rule) was added before the Royer sound-model table was seen.

## 1. Result in short

1. The path-class correction FAILS the pre-registered held-out test. Pooled over 275 held-out bands (5-40 Hz): mean z 0.82 (rule |mean| <= 0.5), SD z 1.59 (rule 0.7-1.4), 90 % interval coverage 46% (rule 80-97 %).
2. The correction makes the forecast worse. Mean CRPS is 10.38 dB with the correction and 7.26 dB without it (same spread). The correction is better in 1 of 6 hold-out units only.
3. The cause is that the error does not transfer between source families. The Atlantic paths (Ascension, all "ridge above the channel axis") carry a large L1-sediment slope error (+8.2 dB/oct). The two Atlantic families disagree in level by about 12 dB (ship shock trials about +12 dB, San Juan charge about 0 dB at their bands). The Indian Ocean deep charges show no such slope (re-built pulse source).
4. No path class can be tested out of source. When its own family is held out, "clear deep path" and "ridge near the channel axis" keep 2 source events each, and "ridge above the channel axis" keeps 1. "Blocked" has no level data at all.
5. Only the one-sided airgun detection floors improve with the correction (mean log score -0.58 against -0.86; information only).
6. Royer 2016 station differences are NOT in this result. The Royer sound-model table did not arrive. The Royer arrival energies are extracted and saved, ready to use.
7. level_correction.json is written as PROVISIONAL with FAIL in its notes, as the pre-registration requires.

## 2. Data used

| Source family (hold-out unit) | Events | Row type | Source term | Bands used (5-40 Hz) |
|---|---|---|---|---|
| Blackman 2003 deep charges (SUS) A6-A10 | 8 shot-sites | known source level | re-built pulse (route B) primary; Gaspin & Shuler scaled (route A) as sensitivity | 21 |
| Blackman 2003 charge A11 (size unknown) | 1 | level free, slope only | cancels | 5 (Diego Garcia South path excluded: N x 2D corridor) |
| San Juan calibration charge 2017 | 1 | known source level | Gaspin & Shuler construction, 30 m | 18 |
| US Navy ship shock trials 2016 and 2021 | 8 shots | known source level | Gaspin & Shuler construction, 61 m | 150 |
| San Juan loss event 2017 | 1 | station difference | cancels | 10 |
| F-35A crash 2019 | 1 | station difference | cancels | 8 |
| Blackman 2001 airguns, Fig. 23 | 6 sites | level free per site | cancels (Blackman spectral convention unknown) | 63 |
| Blackman 2001 airguns, detection floor | 7 sites, 16 case-stations | one-sided | Tolstoy 2004 far-field source, 7.5 m | 96 (check only) |
| Royer 2016 events | 4 events kept (A, B, 5, 10) | station difference, 5-40 Hz energy | cancels | NOT RUN (sound-model table missing) |
| Wake and Juan Fernandez 2008 charges | - | - | - | EXCLUDED: no frozen-chain paths |

Why SUS route B is primary: the charges are at 610 and 915 m, outside the Gaspin & Shuler depth range (about 1,000 ft). Route A also extrapolates below their lowest band. Below the bubble frequency, a pulse with zero net impulse rises at +6 dB/oct. Route A rises at +11 to +13 dB/oct, which is too steep. Route B rises at +3.5 to +10.5 dB/oct. The route difference is carried as source error: sd = sqrt(source sd^2 + ((A - B)/2)^2).

## 3. Model choices and parameters

| Item | Value |
|---|---|
| Sound model | frozen chain tl-chain-2026-10-27, RAM, L1 seabed (GlobSed v3 over 3500 m/s basement), GEBCO 2026, WOA23 March; same as the 7th-arc dense grid |
| Correction | residual mean = bias + slope x log2(f / 10 Hz) per path class |
| Class rule | own bias and slope if >= 3 source events inform the class level; else the pooled global value |
| Path classes | section rule of index 97e0f6e3 (the old ridge/plateau classifier is not used) |
| Random terms | path offset tau (all bands of one path), band term (one per path and band), family source error, 1 dB charge error, observation and model band error, 1.2 dB reciprocity, airgun source-shape slope 1.5 dB/oct |
| Estimation | REML on a 0.25 dB grid for tau and the band term; GLS for bias and slope; weak priors N(0, 30^2) on bias, N(0, 10^2) on slope |
| Fitted variance terms (all units) | tau 4.5 dB, band term 2.75 dB |
| Hold-out scheme | leave one source family out (6 units); each Royer event as its own unit (not run) |
| Pass rules | P1 mean z within +/-0.5; P2 SD z 0.7-1.4; P3 90 % interval covers 80-97 % of bands |
| Not changed against the prereg | no outlier removal; air7 to Cape Leeuwin and the San Juan south-north difference stay in |

Final correction (fit on all six units; bias at 10 Hz; sd_db = predictive sd of one band of a new path, without source, observation and TL-table band sd):

| Class | Bias (dB) | Slope (dB/oct) | sd_db (dB) | Source events | Bands | Basis |
|---|---|---|---|---|---|---|
| global | -5.76 ± 2.71 | 8.01 ± 0.27 | 5.93 | 24 | 275 | own fit |
| clear deep path | -12.76 ± 6.89 | 5.06 ± 2.40 | 8.67 | 7 | 41 | own fit |
| ridge near the channel axis | 0.15 ± 6.59 | 2.20 ± 1.88 | 8.44 | 6 | 56 | own fit |
| ridge above the channel axis | 0.88 ± 3.28 | 8.23 ± 0.28 | 6.21 | 9 | 178 | own fit |
| blocked | -5.76 ± 2.71 | 8.01 ± 0.27 | 5.93 | 0 | 0 | global value (no data) |

Read with care:
- "Clear deep path" bias at 10 Hz is extrapolated from SUS bands at 16-40 Hz. At 31.5 Hz the class value is about -4.4 dB.
- "Ridge above the channel axis" rests on Atlantic paths only.
- "Blocked" has no data and carries the global value.
- tau does not average down over a 5-40 Hz band sum. The band term does.

## 4. Held-out results

By hold-out unit (primary):

| Set | Bands | Mean z | SD z | 90 % cover | CRPS corrected | CRPS uncorrected | P1 / P2 / P3 |
|---|---|---|---|---|---|---|---|
| SUS 2003 | 26 | -1.16 | 0.78 | 73% | 8.44 | 2.90 | FAIL / PASS / FAIL |
| San Juan charge | 18 | -1.72 | 0.81 | 44% | 10.05 | 5.08 | FAIL / PASS / FAIL |
| Ship shock trials | 150 | 1.90 | 0.51 | 23% | 14.17 | 9.85 | FAIL / FAIL / FAIL |
| San Juan loss event | 10 | 0.73 | 0.51 | 90% | 4.03 | 4.03 | FAIL / FAIL / PASS |
| F-35A crash | 8 | -0.34 | 0.22 | 100% | 2.49 | 2.49 | INFORMATION / INFORMATION / INFORMATION |
| Airguns 2001 | 63 | -0.04 | 1.66 | 75% | 4.26 | 4.65 | PASS / FAIL / FAIL |

By path class (primary; "a | b" = station difference between paths of classes a and b):

| Set | Bands | Mean z | SD z | 90 % cover | CRPS corrected | CRPS uncorrected | P1 / P2 / P3 |
|---|---|---|---|---|---|---|---|
| clear deep path | 41 | -0.87 | 1.27 | 78% | 5.77 | 3.75 | FAIL / PASS / FAIL |
| ridge above the channel axis | 168 | 1.51 | 1.25 | 26% | 13.73 | 9.33 | FAIL / PASS / FAIL |
| ridge above the channel axis | ridge above the channel axis | 10 | 0.73 | 0.51 | 90% | 4.03 | 4.03 | FAIL / FAIL / PASS |
| ridge near the channel axis | 48 | 0.07 | 1.64 | 71% | 5.24 | 4.48 | PASS / FAIL / FAIL |
| ridge near the channel axis | ridge near the channel axis | 8 | -0.34 | 0.22 | 100% | 2.49 | 2.49 | INFORMATION / INFORMATION / INFORMATION |

Sensitivities (pooled):

| Set | Bands | Mean z | SD z | 90 % cover | CRPS corrected | CRPS uncorrected | P1 / P2 / P3 |
|---|---|---|---|---|---|---|---|
| primary | 275 | 0.82 | 1.59 | 46% | 10.38 | 7.26 | FAIL / FAIL / FAIL |
| A: ship shock trials split 2016 / 2021 (prereg) | 275 | 0.24 | 1.24 | 86% | 5.47 | 7.40 | PASS / PASS / PASS |
| B: SUS source route A (prereg) | 275 | 0.81 | 1.45 | 55% | 8.84 | 7.58 | FAIL / FAIL / FAIL |
| C: POST HOC source-shape slope term 2 dB/oct | 275 | 0.59 | 1.38 | 72% | 8.15 | 7.23 | FAIL / PASS / FAIL |
| D: POST HOC Indian Ocean rows only | 89 | -0.11 | 1.63 | 70% | 4.93 | 5.15 | PASS / FAIL / FAIL |
| all | 275 | -0.11 | 1.47 | 68% | 7.24 | 4.83 | PASS / FAIL / FAIL |

- Sensitivity A passes, but it is not a valid test. Ship shock trials 2016 and 2021 share one source model, so the source error is in the training data.
- Sensitivity C (POST HOC) adds a source-shape slope error of 2 dB/oct to every explosive family. It improves the result but still fails P1 and P3.
- Sensitivity D (POST HOC) uses Indian Ocean rows only. P1 passes. P2 and P3 fail, because of the airgun air7 to Cape Leeuwin over-blocking (about 20 dB).
- POST HOC option, not pre-registered: zero bias with an extra per-path sd of 12.6 dB gives held-out SD z 1.0 and coverage 90% on the 207 rows with a known source or a station difference.

Airgun detection floor (one-sided check, information only; margin = predicted level minus noise floor, median over bands):

| Site | Station | Path class | Blackman outcome | Margin uncorrected (dB) | Margin corrected (dB) | P(outcome), corrected | P(outcome), uncorrected |
|---|---|---|---|---|---|---|---|
| air1 | H08N | ridge near the channel axis | detected | 1.1 | 8.7 | 0.83 | 0.55 |
| air1 | H08S | blocked | not detected | -11.7 | -13.2 | 0.95 | 0.93 |
| air2 | H08S | blocked | not detected | -10.5 | -12.1 | 0.94 | 0.91 |
| air3 | H08N | clear deep path | detected | 9.4 | 13.4 | 0.91 | 0.82 |
| air3 | H08S | ridge above the channel axis | not detected | -10.4 | -6.5 | 0.79 | 0.90 |
| air4 | H08N | ridge near the channel axis | detected | 1.1 | 9.0 | 0.82 | 0.55 |
| air4 | H08S | ridge above the channel axis | not detected | -0.5 | 3.4 | 0.34 | 0.52 |
| air7 | H01W | ridge near the channel axis | detected | -26.8 | -19.3 | 0.02 | 0.00 |
| air7 | H08N | blocked | not detected | -14.2 | -15.8 | 0.98 | 0.96 |
| air7 | H08S | clear deep path | detected | -3.4 | -0.3 | 0.49 | 0.36 |
| air8 | H01W | ridge near the channel axis | not detected | -18.4 | -10.4 | 0.85 | 0.97 |
| air8 | H08N | blocked | not detected | -19.3 | -20.8 | 1.00 | 0.99 |
| air8 | H08S | clear deep path | detected | -6.6 | -3.5 | 0.35 | 0.24 |
| air9 | H01W | clear deep path | detected | -5.2 | -2.1 | 0.41 | 0.28 |
| air9 | H08N | blocked | not detected | -28.5 | -30.1 | 1.00 | 1.00 |
| air9 | H08S | ridge near the channel axis | detected | -5.2 | 2.5 | 0.61 | 0.29 |

## 5. Royer 2016 (prepared, not run)

- The rule of prereg section 2.3 with amendment A1 keeps 4 events with 2 or more measurable stations: A (SWAMS3, MAD, WKER, SSEIR), B (Cape Leeuwin H01W2, SSEIR), event 5 (SSEIR, Cape Leeuwin), event 10 (SWAMS3, Cape Leeuwin). This gives 6 station differences.
- Royer's observed arrival times put one arrival under several events at some stations. Those stations are dropped for those events.
- The difference rows are built by lvlcore.royer_rows() when the Royer band table arrives. Then all folds and the final fit must be re-run.

## 6. Open issues

1. Royer TL table not received. The Royer differences are the only Indian Ocean data that join path classes with the source cancelled.
2. The absolute level of every class rests on one source family and its source model (SUS route spread 4-17 dB; Gaspin & Shuler construction for the explosions). A class correction cannot be separated from the source-model error with these data.
3. Pete must rule on what the search uses: (a) this provisional class correction, (b) zero bias with a wide per-path sd (post hoc about 13 dB), or (c) the Indian Ocean-only fit.
4. Wake and Juan Fernandez 2008 charges need frozen-chain paths (new sound-model runs) before they can be used.
5. No blocked-path level data exist. A blocked-path correction is not possible from these sources.

## 7. Files

Listed in the structured output of this task: residual table, held-out results, held-out summary, airgun floor check, Royer arrival energies, level_correction.json, chart, prereg, code.
