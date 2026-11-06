# Critical review of the "Sub-noise Spectral Detection Feasibility" thread (5–6 Nov 2026)

Reviewer: independent session, 6 Nov 2026. Scope: all four stages of the thread, as follows.
- Signature test on open IMS data.
- Combined weak-signal detectors.
- Noise and Kadri follow-up.
- Pre-registered 8 March 2014 run, versions 1 and 2, with its internal review and candidate views.

Method: I read the code in the result packages and the thread transcript. I re-ran the key checks from the thread's own saved calibration, event-day series and IMOS cache (read-only; the thread was still active). Every number below comes from those re-runs or from the saved files. The supporting table is `kadri_seeds_bearing_corrected.csv`.

## 1. Verdict

- **The headline null result holds.** No impact time and place has network evidence near any global false-alarm level. I reproduced the final run independently: best evidence 1.758 (reported 1.76) and 5 % level 3.567 (reported 3.57). My global chance is 0.855 from my own 1,000 time shifts (reported 0.875). It stays at 0.80–0.94 under every correction below.
- **Three reported results are not reliable as stated:**
  1. The Kadri seed positions and fit counts. They use published Cape Leeuwin bearings without the project's own array correction (ruling B1, 26 Oct).
  2. The ranked "weak candidates" at 00:53–00:55 UTC, 20–34° S. They come from a tail-fit artefact on a discrete statistic at Scott Reef and Perth Canyon 2.
  3. The statement that the time-shift null is "not biased; the data are just quiet". The null is not exchangeable with the 8 March hours. The effect is conservative and modest.
- **The design has low power for the question Pete asked.** Cape Leeuwin and Diego Garcia South, where Kadri's transients are, cannot confirm anything with the data held: the best possible window p is about 0.01–0.05. In practice the network test is an IMOS-pair test that covers 40–43 % of hypotheses.

## 2. What holds

| Item | Check | Result |
|---|---|---|
| Network statistic, window calibration, time-shift null, global p | Independent re-implementation from saved series | Reproduced (1.758; 3.567; 0.855 vs 0.875) |
| Grid resolution (1° along arc, 25 NM across, 15 s in time) | 3,000 simulated impacts between grid points, 5 station pairs, primary speeds | 100 % captured jointly by some hypothesis; no resolution loss |
| Grid distances | Grid vs WGS84 geodesic, Perth Canyon 1 | Ratio 1.0000 at all points |
| Seeded-test code | Re-implemented; uncorrected bearings | Matches thread values within shift sampling (e.g. 00:54:30: 0.506 vs 0.530) |
| 8 March instrument faults | Scan of the event-day series | One faulty Perth Canyon 2 record (14:44 UTC), outside every arrival window and every shift |
| Stage 1 correction (23/4 vs 6/21) | Already corrected by the thread | Correction stands |
| Corner-frequency answer (1.05 vs 11.7 Hz were random draws) | Transcript and code | Honest and correct |
| Conditional wording of the Kadri timing result | Corrected after Pete's challenge | Correct as revised |

## 3. Errors and bugs, by effect on reported results

### 3.1 Kadri bearings used without the array correction (changes reported results)

- **What was done.** Every Kadri seed and the top-10 table mapped the published bearing onto the arc at ±3°, with no correction.
- **What the project had already established.** The 41-event Cape Leeuwin calibration (artifact 076cefbe) gives raw-geometry bearing biases of +5° to +14° in this sector. Pete's ruling B1 (26 Oct) treats published bearings as uncorrected unless the authors show a correction. The 26 Oct crossing note gives the primary case: 306.18° becomes 299.4° ± 2.0°, which crosses the arc at 27.2° S, not 25.8° S.
- **Re-run with the project correction** (exact inverse of the 076cefbe geometry; 306.18° to 299.07° reproduced):
  - Corrections run from −5.1° to −13.8°.
  - Three seeds move south of 41° S and drop off the grid: 00:38:29, 00:39:53 and 00:42:02. The last is the thread's headline "smallest seeded p, 0.073".
  - 00:47:04 and 00:49:41 still miss the arc.
  - The others move 1–3° of latitude south. For example, 00:54:30 moves from 25–26° S to 27° S.
  - Fits change from "6 of 19 steep dive, 17 of 19 glide or ditching" to **7 of 19 and 14 of 19**.
  - No seed is confirmed. The smallest corrected seed p is 0.46 (±3°) and 0.46 (±4.1°, 2σ).
- **Affected outputs:** the seeded-test figure (panel b and its title), the top-10 table latitudes and windows, the candidate-views PDF, and report items 4–5.
- **Not affected:** the conclusion that no seed is confirmed.
- **Status at the end of this review.** The thread applied the correction itself after Pete's question (repo commit ca4eb652). It reports 13 of 19 Kadri seeds testable, with the smallest seeded p 0.43. This agrees with the independent re-run above (14 testable, one of them with only 2 hypotheses; smallest p 0.46). The top-10 table, the candidate-views PDF and the seeded-test figure still need to be redrawn.

### 3.2 Pareto tail fitted to a discrete statistic (creates the ranked candidates)

- **The cause.** Envelope persistence is a binomial count. At Scott Reef the thinning lag is 50, so each 30-s window holds only 6 samples, and the statistic has 7 possible values.
- **The fit fails at the top value.** The generalised Pareto tail fitted above the 90th percentile has a negative shape (−1.49), and its end point falls at the largest value. That value occurs in 6.6 % of noise looks, but it is mapped to p = 1.0×10⁻⁷, about 640,000 times too small. Perth Canyon 2 shows the same failure: 2.2 % of looks are mapped to 1.1×10⁻⁸.
- **Effect at Scott Reef.** All 459 event-day looks with combined p < 0.05 are persistence-saturated looks. So are 100 % of the top 5 % of calibration scores. At strict levels the combined detector there is one binary flag, and the other four components add nothing. At Perth Canyon 2 the flag makes up 43 % of the top 5 %.
- **Effect on candidates.** The final run's top three hypotheses (ranks 1–3 in report section 4) all rest on that Scott Reef flag. The pre-registered empirical-tail sensitivity (A6) avoids the fit. Under A6 the cluster disappears, and the best hypothesis becomes 00:28:23 at 23° S −50 NM: Cape Leeuwin envelope p 0.065 and Diego Garcia South envelope p 0.15. The thread ran A6 but checked only the global p (0.94), not whether the candidates survive.
- **Same artefact in stage 2.** On the open Cape Leeuwin background, the saturated persistence value occurs in 1.19 % of looks and is mapped to 1.2×10⁻⁹. At 5 % per look the effect is limited, because the combined score is re-calibrated empirically. It governs the strict tail.
- **The false-alarm calibration itself survives.** The combined score is re-calibrated empirically on the same noise. Sensitivity at Scott Reef and Perth Canyon 2 at strict levels is governed by the flag.

### 3.3 The time-shift null is not exchangeable with the 8 March hours (wrong explanation; conservative)

- **What the thread saw and concluded.** The real alignment averaged lower evidence than 97 % of shifts. The thread read this as "the data are quieter; the null is not biased".
- **What the data show.** At Perth Canyon 1, 0 of 333 looks in 00:20–01:40 have p < 0.05; about 17 would be expected. The mean −log10 p there is 0.150, against 0.455 for the rest of the day and a nominal 0.434.
- **This is specific to 8 March.** On the 14 background days the same hours are nominal (0.434 in, 0.434 out).
- **The absolute level is normal.** The 8–40 Hz level on 8 March is inside the background range for those hours (median −21.2 dB, against bin medians of −20.7 to −18.4 dB). So this is not one loud source. The noise simply had fewer transients in that period.
- **Per-station window p, real alignment against 40 shifts** (nominal 0.434): Cape Leeuwin 0.310 vs 0.412 (all 40 shifts higher); Perth Canyon 1 0.128 vs 0.242; Portland 1 0.242 vs 0.375; Perth Canyon 2 0.180 vs 0.247.
- **So the null is conservative.** The shifts draw in hours that are not like the target hours, and the station p-values are not uniform there.
- **Size of the effect.** Recalibrating each station's window p to local 8 March conditions raises the best evidence from 1.76 to 2.55. The global chance falls only to 0.80, which is still null.
- **Correct wording:** "the null is conservative by a small amount; the conclusion does not change".

### 3.4 Smaller implementation issues

- The injection sensitivity tables (`imos_inject.py`) load the pre-cleaning calibration (`imos_calib.pkl`), while the final network run uses the earthquake-cleaned one. The tails differ by 0–0.7 dB, so the effect is small, but the two are not matched.
- The 1,000 shifts are drawn from only 14 shift values per IMOS site, 2,744 combinations in all. Many repeat. The 5 % level is still resolved, but the tail above it is coarse.
- The cyclic wrap of the Kadri traces is one 5-s step short. This is negligible.

## 4. Method limits that cap what this design can find

1. **The Cape Leeuwin and Diego Garcia South envelope null is built from the trace itself.** Window maxima are compared with random windows of the same 29.5-min (19.4-min) trace, which already contains the transients. The strongest point in the Cape Leeuwin trace scores only 0.046 for a 15-point window (0.032 at 10 points, 0.011 at 5). The median window has 13 points. These stations therefore cannot carry or confirm a candidate. They add degrees of freedom and so dilute the Fisher sum. Seeded tests from Kadri's transients are tested in one direction only, at the IMOS loggers.
2. **Scott Reef is in an impulsive environment.** Its envelope repeats about every 8.6 s in 65 % of 8 March records (8.9 s in 42 % of background records). Its typical 30-s band energy sits 9–13 dB above the record median. A seismic airgun survey is likely; I have not confirmed this from survey records. Every Scott Reef path is "large attenuation" or blocked. Scott Reef evidence should not carry a candidate until the pulse train is labelled and handled. The Diego Garcia South airgun ruling (label plus an interference test, never exclude) is the natural model.
3. **Each station gets its own full speed window.** A real arrival shares most of its speed error across stations. Relative timing between stations would cut each extra station's window from about 77–115 s to about 25–40 s for 2,000 and 3,000 km paths (the range depends on how much of the detour is shared). That is the structural analogue of Pete's PRN idea, and it is not used. Amplitude consistency across stations is not used either.
4. **The strongest component is tested against its own model.** The impact-pattern correlation is matched to the same source and channel model that generates the synthetic signals. The recorded-earthquake control is the only model-free check, and there the gains are smaller.
5. **The sensitivity figures understate the signal energy.** They use SNR in 8–40 Hz, while 58–63 % of the synthetic impact energy lies below 8 Hz. They are also relative to each record's own median, with no received-level model. The thread states correctly that nothing is excluded.
6. **Coverage.** Only 40 % (steep dive) to 43 % (glide or ditching) of hypotheses reach two IMOS sites that were recording.

## 5. Process issues

- **A ruling was missed.** The bearing ruling (B1) and the 26 Oct crossing note were in project memory and the artifact store. The pre-registration did not use them. The thread found the note only when Pete asked on 6 Nov.
- **Interim numbers went out before review.** They were sent before the pre-registered review, and they included candidates later reported as "weak candidates". The thread acknowledged this itself.
- **A deliverable was not re-linked.** The candidate-views PDF that Pete asked for was delivered in a mid-turn message (artifact 0f2bb084, 47 pages, with spectrogram, band energy, correlation and combined score per site). The closing summary did not link it, and Pete later asked where it was. That PDF also uses uncorrected bearings and the pre-cleaning calibration.
- **A sensitivity run was not checked for its effect on candidates.** The A6 run was reported only as a global p.

## 6. How reliable each reported result is

| Reported result | Status |
|---|---|
| No network detection (global chance about 0.88) | Holds (0.80–0.94 under all corrections) |
| No seed confirmed at other sites | Holds (also with corrected bearings) |
| Smallest seeded p 0.073 (Kadri 00:42:02) | Withdraw: the seed is off the grid after bearing correction |
| 17 of 19 Kadri transients fit glide, 6 of 19 fit dive | Replace with 14 and 7 (ruling B1, ±3°) |
| Kadri 00:54:30 implies impact 00:31–00:40 at 26° S | Replace with 27° S, impact about 00:32–00:40 (corrected) |
| Weak candidates at 00:53–00:55, 20–34° S, carried by Scott Reef and Perth Canyon 2 | Withdraw: tail-fit artefact, not robust to A6 |
| "Null not biased; data quieter" | Incorrect: conservative null, small effect |
| Single-logger known-time SNR50 (−8 to +1 dB at 5 %) | Provisional: model-matched, in-sample at Perth Canyon 2 and Portland 2, pre-cleaning calibration, flag-dominated at Scott Reef and Perth Canyon 2 |
| Network SNR50 (2.4–8.6 dB at 5 % global) | Provisional: same caveats; Scott Reef pairs are flag-driven |
| Stage 1–2 known-time gains on open IMS data | Qualitatively valid; numbers model-matched and limited at strict levels by the same persistence artefact |
| Stage 3 noise model and earthquake tail removal | Holds as described |

## 7. Fixes needed before this method is used again

1. Apply the ruling B1 bearing correction with its error model (σ about 2.0°, 2σ window) to all Kadri seeds. Report the uncorrected bearing as the sensitivity case. Re-run the seeded tests, the top-10 table and the candidate views.
2. Replace the parametric tail for discrete statistics with the empirical (mid-rank) probability. Alternatively, raise the persistence sample count, for example with a shorter thinning lag or a longer window. Re-calibrate, and check candidates, not only the global p, under every sensitivity run.
3. Build the null from the same hours on other days, which is possible for Scott Reef, Portland 1 and Perth Canyon 1 with 14 background days. Report it beside a local event-day recalibration.
4. Label the Scott Reef pulse train and treat it like the Diego Garcia South airguns before Scott Reef evidence is ranked.
5. Use relative timing between stations, with a shared speed, and amplitude-ratio consistency in the network statistic.
6. Get the raw 8 March 2014 Cape Leeuwin and Diego Garcia South waveforms (CTBTO). This is the largest gain in power, and the only way to test Kadri's transients with the full detector.
