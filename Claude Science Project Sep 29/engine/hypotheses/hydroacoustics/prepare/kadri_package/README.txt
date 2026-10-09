DRAFT Kadri package pieces (brief section 9). For Pete's review; NOTHING is sent.
- reference_measure.py (80 lines): Butterworth bands; peak, RMS, exposure; pre-event noise; SNR; plane-wave
  bearing fit from cross-correlation delays across a triad. numpy + scipy only.
- synth_triad.py: synthetic H01W triad waveforms (plane wave, 5-40 Hz chirp, white noise) for the self-test.
  Self-test result: back-azimuth recovered within 0.05 deg (p90) down to -6 dB in-pulse SNR. That is a
  property of the CODE on ideal data (perfect coherence, no multipath, exact element positions) and says
  nothing about field accuracy; the demonstrated field figure is 3.3 deg (Kadri 2024 p. 15).
- data/kadri_package/windows.csv (build_windows.py): stand-in arrival windows, back-azimuths, ranges and a
  declared blockage flag from the shared ocean transport. H08N and Scott Reef (3250) are BLOCKED (Great
  Chagos Bank; North West Shelf). Rerun on end of flight's impacts when they exist.
Still to come before the package is complete: predictions.csv (needs item 3 stage B TL and P_D), the
requests list, and Pete's review.
