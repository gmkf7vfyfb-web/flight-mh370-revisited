# First network detection search, 8 March 2014 data held — REAL RUN (final inputs)

Date: 3 Nov 2026. Method: source-grid search (proposal X18).
Pre-registration: ns-prereg-2026-11-03a (v ae310c86), amendment A1 (v 83dd444b, exact path types) and amendment A2 (v 5eb84cde, final inputs and lead decisions). We saved each one before the run it governs.
Inputs: level_correction.json v2 (v 36a7e196) and pd_curves.json v2 (v de400f7e; detector report dd6d1937, thresholds dbb67e9d).
Language: ASD-STE100 for work-specific text. All values come from the run files listed in section 8.

## 1. Result in short
- **The data held show no network signal.** No result in any case or sensitivity reaches an empirical p below 0.05.
- **Primary case** (zero bias, sd 12.58 dB; OHASISBIO not used):
  - Graded network score, best cell: 7.00 at 39.5 S, impact 00:44:30, corner 1 Hz. **Empirical p = 0.33** (500 time slides; null median 4.96, 95th percentile 9.60).
  - IMOS-only strict null (1,325 common shifts of 3 h or more): p = 0.71.
  - Threshold statistic at one false alarm per day: no window at any station passes. Best score 0.00, p = 1.00.
  - Threshold statistic at one false alarm per hour: best 3.17, p = 0.81.
- **The best primary cell rests on one window.** That window is at Cape Leeuwin, 01:13:29 UTC, read from Royer's spectrogram: T1 = 5.6 dB, station p = 0.006. It coincides with Royer's pick of his event 6. Royer puts event 6 in his "uncertain" class, so it is a candidate, not an explanation. It also matches catalogued earthquake EV081 (Talaud Islands, mb 3.37); that path crosses land, so the match is weak. No other station supports the cell.
- **Upper limits are weak.**
  - At one false alarm per day, a 90 % exclusion below 10^10 J exists at only 1.3 % of cells (5 Hz corner) and 0 % (1 and 0.2 Hz). The lowest is 10^9.65 J, at 32.0 S.
  - At one false alarm per hour: 75.3 % / 1.3 % / 0 % of cells; the lowest is 10^8.15 J (5 Hz) and 10^9.65 J (1 Hz).
  - Kinetic energy at impact is 0.4–10 GJ, so these limits need a coupling efficiency near 1 to constrain a real impact.
- **Important (detector track, lead instruction):**
  - A blind scan at one false alarm per day MISSES the real F-35A arrival at Wake Island: T1 4.2–7.3 dB against a threshold of about 27 dB. A scan at one false alarm per hour detects it.
  - For a single window at a known time, the 1 % noise tail is about 6 dB.
  - Thus the 1/day exclusion limits are conservative. The 1/hour row and the graded statistic carry more of the information.
  - The graded statistic with the time-shift null is the network detection test.

![Upper limits, primary case]({{artifact:f3767fea-7a4c-4f0a-a5e9-86baee47634d}})
![Null distributions, primary case]({{artifact:fb797e7e-b5b4-475d-a91c-05535fc601b3}})

## 2. Comparison of the cases
| Run | Best cell, graded (arc, impact, corner) | Graded score | Empirical p (500 time slides) | IMOS strict-null p | Threshold best, 1/day (p) | Threshold best, 1/hour (p) | Cells with 90 % exclusion below 10^10 J, 1/day, 5 / 1 / 0.2 Hz (%) | Lowest exclusion, 1/day, log10 J | Cells with exclusion, 1/hour (%) | Lowest exclusion, 1/hour, log10 J |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 **Primary**: zero bias, sd 12.58 dB | 39.5 S, 00:44:30, 1 Hz | 7.00 | **0.33** | 0.71 | 0.00 (1.00) | 3.17 (0.81) | 1.3 / 0.0 / 0.0 | 9.65 / – / – | 75.3 / 1.3 / 0.0 | 8.15 / 9.65 / – |
| R2 Sensitivity: Indian Ocean post hoc fit (spread x1.98) | 39.5 S, 00:44:30, 5 Hz | 6.37 | 0.39 | 0.70 | 0.00 (1.00) | 2.96 (0.94) | 0.1 / 0.0 / 0.0 | 9.95 / – / – | 27.0 / 0.1 / 0.0 | 8.45 / 9.90 / – |
| R3 Check only: failed all-ocean fit | 41.0 S, 00:41:00, 5 Hz | 5.35 | 0.48 | 0.69 | 0.00 (1.00) | 3.44 (0.93) | 2.1 / 0.0 / 0.0 | 9.35 / – / – | 67.3 / 2.1 / 0.0 | 7.85 / 9.30 / – |
| R4 Sensitivity: primary + OHASISBIO picks (post hoc curve) | 39.5 S, 00:44:30, 1 Hz | 7.00 | 0.33 | 0.71 | 7.56 (**0.06**) | 7.12 (0.17) | 42.7 / 2.2 / 0.0 | 7.95 / 9.45 / – | 89.2 / 2.8 / 0.0 | 7.35 / 8.85 / – |
| R5 Sensitivity: primary without the Royer spectrogram at Cape Leeuwin | 23.5 S, 00:33:00, 5 Hz | 3.75 | 0.70 | 0.71 | 0.00 (1.00) | 3.67 (0.85) | 1.3 / 0.0 / 0.0 | 9.65 / – / – | 61.0 / 1.3 / 0.0 | 8.15 / 9.65 / – |

Notes on the table:
- R4's graded score equals R1's, because picks enter only the threshold statistic (A2 item 11).
- **R4, one false alarm per day (p = 0.06).** The best threshold cell is 32.0 S, impact 00:22:00, corner 5 Hz. It scores because four Royer picks fall inside the predicted windows: SWAMS1, SWAMS2 and SWAMS3 picks of Royer's event B (00:47:39–00:47:44), and the MAD pick of his event A (icequake, 01:04:25).
  - Royer located event B at 35.22 S, 99.92 E, origin 00:21:30.6. That is about 494 km from the nearest arc point (32.5 S).
  - Our grid samples only the arc line, so a source off the arc can partly fit an arc cell.
  - Event B is in Royer's "uncertain" class. By the project rule it stays a candidate. We do not use it to explain the cell away, and we do not claim it as a detection.
  - This result uses a picks curve that the detector track could not identify (post hoc: 50 % at 27.9 dB, sigma 20 dB). It is a labelled sensitivity only.
- **R5 shows the Royer spectrogram part at Cape Leeuwin drives the primary best cell.** Without it, the best score falls to 3.75 (p = 0.70).
- The null distribution of R1 has two modes; 34.6 % of trials exceed 6.5. The second mode comes from trials where the same kind of strong Cape Leeuwin transient lands inside some cell's window. Thus a score of 7 from one transient is common by chance.

## 3. Stations and coverage (primary)
| Station | Data held | Fraction of cell windows observed | Threshold, 1/day (dB) | Threshold, 1/hour (dB) |
|---|---|---|---|---|
| Cape Leeuwin (H01W) | Kadri 2024 Fig. 9 trace 00:27–00:57; Royer H01W2 spectrogram 00:01–02:03 (never both) | 0.91 | 15.7 (trace); 17.0 (spectrogram, raw-hydrophone curve assumed) | 5.8 / 5.95 |
| Diego Garcia South (H08S) | Kadri 2024 Fig. 9 trace 01:00–01:20 | 0.72 | 20.3 | 4.35 |
| Perth Canyon 3315, 3376 | raw, 307 s in each 15 min, 10–40 Hz | 0.31, 0.30 | 19.15 (3376 curve for both) | 6.9 |
| Scott Reef 3250 | raw, same | 0.25 (every path blocked) | 30.15 | 13.05 |
| Portland 3274, 3275 | raw, same | 0.17, 0.17 (land north of 28.5 S) | 14.2; **20.05 for 3275** (own lower bound, lead decision) | 4.6 |
| OHASISBIO SSEIR, SWAMS1–3, MAD, NCRO, WKER | Royer 2016 picks only (R4 only) | 0.95–1.00 | picks curve not identified | – |

- Threshold passes in the primary case:
  - One false alarm per day: none.
  - One false alarm per hour: Diego Garcia South 62 cell-windows; Scott Reef 12; Cape Leeuwin 1.
- The station windows behind those passes (station_windows.csv):
  - Diego Garcia South, 01:14:17 and 01:15:02 (T1 5.0 and 4.9 dB). These coincide with airgun shots and with CMST detections at bearing 36.4 deg. Shot coincidence is a label, not an exclusion (Pete's rule).
  - Scott Reef, 01:04:06 (T1 13.3 dB). Every path to Scott Reef is blocked.
  - Cape Leeuwin, 01:13:23 (T1 6.3 dB, Royer spectrogram; it passes the 1/hour threshold of 5.95 dB). This is the local peak of the same transient. It is NOT the window of the best primary cell. That window starts 6 s later (01:13:29, T1 5.6 dB), and it does not pass the 1/hour threshold. The best cell scores through the graded statistic, not through a threshold pass.
- Candidate list: 3,828 cells with a positive graded score, with no threshold (candidates_no_threshold.csv). No cell has a global empirical p below 0.1.
- Chance-match rate for the known-event catalogue, per window: Diego Garcia South about 1.0 (shots); Cape Leeuwin about 0.6.

## 4. Parameters
| Item | Value |
|---|---|
| Arc points | 43, 41.0–20.0 S every 0.5 deg, on the 7th-arc line. **Cross-arc offsets are not sampled.** |
| Impact time | 00:19:30–00:45:00 UTC, 30 s steps (52). Dives reach the sea about 00:20–00:22:20; glides can last to about 00:40. |
| Acoustic energy | 10^1–10^10 J, steps of 0.05 decade |
| Source | 10 m depth; flat spectrum to the corner, then f^-3.1; corners 5, 1, 0.2 Hz; SEL = 170.8 + 10 log10(E_a / 1 J) dB re 1 µPa² s at 1 m |
| Sound model | RAM, frozen chain tl-chain-2026-10-27 (GEBCO 2026, WOA23 March, GlobSed v3), dense grid, 341 water paths to the 9 stations used |
| Path type | exact type per path, from path-classes-royer-dense.csv (v b3106ff5) (A1) |
| Model error, primary | bias 0 dB, slope 0, sd 12.58 dB per path (alternatives.zero_bias_wide; post hoc, gives held-out z sd 1.0 over all oceans, 212 rows, coverage 91 %) |
| Model error, R2 | Indian Ocean post hoc fit: bias −14.0 dB (clear deep path), −1.4 dB (ridge near the channel axis), −8.5 dB (others), slopes +2.3 to +5.0 dB per octave, sd 21.2–22.1 dB |
| Model error, R3 | failed all-ocean class fit (check only) |
| Arrival time | path length / 1.480 km/s − 3.1 s, sd 8.6 s (143 Royer hydrophone picks) |
| Window | 30 s, from 10 s before to 20 s after the predicted onset |
| Statistic | T1 = 10 log10(E_W / median E_W), median over reference windows (IMOS: within 1,207 s; digitised data: within 300 s, same panel), at least 30 s away |
| Noise for the prediction | pd_curves noise_level_db: Cape Leeuwin 103.68, Diego Garcia South 100.43 (**between-shot level; conversion not measured**), IMOS 3315 101.55, 3376 100.03, 3250 109.12, 3274 104.4, 3275 94.7 dB re 1 µPa |
| Detection curve | P_D = floor + (1 − floor) Φ((SNR − snr50) / √(σ² + noise sd² + model sd²)); likelihood relative to p0 = max(floor, false-alarm probability per window) |
| False-alarm rate | one per station per day (primary); one per hour (sensitivity) |
| Null A | 500 time slides, seed 20261103; groups: Cape Leeuwin, Diego Garcia South, Perth Canyon pair, Scott Reef, Portland pair (and OHASISBIO groups in R4) |
| Null B | IMOS loggers shifted together, 15-min steps, 3 h or more, 8 Mar and the 14-day background; 1,325 of 1,418 shifts kept (at least half the observed window count) |

## 5. Deviations from the pre-registration (all recorded before the run they govern)
1. A1: exact path types replace the nearest-sparse-point rule (that rule agreed on 76 % of paths).
2. A2: the primary model error is zero bias with wide spread. The Indian Ocean fit is a sensitivity, and the failed all-ocean fit is a check (lead decision, with the lead's reasons).
3. A2: window 30 s (from pd_curves.json). T1 uses the median-reference definition of the detector track, in place of the trimmed-mean form of the dry run.
4. A2: OHASISBIO is excluded from the primary likelihood (picks curve not identified). It enters only R4, with the post hoc curve. Picks are scored as "a pick in the window" against an assumed Royer analysed span of 00:00–03:10 UTC.
5. A2: IMOS 3275 threshold 20.05 dB (its own lower bound) in place of the proxy 14.2 dB; its snr50 is moved by the same +5.85 dB.
6. A2: the Cape Leeuwin spectrogram part uses the raw single-hydrophone curve, because no curve exists for that data form. R5 shows the effect.
7. Not run: source depths 2 m and 30 m; the deep-implosion branch; the IDC timing rule as a search case; the airgun-residual statistic at Diego Garcia South. Kadri 2019 Table 3 is not in the known-event catalogue.

## 6. Assumptions and limits
1. Stations are combined as independent. The Perth Canyon pair and the Portland pair are not independent; the nulls move each pair together.
2. All predicted signal energy is inside the 30-s window. Timing error (sd 8.6 s) and signal spread outside the window are not integrated, so the limits are a little too tight.
3. The graded statistic uses each station's own noise sample. Diego Garcia South has only 39 windows (smallest station p about 0.025). The Cape Leeuwin trace part has 58 windows, and the Cape Leeuwin spectrogram part 180.
4. Royer spectrograms are colour readings (70–100 dB scale) and can saturate. T1 is a ratio inside one panel, so the colour offset cancels.
5. Kadri traces give the envelope only (about 15 vertices per second).
6. The credible limit (row 3 of the map) depends on the log-uniform prior from 10^1 J. The exclusion limit is the primary limit.
7. The model bias is not removed in the primary case (bias 0). The frozen chain lost 5–14 dB too much on deep Indian Ocean known-source paths. If that loss is real for the arc paths, true received levels are higher and the limits would be tighter.

## 7. Conclusion
- The data held for 8 March 2014 do not contain a network signal from a 10 m source on the 7th arc between 41 S and 20 S for impact times 00:19:30–00:45:00.
- This is not an exclusion of an impact. With these data the energy limits lie near or above the kinetic-energy range for most of the arc.
- The strongest single feature is a Cape Leeuwin transient at 01:13 UTC, recorded by Royer as his event 6.
- The strongest picks coincidence is Royer's event B. It reaches p = 0.06 only with an unidentified picks curve.
- Both stay on the candidate list. Neither is a detection.
- The decisive test remains a run of this code on Kadri's raw IMS data for 8 March 2014.

## 8. Files
cells.csv, candidates_no_threshold.csv, best_cells.json, station_windows.csv and summary.json (primary case); case-comparison.csv (all runs); upper-limit-map.png and null-distribution.png (primary case); the code and every run folder are in the package zip.
