# Clean-sheet detector T1: thresholds, detection probability and held-out detection outcomes

Date: 3 Nov 2026. Status: complete. The Royer 2016 test was run after the lead session sent its loss table (tl_royer_bands.csv, artifact version adc493a6). Language: ASD-STE100 for work-specific text.
Pre-registration: {{artifact:56ba5691-a0e3-455d-8d91-60ed34958455}} (saved before scoring) and amendment 1 {{artifact:64024985-a75d-44eb-b6c2-c8e3ea63ee73}} (saved before scoring).
Nothing in this work uses the 8 Mar 2014 MH370 prediction windows. IMOS records that start between 7 Mar 23:00 and 8 Mar 07:30 UTC were not read.

## 1. Summary
- The detector T1 compares the 5-40 Hz band energy in a 30 s window with the local median window energy. An alarm is a run of windows above a threshold.
- The thresholds come from empirical alarm rates in real noise. At one false alarm per day, a single Cape Leeuwin hydrophone needs T1 = 17.0 dB and a Diego Garcia South hydrophone needs 21.9 dB. At one per hour, the values are 6.0 and 4.5 dB.
- The tails come from real long transients (60-300 s, on all three elements together), mainly earthquake T-phases. Single-second spikes are few (5 of 54 alarms at Cape Leeuwin).
- With SNR measured against the local median noise, the detection probability is almost a step function. It goes from 10 % to 90 % within 0.06-0.31 dB (raw data). So the uncertainty in P_D for a predicted arrival comes from the noise level and the propagation model, not from the detector.
- The three-element incoherent sum gives no gain at one per day (Cape Leeuwin 50 % point 17.4 dB against 16.9 dB for one element), because the tail events are real and coherent.
- An arrival with 90 % of its energy in 60 s needs 1.5-2 dB more than one in 15 s (30 s window).
- Held-out outcomes (pre-registered, one per day): the airgun test FAILS. Blackman reported 10 detections; our prediction gives P_D below 0.1 for 9 of them. The Wake test agrees on all 4 triad outcomes, but our detector did NOT detect the F-35A arrival at one per day (T1 only 6.6-7.3 dB at Wake North and 4.2-5.6 dB at Wake South, threshold about 27 dB).
- Main reason (post hoc): a scan at one false alarm per day is much less sensitive than a look at a known time. The single-window 1 % tail of T1 is 5.6-6.4 dB; the one-per-day scan threshold is 17-22 dB. Blackman knew the shot times. In addition, the frozen propagation chain is too lossy on deep Indian Ocean paths.
- Royer 2016 events (200 station outcomes, leave one receiver out): PASS over all 10 receivers (Brier 0.162 against 0.204, log-score skill 0.14, 5 confident misses of 74). The OHASISBIO receivers alone FAIL (log-score skill -0.09). The OHASISBIO picks curve is not identified: its spread reached the 50 dB numerical bound.
- Transair 810: no alarm in the predicted window (T1 at most 1.0 dB). At one per day this gives no useful energy limit; every limit is above the 73.6 MJ kinetic energy.

## 2. Parameters
| Item | Value |
|---|---|
| Band | 5-40 Hz, Butterworth 4 poles, zero phase |
| Windows | 30 s primary; 10 s and 60 s sensitivity; step 1 s |
| Noise reference | running median of window energy, 1801 s centred (IMS); record plus neighbours 15 min either side (IMOS); 10-min panel (envelope form) |
| Alarm | windows above threshold; runs closer than W are one alarm |
| False-alarm rates | 1 per day (primary), 1 per hour (sensitivity); IMOS per clock day (recorded fraction 0.339) |
| IMS null data | open EarthScope FDSN, network IM, EDH, March 2015-2019, 23:45-04:15 UTC fetched, 00:00-04:00 evaluated; Cape Leeuwin 113 days, Diego Garcia South 153 days |
| Response | full StationXML response removed (pre-filter 2-3-45-55 Hz) |
| IMOS null data | background records 1-15 Mar 2014 without 8 Mar (3250, 3274, 3376); event-day records outside the exclusion span (all five); 2 dead records left out |
| Wake null data | H11N and H11S, 7 days before and after each event day, 08:00-14:00 UTC |
| Injected signal | Gaussian noise, energy spectrum flat to 5 Hz then f^-3.1; gamma(k = 2) envelope; 90 % energy duration 15 s (primary) and 60 s |
| Injection levels | E/N0 -2 to 56 dB in 0.5 dB steps; 16 per IMS block per duration; 1 per IMOS record per duration; each injection processed alone |
| P_D model | P_D = p0 + (1 - p0) Phi((SNR - snr50)/sigma), p0 from noise-only maxima |
| Outcome prediction | s_prop 6 dB, s_src 3.5 dB (airguns), bias 0 (primary) |

## 3. Thresholds and detection probability (30 s window)
Values: threshold dB (bootstrap 5-95 %); snr50 / sigma in dB; floor p0. D = 90 % energy duration.

| Station | Data form | Threshold, 1/day | snr50 / sigma, 1/day, D 15 s | snr50, 1/day, D 60 s | Threshold, 1/hour | snr50 / sigma / p0, 1/hour, D 15 s |
|---|---|---|---|---|---|---|
| Cape Leeuwin (H01W) | raw_ims_single | 17.00 (15.35-18.80) | 16.91 / 0.12 | 18.58 | 5.95 (5.65-6.25) | 4.58 / 0.29 / 0.024 |
| Cape Leeuwin (H01W) | raw_ims_array_incoherent | 17.40 (15.80-19.30) | 17.43 / 0.13 | 18.98 | 6.00 (5.70-6.30) | 4.67 / 0.29 / 0.024 |
| Cape Leeuwin (H01W) | envelope_kadri | 15.70 (14.45-17.40) | 16.63 / 0.82 | 18.46 | 5.80 (5.50-6.15) | 5.24 / 1.00 / 0.022 |
| Diego Garcia South (H08S) | raw_ims_single | 21.90 (18.80-24.70) | 21.87 / 0.02 | 23.55 | 4.50 (4.20-4.90) | 2.46 / 0.39 / 0.023 |
| Diego Garcia South (H08S) | raw_ims_array_incoherent | 22.10 (18.80-24.40) | 21.93 / 0.07 | 23.75 | 4.45 (4.05-4.85) | 2.41 / 0.32 / 0.025 |
| Diego Garcia South (H08S) | envelope_kadri | 20.30 (17.05-23.25) | 21.38 / 0.82 | 23.17 | 4.35 (4.05-4.65) | 3.09 / 1.02 / 0.022 |
| Perth Canyon logger (IMOS 3376) | raw_imos_duty_cycled | 19.15 (17.80-23.60) | 18.84 / 0.05 | 20.76 | 6.90 (6.25-7.45) | 5.73 / 0.51 / 0.062 |
| Perth Canyon logger (IMOS 3315), proxy 3376 | raw_imos_duty_cycled | 19.15 (17.80-23.60) | 18.84 / 0.05 | 20.76 | 6.90 (6.25-7.45) | 5.73 / 0.51 / 0.062 |
| Scott Reef logger (IMOS 3250) | raw_imos_duty_cycled | 30.15 (25.44-32.35) | 29.94 / 0.09 | 31.82 | 13.05 (11.75-14.65) | 12.66 / 0.37 / 0.057 |
| Portland logger (IMOS 3274) | raw_imos_duty_cycled | 14.20 (12.90-15.35) | 13.92 / 0.10 | 15.66 | 4.60 (4.05-5.10) | 2.57 / 0.53 / 0.063 |
| Portland logger (IMOS 3275), proxy 3274 | raw_imos_duty_cycled | 14.20 (12.90-15.35) | 13.92 / 0.10 | 15.66 | 4.60 (4.05-5.10) | 2.57 / 0.53 / 0.063 |

Notes:
- IMOS 3315 and 3275 have only 5-6 recorded hours outside the exclusion span. Their own one-per-day thresholds are lower bounds (15.35 and 20.05 dB). The primary values are proxies from the other logger at the same site (amendment A3). At 3275 the proxy (14.20 dB) is LOWER than the own lower bound (20.05 dB). So the proxy is not consistent with the 3275 data, and the 3275 curve is not reliable.
- The Scott Reef logger (3250) has very loud transients (median level 109 dB, p90 120 dB). Its one-per-day threshold is 30 dB.
- The envelope form (Kadri digitised traces) is an emulation on raw IMS data. Its fit is poor (largest bin gap 0.13-0.34). pd_curves.json carries its empirical table; use that table.
- The detector sigma does not include the noise-level spread or the propagation error. The search must add noise_sd_db and the propagation sd.

![Detection probability by station]({{artifact:696ba7c3-0597-48fd-a782-17f0d26832d5}})

## 4. Held-out detection outcomes
Pre-registered family scores at one false alarm per day (primary, no bias correction):

| Family | n (detected) | Brier / constant rate | Log-score skill | Confident misses | Verdict |
|---|---|---|---|---|---|
| Airguns 2001 | 18 (10) | 0.536 / 0.247 | -3.61 | 9 of 17 | FAIL |
| Airguns, SUS-derived bias | 18 (10) | 0.522 / 0.247 | -3.04 | 9 of 17 | FAIL |
| Wake (F-35A, Transair 810) | 4 (0) | 0.0000 / 0.0000 | n/a | 0 of 4 | NOT SCORABLE for skill (one outcome class); confident misses 0 of 4 |
| Pooled | 22 (10) | 0.439 / 0.248 | -2.76 | 9 of 21 | FAIL |
| Glass spheres (report only) | 27 (9) | 0.328 / 0.222 | -1.94 | 9 of 27 | not scored |
| Royer 2016, all 10 receivers | 200 (143) | 0.162 / 0.204 | 0.14 | 5 of 74 | PASS |
| Royer 2016, OHASISBIO receivers | 140 (86) | 0.231 / 0.237 | -0.09 | 5 of 17 | FAIL |
| Royer 2016, Cape Leeuwin elements | 60 (57) | 0.003 / 0.048 | 0.90 | 0 of 57 | PASS (see note) |
| Pooled airgun + Wake + Royer | 222 (153) | 0.190 / 0.214 | -0.16 | 14 of 95 | FAIL |

One false alarm per hour (sensitivity, not the pre-registered level): airguns Brier 0.306 against 0.247, 3 confident misses of 12 (FAIL); with the SUS-derived bias 0.223, skill 0.10, 1 miss of 9 (FAIL, the miss fraction is 11 %). Wake PASS. Pooled FAIL.
Post hoc: the level track's option (no bias, per-path sd 12.6 dB) does not change the airgun verdict (FAIL at both rates). The level track's level_correction.json was not applied: it is provisional, its own held-out test failed, and it is not leave-one-source-out.

Confident misses (one per day, primary, scored families):

| Unit | Predicted SNR, 30 s (dB) | P_pred | Observed |
|---|---|---|---|
| air1-H08N | 2.0 | 0.006 | detected |
| air2-H08N | -0.0 | 0.004 | detected |
| air3-H08N | -0.2 | 0.003 | detected |
| air4-H08N | -2.7 | 0.002 | detected |
| air7-H08S | -1.6 | 0.003 | detected |
| air8-H08S | -8.8 | 0.002 | detected |
| air9-H08S | -8.1 | 0.002 | detected |
| air9-H01W_2001 | -8.9 | 0.000 | detected |
| air7-H01W_2001 | -24.8 | 0.000 | detected |

Every airgun confident miss is a published detection that the model calls too faint.

Royer confident misses: ev7-MAD (P 0.001, detected); ev13-MAD (P 0.901, not detected); ev17-MAD (P 0.949, not detected); ev7-NCRO (P 0.010, detected); ev3-WKER (P 0.010, detected). Event 7 (C1, near Chagos) is picked at MAD and NCRO although the chain gives no water path or a 247 dB loss.

### 4.2 Royer 2016 notes
- Loss: tl_royer_bands.csv (148 water paths; 12 land-crossing paths not run, P_pred 0.01). Cape Leeuwin elements 1 and 3 use the element 2 loss.
- After the first run the optimiser diverged (OHASISBIO spread unbounded, P 0.5 everywhere). Start values and a 0.5-50 dB bound on the spread were added. This is a numerical guard, not a model change, but it was added after the pre-registration.
- The OHASISBIO curve: 50 % point 15.9 dB, spread 49.4 dB (at the bound). It is not identified. Post hoc, without the 9 paths of effective loss above 160 dB: 50 % point 27.9 dB, spread 20.0 dB. Neither is usable as a likelihood.
- The Cape Leeuwin PASS is weak: holding out one element leaves two elements with the same path, and 57 of 60 are detected.
- Royer events were found because 6 or more stations saw them. This raises the detection rate. It is not corrected.
- pd_curves.json has OHASISBIO_* entries with this curve, flagged NOT IDENTIFIED, and Royer's detection rate per site (SWAMS1-3 0.90, MAD 0.60, SSEIR 0.55, NCRO 0.35, WKER 0.10).

![Predicted detection probability against observed outcome]({{artifact:dcf3e489-f090-48b3-a26e-bc8902ed7f90}})

### 4.1 Wake event days (our detector on the raw data)
- F-35A, 9 Apr 2019: in the arrival frames plus or minus 30 s, T1 reaches 7.3 dB (Wake North) and 5.6 dB (Wake South). One per day needs 27.0 and 27.1 dB: not detected. One per hour (4.2 and 5.5 dB): detected on 3 of 3 north and 1 of 3 south elements.
- Transair 810, 2 Jul 2021: T1 at most 1.0 dB (north) and 0.3 dB (south) in the predicted windows. Not detected at either rate.
- Transair 810 acoustic-energy upper limit (P_D = 0.9, s_prop 6 dB, frozen chain loss): at one per day, 5.4e+08 to 3.3e+12 J for a 10 m source (corners 5 to 0.2 Hz); all exceed the kinetic energy (73.6 MJ), so there is no constraint. At one per hour with a 5 Hz corner and a 10 m source: 5.8e+06 J (south) and 1.7e+07 J (north).

## 5. What this means for the search
1. A blind scan at one false alarm per day per station needs an arrival 17 dB (Cape Leeuwin) to 22 dB (Diego Garcia South) above the 30 s noise energy. The real F-35A arrival at Wake, about 3,300 km away, gave T1 of 6.6-7.3 dB (Wake North) and 4.2-5.6 dB (Wake South); its predicted SNR from the measured exposure is 1.9-5.3 dB.
2. The search does not need a blind scan. It predicts the arrival time, so it can use the false-alarm rate per predicted window. The single-window 1 % tail is about 6 dB. This is a gain of 11-16 dB. The Bayes-factor search (spec section 2) uses this structure; the one-per-day curve is the conservative limit.
3. Known-event association (spec section 7) can remove catalogued earthquake T-phases from the tail. That would lower the one-per-day threshold. It is not applied here.
4. The airgun failure is consistent with the frozen chain being too lossy on deep Indian Ocean paths. The model-free part of the result is the threshold and the P_D shape.

## 6. Open issues
- The OHASISBIO picks curve is not identified from Royer's 20 events. Calibrated OHASISBIO noise levels and source levels from other stations' amplitudes would be needed.
- IMOS 3315 and 3275: null too short; proxy for 3275 conflicts with its own data.
- Diego Garcia North has no open data; its airgun predictions use the Diego Garcia South curve.
- The envelope form is an emulation. The real digitised panels have plot effects that are not modelled.
- The noise_level_db for Diego Garcia South (between-shot value) and Cape Leeuwin (mean-power value minus 0.60 dB) convert the 8 Mar 2014 preferred values to the median-window definition. The Diego Garcia South conversion is not measured.
- 3-element coherent beamforming was not tried (incoherent sum only).
- Deskstar IMOS spectrogram cube not used; the on-disk 14-day background records were used instead.

## 7. Files
- Reproduction check: run_analysis.py re-ran the thresholds (138 rows, largest difference 0.00 dB) and the primary fits (36 rows, largest snr50 difference 0.000 dB) from the stored blocks.
- Code: {{artifact:ab2d31d1-56de-446c-bfd0-8f62fad9da40}} (t1core.py detector; ims_blocks.py download, null and injection; imos_blocks.py logger reader and injection; analyse.py and run_analysis.py thresholds and fits; royer_loso.py Royer test).
- Thresholds: {{artifact:dbb67e9d-01f8-4f70-bf60-a3e55e3db8e4}}. Injection results (binned): {{artifact:de888175-8eb5-42ed-bb46-6dfd23bc4a43}}. Curve fits: {{artifact:b448cecf-9c45-4f67-9d79-b03a58313cc7}}. pd_curves.json: {{artifact:de400f7e-b17d-44fb-83f1-e80710b35406}}.
- Outcome predictions: {{artifact:16b7248d-648c-4a16-8a1d-d972dd1014cc}}. Scores: {{artifact:048977e5-a717-4b22-8beb-e7090becc597}}. Calibration table: {{artifact:c41fa7c5-f453-4a09-b70e-7b9ff2edff19}}. Wake detector output: {{artifact:a366311d-ce52-4a3e-bfca-af9e07212690}}. Royer predictions: {{artifact:81c9a0b9-29c8-471d-85d3-7d22b52ee27c}}. OHASISBIO fit: {{artifact:8a5e9134-17f2-43dc-b414-9e8c0d7868c1}}. Transair 810 limit: {{artifact:7829f946-4189-437c-bd63-8e8827846dd7}}. Known-time tails (post hoc): {{artifact:52f19d53-4530-4a29-9fe4-23f587c90f6c}}.
