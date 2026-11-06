# Spectral-signature detection below the noise: test of the idea (5 Nov 2026)

Status: methods test on open data. No 8 March 2014 data were used. Provisional.

## 1. The question

Pete's idea has three parts. The received spectrum of (a) a high-energy dive and (b) a prolonged shallow ditching is
(i) predictable within bounds and (ii) distinctive against other sources. If both hold, (iii) a known signature can
find a signal below the site noise, as a GPS receiver finds a code below thermal noise.

## 2. Verdict in one paragraph

The idea is partly valid. It works when the arrival time is known to about two minutes. Then a test on the change
in spectral shape finds dive and ditching signals 2 to 7 dB below the band noise, where band energy needs +3.6 dB.
A stereotyped whale call (the Z-call) is found 7 to 10 dB below the noise with its own template. That is the true
GPS analogue. The idea fails as a blind or wide-window search at one station. There the strongest real transients,
mostly earthquake sound, set the threshold. Real earthquake sound has the same spectral signature as an impact
(54-86 % labelled impact-like), so no single-station signature removes it. The signature does separate impacts from
whales, ships, ice tremor and airgun trains (at most 10 % of these are labelled impact-like). The way forward is to
make every station a known-time test, with timing that a source on the arc predicts, and to combine stations.
This is a coincidence search: the timing pattern across stations takes the place of the GPS code.

## 3. Why the GPS analogy holds only in part (theory)

1. GPS gain comes from a deterministic code and coherent integration: about 30 dB for 1 ms of C/A code and
   43 dB for 20 ms. An impact sound is a random-phase transient. Only its power spectrum and envelope are known,
   and only roughly. The gain is then incoherent and grows as the square root of bandwidth x time.
2. That gain is already in plain band energy. For 5-40 Hz and 30 s (BT about 1,050), band energy finds a band SNR
   of -10 to -13 dB in stationary Gaussian noise. No template is needed.
3. Knowing the spectrum adds the Eckart weighting gain. With the measured noise spectra at Cape Leeuwin and
   Diego Garcia South this is 0.3 to 4.7 dB (typically 1 to 3 dB) for corners of 1 to 20 Hz and slopes of 2 to 4
   (gain_budget.csv).
4. The working limit is the uncertainty in the noise level, not the noise. A 1 dB uncertainty gives a detection
   wall at -3.3 dB, and 2 dB gives -0.2 dB (Tandra and Sahai). Real thresholds are higher still, because real
   transients are present: 1 false alarm per day needs +18.8 dB (Cape Leeuwin) and +26.2 dB (Diego Garcia South)
   with band energy in this test.
5. Thus a signature can only help in two ways: (a) a shape test that ignores level changes, and (b) rejection of
   clutter that has a different signature. The tests below measure both.

## 4. Data and method

- Open IMS hydrophone data (EarthScope FDSN), element 1, 250 samples/s. Cape Leeuwin (H01W1), Diego Garcia South
  (H08S1).
- Background: 144 (Cape Leeuwin, 2015-2019) and 178 (Diego Garcia South, 2015-2025) random-time 40 min records.
  These give 2,869 and 3,553 two-minute looks that set every threshold.
- Real events: 237 and 448 catalogued earthquakes with predicted sound arrival times (bearing-check event set).
  These were 40 min records centred on the arrival.
- Spectrogram: 1.024 s Hann, 50 % overlap, 3-60 Hz. Whitened by a 10 min running median. Cells clipped at 4 x noise.
- Detectors:
  - Band energy only: 5-40 Hz, 30 s window over the running median (as the earlier T1 detector).
  - Loose impact spectral templates: locally optimal weak-signal score. The whitened spectrogram is projected onto
    20 spectral shapes (corner 0.7-20 Hz, slope 0-4.5, through the channel) and 9 envelopes (dive 4-25 s decay,
    ditching 20-70 s emergent). This follows Pete's loose impact class.
  - Spectral shape change only: the same, after the broadband level of each 1 s frame is removed. This test is
    blind to level changes.
  - Discrimination: the impact score against the best clutter-class score (earthquake, airgun, ship, ice tremor,
    whale templates).
- Injections: 9 synthetic classes plus real strong earthquake sound from the same station, scaled down. 80 cases per
  class and station, at -20 to +30 dB. The SNR is the largest 30 s signal energy in 5-40 Hz over the local noise
  energy in 30 s.
- False-alarm levels: known time, 5 % per 2 min look; 30 min search window, 5 % per window; blind, 1 per day.
- Null check: at -20 dB injected, the exceedance rates are 0.049-0.066 for a nominal 0.05.

## 5. Results

### 5.1 Known arrival time (5 % per 2 min look): SNR (dB) for 50 % detection (snr50_rnd.csv)

| Signal | Station | Band energy | Loose impact templates | Shape change only | Whale template |
|---|---|---|---|---|---|
| High-energy dive | Cape Leeuwin | 3.7 | 3.2 | -3.7 | |
| High-energy dive | Diego Garcia South | 3.6 | 0.8 | -2.1 | |
| Shallow ditching | Cape Leeuwin | 3.6 | 3.2 | -6.6 | |
| Shallow ditching | Diego Garcia South | 3.6 | 0.8 | -2.7 | |
| Real earthquake (scaled) | Cape Leeuwin | 3.7 | 3.2 | -1.8 | |
| Real earthquake (scaled) | Diego Garcia South | 3.6 | 1.3 | -2.2 | |
| Implosion | Cape Leeuwin | 3.6 | -1.4 | not reached | |
| Implosion | Diego Garcia South | 3.6 | -2.1 | not reached | |
| Blue whale Z-call | Cape Leeuwin | 3.6 | not reached | not reached | -6.9 |
| Blue whale Z-call | Diego Garcia South | 3.6 | not reached | not reached | -10.3 |

The shape-only test saturates on strong broadband signals, so it does not reach 50 % for the implosion. Its use is
for weak signals, combined with band energy. The min-p combination ("band energy or shape", calibrated on the background) is valid at this level only; at the
strict levels its empirical p-values floor at 1/(n+1) and it saturates. At the known-time level it gives
ditching -4.0 / -0.4 dB and dive -0.2 / 1.1 dB (Cape Leeuwin / Diego Garcia South; snr50_combo_rnd.csv).

### 5.2 The gain does not survive an unknown time: dive, SNR (dB) for 50 % detection

| Station | Level | Band energy | Loose impact templates | Shape change only |
|---|---|---|---|---|
| Cape Leeuwin | 30 min window | 14.0 | 15.4 | not reached |
| Cape Leeuwin | blind, 1 per day | 18.8 | 17.1 | not reached |
| Diego Garcia South | 30 min window | 16.2 | 17.3 | not reached |
| Diego Garcia South | blind, 1 per day | 26.2 | 21.9 | not reached |

### 5.3 Distinctiveness: largest fraction detected and labelled impact-like (known time, any SNR)

Dive 0.82-0.91, ditching 0.66-0.91, implosion 0.98-1.00, real earthquake 0.54-0.85.
Model earthquake 0.02-0.08, ice tremor 0.05-0.09, airgun shots 0.08-0.09, ship 0.04-0.09, Z-call 0.09-0.10,
fin whale 0.04-0.06. (Ranges are Cape Leeuwin and Diego Garcia South.)

The synthetic earthquake is not labelled impact-like, but real earthquake sound is. The earthquake model is
too narrow. This is a warning about template mismatch: on real catalogued earthquakes the narrow earthquake template
did worse than band energy (Cape Leeuwin 1 gained, 11 lost; Diego Garcia South 8 gained, 24 lost).

### 5.4 Control: real weak earthquakes at their predicted times (earthquake-centred records)

- Loose impact templates ALONE against band energy ALONE, each at 5 % per look (known_events_p.csv): Diego Garcia
  South 23 found only by the templates, 4 only by band energy (McNemar p = 0.0003). Cape Leeuwin 3 against 2 (p = 1.0).
  For catalogue SNR < 10 dB at Diego Garcia South: 16 % against 5 %; for 10-15 dB: 64 % against 33 %.
- This gain is NOT robust. A combined detector (band energy at 2.5 % OR templates at 2.5 %), compared with band energy
  at 5 % (known_events_control.csv), loses: Diego Garcia South 6 gained, 21 lost (p = 0.0059); Cape Leeuwin 0 gained,
  3 lost (p = 0.25). Many real arrivals sit just above the band-energy threshold, so halving its false-alarm budget
  costs more than the templates add. The real-event control therefore does not establish a template gain.
- Shape change only, combined with band energy (2.5 % each): no clear gain on the weak events (Cape Leeuwin 3/18
  against 2/18; Diego Garcia South 4/59 against 4/59). This does not confirm the 5 to 6 dB injection gain for real
  earthquake waveforms. Possible causes: active records, larger travel-time errors on weak paths, and weak events that
  may not be in the data at all. Several detector variants were tried, so treat single results with care.
- Two-station test: only 5 events are weak at both stations. Too few to judge.

## 6. What this means for the 8 March 2014 data held

1. Spectral tests need raw waveforms. Of the 2014 data held, only the five IMOS loggers have them (307 s in every
   15 min; 30-42 % of the arrival windows). The Kadri traces for Cape Leeuwin and Diego Garcia South are envelopes and
   have no spectrum. The Royer spectrogram colour readings are too coarse for a shape test.
2. At a single station with a 20-30 min arrival window, the signature gives at most a few dB, or nothing.
3. A real gain needs known-time tests: for each arc point and source time, every station gets a 2 min look at its
   predicted arrival. The look-elsewhere cost is then paid once over the grid, not once per station.

## 7. Recommended development (decided, with reasons)

1. Adopt the shape-change score as the per-station statistic for weak signals, always paired with band energy.
   Reason: it is the only test that went below the noise for impact-type signals with real noise.
2. Build the network coincidence test on hypotheses (arc point x source time). Set the null by time slides (shift
   station records against each other by more than the travel-time spread), as gravitational-wave searches do.
   Reason: the timing pattern across stations is the only "code" an impact has.
3. Keep the impact class loose. Use catalogue timing and the network geometry, not the spectrum, to separate impacts
   from earthquake sound. Reason: real earthquake sound passes as impact at 54-86 %.
4. Use spectral templates where the signal is stereotyped (whale calls, airgun bubble ripple) to remove that clutter
   with positive evidence, as in the 0.95 rule. Reason: this gave 10-14 dB of gain for Z-calls.
5. Add the secondary-implosion lag (Amendment 3) as a second within-station timing pattern. Reason: it shares the
   path, so the lag is a known structure that earthquakes do not have.
6. Before any 2014 run, measure the IMOS background with the same detectors on the IMOS background days held.

## 8. Files

Scripts: sigdet.py (library), fetch_eq.py, fetch_bg.py, score_records.py, background.py, background2.py, inject.py,
analyse_inj.py, combo.py, known_control.py. Tables: snr50_rnd.csv, snr50_combo_rnd.csv, pd_rnd.csv, thresholds_rnd.csv,
gain_budget.csv, known_events_p.csv, known_events_control.csv, two_station_known.csv, injections_rnd.csv,
injections_eq.csv (earthquake-centred background, sensitivity case). Raw records: Pete's Downloads folder,
mh370-inputs/hydroacoustics/ims_eq_records and ims_random_background (open data, re-downloadable).
