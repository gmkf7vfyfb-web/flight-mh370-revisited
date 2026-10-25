# F-35A raw Wake Island records: pre-registration of measurements, the 20 Hz gap test and the coupling ridge

Written 25 Oct 2026, BEFORE any statistic below was computed on the raw records by this track.

**Disclosure.** A previous session (25 Oct 2026) already measured, on the 10:50-11:20 UTC raw records: 1-s RMS peaks
(0.31-0.38 Pa H11N, 0.20-0.27 Pa H11S, 4-40 Hz), instantaneous peaks 0.69-1.26 Pa (4-40 Hz), exposures over peak +/-15 s
(0.24-0.28 Pa^2 s H11N, 0.07-0.12 Pa^2 s H11S) and peak times (db_received_observation OB01-OB06). I have read those
values, the digitised Metz numbers (obs_envelopes.csv, obs_summary.json, fig3EH detection windows) and the Metz near-field
note (20 Hz gap, implied slopes -9.4 to -14.9 dB/octave). I have NOT seen any raw spectrum, band exposure, back-azimuth fit,
TL at the new depths or bands, or raw-based coupling. Everything is EXPLORATORY calibration of the source model on another
event; nothing returns to end of flight; no received duration is used for MH370.

## Data and processing (P)
- P1. Records: IM.H11N1-3, H11S1-3, channel EDH, 250 Hz, EarthScope FDSN dataselect; event window 10:30-11:40 UTC; seven
  30-min background windows the same day starting 01, 04, 07, 14, 17, 20, 23 h UTC. Response: StationXML (level=response)
  for 9 Apr 2019. Element coordinates: the StationXML channel epoch valid on 9 Apr 2019.
- P2. Response removal: obspy remove_response(output = pressure, Pa), pre_filt (0.5, 1, 110, 120) Hz, no water level,
  after demean and 5 % cosine taper of the full window. Units Pa throughout.
- P3. Metz band: 4-pole zero-phase Butterworth 4-64 Hz. 1-s moving mean square (boxcar), hop 0.02 s (Metz 98 % overlap);
  level L in dB re 1 uPa.
- P4. Analysis frames for the module observation operator (obs.py conventions, unchanged): the Metz Fig. 3C/D frames,
  H11N 11:02:55-11:03:25, H11S 11:03:55-11:04:25 UTC. L_n = median L outside peak +/-8 s inside the frame; arrival window =
  contiguous samples around the peak with L > L_n + 1 dB; SE_obs = sum (10^(L/10) - 10^(L_n/10)) dt (Pa^2 s, 4-64 Hz);
  -6 dB width (contiguous samples >= peak - 6 dB); 5-95 % span of the noise-subtracted energy in the window.
  Variant N2 (long noise): L_n replaced by 10 log10 of the mean 1-s mean square over 10:45:00-11:01:00 (both triads).
- P5. Arrival time per element: time of the 1-s RMS peak (4-64 Hz) and onset (last sample before the peak with
  L <= L_n + 3 dB).
- P6. Back-azimuth: per triad, 4-64 Hz (primary) and 5-40 Hz; 6-s windows (Metz), 1-s step, over the arrival window +/-3 s;
  pairwise cross-correlation delays (parabolic sub-sample), least-squares horizontal slowness from the three pairs; report
  back-azimuth, apparent velocity and closure (|d12 + d23 + d31|, ms). Element positions to local east-north (WGS84 geodesic
  from the triad centroid); 3-m depth differences ignored (declared). Triad value = energy-weighted circular mean over
  windows with closure <= 16 ms and apparent velocity 1430-1530 m/s (Metz gates); uncertainty = weighted SD over windows.
  Compared with the geodesic back-azimuth from the module working point W (40.64 N 142.96 E) and from the Metz-consistent
  point P (40.4496 N 142.9237 E).
- P7. Third-octave band exposures, centres 2, 2.5, 3.15, 4, 5, 6.3, 8, 10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80, 100 Hz
  (4-pole zero-phase Butterworth on the edges fc 2^(+/-1/6)). Common window W_b = [arrival start - 2 s, arrival end + 2 s]
  from P4. Excess E_b = sum_W x_b^2 dt - N_b |W|, N_b = mean of 1-s mean squares over 10:45:00-11:01:00 (variant: median).
  Noise uncertainty sigma_b = SD of (sum x_b^2 dt over |W| - N_b |W|) over non-overlapping windows of length |W| in the
  seven background windows and the pre-event segment. A band counts as measured when E_b >= 2 sigma_b AND the
  window/noise ratio >= 3 dB (the route-2 rule).
- P8. Spectrum to 100 Hz: Welch PSD (1-s Hann, 50 % overlap) over W_b, minus the noise PSD (same estimator, pre-event
  segment) times |W| = excess ESD (Pa^2 s/Hz); noise PSD percentiles (5/50/95) from the 30-min background windows.
- P9. Instantaneous peak |p| per element in 2-100, 4-64 and 4-40 Hz, and after response removal only (1-110 Hz).

## 20 Hz gap test (G), descriptive, thresholds fixed now
- G1. Gap depth D20 = mean excess ESD in dB over 18-24 Hz minus the mean of the 12-17 Hz and 26-34 Hz means (dB).
  95 % interval by bootstrap over the 1-s Welch segments in W_b (2000 resamples, seed 20261025).
  "Gap present" at an element if D20 <= -3 dB and the upper 95 % bound < 0; "absent" if the lower bound > -3 dB;
  otherwise "unresolved".
- G2. Instrument: amplitude response of the full StationXML response at 12-34 Hz; a response artefact needs a feature
  of >= 1 dB in 18-24 Hz relative to the 12-17/26-34 Hz means.
- G3. Noise: the same D20 statistic on the noise PSD (pre-event and backgrounds). A noise peak (e.g. 20 Hz fin-whale
  pulses) would make D20_noise > +3 dB, which can turn noise subtraction into an apparent gap in a figure.
- G4. Two-pulse check: the same statistic at 60 Hz (55-65 Hz against 45-52 and 68-80 Hz). A 25-ms two-pulse source
  predicts notches at 20 and 60 Hz.
- G5. Metz filtering: Metz state a 4-64 Hz band-pass; a band-pass does not make a notch at 20 Hz. Their spectrogram
  window and colour scale are compared with ours descriptively only.

## Coupling ridge (D1, D4, D2)
- R1. TL: the module chain unchanged (tl_grid_run_j.run_path with the step2_tl.py loaders: GEBCO_2026 NW Pacific layer,
  WOA23 B5C2 April, KRAKEN adiabatic incoherent, hard bottom cp 1650 / rho 1.9 / 0.5 dB/lambda, Francois-Garrison,
  spherical correction), receivers = triad centroids and mean hydrophone depths (stations.csv). Source depths
  1, 2, 5, 10, 20, 30, 50 m; the 18 bands of P7. Paths W->H11N, W->H11S (primary) and P->H11N, P->H11S (location
  sensitivity).
- R2. KRAKEN+RAM: delta = TL_RAM - TL_KRAKEN from results-data/ram_check/ram_vs_kraken.csv (f35a_H11S, 5/10/20/40 Hz,
  z 10/30 m), as step2_invert.ram_delta: interpolated in log f, held at the end values outside 5-40 Hz; z <= 10 m takes the
  10 m delta, z >= 30 m the 30 m delta, 20 m the mean; H11N takes the H11S delta (module convention). If a new pyram run on
  W->H11N (same ram_band settings) completes, its own delta is reported as a sensitivity, not as primary.
- R3. Families S: F2 = band_fraction(fc, 1/tau, 2), F4 = band_fraction(fc, 1/tau, 4), tau = 3.30 s (module fallback; eta is
  the same for every tau >= 1.1 s); Ffit = band_fraction with exponent n_fit = -(fitted source ESD slope)/3.01, the slope
  fitted per depth by OLS on log2 f over the measured bands (P7 rule) in 5-63 Hz, pooled over six elements (element means of
  S_b). Low-frequency cavity branch only if the implied source ESD in 2-4 Hz exceeds the Ffit power-law extrapolation by
  >= 3 dB at both triads with the bands measured; otherwise reported as not supported (limited power below 4 Hz).
- R4. D1 primary (like-for-like with CV01-CV03): eta = SE_obs(4-64, P4) / [E rho c/(2 pi) sum_{5-63} W_b S_b 10^(-TL_b/10)],
  W_63 = 0.54, E 900 MJ, rho c 1025 x 1500. Per element, per triad (linear mean of three exposures) and pooled (geometric
  mean of the two triads). Extension: the same over 2-100 Hz with SE_obs = sum of band excesses E_b (unclipped).
- R5. D4 in-band: (2 pi / rho c) sum_b E_b 10^(TL_b/10) / E over 5-63 Hz (bands scaled to SE_obs as route B) and over the
  measured bands 2-100 Hz.
- R6. D2 Arons: W_TNT = [R / ((P/52.4e6)^(-1/1.13))]^3 kg, 4.184 MJ/kg, / E; P = instantaneous peak (P9, every band) and the
  1-s RMS peak; R = geodesic range W->triad centroid.
- R7. Error budget per ridge point (log-normal, 1 sigma): energy +/-200 MJ as 1 sigma; element-to-element = SD of ln eta
  over the three elements of a triad / sqrt(3), pooled; station-to-station = |ln(eta_N/eta_S)|/2; location = |ln(eta_P/eta_W)|;
  combined in quadrature into value_low/value_high (68 %). Propagation option (RAM vs KRAKEN-only) and spectral family are
  epistemic switches: reported as separate rows with their ratios, never averaged.
- R8. Comparisons: near-field digitised ridge 0.106 / 4.43e-3 / 6.79e-4 (2/10/30 m, KRAKEN-only); project far-field values
  CV01-CV03 (KRAKEN+RAM) and CV10-CV12 (KRAKEN-only); digitised D4 1.2e-3; D2 2.08e-4 (0.7 Pa).

Standing caveats travel with every number: (1) the module TL fails the 2001 airgun frequency-slope check (+10 dB/octave
at H01W, +7 at H08S) although levels pass; (2) detection probability is a proxy unless measured on real data.
