"""PRE-REGISTRATION, work card X06 (proposal X06; registry defect D05; gap G-W1): FIRST REAL-ARRIVAL TEST of the module's
detectors on held IMOS raw records. Approved by Pete, 23 Oct 2026 (overnight run, item 4).

This docstring is committed BEFORE any recording sample at an event time is read by this work card. Up to this commit
the work card has read only: the registry (REGISTRY.json, INDEX.md), the module code, data/imos/recordings.csv, the
.DAT footers (start time, sub-second field), the IMOS metadata, Royer 2016 digitised tables (royer_events.csv,
royer_arrivals.csv, royer_stations.csv), the Royer cross-ID table, and the existing products' file listings and
CSV headers (ex.weak_signal injection tables, ex.searches null files). Earlier module work (items 1d/2b, run J
searches) has read some of these recordings before; their outputs (results-data/imos2b/controls.csv) are cited as a
regression check only, not used to move windows.

QUESTION. On real long-range arrivals of known events recorded by the held IMOS loggers: (1) does each detector find the
arrival at the report level alpha = 0.05 per window with the module's own window null; (2) what is the pick error
(detector pick minus reference time); (3) how does the measured detection rate compare with the injection-recovery
P_D prediction at the measured SNR (D05: P_D was measured only on model-matched templates)?

INPUTS (registry ids; read only through registry/registry.py):
  in.imos_raw (CURRENT)                 IMOS .DAT records, loggers 3315, 3376 (Perth Canyon), 3250 (Scott Reef),
                                        3274, 3275 (Portland).
  in.module_data (CURRENT)              data/imos/recordings.csv (file list, roles S/B/other from item 1d).
  code.module_prepare (CURRENT)         imos_noise.py, imos_preregistration.py, imos_detectors.py (D1, D2, Rec,
                                        null_max), searches_run_j/detectors.py (M1b, bank_env), searches_run_j/
                                        preregistration.py (bank ranges, taus, 55 s window), gates/gates.py (Land).
  results-data/imos1d/noise_bands.csv, clock_test.json (module results-data; part of the module branch).
  in.royer_2016_digitised (CURRENT)     royer_events.csv (Table 4: origin, position, standard errors), royer_arrivals.csv
                                        (Table 5 picks; implied speeds).
  art.royer_crossid (CURRENT_WITH_CAVEATS; geodesic/speed predictions, exploratory)  second source for predicted times.
  ex.searches (CURRENT_WITH_CAVEATS: D06, D24, D26)  null/null_<logger>.npz, the run J M1b window null (3315 <- 3376 and
                                        3275 <- 3274 paired-logger stand-ins, D06).
  ex.weak_signal (CURRENT_WITH_CAVEATS: D05)  templates/templates_raw.npz (M1b bank), injection/ and injection_ext/
                                        (injection scores and null maxima) for the P_D prediction.
  in.gebco_2026 (CURRENT)               land-path label (gates.Land).

KNOWN EVENTS (reference times are independent of our detectors):
  K-CMST (item a and module positive controls C1-C4 of imos_detectors.py, CMST 2014-30):
    C1 3315 01:33:44 UTC (peak energy; CMST p. 6). TIMING NOT INDEPENDENT: C1 chose the clock sign at item 1d
       (clock_test.json, +25.82 s, convention A). Its pick error is reported but kept out of the timing summary.
    C2 3315 05:03:01 (CMST p. 15/17), C3 3315 05:18:13 (CMST p. 15, 'much lower amplitude'),
    C4 3250 01:32:49 onset (CMST Scott Reef note p. 1). Reference 1-sigma: 4 s (CMST's stated +/- 4 s for C1, applied
       to all four; disclosed assumption).
  K-ROYER (item b): every Royer (2016) Table 4 solution (20 events) x IMOS logger whose PREDICTED arrival (mean) lies
    inside a held recording (time base below). Predicted arrival = origin + geodesic range (WGS84, event to logger)
    / c. c = 1.4842 km/s, sd 0.0090 km/s (Royer's own implied speeds, 143 Table 5 arrivals; recomputed by this script
    from royer_arrivals.csv as the check). 1-sigma = sqrt(sd_origin^2 + (r sd_c / c^2)^2 + (sd_range / c)^2), sd_range
    from the Table 4 lat/lon standard errors by finite difference. Sensitivity: c = 1.482 +/- 0.006 (registry c_sofar).
    Not modelled: bathymetric (non-geodesic) paths, the up-slope leg to the shallow logger, T-phase conversion.
    Pairs whose mean lies outside every recording are listed as 'not covered' with the probability that the arrival
    falls inside any recording. Royer C1 at 3315 and CMST C1 are the same arrival (counted once in counts of unique
    arrivals); Royer C2 and C3 (1.1 s and 0.07 deg apart) are counted as one arrival.
  K-OTHER (item c): no other event with an independent (catalogue or published) time is identified in the module
    notes for the held IMOS records; none is added. (Events found only by our detectors are not used.)

TIME BASE (item 1d, fixed): true UTC = footer 'First Data' + sub-second field / 65536 s - e(t) (convention A).

DETECTORS (no detector is re-implemented; module code is called):
  M1b  envelope matched filter exactly as in the run J searches (searches_run_j/detectors.imos_stats on the 500 Hz
       decimated series; 18-template bank: ranges {1800, 2200, 2376.1, 2600, 3000, 3703.5} km x tau {0.1, 1, 10} s).
       Pick = time of the maximum (template energy-peak convention, 35 s into the 50 s template).
  D1   STA/LTA of imos_detectors.Rec (5-40 Hz, STA 2 s, LTA 30 s preceding, 0.1 s step). Pick = STA centre at max.
  D2   band-power exceedance of imos_detectors.Rec (5-20 / 10-40 Hz minus 1d median, 3 s mean). Pick = 1 s frame centre.

TEST WINDOW (55 s, as the run J window length): peak-type references [t_ref - 27.5, t_ref + 27.5] s; onset-type (C4)
  [t_ref - 10, t_ref + 45] s; clipped to the part of the recording each detector can score. covered_s is reported per
  detector. Coverage probability = P(true arrival inside the scored window) under the Normal prediction.

WINDOW NULL AND p (primary, the module's own nulls):
  D1, D2: imos_detectors.null_max over the SAME logger's background recordings (role B, item 1d), sliding windows of
          the covered length, step 1 s, LEAVE-ONE-RECORDING-OUT when the tested record is in B; p = fraction >= obs.
  M1b:    the run J searches null (ex.searches null/null_<NULL_STANDIN[logger]>.npz, 'M1b', 55 s grid windows on other
          days; D06 stand-ins for 3315 and 3275); p = (k + 1) / (n + 1) as in the run J searches.
  Sensitivities (reported beside, not used for the detection call): (s1) M1b with the same-logger role-B null, sliding
  windows of the covered length, leave-one-recording-out; (s2) all three detectors with a CLEAN null that also leaves
  out every B recording holding any included reference arrival (mean +/- 3 sigma).
DETECTION: p < 0.05 per detector per window (report level, ruling 13 Oct). No other threshold. 'Any of three' is
  reported as a count only (its false-alarm rate is up to about 0.14 per window).
SNR (5-40 Hz): imos_detectors definition: max 1 s 5-40 Hz SPL in the window minus the logger's background median 1 s
  5-40 Hz SPL (dB); signal-only estimate SNR_sig = 10 log10(10^(SNR/10) - 1) (NaN if SNR <= 0; biased high near 0 dB,
  disclosed). Also reported: the same SNR statistic on the null windows (median and 95th percentile), so a reader can
  see which arrivals stand out from noise.
INJECTION P_D AT THAT SNR (D05 comparison): from ex.weak_signal injection_scores.csv + injection_scores_ext.csv and the
  null_maxima_<target>.npz of the same product (60 s windows): threshold = 95th percentile of the null maxima
  (alpha 0.05), P_D(SNR) = share of injections (pooled over tau) above it, linear in SNR between grid points
  (-15 ... 30 dB, 5 dB step), clamped at the ends. Method mapping: M1b -> M1b_mf_envelope (same statistic);
  D1 -> M0a_stalta; D2 -> M0b_bandenergy (closest weak-signal baselines; NOT identical to D1/D2, disclosed).
  Injection target: 3376 for 3315 and 3376; 3274 for 3274 and 3275; 3250 for 3250 (3315 and 3275 have no injection
  set; paired-logger targets, disclosed). P_D at alpha 0.01 from pd_vs_snr_union.csv is reported beside.
STATISTICS AND READING (fixed now):
  - Counts per detector: detected / tested, over all included windows and over unique arrivals.
  - Predicted count = sum of P_D(SNR_sig); Poisson-binomial P(N <= n_obs) and P(N >= n_obs). Reading: 'measured
    detection BELOW the injection prediction' if P(N <= n_obs) < 0.05; 'ABOVE' if P(N >= n_obs) < 0.05; else 'consistent
    with the prediction at these counts'. Fewer than 5 detected arrivals per detector: no validation claim, counts only.
  - Pick error = pick - reference time, per detected window; mean, sd, n per detector, excluding C1 (circular); also
    standardised by the prediction 1-sigma. Secondary reading on the 16 s time-base question: the mean pick error with
    its 95 % interval is compared with 0 s and with +/-16 s (GPS - UTC in 2014); no reading if n < 5.
  - Labels only (no exclusion): land path (gates.Land, GEBCO 2026), window partly in warm-up/edge, Scott Reef 3250
    path note (D03 concerns MH370 paths; here each Royer path is checked by the land label).
OUTPUTS: results-data/real_arrival_test_x06/x06_table.csv (one row per event x logger x detector), x06_summary.json,
  x06_coverage.csv (all event x logger pairs, covered or not).
COMPUTE ESTIMATE: local, about 10 min at 4 threads (about 200 recordings of 307 s read once); development 1 h.
"""
