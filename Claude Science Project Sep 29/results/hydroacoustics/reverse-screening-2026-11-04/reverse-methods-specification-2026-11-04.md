# Reverse-sensing hydroacoustic methods: pre-registered specification

Version 1.0, 4 November 2026 (section 14 deviations log filled after the screening run, same date; no other text changed). Code: `reverse_detectors.py` version 1.0.0 with `tests/test_reverse_detectors.py` (25 tests, all pass). Literature basis: `literature/reverse-methods-literature-note-2026-11-04.md`.

## 0. Status of this document

1. This specification is fixed BEFORE any arrival window is opened. When it was written, no detector had been run on 8 March 2014 data, and no arrival-window table had been read.
2. Each change after a window is opened is a deviation. Record it in section 14 with the date and the reason, and report results with and without the change.
3. Propagation is used for TRAVEL TIME ONLY. No method in this document predicts or uses a received amplitude.
4. The rulings of 4 November 2026 apply:
   - Source (impact) time is 00:19:38-00:29:44 UTC.
   - The arc span is 20-41° S on the 7th arc, ±50 NM across the arc. Sample it sparse and wide first, then denser.
   - Use the widest physically feasible propagation speeds.
   - Remove known events at an association probability of 0.95 or more, EXCEPT airgun shots at Diego Garcia South. Label those shots and give them the interference test. Never remove them.
   - Weak candidates are wanted. Give each one a p-value against an empirical null.
5. Detector codes (S1, B1, C2 and so on) are used only in code and in this document. Charts and reports use the plain names in the tables below.

## 1. Data held and their forms

| Station | Data form | Rate | Span on 8 Mar 2014 | Primary null source | Fallback null |
|---|---|---|---|---|---|
| Cape Leeuwin (H01W) | Kadri 2024 Fig. 9 plot vertices, signed Pa, 5-40 Hz | ~14.5 vertices/s, irregular | 00:27:00-00:57:00 | form-matched open IMS H01W data, March 2015-2019 (N3) | surrogates of the record (N4) |
| Diego Garcia South (H08S) | Kadri 2024 Fig. 9 plot vertices, signed Pa, 5-40 Hz; panel e has a +8.8 dB level step at the panel join | ~15 vertices/s | 01:00:00-01:19:59 | shot population of the record (S7); open IMS H08S data, March 2015 onward (N3) | N4 |
| Perth Canyon 3376, Portland 3274, Scott Reef 3250 | raw counts, 6 kHz, 8 Hz high-pass, 307 s every 900 s | 6000 Hz | full day | background days 1-15 Mar 2014, same clock hours (N2) | same-day off-window records (N1) |
| Perth Canyon 3315, Portland 3275 | as above | 6000 Hz | full day | same-day off-window records (N1) | N2 from the nearest logger at the same site |
| OHASISBIO and Cape Leeuwin picks (Royer 2016), CMST detections, Kadri Table 1 | point picks | n/a | 00:06-03:02 (Royer) | same pick list outside the windows (N1) | n/a |

IMOS times use the project clock convention A: true UTC = logger time − e(t).

## 2. Pre-processing (fixed)

1. **Plot vertices to envelope.** The signed vertices alternate between the top and the bottom of the plotted trace, so they are strongly anti-correlated by construction (unit test: lag-1 correlation below −0.8). No persistence or correlation statistic is computed on them. Convert them with `vertices_to_envelope`: envelope = maximum |x| of the vertices in each 0.1 s bin. This gives a uniform rate of 10 samples/s, which is below the vertex rate, so most bins hold at least one vertex. Empty bins are interpolated and flagged. A window with more than 20 % flagged bins is not tested.
2. **Panels.** Each published panel is a separate segment. No test window, reference ring or shot cycle crosses a panel join. This removes the H08S panel-e level step.
3. **Raw IMOS.** Use the band envelopes from `raw_to_envelope` at 10 samples/s, mode `max`, which emulates the plot extremes. Bands: 8-20, 20-40 and 40-100 Hz, plus 8-40 Hz. The last band is the overlap with Kadri's 5-40 Hz plots. The waveform detectors (S5, S6) use the band-passed pressure, decimated to 500 Hz.
4. **Levels.** All envelope statistics use y = 20 log10(envelope). No absolute calibration is needed, because every statistic is relative to a local or off-window reference.
5. **Form-matched null data (N3).** Open IMS records (EarthScope, network IM) are processed into the same form as the Kadri plots: 5-40 Hz band-pass, then the per-bin maximum |x| at the plot's time resolution, then `vertices_to_envelope`. Before use, check that the null envelope matches the quiet parts of the Kadri record in lag-1 autocorrelation (within 0.1) and in the robust spread of y (within 1 dB). If it does not match, the station falls back to N4.

## 3. Null sources

| Code | Null | Use | Note |
|---|---|---|---|
| N1 | same record, outside the arrival window ± 60 s guard | all forms | most direct; small for the Kadri records |
| N2 | IMOS background days 1-15 Mar 2014, same clock hours ± 2 h | raw IMOS | 2 weeks, about 1300 records per logger |
| N3 | open IMS H01W/H08S data, March 2015-2019, same hours, converted to the Kadri form | Kadri envelopes | H01W open data stop about mid-2019 |
| N4 | IAAFT phase surrogates and block bootstrap (block = 10 × decorrelation lag) of the record itself | fallback | conservative if the record holds a signal |
| N5 | time slides (sections 6 and 7) | network | look-elsewhere is inside the maximum |

Known natural transients (earthquakes, ice) are NOT removed from null data. The null therefore carries the natural transient rate, which makes it conservative.

## 4. Arrival windows (input, not opened here)

The arrival-window step gives each station an interval [t_lo, t_hi]. It takes the source interval 00:19:38-00:29:44, the arc span (20-41° S, ±50 NM), WGS84 geodesic distances and the widest feasible speeds. It must include at least the measured Royer path range of 1.467-1.518 km/s. Mixed land-water paths, such as Kadri's San Juan case, add an earlier branch. Each detector here runs on the whole interval plus 60 s at each end. Only the off-window null may be read before the windows are opened.

## 5. Single-station screening detectors

Each window carries all three p-values: local, station-global and method-global. Candidate rule: local empirical p ≤ 0.05. This rule is deliberately generous.

| Code | Plain name | Data forms | Window and step |
|---|---|---|---|
| S1 | Energy above the local noise | envelope (Kadri, IMOS bands) | L = 2, 5, 10, 30 s; step L/4 |
| S2 | Sample-to-sample persistence | envelope | L = 10, 30 s; step L/4 |
| S3 | Energy and persistence combined | envelope | L = 10, 30 s |
| S4 | Onset by cumulative sum (Page test) | envelope | per sample; window maxima at L = 10, 30 s |
| S5 | Impulsiveness (spectral kurtosis, Teager-Kaiser) | raw IMOS only | 10 s; step 2.5 s |
| S6 | Time-frequency excess power | raw IMOS only | tiles 0.5-8 s × 2-32 Hz |
| S7 | Shot-population anomaly | Diego Garcia South envelope | one shot cycle |
| S8 | Pick-cluster scan | picks | widths 10, 30, 60 s |

### S1 Energy above the local noise (Pete's detector 1)

- **Statistic.** L_k = 10 log10(mean power in window k). z_k = (L_k − median of L in the ring) / (1.4826 × MAD of L in the ring). The ring holds the non-overlapping windows within max(120 s, 6L) on each side, outside a guard of max(10 s, L). This is an ordered-statistic CFAR.
- **Threshold.** z ≥ 2 is the candidate flag (Pete's "about 2 sigma"). The decision value is the empirical p of z.
- **Null.** z computed the same way on the null data (N1 to N4 by station, section 1). Synthetic check: with noise only, z ≥ 2 occurs in 3.3 % of windows, so the robust-normal reading of z is nearly correct.
- **Code.** `energy_excess`.

### S2 Sample-to-sample persistence (Pete's detector 2)

- **Idea.** Under noise, the signs of the deviations from the local median sum to zero quickly. A signal holds them positive over successive samples.
- **Statistic.** d_i = y_i − median(y in the ring). Thin the samples by lag τ, where τ is the first lag at which the null autocorrelation of y falls below 0.1. Then:
  - K = the number of positive d among the n thinned samples;
  - p_bin = P(Binomial(n, 0.5) ≥ K);
  - T2 = −log10 p_bin is the decision statistic.
- **Secondary labels.** The Wald-Wolfowitz runs z on the unthinned signs (negative = clustering), and the lag-1 autocorrelation r1 of d inside the window.
- **Why thinning is fixed at 0.1.** Synthetic noise with a 1 s correlation time gave these false-alarm rates at a nominal 0.05:
  - no thinning: 0.22;
  - thinning at the 1/e lag: 0.11;
  - thinning at the 0.1 lag: 0.049.
- **Null.** T2 on the null data. The decision p is empirical. p_bin is reported as the nominal value only.
- **Code.** `persistence`, `decorrelation_lag`, `runs_test_z`.

### S3 Energy and persistence combined (Pete's detector 3)

- **Statistic.** F = −2 [ln p1 + ln p2], where p1 and p2 are the empirical p-values of S1 and S2 for the same window. The two are dependent, so the null of F is taken empirically on the same null windows and not from chi-square with 4 degrees of freedom.
- **Label.** "Both" when z ≥ 2 and p2 ≤ 0.05.
- **Code.** `fisher_combine`, `empirical_p`.

### S4 Onset by cumulative sum (refinement 1)

- **Statistic.** Standardise y by the median and robust spread of the 300 s before the window (a one-sided, causal reference). Then g_i = max(0, g_{i−1} + u_i − δ/2), with δ = 1 robust sd. The statistic is the maximum of g in the window. The onset is the last zero of g before that maximum.
- **Use.** The onset time is the value passed to the arc mapping (section 9).
- **Code.** `page_cusum`, `window_max`.

### S5 Impulsiveness (refinement 2, raw only)

- **Statistic.** Spectral kurtosis SK(f) over STFT frames inside 10 s (500 Hz rate, 128-point frames, 50 % overlap), 8-100 Hz. The statistic is max over f of SK × √M / 2, which is a Gaussian z under noise. The Teager-Kaiser energy ratio (window mean / ring median) is a secondary label used to refine the onset.
- **Null.** N2 or N1.
- **Code.** `sk_statistic`, `spectral_kurtosis`, `teager_kaiser`.

### S6 Time-frequency excess power (refinement 3, raw only)

- **Statistic.** Whiten the STFT power by the off-window noise spectrum, which comes from the rest of the same 307 s record and the same-hour background records. Sum the whitened power over tiles of 0.5, 1, 2, 4 or 8 s by 2, 4, 8, 16 or 32 Hz, inside 8-100 Hz. Each tile sum is nominally Gamma(N, 1). The statistic is max over tiles of −log10 p_nominal. The decision p is empirical, with the maximum over tiles inside each null trial.
- **Code.** `excess_power`.

### S7 Shot-population anomaly test at Diego Garcia South (Pete, 4 Nov 2026)

- **Purpose.** Use the airgun shots themselves as the reference population. A second, unrelated signal mixed into a shot cycle should make that cycle an outlier: excess energy, changed persistence of the residual, or altered shape. Energies of unrelated broadband sources add on average, so excess energy is the main feature and a deficit is secondary. The inter-shot gap is the most sensitive interval.
- **Resolution.** On raw waveforms this test would work at sample resolution, with waveform subtraction and phase. The data held allow envelope resolution only (Kadri plot, about 15 vertices/s, 10 samples/s after conversion). The test therefore sees only envelope shape and energy.
- **Measure the shots from the record, assume nothing.**
  - Floor: running 10th percentile of y over 30 s.
  - Burst: y − floor > max(6 dB, 3 robust sd); runs closer than 0.3 s are merged; minimum duration 0.2 s.
  - Shot interval: median onset difference, checked against the first autocorrelation peak of y in 2-60 s.
  - Burst duration: measured per cycle. (The module's earlier derived table gave 110 shots at about 9.98 s. This must be re-measured, not reused.)
  - Shot cycles: a least-squares comb is fitted to the onsets, and the record is split into whole cycles [onset − 0.5 s, next onset − 0.5 s). Every sample therefore belongs to one cycle, so a signal in a burst or in a gap is always inside some cycle. Only cycles between the first and last measured shot are used. Bursts more than 20 % of a period off the comb are listed separately and also go to S1-S4.
- **Features per cycle**, against a leave-one-out running median template (the median of the 10 neighbouring cycles, not including the cycle itself):
  - energy above the floor;
  - rise time (10-90 % of peak power);
  - decay rate (dB/s from the peak to the end of the burst);
  - burst duration;
  - persistence of the template residual (sign-count z after thinning; Pete's statistic);
  - residual rms;
  - correlation with the template;
  - fraction of the cycle outside the rank-r subspace of all cycles, where r captures 90 % of the energy.
- **Score.** Q = sum of squared leave-one-out robust z. Scale floors: one sample period for the time features.
- **p-values.**
  1. Local p is the exact rank among cycles (minimum 1/N).
  2. Global p is P(max Q in a null pseudo-population ≥ Q_i). It uses 1000 pseudo-populations, each built from the measured running template, the measured amplitude jitter and REAL noise blocks taken from the quiet last 30 % of randomly chosen cycles. Look-elsewhere over all cycles is inside the maximum.
- **Why the global p is a Monte Carlo value.** Parametric tails failed the null test on synthetic populations of 60 shots:
  - chi-square on Q with Šidák: global p ≈ 0 on a noise-only population;
  - generalised Pareto tail on the leave-one-out Q: 8 of 12 noise-only populations below 0.05;
  - Hotelling T² with an F reference: 16 of 40 below 0.05;
  - the Monte Carlo population null: 0 of 20 below 0.05 (minimum 0.18, so it is conservative).
- **Synthetic sensitivity.** A transient added 1.5 s after a shot onset, at the 10-s SNR relative to the floor, was found in the right cycle at global p < 0.05 in 0 of 10 trials at +3 dB, 7 of 10 at +6 dB and 9 of 10 at +8 dB.
- **Relation to the airgun rule.** S7 is the interference test that the 23 October rule requires. A candidate from any detector that coincides with a shot carries the S7 result of its cycle. It is never removed.
- **Code.** `segment_shots`, `shot_cycles`, `shot_features`, `features_from_matrix`, `shot_Q`, `simulate_population`, `shot_population_test`.

### S8 Pick-cluster scan (picks)

- **Statistic.** The maximum number of picks at one station in any interval of 10, 30 or 60 s inside its arrival window.
- **p-value.** Monte Carlo homogeneous Poisson at the off-window pick rate of the same list (20 000 trials).
- **Code.** `scan_count`, `scan_p_poisson`.

## 6. Cross-station time-shift coincidence (B1)

1. **Hypothesis grid.** Each cell is (arc latitude, cross-arc offset, source-time bin), sampled in three passes. Pass 2 and pass 3 refine only the cells whose pass-1 or pass-2 network p is ≤ 0.2.

   | Pass | Latitude step | Cross-arc offsets | Source-time step |
   |---|---|---|---|
   | 1 | 1.0° | −50, −25, 0, 25, 50 NM | 30 s |
   | 2 | 0.25° | 10 NM | 10 s |
   | 3 | 0.05° | 2 NM | 2 s |

   Points are placed by `arc_point` (7th arc as a spherical small circle, centre 0.570° N 64.252° E, radius 44.501°).
2. **Arrival interval per station and cell.** [t0_lo + D/v_hi − 5 s, t0_hi + D/v_lo + 5 s]. D is the WGS84 geodesic distance (`geodesic_km`), v_lo and v_hi are the speed bounds from the window step, and ±5 s is the onset-picking tolerance.
3. **Triggers.** Local maxima, at least 5 s apart, of the S3 score expressed as z = Φ⁻¹(1 − p_local), with p_local ≤ 0.05. For raw IMOS, use the best band.
4. **Statistic.** For each cell, the sum over stations of the best trigger z inside that station's interval. At least 2 stations must contribute. The network statistic is the maximum over all cells.
5. **Null (time slides).** Shift every station except the reference station by a random offset. The offset is at least the largest physical lag spread over the grid plus 60 s.
   - Kadri records: wrap the shift inside each record (circular).
   - IMOS: take the slid station's triggers from a background day at the same clock time (N2), which keeps the duty cycle.
   - Recompute the maximum over the WHOLE grid in each slide, with 2000 slides.
   - The global p is the fraction of slide maxima ≥ the observed value. This handles look-elsewhere over cells, stations and source times.
6. **Report two values.** Global p with the candidate's own triggers included in the background and with them excluded (Capano et al. 2017). Also report the minimum achievable p. For the 20-min Diego Garcia South record it is about 1/(number of independent shifts), where the number of independent shifts is the record length divided by the interval width.
7. **Mapping.** Each cell with network p ≤ 0.05 gives an arc-crossing band in position (the latitudes and offsets of the passing cells) and in source time.
8. **Code.** `arc_point`, `geodesic_km`, `arrival_interval`, `triggers_from_series`, `grid_coincidence_max`, `time_slide_null`, `coincidences`.

## 7. Further reverse-detection methods

### C1 Travel-time stacking over the arc grid (source scanning, non-coherent integration)

- **Statistic.** B(cell) = sum over stations of the maximum S3 z inside the station's arrival interval. The trigger threshold is not applied, so sub-threshold evidence also adds.
- **Rationale.** Envelopes on different paths are not phase-coherent, so the GNSS non-coherent rule applies and waveform stacking does not. The radar track-before-detect analogue: a cell is a "track" through station-time space, and evidence is integrated along it before any threshold.
- **Null.** The same time slides as B1, with the maximum over the grid in each slide.
- **Check.** Drop each station in turn and recompute.
- **Code.** `stack_brightness`.

### C2 Unique-transient search (matrix-profile discord and repeat count; FAST idea)

- **Statistic.** For each subsequence of y with m = 10 s or 30 s, compute:
  - the nearest-neighbour z-normalised distance to the rest of the record and the same-station null pool, excluding ±m. A large distance means a unique transient.
  - the number of near-repeats with correlation ≥ 0.875 (distance ≤ 0.5√(2m)).
- **Rule.** A candidate needs a discord p ≤ 0.05 (empirical, against off-window queries) AND S1 z ≥ 2. A window with 3 or more repeats is labelled "repeating source" (airgun, call or ice). That label goes in the table and is not used for removal.
- **Code.** `mass_distance`, `discord_and_repeats`.

### C3 Analogue-shape correlation with an energy gate

- **Templates.** Envelopes digitised from F-35A at H11 (Metz et al.), ARA San Juan, the depth charge and AF447 at H10S. They are resampled to 10 samples/s in dB and time-stretched by factors 0.5, 1 and 2 to cover range spreading.
- **Statistic.** The maximum normalised correlation over templates and stretches.
- **Gate.** A candidate needs S1 z ≥ 2 in the same window. An earlier project test showed that shape correlation alone does not respond to amplitude.
- **Null.** Off-window, with the maximum over templates and stretches.
- **Code.** `template_ncc`.

### C4 Change-point onsets (PELT)

- **Statistic.** PELT segmentation of y for mean changes, with σ from the first differences. The penalty is calibrated on the null to give one false change point per 10 min. A candidate is an upward change of ≥ 2 robust sd that is followed by a downward change within 2-120 s. The statistic is the jump size divided by σ.
- **Null.** Empirical.
- **Use.** It gives a second, independent onset time for the arc mapping.
- **Code.** `pelt_mean`.

### Confirmatory step for raw IMOS candidates only: dispersion range

If a raw candidate has 5 Hz or more of bandwidth within 5-35 Hz, fit the arrival time against frequency on the spectrogram ridge. Then invert for range with the normal-mode group speeds (Li and Gavrilov 2008). This uses timing only. It gives a range that does not depend on the arc, and it is reported as a consistency check, not as a detector.

## 8. Known events

1. **Catalogue.**
   - Royer 2016 located events and picks;
   - Kadri 2024 Table 1 transients;
   - CMST detections;
   - Royer icequake A;
   - earthquakes of M ≥ 4 on 7-8 March 2014 in the Indian Ocean and on the Antarctic margin, from an open catalogue (USGS or ISC), with predicted T-phase arrivals;
   - the H08S airgun shots, re-measured by S7.
2. **Association probability.** P = λ_k / (λ_k + λ_0) (`association_probability`):
   - λ_k is the normal density of the candidate time about the predicted arrival of known event k. Its σ is the root-sum-square of the pick uncertainty and the speed-range half-width divided by √3.
   - λ_0 is the off-window rate of candidates from the same detector at the same station.
3. **Removal.** Remove at P ≥ 0.95. The removed candidate stays in the table with its label, and its p-values are still shown.
4. **Airguns at Diego Garcia South.** Label a coincident candidate with the shot number and its offset from the shot onset, attach the S7 result for that cycle, and never remove it.
5. **Repeating-source label.** The C2 "repeating source" label is information only.

## 9. Mapping to the arc

The onset time of a candidate (from S4, refined by C4 or S5) at station s gives a source-time interval for every arc cell: [t_onset − D/v_lo − 5 s, t_onset − D/v_hi + 5 s]. The cell is kept if that interval overlaps 00:19:38-00:29:44. The set of kept cells is the station's arc-crossing band. A multi-station intersection is the set of cells kept by two or more stations whose source-time intervals overlap. Multi-station intersections are ranked above single-station bands.

## 10. p-values and look-elsewhere

| Level | Definition | Code |
|---|---|---|
| Local | empirical p of the window statistic against null windows of the same length and form; never 0; GPD tail above the null range, labelled "extrapolated" | `empirical_p`, `gpd_tail_p` |
| Station-global | minimum local p over all windows, lengths and steps inside the station's arrival window, compared with pseudo-windows of the same number of tests in the null | `pseudo_window_global_p` |
| Network-global | maximum over the whole grid in each time slide (B1, C1) | `time_slide_null` |
| Across methods | final score = minimum station-global p over methods, calibrated by the same minimum on common null pseudo-windows | `empirical_p` |

- **Ranked list.** All candidates with local p ≤ 0.05, ordered by network-global p, then by across-method p.
- **Notable.** Benjamini-Hochberg q ≤ 0.10 on the across-method p (`bh_fdr`).
- **Detection claim.** Only if network-global p ≤ 0.01 with the candidate excluded from the background, after the known-event screen, at two or more stations. Nothing weaker is called a detection.

## 11. Synthetic injection tests on the real data

1. **Where to inject.** Only into null data (N1 to N3) and into the off-window parts of the 8 March records. Injection into an opened arrival window is allowed only for upper limits, reported separately.
2. **Envelope shapes.**
   - impulsive shapes with rise times of 0.5, 1 and 2 s and decay constants of 2, 5, 15 and 40 s;
   - the analogue envelopes (F-35A at H11, San Juan, depth charge), used for shape only.
3. **Raw shapes.** Band-limited Gaussian transients modulated by the same envelopes (`inject_raw`), in each band.
4. **SNR definition (fixed).** Mean signal power over the first 10 s after onset, divided by the median noise power of the reference (`inject_envelope`). Power adds incoherently on envelopes. Grid: −12 to +12 dB in 3 dB steps.
5. **Numbers.** 200 injections per (station, shape, SNR) for S1-S6 and C2-C4. The same injected data go through every detector, so the comparison is paired. 100 per SNR for S7, with offsets uniform over the cycle (burst against gap reported separately). 500 network injections at random cells, for B1 and C1.
6. **Outputs.**
   - detection probability against SNR at local p ≤ 0.05 and at station-global p ≤ 0.05;
   - SNR50 from a logistic fit;
   - onset-time error;
   - for the network methods, the cell error (km along the arc, NM across it, s in source time);
   - the false-alarm rate on records with no injection.
7. **Synthetic reference (not real data).** Detection probability at local p ≤ 0.05 for a 1 s rise, 5 s decay shape in synthetic envelope noise (40 injections per SNR):

| 10-s SNR (dB) | S1 energy | S2 persistence | S3 combined | S4 cumulative sum |
|---|---|---|---|---|
| −9 | 0.05 | 0.00 | 0.08 | 0.08 |
| −6 | 0.08 | 0.05 | 0.15 | 0.18 |
| −3 | 0.15 | 0.35 | 0.48 | 0.42 |
| 0 | 0.72 | 0.72 | 0.95 | 1.00 |
| +3 | 1.00 | 1.00 | 1.00 | 1.00 |

On synthetic data, the combination (S3) and the cumulative sum (S4) gain about 3 dB over energy alone. This supports Pete's combined detector. The values on the real data come from item 6.

## 12. Candidate table (output schema)

`station, data_form, method, window_length_s, t_start_utc, t_onset_utc, statistic, p_local, p_local_flag (empirical/extrapolated), p_station_global, p_network_global_incl, p_network_global_excl, p_across_methods, bh_q, known_event_label, association_prob, removed (y/n), airgun_shot_no, airgun_offset_s, s7_p_global, repeating_source (y/n), arc_band_lat_min, arc_band_lat_max, arc_band_offset_nm, source_time_lo_utc, source_time_hi_utc, n_stations_intersection, null_source, notes`

## 13. Chart rules

Titles, axes and legends use plain words, with no detector codes. Every chart is footnoted with:
- the source time window and the arc span;
- the speed bounds and the station list with data forms;
- the null source per station and the number of null trials;
- the detector parameters (window, band, step);
- the known-event rule (0.95 removal; airguns labelled, not removed);
- the statement that propagation is used for timing only.

## 14. Deviations log

Recorded 4 November 2026 during the screening run (results/hydroacoustics/reverse-screening-2026-11-04). Each deviation is also listed in the run report.

| ID | Section | Change | Reason |
|---|---|---|---|
| D1 | 2.1 empty-bin gate (Kadri envelopes) | A window is not tested when more than 20 % of its bins lie in runs of 3 or more empty 0.1 s bins (gaps of 0.3 s or longer). Isolated empty bins are interpolated. | The plot vertices come in top/bottom pairs (25 % of spacings under 0.013 s), so the column rate is about 7 per second and about 22 % of 0.1 s bins are empty everywhere. The original gate rejected 66-94 % of 10-30 s windows. Every Kadri candidate carries spec_gate_20pct (pass/fail under the original rule), so results exist with and without the change. |
| D2 | 5 S7 shot interval | The shot period is found by a comb scan (2-60 s) of the onsets of the stronger half of bursts, then refined by the module's least-squares comb. | Panel e: median onset difference of all bursts 3.3 s, ACF peak 10.0 s, because 78 secondary bursts sit between shots. The specification asks for a check but gives no rule for a disagreement. Result 9.93 s (panel d) and 9.96 s (panel e). |
| D3 | 5 S6 numerical tail | Where scipy's Gamma log survival function underflows, the asymptotic series of the upper incomplete gamma function is used. | Numerical fault only: the first run floored the statistic at p = 1e-300 and 4-60 % of noise windows hit the floor. The statistic is unchanged. |
| D4 | 5 S6 noise spectrum | The whitening spectrum is the median over the frames of the same 307 s record only. | Same-hour background records were not blended in. The median over frames is robust to the transient itself. |
| D5 | 3 N2 span | N2 uses background days 1-14 March 2014 (1,344 records per logger held; 252-266 inside the clock hours). | Day 15 is not held. |
| D6 | 2.5/3 N3 form check | Pre-registered rule applied: N3 failed (lag-1 ACF of quiet parts 0.01-0.05 in the Kadri record against 0.19 in the emulated open data), so N4 is the primary null at both Kadri stations. N3 p-values are reported as p_local_altnull. | Not a deviation of the rule; recorded because it changes the calibration and because N4 proved anti-conservative for S2-S4 (see the run report). |
| D7 | 11 injection numbers | Raw IMOS: 50 injections per (logger, shape, SNR, band) instead of 200 (135,000 in total). Kadri: 200 per cell on the 8 March off-window part at Cape Leeuwin; 100 per cell on N3 hosts. Diego Garcia South: N3 host only (no off-window part of the record). S7: 100 per SNR as specified. Network injections (B1, C1) and C2-C4 not run: outside this step. | Compute time: 200 per cell would take about 3.6 h on 14 cores. Binomial standard error at a detection probability of 0.5 is about 7 % with 50. |
| D8 | 1 data forms | Added: Royer 2016 spectrogram 5-40 Hz band series (S1-S4), with a null pooled over the off-window parts of all Royer panels of the same time resolution. | Instruction to run on all data held. Colour scale saturates; marked in notes. |
| D9 | 5 S4 reference | Where fewer than 60 s precede the window in its segment, the reference is the 300 s after the window (flag 'forward'). | 307 s records and 600 s panels make a 300 s causal reference impossible at segment starts. |
| D10 | 5 S2 ring | S2 uses the S1 ring geometry (max(120 s, 6L) each side, guard max(10 s, L)). | Not stated explicitly for S2. |
| D11 | 10 station-global p | Pseudo arrival windows of the same covered duration are drawn on a virtual timeline of the null segments (5,000 draws); the same draws serve every detector at a station for the across-method calibration. S8: 3 x the minimum p over the three widths. | Equivalent to 'the same number of tests' when the duty cycle differs between records. |
| D12 | 5 candidate definition | Overlapping windows of the same station, data form, detector, window length and band that pass local p of 0.05 or less are merged into one candidate (best window kept). | Without merging, one transient gives up to 40 rows per setting. |
| D13 | 8 association | Where Royer observed the arrival at the station, t_pred is the observed time and sigma is max(2 s, element spread). Antarctic blue whale Z-call detections (113 calls at OHASISBIO sites, station times, sigma 5 s) were added on the lead's instruction of 4 Nov 2026. Kadri 2024 Table 1, Kadri 2019 and CMST transients are labels only, as their catalogue treatment states. | Inputs supplied after the specification; no detector changed. |
| D14 | Amendment 1 W1 | W1 implementation: 2 s columns, Welch 0.5 s Hann segments (7 per column), Gamma likelihood, slope grid, path term with prior sd 1, weight = 2 x null percentile (1 = null median). W1_wide (primary, Pete Large, 4 Nov 2026, via the lead): flat to a free corner 0.5-20 Hz then slope 0-5, path term, free level, and bins that the smooth fit under-explains by more than 3x count against the shape. The F-35A-centred W1 (W1_metz) is reported beside it. | Pete's steer: the F-35A comes from a much smaller aircraft. W1 changes rank only. |
| D15 | Amendment 1 classes | Source-class scores are rule-based. They were defined after the windows were opened and revised once (v2): tonality became the count of narrow bins under-explained by the smooth fit, and duration and rise were measured on the 1 s smoothed envelope. v1 measured spectral dynamic range, not tonality. Both versions are in the table. The spectral multiplier is clipped to 0.1-10. | No removal changed between v1 and v2. The class factor cannot remove a candidate alone. |
| D16 | 9 intersections | Co-located loggers (Perth Canyon 3315/3376, Portland 3274/3275) count as one site. | Avoids trivial intersections. |
| D17 | 1 Kadri vertex rate | Measured vertex rate is about 19 per second (median spacing 0.049-0.052 s), not about 14.5-15. | Observation; no parameter depends on it except D1. |
| D18 | Amendment 1 W1 injection | Reduced W1 injection check: 30 per (logger, signal class, SNR) at 0, +6 and +12 dB, impact-like and tonal control. | Compute time; it checks the direction of the weight only. |

## 15. Limits

1. **Envelope only at the IMS stations.** Cape Leeuwin and Diego Garcia South are held only as envelopes. Impulsiveness, excess-power and dispersion methods cannot run there.
2. **Short Kadri records.** They probably lie mostly inside the arrival windows (the window step confirms this). The same-record null is then small, and N3 or N4 must carry the calibration.
3. **IMOS duty cycle.** The loggers cover 34 % of the time, so a short arrival can fall in a recording gap. Coverage per window must be reported with every IMOS result.
4. **No impact template.** No recorded template exists for an aircraft impact on these paths. Sensitivity is therefore defined only through injection.
5. **Conservative population test.** The S7 Monte Carlo null is conservative on synthetic data. Real shot-to-shot variability beyond amplitude jitter (for example multipath change as the survey ship moves) is only partly modelled by the running template.
