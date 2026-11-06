# Combined weak-signal detection: why the arrival time matters, looser false-alarm levels, and successive-sample correlation (6 Nov 2026)

Status: methods test on open IMS data (EarthScope), Cape Leeuwin and Diego Garcia South element 1. No 8 March 2014 data used. Provisional.
Follows signature-detection-test-2026-11-05.

## 1. Why the arrival time changes the result

1. Every detector is a score with a background distribution. In Gaussian noise that distribution has a thin tail.
   In real ocean noise it has a heavy tail of real events, mostly earthquake sound, which look like impacts.
2. The typical (median) real noise looks Gaussian. The tail does not. Thresholds per 2 min look
   (Cape Leeuwin, real / Gaussian with the same spectrum), from joint_background.csv:

   | Detector | 50 % | 20 % | 5 % | 5 % per 30 min | 1 per day |
   |---|---|---|---|---|---|
   | Band energy (dB above median) | 2.3 / 1.9 | 3.9 / 2.0 | 7.5 / 2.0 | 16.5 / 2.2 | 19.8 / 2.2 |
   | Correlation, impact pattern (standard units) | 2.4 / 2.1 | 4.8 / 2.6 | 16.0 / 3.2 | 78.2 / 4.2 | 118.5 / 4.6 |

3. A known arrival time means one look. An unknown time means many looks. Each extra look is another chance for a
   real impact-like event, so the threshold must rise to keep the same total false-alarm chance. In Gaussian noise
   it hardly rises. In real noise it rises steeply. That is why a signature that is rare in white noise is not rare
   enough in real noise once you search many looks.
4. The way to keep a signature's gain is to keep the number of looks small: test each station at the time that a
   hypothesised source (arc point and impact time) predicts, and combine stations.

## 2. Successive-sample correlation, and how it relates to the spectral tests

1. Raw ocean noise is coloured, so successive samples are correlated even with no signal. The noise must be
   whitened first. Here: an order-200 prediction-error filter fitted on 10 min around each 30 s window (the window
   excluded). Then the sample correlation at lags 4 ms to 0.5 s should average to zero in noise.
2. In real noise it does not fully average to zero: after whitening, lag 1 keeps a bias of about +6 standard units
   and the spread is 1.3-1.4 times the ideal; Gaussian noise with the same spectrum gives +5 and 1.05.
   The correlations are therefore standardised on the real background (median and robust spread per lag).
3. Two forms: no template (sum of squared lag correlations, any persistent structure), and matched to the lag
   pattern of the loose impact spectra.
4. By the Wiener-Khinchin theorem the lag correlations are the Fourier transform of the whitened spectrum. So the
   correlation tests are close relatives of the spectral-shape test; both ignore the overall level.
5. The earlier "persistence" test (reverse-sensing S2) works on the level envelope (sign count of samples above the
   local median, thinned, binomial tail). It was run here too, with a fixed thinning lag (0.3 s Cape Leeuwin,
   1.0 s Diego Garcia South).

## 3. Calibration checks

- Null check (signal added at -20 dB): exceedance rates match nominal for all detectors at all levels, except
  envelope persistence at the strictest levels (0.0069 against 0.0033 and 0.0014). Its strict-level numbers are optimistic.
- Two faults were found and fixed before the final run: synthetic signals had energy up to 125 Hz where the real
  instrument has none (fixed with a 1-95 Hz instrument response), and the persistence thinning lag varied by record
  (fixed per station).

## 4. Results: SNR (dB) for 50 % detection (snr50_v3.csv), Cape Leeuwin / Diego Garcia South

| Signal | Level | Band energy | Spectral shape change | Correlation, impact pattern | Combined |
|---|---|---|---|---|---|
| Dive | known time, 20 % per look | -2.0 / -2.1 | -11.9 / -10.0 | -13.6 / -13.1 | -11.1 / -10.6 |
| Dive | known time, 5 % per look | 3.8 / 3.6 | -2.8 / -1.7 | -6.9 / -5.6 | -1.5 / -1.9 |
| Dive | 30 min window, 20 % | 8.7 / 11.2 | not reached | -1.1 / 1.6 | 9.2 / 5.7 |
| Dive | 30 min window, 5 % | 13.7 / 21.2 | not reached | 4.3 / 13.5 | 13.7 / 15.0 |
| Ditching | known time, 20 % | -1.7 / -1.8 | -13.5 / -11.2 | -16.5 / -14.2 | -12.5 / -11.7 |
| Ditching | known time, 5 % | 3.7 / 3.6 | -5.4 / -2.7 | -9.6 / -6.4 | -3.5 / -2.9 |
| Real earthquake sound | known time, 20 % | -2.0 / -1.9 | -8.2 / -9.5 | -9.8 / -10.6 | -8.0 / -9.0 |
| Real earthquake sound | known time, 5 % | 3.8 / 3.6 | -1.0 / -1.9 | -2.3 / -3.8 | 0.5 / -1.6 |
| Real earthquake sound | 30 min window, 5 % | 13.8 / 21.2 | not reached / 16.7 | 15.0 / 14.2 | 11.5 / 10.4 |

Detection at -5 dB, dive, Cape Leeuwin, known time (roc_known_time.csv): at 5 % / 20 % / 50 % false alarms per look,
band energy 0.01 / 0.19 / 0.96; spectral shape change 0.32 / 0.85 / 0.98; correlation with the impact pattern
0.62 / 0.86 / 1.00; combined 0.15 / 0.94 / 1.00.

Caution: the synthetic dive and ditching signals come from the same model family as the impact templates, so their
gains are optimistic. The real earthquake waveforms (scaled down) are the realistic test: correlation with the impact
pattern gains about 6-8 dB over band energy at a known time, and little or nothing in a 30 min window.

## 5. Control on real catalogued earthquakes at their predicted times (known_events_corr.csv)

Per-look background chance below 5 %, events with catalogue SNR < 10 dB (n = 18 Cape Leeuwin, 58 Diego Garcia South):
band energy 0.17 / 0.24; combined 0.50 / 0.47; spectral shape change 0.67 / 0.41; correlation with the impact
pattern 0.39 / 0.41. Combined against band energy over all events: Cape Leeuwin 9 found only by the combined test,
0 only by band energy (McNemar p = 0.0039); Diego Garcia South 16 against 0 (p < 0.0001).
Correlation with the impact pattern alone loses at Diego Garcia South (15 against 33, p = 0.013), because it misses
some strong arrivals.
Off-arrival looks in the same records (10 min from the arrival) give false-alarm rates at the 5 % level of
0.072 / 0.103 for band energy and 0.076 / 0.114 for the combined test, so the gain is not from looser triggering.
At the 20 % level the combined test fires more often off-arrival (0.275 / 0.317 against 0.199 / 0.259), so its net
gain there is small.

## 6. What this means

1. Pete's correlation idea works once the noise is whitened, and in its matched form it is the strongest single
   detector at a known time. It is not a different signal from the spectral shape; it is the same information in
   the time domain.
2. The combined detector (band energy + spectral shape change + correlation with the impact pattern + envelope
   persistence, Fisher sum calibrated on real background) is the most robust: it is the only one that beats band
   energy on real weak earthquakes at both stations with no losses.
3. Allowing 20 % false alarms per look at a known time lets every signature detector find signals 8-16 dB below the
   noise. A 20 % rate per look is acceptable only if candidates are then tested for agreement across stations; at one
   station it gives one false candidate in five looks.
4. None of this removes earthquake sound. Real earthquake arrivals are found as easily as impacts.
5. For 8 March 2014 the data held with waveforms are the IMOS loggers only. The method needs the hypothesis grid
   (arc point x impact time) so that each logger is a known-time look, and a cross-station null by time shifts.

## 7. Files

Figure weak_signal_detector_comparison.png; gallery spectral-detection-gallery.pdf (19 pages, 38 examples: dive,
ditching, real earthquake, Z-call, airgun and implosion signals added at -10 to +5 dB at both stations; 6 real weak
catalogued earthquakes; 6 of the strongest background false alarms). Scripts: sigcorr.py, corr_records.py,
corr_post.py, joint_bg.py, pmap.py, inject.py, analyse_v3.py, looks_roc.py, known_corr.py, offlook.py, gallery.py.
Tables: injections_rnd_v3.csv, snr50_v3.csv, pd_v3.csv, snr_vs_looks.csv, roc_known_time.csv, joint_background.csv,
known_events_corr.csv, known_events_corr_offlook.csv. Inventory of earlier techniques: hydro-detection-techniques-inventory.md.
