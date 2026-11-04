# Reverse-sensing spectral search (S10) and source classifier, 4 Nov 2026

Folder: `Claude Science Project Sep 29/results/hydroacoustics/reverse-spectral-2026-11-04/`. Commit 1 (709b2da1) holds Amendment 2, fixed BEFORE the search ran. Commit 2 (this commit) holds the results, the module, the tests and the methods note.

S10 is post hoc in origin (it was added after the screening began), but its parameters were fixed before it ran. Propagation is used for travel time only. No result in this folder is a detection.

## 1. Summary (ASD-STE100)

1. S10 searched all raw IMOS logger records that overlap the arrival windows: 13 records at five loggers. The recording covers 28-40 % of each window.
2. S10 found 7 candidates at local p of 0.05 or less. There were none at Perth Canyon. All 7 are single-station candidates.
3. The best candidate is Portland 3275 at 01:07:45.4 UTC: R 327, local p 0.0043, station-global p 0.19, method-global p 0.65. It is the same burst that the screening track called "the one spectrally impact-like item".
4. No candidate reaches station-global p of 0.05. No candidate is significant after the look-elsewhere correction.
5. The classifier labels that burst "impact-like" (probability 0.86-0.94). Its time also matches the predicted arrival of Royer event 6 (class uncertain; association probability 0.75), which is a strong natural explanation. The burst is kept and the conflict is flagged.
6. No candidate was removed. Removal needs a known class with positive evidence and a combined probability of 0.95 or more.
7. Sensitivity (injections into null records only). At local p of 0.05, 50 % of impact-like signals are found at a 10 s SNR of about -3 to 0 dB at Perth Canyon and Portland. At station-global p of 0.05, only Portland 3275 reaches 50 % (at about +8 dB). Scott Reef is effectively blind, because local sounds set its threshold.
8. Classifier, cross-validated by leave-one-group-out: 87 % correct on full spectra (Brier 0.214, calibration error 0.048), 57 % on time shape only (Brier 0.534). The whale, ship and airgun scores are optimistic. About half of the earthquake labels may be chance matches. No ice event could be labelled.
9. Natural long-range arrivals (Royer events) also score as impact-like (up to 0.75). Spectrum and time shape do not separate an impact from such an arrival. Catalogue timing must do it.

## 2. Files

| File | What |
|---|---|
| `reverse-methods-amendment-2-spectral-search-2026-11-04.md` | Amendment 2 (commit 1, unchanged) |
| `amendment-2-deviations-log-2026-11-04.md` | Deviations 1-12 with dates, reasons and effects |
| `methods-note-spectral-search-classifier-2026-11-04.md` | Methods note with verified references |
| `reverse_spectral.py` | Module: S10 (fixed part, sha256 in `amendment-2-fixed-code.json`), features, classifier, `classify(candidate_window)` |
| `classifier_models.pkl` | Trained models (full-spectrum and time-shape) and station level references, used by `classify()` |
| `tests/test_reverse_spectral.py` | 8 tests, all pass |
| `pipeline_records.py`, `pipeline_injections.py` | Null-record and injection pipelines (multiprocessing) |
| `s10_candidates.csv` | S10 candidate table (spec section 12 schema, plus impact time, predicted arrival window, template parameters and class probabilities) |
| `s10_null_summary.csv` | Per logger: run window, coverage, null pools, thresholds, null candidate rate |
| `s10_injections.csv`, `s10_injection_detection_vs_snr.csv`, `s10_injection_summary.csv` | 14,850 injections (inside family, Metz et al. member, outside family) |
| `classifier_validation.csv`, `confusion_matrix_raw.csv`, `confusion_matrix_envelope.csv`, `classifier_training_set.csv` | Classifier validation and training data |
| `catalogued_event_windows_classified.csv` | Every catalogued-event window at the IMOS loggers on non-blocked paths (59 windows) |
| `royer_timing_labels.csv` | Royer spectrogram timing labels (Cape Leeuwin, SWAMS3, SSEIR); no p-values |
| `crosscheck_back_to_basics_cases.csv` | The 28 back-to-basics case windows classified by this track |
| `classifier-confusion-and-calibration.png/.pdf`, `spectrogram-gallery-candidates-and-classes.png/.pdf` | Footnoted charts |

## 3. Cross-check against the back-to-basics thread

| Back-to-basics conclusion | This track | Agrees? | Why |
|---|---|---|---|
| Cape Leeuwin 00:54:30 = Royer event 5 | Royer timing label at 00:54:29.5 (rise 6.6 dB), association with Royer event 5 P = 0.93; Kadri envelope window association P = 0.68; label "unclassified" | Yes | Timing matches; the envelope cannot show a spectrum, so no class is assigned (deviation 2) |
| Cape Leeuwin 01:13:29 = Royer event 6 (uncertain) | Not tested at Cape Leeuwin: after the Cape Leeuwin run window (ends 01:07:50) and outside the Kadri trace | Not tested | But the same Royer event 6 matches the Portland 3275 burst at 01:07:35-45 (P 0.75), so the two conclusions are consistent |
| Cape Leeuwin 00:51:4x = Royer icequake A / Kadri T1 00:51:50 | Kadri envelope window 00:51:49 associates with Royer icequake A (P = 0.76); label "unclassified"; time-shape impact-like p 0.66 | Yes (timing) | The ice class has no training examples, and the envelope time shape alone does not separate an ice event from an impact |
| Diego Garcia South 01:13-01:16 rise = airgun shots | All 8 windows labelled "airgun shot" (p 0.65-0.88) by the time-shape model with the measured shot train | Yes | Label only; never removed (23 Oct rule) |
| Perth Canyon 3376 windows carry steady tonal lines (positive slopes) | No S10 candidate at Perth Canyon (window max R 23.5 against local threshold 63.1). 00:37:51 "whale call" (tonality 11.6 dB; also Royer 4-B timing P 0.79), 00:39:08 "ship", 00:53:27 "noise only" | Yes | The shape test penalises tonal energy; the classifier finds tonal or noise content, not impact-like content |
| Portland 3275 01:20:35 = call-like tone 25-40 Hz | No S10 candidate (R 55 against threshold 74). Label "unclassified" (whale p 0.28; tonality 7.3 dB, under the 8 dB evidence level). Excess slope -9.1 dB/octave | Partly | Not impact-like by S10. The tone is too weak at 0.25 Hz resolution for a whale label. The slope differs from the +10 dB/octave of the back-to-basics thread, because this track fits the pressure-corrected excess over 8-100 Hz on the half-peak frames, not the 1/3-octave excess over the 30 s window |
| Portland 3275 01:07:40 = the one spectrally impact-like item | The strongest S10 candidate: R 327, local p 0.004, station-global p 0.19, method-global p 0.65; impact-like p 0.86-0.94; excess slope -7.6 dB/octave | Yes (shape) | NEW: its timing matches Royer event 6 (predicted 01:07:38.9 +/- 44 s with the 113 km rock leg; P 0.75). Royer event 6 has class "uncertain", so it is not removed. The path is disputed: the catalogue says "large attenuation", the Royer labelled set says "blocked" |

## 4. Use by the association track

`classify(dict(form='raw', x=<record volts at 250 Hz>, t_on=<s>, t_off=<s>, station='IMOS3275', gain=(gain_f_hz, gain_db), timing_match={'earthquake sound arrival': P}))` returns the label, the class probabilities, the open-set p, the features and the evidence flags. For Kadri traces, use `form='envelope', env=<10 Hz envelope>`; such windows are never labelled impact-like (deviation 2). The class scores feed only the known-event probability and the ranking weight; they never remove a candidate alone.

## 5. Inputs

Station data package (artifact vcb44406a, commit 264a9a4); raw IMOS DAT files of 8 March and 1-15 March 2014 (SHA-256 in hydro_data.sqlite); known-event catalogue and arrivals (commit 264a9a4); Royer labelled set and island checks; Z-call detections (Leroy et al. 2016, SEANOE); back-to-basics case statistics; USGS FDSN catalogue (downloaded 4 Nov 2026).
