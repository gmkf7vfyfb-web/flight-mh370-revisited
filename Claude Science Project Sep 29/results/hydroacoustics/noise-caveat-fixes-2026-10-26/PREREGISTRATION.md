# Noise caveat fixes C1-C3: pre-registration (written 2026-10-26T20:42:32Z, before the final numbers)

Disclosure. Before this file, one exploratory pass was made on the Kadri Fig. 9 vertices (C1): vertex statistics, and a
first 1-s peak-to-peak estimate with a ratio of 5.18 from raw H01W (Dec 2014). It gave about 104 dB re 1 uPa at H01W.
The C2 code reading and the existing module result results-data/digitised/waveform-rasters/cmst_fig1_overlay/cmst_fig1_vs_imos3315.json
(22 Oct 2026) were also read before this file. Nothing below is tuned to those numbers.

## C1. 8 Mar 2014 IMS levels from the digitised Kadri 2024 Fig. 9 pressure traces
- Input: DB tables dg_data_kadri_fig9_digitised_kadri_2024_figure9_panel_{a,b,c}_h01w and _{d,e}_h08s (PDF vector vertices,
  about 14.5 per second; most vertices are local extrema, so the vertex RMS is not the signal RMS).
- Estimator: for each whole UTC second, the peak-to-peak range of the vertices, PP. RMS estimate = PP / k.
  k = median over 1-s windows of PP/RMS, measured on held raw IMS records (EarthScope, response removed), filtered 5-40 Hz
  (4-pole Butterworth, zero phase). H01W: k from QZ8501_H01W.mseed (H01W1-3, 27 Dec 2014). H08S: k from the four held H08S
  records (QZ8501 2014, JT610 2018, SJ182 2021, AB1103 2022), segments outside the impact windows not removed (k is a shape ratio).
- Statistic: median over quiet seconds of 20 log10(PP/k / 1 uPa). Quiet = at least 8 vertices in the second; not within
  3 s of a Kadri Table 1 transient (H01W); not within -1.5 s to +3.5 s of an H08S airgun shot (pick kind 'airgun shot', H08S).
- Rows: one per panel and one pooled per station (H01W a-c; H08S panel d only; panel e is computed but not pooled, because
  of the recorded +8.8 dB step at the panel join). H08S also gets an 'all seconds, shots included' row for context.
- Uncertainty (1 sigma, dB, in quadrature): (a) sampling: 30-s block bootstrap of the median (2,000 draws, seed 20261026);
  (b) ratio k: half the range of k over the filter variants (zero-phase 4-pole 5-40 Hz; causal 4-pole 5-40 Hz; causal
  2-pole high-pass 5 Hz then 4-pole 2-40 Hz, Kadri Methods) and records; (c) vertex reduction: half the difference
  between PP from the raw signal and PP from a min/max decimation of the raw signal at the observed vertex rate.
- Second estimator (cross-check, not used for the row): vertex RMS divided by the vertex-RMS/true-RMS ratio of a min/max
  decimation of the raw record with 0.138 s bins.
- Second source: Royer 2016 H01W2 spectrogram band tables (psd_db_5_40, mean of dB over 5-40 Hz), same clock span.
- Expected order (stated by the task): H01W about 102-103 dB. If the result differs by more than 2 dB, report it and the cause.

## C2. IMOS logger gain
- Question: do the IMOS band levels in noise_estimate include the frequency-dependent logger gain? Answer by quoting
  prepare/imos_noise.py and build_noise_coupling.py, and by recomputing one record (3315, 531A728A.DAT) with the module
  reader: with the gain per frequency bin, and with a flat gain equal to the 100 Hz value. Pass: the per-bin recompute
  equals noise_per_recording.csv within 0.05 dB.

## C3. Absolute level checks
- (i) IMOS 3315 against CMST 2014 Fig. 1. Pass criterion: peak |p| and the 99th percentile of the column envelope outside
  205-245 s (measured, module calibration, 1-120 Hz) agree with the digitised CMST figure within 2 dB.
- (ii) One view of H01W and H08S 5-40 Hz levels from every held source: Blackman 2003, open raw March 2015-2019,
  Kadri 2014 trace (C1), Kadri 2014 spectrogram colour, Royer 2014 H01W2 colour. No pass criterion (a comparison table).
- (iii) OHASISBIO transfer. offset = C1 H01W SPL (00:27-00:57) minus [Royer H01W2 median psd_db_5_40 over the same span
  + 10 log10(35 Hz)]. Apply the same offset to SSEIR and SWAMS3 medians over the same span and over 00:00-02:00.
  Hypothesis A: Royer's colour scale is calibrated (dB re 1 uPa^2/Hz) at every station. Then |offset| <= 6 dB.
  Hypothesis B: the scale is uncalibrated counts. Then the offset is near +52.6 dB (H01, Table 3: 0.848 uV/count,
  -174 dB re 1 V/uPa) and an OHASISBIO station needs a further -19.1 dB (0.298 uV/count, -164 dB).
  Decision rule: |offset| <= 6 dB -> A, and the transferred rows use the same offset; otherwise B, and the
  rows use the Table 3 difference. Uncertainty: C1 sigma, colour digitisation +/-1.5 dB, and the half-hour spread of
  the H01W2 offset, in quadrature. Caveat on every row: Royer reports that seismic-survey shots obscured much of the data that day.

## Amendment 1 (2026-10-26T20:46:28Z, before any C1 row is computed)
- Reason: the Kadri vertices have excess kurtosis about -1.1. A min/max decimation of the December 2014 H01W record gives
  about -0.2. The signal shape on 8 March may differ (for example whale chorus near 18-25 Hz, which lowers PP/RMS).
  k depends on the signal shape. So the primary k comes from the same season and clock time:
  raw H01W1-3 on 8 March 2015-2019, 00:27-00:57 UTC, and raw H08S1-3 on 8 March 2015-2019, 01:00-01:20 UTC,
  downloaded now from EarthScope FDSN (open, no credentials). Years with no data are skipped and listed.
- The held records of the first version (December 2014 and later H08S cases) stay as variants in the k spread (b).
- Term (c) as first written is zero by construction (a min/max decimation keeps the 1-s extremes). It is replaced by:
  the difference between k from the March records and k after decimating the March records to 80 samples/s
  (a plausible plotting rate), half of it as the 1-sigma term.
- New diagnostic (no decision depends on it): excess kurtosis of min/max-decimated March vertices against the Kadri value.
