# Transair 810 (H11, Wake Island): pre-registration of windows, statistics and thresholds

Written 25 Oct 2026, BEFORE any statistic was computed on the H11 hydrophone data. The raw records were being
downloaded while this was written; no waveform, spectrum or statistic had been looked at. Model and figure-reading
inputs used here (not statistics on data): NTSB facts, WGS84 geodesics, GEBCO path, Kadri Fig. 5b box positions.

## 1. Source and predicted windows
- Source time t0 = 2021-07-02 11:45:17 UTC (+/-1 s): CVR "sounds consistent with impact" 01:45:17 HST (NTSB final
  report DCA21FA174, p. 18); ADS-B ends 11:45:17.902 UTC; FDR record ends 01:45:16.94 HST.
- Source position 21.27616 N, 158.02565 W (NTSB Aircraft Performance Group Study, Table 4, "Estimated water impact",
  ADS-B). Wreck (forward fuselage) 167 m away.
- Receivers: IM H11N1-3, H11S1-3 (EarthScope StationXML, epoch from 2007-02-12; positions identical to stations.csv).
- c = 1.482 +/- 0.006 km/s (registry c_sofar). Triad-centroid geodesics: H11N 3655.44 km, back-azimuth 81.07 deg,
  arrival 12:26:23.6 UTC (sd 10.0 s); H11S 3699.58 km, back-azimuth 79.22 deg, arrival 12:26:53.3 UTC (sd 10.1 s).
- PREDICTED WINDOW (PW), 90 s, centred on the prediction: H11N 12:25:39-12:27:09; H11S 12:26:08-12:27:38 UTC
  (+/-45 s = 4.5 sd of the speed term, plus source duration and envelope-peak lag allowance).
- KADRI WINDOW (KW), 90 s, his Fig. 5b rectangles read at 2.4 s per pixel: H11N 12:32:12-12:33:42;
  H11S 12:31:10-12:32:40 UTC. (Rectangles: H11N 12:32:13-12:33:40, H11S 12:31:11-12:32:39.)
- Geometric fact fixed now: a SOFAR arrival from the NTSB source at 1.482 km/s cannot fall in KW (KW centre implies
  1.32 km/s at H11S and 1.30 km/s at H11N from t0); a KW signal can be the ditching only through another source time,
  place or path.

## 2. Data and pre-processing
- EarthScope FDSN dataselect, net IM, cha EDH, 250 Hz. Full StationXML response removed to Pa (pre-filter
  1/2/110/120 Hz), as OB01-OB06. Band-pass 5-40 Hz, Butterworth 4 poles zero-phase; decimate to 100 Hz.
- Windows with > 1 % missing samples are excluded from data and null (count reported).

## 3. Statistics (each a time series; a window's score is its maximum, timed at the maximum)
- D1 (module detector, searches_run_j/detectors.d1_stalta, 100 Hz variant): STA 2 s / LTA 30 s on the squared
  5-40 Hz series, hop 0.1 s. Triad statistic = mean of the three element series.
- M1b (module envelope matched filter, detectors.m1b_env): envelope = squared 5-40 Hz series smoothed 0.5 s, 10 Hz;
  correlation coefficient (local mean removed) with a zero-mean unit-energy template envelope. TEMPLATE = the F-35A
  raw-record arrival (artifact f35a_H11_raw.mseed) at the SAME triad: mean of the three element envelopes, 50 s
  long, energy peak at 35 s (module convention). Triad statistic = M1b on the triad-mean envelope. No range scaling
  (F-35A path about 3,340 km, Transair 3,655-3,700 km; declared).
- C3 (triad coherence): 5-40 Hz, 8 s frames, hop 1 s; per element pair the maximum normalised cross-correlation
  over lags |tau| <= pair distance / 1.40 km/s + 0.1 s; C3 = mean of the three pair maxima. At the frame of maximum C3,
  back-azimuth and apparent speed from a least-squares plane-wave fit to the three pair lags.
- Reported beside each score (not tests): SNR (dB) = 10 log10(max 1-s mean square in the window / median 1-s mean
  square in the 600 s before the window), triad mean; peak 1-s RMS (Pa); instantaneous peak (Pa); 4-40 Hz exposure
  over +/-15 s about the 1-s RMS peak minus median noise x 30 s (Pa^2 s), as OB01-OB06.

## 4. Null and p-values
- Background = non-overlapping 90 s windows, tiled after a 60 s warm-up, in: (a) 14 adjacent days, 2021-06-25 to
  07-01 and 07-03 to 07-09, 11:30-13:30 UTC (same clock times); (b) the event day 10:00-12:20 and 12:40-14:00 UTC
  (12:20-12:40 excluded; it holds PW and KW). Same pre-processing, detectors and window rule. Null per triad and per
  statistic. p = (k + 1)/(n + 1), k = null window scores >= the observed score; floor 1/(n + 1), stated.
- Thresholds (ruling 13 Oct): screen p < 0.3, mark p < 0.1, report p < 0.05.
- Tests: 2 triads x 2 windows (PW, KW) x 3 statistics (D1, M1b, C3) = 12. Expected by chance: 3.6 screen, 1.2 mark,
  0.6 report. Element-level D1/M1b rows are secondary.
- Likelihood ratio (M1b): LR = f_inj(s_obs) / f_null(s_obs), Gaussian kernel densities, f_inj from injections at
  the level of Kadri's reading (instantaneous peak 0.40-0.45 Pa, converted with the template's peak ratio).

## 5. Decision rules
- DETECTION AT THE DITCHING SITE: in PW, M1b p < 0.05 at both triads; or M1b p < 0.05 at one triad with C3 p < 0.05
  and bearing consistent at that triad. Bearing consistent: |baz - expected| <= 10 deg (3 x 3.3 deg demonstrated
  sd) and apparent speed 1.35-1.65 km/s. Otherwise: "no significant detection with limited power".
- KADRI WINDOW: the same rule in KW decides "signal present in his window". Its source is then tested by bearing
  (as above) and time (section 1 fact). Kadri's level is compared through peak 1-s RMS and instantaneous peak.

## 6. Measured detection probability (injection) and coupling upper limit
- Template waveform: F-35A raw record, 5-40 Hz, element H11N1 (for H11N) or H11S1 (for H11S), [peak - 35 s,
  peak + 15 s], 2 s cosine tapers. Injected into all three elements with plane-wave delays for the expected
  back-azimuth at 1.482 km/s; energy peak placed uniformly at random inside the 90 s window.
- Levels: triad-mean injected 1-s RMS peak L, 16 values log-spaced 0.003-0.3 Pa; 150 injections per level per triad,
  into background windows of the 14 adjacent days (event day excluded). Detected = M1b p < threshold against the
  null of section 4 (report, mark, screen levels). L50 from a logistic fit in log10 L. D1 and C3 P_D also reported.
- Conversion: L50 -> SE_50 (4-40 Hz exposure, Pa^2 s) with the template's exposure-to-peak ratio. Upper limit
  eta_rad,UL(z_eff, S) = SE_50 / [E rho c/(2 pi) sum_b W_b s_b(tau, slope) 10^(-TL_b/10)] (step2_invert.py relation,
  unchanged; rho c = 1025 x 1500; bands 5-63 Hz third octaves, W63 as step2). E = total kinetic energy (D1
  definition, as the F-35A 900 MJ); vertical kinetic energy as a declared alternative. z_eff 0.5, 1, 2, 5, 10 m;
  slope 2 and 4; tau 0.3, 1, 3, 10 s. TL from the module KRAKEN chain on the Oahu -> H11N/H11S paths (GEBCO 2026,
  WOA23 B5C2 July, hard bottom as step2), with a RAM check if it runs in the time available (declared if not).
- If a detection is made, eta_rad is inverted instead with the same relation, as a ridge over z_eff and S.

## 7. Standing caveats carried by every result
(C1) the propagation model failed the frequency-slope check against the 2001 airguns (+10 dB/octave H01W,
+7 dB/octave H08S) although levels passed; (C2) detection probability is a proxy unless measured on real data
(here it is measured by injection of a real arrival into real background, which removes part of C2 but not the
template-shape assumption).
Exploratory, not pre-registered: any look at the 12:20-12:40 interval outside PW and KW, and any analysis added after
the first run (labelled as such).
