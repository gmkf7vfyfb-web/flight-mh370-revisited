# Pre-registration amendment A2 — network detection search (amends ns-prereg-2026-11-03a and A1)

Date: 3 Nov 2026. Written after receipt of level_correction.json v2 (artifact v36a7e196) and pd_curves.json v2 (artifact vde400f7e), and BEFORE the real run. No real-run statistic has been computed.
Sources of the decisions: the lead session (items 1-5, made before any result) and this session's technical choices (items 6-12, each with its reason). Language: ASD-STE100.

## Lead decisions
1. Model-error cases, new order:
   - PRIMARY: alternatives.zero_bias_wide. Bias 0 dB, slope 0, sd 12.58 dB for every path.
   - SENSITIVITY: the top-level classes and global entry. Label: "Indian Ocean post hoc fit". Its spread is inflated x1.98, which gives sd 21.2-22.1 dB. Note: its biases are negative (-14.0 to -1.4 dB at 10 Hz) and slopes positive. They are applied as the file defines them: corrected level = model + bias + slope x log2(f/10).
   - CHECK: alternatives.all_ocean_class_fit. This fit FAILED its own test. Label: "check only". It is not a result.
   - Reason (lead): the Indian Ocean fit rests on one source family for absolute level, its 10 Hz bias is extrapolated, its inflated sd is larger than the zero-bias sd, and it barely beats no correction (CRPS 5.90 vs 6.14 dB).
2. False-alarm rates: 1/day is primary and 1/hour is a sensitivity, both from pd_curves.json. The report must state prominently: (a) the detector track found that a blind 1/day scan MISSES the real F-35A arrival at Wake (T1 4.2-7.3 dB against a threshold of about 27 dB), and the 1/hour scan detects it; (b) known-time single-window 1 % tails are about 6 dB. The graded statistic with the time-shift null stays the network detection test.
3. OHASISBIO (SSEIR, SWAMS1-3, MAD, NCRO, WKER): the picks detection curve is NOT identified. OHASISBIO is excluded from the PRIMARY likelihood, both threshold and graded. A labelled sensitivity uses the post hoc picks curve (50 % at 27.9 dB, sigma 20 dB).
4. IMOS 3275: its proxy threshold (14.2 dB) conflicts with its own lower bound (20.05 dB). We use 20.05 dB, the more cautious value. IMOS 3315 uses the 3376 proxy as given.
5. Diego Garcia South noise: we use the 8 Mar 2014 between-shot level (100.43 dB) as given. Its conversion is not measured; the report flags this.

## Technical choices made here (before the run)
6. Window: window_s = 30 s from pd_curves.json. By the pre-registered split it runs from 10 s before to 20 s after the predicted onset.
7. Statistic: the pd_curves definition replaces the trimmed-mean form. T1 = 10 log10(E_W / median E_W). Here E_W is the band energy in the window and median E_W is the median energy of the reference windows. The threshold applies to T1. The graded statistic uses the same ratio R = E_W / median E_W.
   - Reference windows, IMOS: window starts every 5 s within 1,207 s (the record and its neighbours, 15 min either side, as in the detector basis). Each window must be fully recorded and at least 30 s from the tested window.
   - Reference windows, digitised series: window starts every 5 s within 300 s, in the same panel, at least 30 s from the tested window. A window that crosses a panel join is MISSING, because panels can have different amplitude scales.
8. Detection curves by data form:
   - Cape Leeuwin, Kadri trace part: H01W_envelope.
   - Cape Leeuwin, Royer spectrogram part: H01W (raw single hydrophone). Assumption: no curve exists for the spectrogram form. The raw curve is the nearest form.
   - Diego Garcia South: H08S_envelope.
   - IMOS loggers: their own entries.
   - A sensitivity run removes the Royer spectrogram part at Cape Leeuwin. It shows the effect of the assumed raw curve.
9. P_D = pd_floor + (1 - pd_floor) Phi((SNR - snr50) / sqrt(sigma^2 + noise_sd^2 + sd_model^2)), as the pd_curves notes say.
   - The no-signal detection probability is p0 = max(pd_floor, p_fa). Here p_fa = W / 86,400 s for 1/day and W / 3,600 s for 1/hour; for IMOS it is per clock day, divided by the recorded fraction 0.339.
   - The likelihood ratio is relative to p0.
   - For IMOS 3275 at 1/day we move snr50 with the threshold: snr50 = 20.05 - (14.2 - 13.915) = 19.77 dB, sigma 0.105 dB. At 1/hour we keep the proxy values.
10. Noise level for the predicted SNR: noise_level_db from pd_curves.json. These are median window energy levels; they replace the data-store values of the dry run.
11. OHASISBIO picks sensitivity:
   - Observation: a Royer 2016 Table 5 pick at that station inside the predicted window (detection), or no pick (non-detection). The coverage is Royer's analysed span, taken as 00:00-03:10 UTC.
   - p0 = (number of picks at the station) x W / span.
   - Noise levels: the OHASISBIO_* entries.
   - Picks give only the threshold statistic, not the graded one.
   - Time slides shift the picks cyclically in the span: SWAMS1-3 together, and SSEIR, MAD, NCRO and WKER each alone.
12. Exclusion limit: the smallest energy at which the product over non-detecting observed stations of (1 - P_detect(E)) / (1 - p0) is 0.10 or less.

## Runs
- R1 primary. R2 Indian Ocean post hoc fit. R3 failed all-ocean fit (check only). Each run includes the 1/hour threshold sensitivity, null A (500 time slides, seed 20261103) and null B (IMOS common shifts).
- R4: the OHASISBIO picks sensitivity, with the primary model error.
- R5: primary without the Royer spectrogram part at Cape Leeuwin.
- Everything not listed here stays as in ns-prereg-2026-11-03a and A1.
