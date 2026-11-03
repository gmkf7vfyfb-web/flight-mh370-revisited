# Pre-registration: clean-sheet detector T1, detection-probability curves and held-out detection-outcome tests

Date: 3 Nov 2026. Written and saved BEFORE any held-out outcome is scored and before any Royer prediction is made.
The noise nulls and injections (calibration, not held-out data) were already running when this was written. No P_D value or threshold was known when the rules below were fixed.
Nothing here is run on the 8 Mar 2014 MH370 prediction windows. IMOS records that start between 7 Mar 23:00 and 8 Mar 07:30 UTC are never read.
Language: ASD-STE100 for work-specific text.

## 1. Detector T1 (band-energy excess)
- Input: pressure in Pa after the instrument response is removed (IMS: full StationXML response, pre-filter 2-3-45-55 Hz; IMOS: system gain per band plus hydrophone sensitivity).
- Band-pass 5-40 Hz, Butterworth 4 poles, zero phase.
- e1[n] = band energy in second n (Pa^2 s). E_W(t) = sum of e1 over the window [t, t+W). Step 1 s.
- Noise energy level in the same window N_W(t): running median of E_W over 1801 s, centred (IMS). IMOS: median of E_W over the record and the records 15 min before and after. Envelope form: median of E_W over its 10-min panel.
- T1(t) = 10 log10(E_W / N_W) dB.
- Window: W = 30 s primary. W = 10 s and 60 s are sensitivity cases.
- Alarm: a run of windows with T1 above the threshold. Runs closer than W seconds count as one alarm.
- Flagged data (gaps, constant counts, 10 s either side) are not used.
- SNR_dB = 10 log10(E_s / N_W), with E_s the band energy of the whole arrival (5-40 Hz). This is the shared schema definition.

## 2. Thresholds (empirical tails)
- Raw IMS, Cape Leeuwin (H01W1-3) and Diego Garcia South (H08S1-3): March 2015-2019, 00:00-04:00 UTC each day, open EarthScope data.
- Wake (H11N, H11S): 7 days before and 7 days after each event day (F-35A 9 Apr 2019; Transair 810 2 Jul 2021), 08:00-14:00 UTC. The event days are not in the null.
- IMOS loggers: 14-day background records (1-15 Mar 2014 without 8 Mar; loggers 3250, 3274, 3376) and event-day files outside the exclusion span (all five loggers).
- Rate = alarms per hour of valid data. IMOS: alarms per CLOCK day, so rate per recorded hour x (307/900) x 24.
- Threshold for rate r = the lowest threshold on a 0.05 dB grid at which the empirical rate is at most r. r = 1 per day (primary), 1 per hour (sensitivity).
- Uncertainty: 1000 bootstrap resamples of whole days (whole blocks).
- All real transients stay in the null (earthquakes, ice, whales, ships, airgun surveys). They are real false-alarm sources for a scan detector.

## 3. Data forms
1. raw_ims_single: one IMS element. The three elements are pooled as samples of one detector.
2. raw_ims_array_incoherent: mean of the three element energies e1. No beamforming.
3. raw_imos_duty_cycled: one logger hydrophone, 307 s per 15 min. A missed record is missing data, not a non-detection.
4. envelope_kadri: emulation of the digitised Kadri traces. Per 0.0523 s bin the largest |p| of the 5-40 Hz trace is kept (vertex), energy = sum of vertex^2 x 0.0523 s, reference = 10-min panel median. The emulation uses raw IMS data; its fidelity to the printed plots is not tested here.
5. picks_ohasisbio: published arrival picks (Royer 2016 Table 5). Detection = a pick is listed. P_D comes from section 6.

## 4. Injection bench
- Signal: Gaussian noise with energy spectrum flat to f_c then (f/f_c)^-3.1, f_c = 5 Hz (inside 5-40 Hz the shape is the same for f_c = 1 and 0.2 Hz). Intensity envelope gamma(k = 2). 90 % energy duration D = 15 s (primary, impulsive source at 1,000-5,000 km) and D = 60 s (long T-phase, sensitivity).
- Each injection is processed alone. The noise reference N_W is taken from the noise-only data. So no detector memory is shared between injections.
- Levels: E_s / (noise power x 1 s) from -2 to 36 dB, 1 dB steps. 16 injections per IMS block per duration; one per IMOS record per duration.
- Detection of an injected arrival: any window that overlaps the 5-95 % energy span has T1 above the threshold.
- Fit: P_D = Phi((SNR - snr50)/sigma) by maximum likelihood on the binary outcomes. Report the empirical P_D in 1 dB SNR bins and the largest gap between fit and bins.
- sigma_db describes the detector and short-term noise only. The noise-level spread (noise_sd_db) and the propagation error (level_correction sd_db) are added by the user of the curve.

## 5. Predicted P_D for a known outcome
P_pred = Phi( (SNR_pred + bias - snr50) / sqrt(sigma^2 + s_prop^2 + s_src^2 + s_noise^2) )
- Detector: single element, raw IMS form, 1 per day threshold, W = 30 s, D = 15 s (airguns, F-35A, Transair 810) and D = 60 s (Royer events).
- s_prop = 6.0 dB (interim value: the level-track file level_correction.json does not exist when this is written). bias = 0 (primary).
- Sensitivity (Indian Ocean only, from the SUS charges, a different source type from the airguns): bias = +8.75 dB at Cape Leeuwin and +3.25 dB at Diego Garcia South and North (mean of route A and route B results). 
- If a leave-one-source-out level_correction.json from the level track becomes available, it is reported as a third variant, labelled post hoc.

### 5.1 Blackman 2001 airguns
- Outcomes: the 18 paths with a printed detected or not-detected status (10 detected, 8 not detected) in dg_data_blackman_blackman_receiver_observations. 1 ambiguous path (air6 to Diego Garcia North) and 8 not-reported paths are not scored.
- Source: Tolstoy 2004 far-field back-projection (nominal grid rows), energy spectral density per third-octave band x bandwidth, bands 5-40 Hz. s_src = 3.5 dB.
- Loss: frozen chain tl-chain-2026-10-27, source depth 9 m (the nearest to the 7.5 m tow depth), receiver depth of the 2001 station.
- A path that the chain marks as blocked on the geodesic gets P_pred = 0.01.
- Noise: Blackman 2003 cruise medians (5-40 Hz): Cape Leeuwin 101.61, Diego Garcia South 95.87, Diego Garcia North 90.97 dB re 1 uPa^2. s_noise = (p90 - p10)/2.563.
- P_D curve: Cape Leeuwin for H01, Diego Garcia South for H08S and (as a proxy, no open data) for H08N.
- One shot is the unit. Blackman used single-shot spectrograms with no stacking. The test checks the whole chain (source, loss, noise and our detector), not Blackman's analyst.

### 5.2 Blackman 2003 glass spheres (deep branch)
- Reported, not scored in the pooled result. The test-C received SNR (40-100 Hz band, its own definition) is passed through our curve. The band and the SNR definition differ from ours; the numbers are indicative only.

### 5.3 F-35A at Wake (detected)
- SNR_pred from the measured triad exposures (H11N 0.284, H11S 0.0955 Pa^2 s, 4-64 Hz) and the Wake noise from the H11 null blocks. This is NOT an independent source level (the coupling is calibrated on this event). Flagged.
- Observed outcome under our detector: an alarm at the 1 per day threshold whose windows overlap the Metz arrival frames (H11N 11:02:55-11:03:25, H11S 11:03:55-11:04:25 UTC) +- 30 s, on the event-day block.

### 5.4 Transair 810 at Wake (not detected)
- SNR_pred from the test-B model received energy (median; spread from q05-q95 / 3.29 replaces s_prop).
- Observed outcome under our detector: an alarm overlapping [t_pred - 30 s, t_pred + 90 s], t_pred = 12:26:24 (H11N), 12:26:53 (H11S) UTC.
- Energy upper limit: the acoustic energy E_a (shared source model, depth 10 m; 2 m and 30 m reported; corners 5, 1, 0.2 Hz) at which P_pred = 0.9, with the frozen-chain loss to each triad and s_prop = 6 dB. If our detector alarms in the window, no limit is given.

### 5.5 Royer 2016 events
- Outcomes: 20 events x 10 receivers (H01W1-3, MAD, NCRO, WKER, SWAMS1-3, SSEIR). Detected = an arrival is listed in Royer Table 5.
- Loss: the Royer TL table from the lead session (RAM, same settings as the dense grid). Effective band loss with the shared source shape (f_c = 5 Hz, n = 3.1). Paths with no water path get P_pred = 0.01.
- Noise: Cape Leeuwin 104.28 dB (8 Mar 2014 preferred value). OHASISBIO: Royer figure noise medians (5-40 Hz): SSEIR 102.6, SWAMS3 101.8, SWAMS1 and SWAMS2 103.3, MAD 91.9, NCRO 105.0, WKER 106.7 dB. These are colour readings, not calibrated, s_noise = 3 dB.
- Model: P(detect at k, s) = Phi((SL_k - TL_ks - N_s - 10 log10 W - c_f) / sigma_f), with one curve (c_f, sigma_f) for each data form: IMS raw (fixed from our injection curve, with s_prop added) and OHASISBIO picks (free). SL_k is free for each event, prior N(median, 20 dB).
- Leave-one-station-out: for each receiver s, fit SL_k and the OHASISBIO curve on the other 9 receivers, then predict s. These held-out predictions are scored.
- The OHASISBIO curve for pd_curves.json is the fit on all receivers. It is anchored only through the Cape Leeuwin detections, so its absolute level is weak. It is labelled provisional.
- Bias: Royer events were found because they were detected at 6 or more stations. This selection raises the detection rate. It is stated, not corrected.

## 6. Scores and pass/fail
- Brier score; log score (natural log, P clipped to [0.001, 0.999]); baseline = constant rate equal to the observed fraction in the same family. Skill = 1 - score/baseline.
- Calibration table: P_pred bins [0, 0.1), [0.1, 0.3), [0.3, 0.5), [0.5, 0.7), [0.7, 0.9), [0.9, 1]; observed fraction and count per bin.
- Confident miss: P_pred > 0.9 and not detected, or P_pred < 0.1 and detected. Every one is listed.
- PASS for a family: Brier skill > 0 AND log-score skill > 0 AND confident misses <= 10 % of the confident predictions. Otherwise FAIL. Families: airguns, Royer (held-out receivers), Wake (F-35A + Transair 810, 4 triad outcomes; scored but flagged), pooled (airguns + Royer + Wake). Glass spheres: reported only.
