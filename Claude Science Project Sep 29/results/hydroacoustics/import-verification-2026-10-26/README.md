# Independent verification: hydroacoustics repository import of 26 Oct 2026 (producer session d8445a3f)
Verifier session 8b907e71. Report only: no commit, no push, no host file changed.
Heads read with git ls-remote: hypothesis/hydroacoustics 4452f265, claude-science-sep29 573a4588.
Pass criteria were written before any computation: verify/preregistered_criteria.md (copy saved with this report).

## V1. C1: ratio k and 5-40 Hz trace levels (Kadri 2024 Fig. 9)
Own code: raw IM H01W1-3 and H08S1-3 EDH (EarthScope FDSN, anonymous), StationXML response removed (obspy, output DEF), 5-40 Hz 4-pole Butterworth zero-phase, 1-s windows.
Data available: H01W 2015, 2017, 2019 (2016 and 2018 return no data); H08S 2015-2019.
| quantity | producer | verifier | difference |
|---|---|---|---|
| k H01W (pooled median PP/RMS, 16,194 s) | 5.176 | 5.179 | +0.06 % (0.005 dB) |
| k H08S (17,865 s) | 5.145 | 5.149 | +0.07 % |
| k after resample to 80 sps, H01W | 4.79 | 4.794 | 0.00 |
| H01W panels a-c, quiet (1,692 s) | 104.28 +/- 0.34 | 104.28 +/- 0.34 | 0.00 |
| H01W panel a / b / c | 104.55 / 104.38 / 103.85 | 104.54 / 104.38 / 103.85 | <= 0.01 |
| H08S panel d between shots (239 s) | 100.43 +/- 0.40 | 100.42 +/- 0.40 | -0.01 |
| H08S panel d all seconds | 102.33 | 102.33 | 0.00 |
| H08S panel e (shots excluded) | 103.54 | 103.54 | 0.00 |
| second estimator H01W / H08S d | 103.49 / 99.27 | 103.47 / 99.24 | -0.02 / -0.03 |
Own min/max decimation ratio (vertex RMS / RMS, 14.5 vertices/s): 1.871 H01W, 1.853 H08S.
Note on the shot guard: my first guard choices (before I read the producer code) gave 101.91 (shot second only), 101.61 (shot second + next), 100.47 (2 s before, 3 s after). The producer uses 1.5 s before to 3.5 s after. Over guards 0.5/1.5 s to 2.5/5 s the result runs from 101.23 to 100.26 dB.
Is the 1-sigma adequate? No, not as a total uncertainty. The stated 0.34 / 0.40 dB has three parts: sampling (0.06 / 0.20), filter spread of k (0.03 / 0.07) and plotting rate (0.34 / 0.33). It leaves out:
- the estimator difference (0.81 dB H01W, 1.18 dB H08S);
- the spread of the panel medians at H01W (range 0.69 dB, SD 0.36 dB). This is six times the bootstrap sampling term;
- the shot-guard choice at H08S (about +/-0.5 dB);
- the spread of k between records at H08S (5.04-5.29, 0.43 dB).
My combined estimate is about 0.6 dB (H01W) and 0.9 dB (H08S). This agrees with the producer's own statement "treat about 1 dB as the method uncertainty". The number to carry forward is that statement, not the 0.34 / 0.40 dB.

## V2. C2: IMOS logger gain
Own reader written from the CMST loader load_loggerdatanew.m: big-endian uint16, 5 header lines, footer at 'Record', 5 V / 65536.
Gain G(f) = Welch PSD of the calibration record 52946955.DAT + 90 dB (CalibrationNotes.txt). Sensitivity -197.8 dB comes from 3315_3250_3376__MetaData.txt; the DAT header carries no sensitivity value. Per-bin division by G(f), Hann Welch with nperseg 24,000 (0.25 Hz), linear band mean.
| record | band | producer | verifier |
|---|---|---|---|
| 3315 531A5D72 | 10-20 Hz | 89.70 | 89.700 |
| 3315 531A5D72 | 20-40 Hz | 90.67 | 90.674 |
| 3315 531A728A | 10-20 Hz | 85.68 | 85.678 |
| 3315 531A728A | 20-40 Hz | 84.04 | 84.038 |
All 14 band values agree within 0.005 dB, except 531A728A 160-240 Hz (0.011 dB).
The gain IS applied. A flat gain at 100 Hz would lower 10-20 Hz by 4.65 dB on 531A5D72. Applying the band-mean gain table instead of the per-bin gain changes 5-240 Hz levels by up to 0.35 dB, and 2-5 Hz by 2.4 dB.
Note: in the gain table, the 3315 160-240 Hz row is 39.85 dB. My linear band mean of the same calibration record is 40.12 dB. The table row does not affect noise_estimate, but it should be checked.
Note: with 1-Hz Welch bins, the 20-40 Hz level differs by up to 0.2 dB. So the 0.005 dB match depends on the 0.25 Hz resolution.

## V3. C3(i): IMOS 3315 531A728A against CMST 2014 Fig. 1
Own chain from the raw record: per-bin gain, 1-120 Hz 4-pole zero-phase, 0.6904-s columns on the overlay-table grid. p99 = 99th percentile of the per-column max |envelope| outside 205-245 s. This definition reproduces the producer's 0.628 / 0.660 exactly from the tables.
| quantity | producer | verifier |
|---|---|---|
| peak | 1.310 vs 1.418 Pa (-0.69 dB) | 1.3245 vs 1.4175 Pa (-0.59 dB) |
| p99 | 0.628 vs 0.660 Pa (-0.42 dB) | 0.6308 vs 0.6596 Pa (-0.39 dB) |
The 5-40 Hz peak is -2.02 dB (producer 2.0 dB lower).
Timing note: in noise_estimate, 531A728A starts at -24.824 s from its header time. All other 25 records of logger 3315 on 8 March start at -25.81 to -25.88 s (linear clock drift). The overlay table follows the -24.8 s value. The effect on these metrics is below 0.01 dB, but the 1-s anomaly should be checked.

## V4. C3(iii): Royer colour-scale offset
Royer level = median over time columns of psd_db_5_40, + 10 log10(35). Rows from both overlapping panels kept.
| quantity | producer | verifier |
|---|---|---|
| H01W2 colour level 00:27-00:57 | 98.48 | 98.476 |
| offset | +5.81 | +5.80 |
| 10-min offsets | 6.01 / 6.12 / 5.24 | 6.00 / 6.11 / 5.24 |
| SSEIR 00:27-00:57 / 00:00-02:00 | 104.45 / 104.79 | 104.45 / 104.79 |
| SWAMS3 00:27-00:57 / 00:00-02:00 | 103.96 / 104.22 | 103.96 / 104.22 |
| 1 sigma | 1.61 | 1.61 |
Royer Table 3 gives 52.57 dB re 1 uPa per count for H01 and 33.48 dB for OHASISBIO (difference 19.08 dB).
Fragility:
- The A-against-B decision is robust. Hypothesis B predicts about +52.6 dB, which is 46.8 dB away from the measured +5.8 dB.
- The pre-registered |offset| <= 6 dB flag is fragile. The margin is 0.20 dB. P(offset > 6) is 0.28 with the C1 sigma alone and 0.45 with the full 1.61 dB sigma. Two of the three 10-min offsets are already above 6 dB.
- With the second C1 estimator the offset is +4.99 dB. With a mean-of-dB Royer statistic it is +5.70 dB.
- The transfer also assumes the same colour bias at OHASISBIO as at H01W2. The H01W2 offset rules out a uniform counts scale, but it does not test a bias specific to one station.

## V5. Ten stage-3 tables (sources on claude-science-sep29 573a4588)
For all ten tables, the source SHA-256 equals imports.yaml, the row counts are exact and the column sums agree exactly:
known_event (298 rows; sum lat -5904.8761), ims_march_noise_percentile (6704; freq_hz 278779.2), ims_false_alarm_rate (900; p_threshold 135.0), array_calibration (12 parameters; sum -477.3142055; array_calibration_event 41 rows, sum res_deg -7.394), coupling_value CV26-CV123 (98; value 8.471193; id set exact), received_observation OB07-OB81 (75; peak_1sRMS_Pa 355.6923; id set exact), source_type (41; source_class text hash equal), source_catalogue (45; name text hash equal), royer_event_labelled (840; royer_event 8820), explosion_radiated_fraction (23; W_kg 218781).

## V6. Data store
- The committed hydro_data.sqlite SHA-256 is e0442ace...caf91, as expected.
- Clean rebuild: rebuild_all.sh with the module clone at 4452f265 and the claude-science-sep29 Sep 29 folder. Build inputs (IMOS, GEBCO) were read only. Run time 58 s.
- The rebuild gives 182 checks: 179 PASS and 3 REVIEW (K11, K09, I08c_coupling_wave3).
- Both files have 208 tables. All tables have identical content, except for build timestamps in attribute, import_block, meta and package_row_history.
- meta.module_git_head differs: 53db6372 in the committed file, 4452f265 in the rebuild. The committed file was built before its own commit.
- The rebuilt file SHA-256 is 00e32771... The file is reproducible in content, but not byte for byte, because of the timestamps.
