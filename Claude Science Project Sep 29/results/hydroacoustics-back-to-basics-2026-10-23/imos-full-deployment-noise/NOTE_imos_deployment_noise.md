# IMOS full-deployment noise statistics and the place of 8 March 2014 in them

Date: 23 Oct 2026. Track: IMOS full deployments, noise statistics (stream-processed on deskstar).

## Deviations and scope (read first)
- **Data processed: all records of the three deployments that are in the IMOS bucket** (948 logger-days, 90,577 records, 334 GB raw). Nothing was subsampled. Loggers 3315 and 3275 are not in the bucket and were not processed.
- Missing from the archive: 3274 day 2014-07-23 (one day). 3250 days 2014-06-03 to 2014-07-09 are absent except 06-24 (1 record) and 07-10 (7 records); these fall after the metadata 'last sample in water' (2014-06-02 04:15) anyway.
- QC exclusions: Scott Reef 44, Portland 2808, Perth Canyon 49 records (out-of-water records, plus DC faults/all-zero records; table below). Clipped and 'overwritten' records were kept and flagged.
- Pooled 1 s histograms: the 213 excluded records in partly valid days were re-fetched, reprocessed with the same code and subtracted exactly; 30 days with every record excluded were dropped. Pooled 1 s percentiles have 0.5 dB resolution.
- The 'night of 8 March' is not one defined interval, so three windows are reported: W1 08 Mar 00:00-08:00 UTC (primary; the span of the module's signal and background sets), W2 07 Mar 16:00 - 08 Mar 02:00 UTC (flight night), W3 the UTC day of 8 March. The window choice is mine.
- The 2-1000 Hz chain at 6 kHz uses 1 s Hann periodograms without overlap; the gain is a 1 s Welch of the same calibration file. Over 20-240 Hz it agrees with the module's 500 Hz chain to about 0.15 dB.
- The spectrogram cube holds every record that processed (faulty records included). Use the per-record QC flags.
- Levels below the 8 Hz analogue high-pass corner (the 2-5 Hz band and the lower part of 5-10 and 5-40 Hz) depend on the gain correction there and are provisional.
- Source-type remarks below (whale chorus, tidal flow) are interpretations, not tested here.

## Data and processing
- Source: `https://imos-data.s3-ap-southeast-2.amazonaws.com/IMOS/ANMN/Acoustic/<site>/<logger>/<yyyymmdd>/raw/*.DAT`; calibration files `extras/calibration_raw/` (529482AC, 54E49F6D, 5236BCF7, the same names as the MH370 package). Sensitivities: -196.0 (3376), -196.0 (3274), -197.7 (3250) dB, read as re 1 V/µPa, which is the module's disclosed units deviation.
- Every logger-day was downloaded on deskstar (128 streams, about 65 MB/s mean), processed and deleted. Raw data in flight stayed under 3 GB. 0 download or processing errors. Wall time 1 h 24 min.
- Calibration is the module chain (`imos_noise.py`): volts = counts·5/65536 with the mean removed; decimate to 500 Hz; Welch 4 s Hann 50 %; system gain from the white-noise file + 90 dB; µPa²/Hz = V²/Hz / 10^((G+S)/10).
- Per record: Welch band levels (mean PSD in band) for 2-5 ... 160-240 Hz and 5-40 Hz; 5-40 Hz band SPL (mean PSD × 35 Hz, dB re 1 µPa); base-10 third-octave SPLs 5-40 Hz; 1 s band-level p5/p50/p95 and the excess kurtosis of 1 s band energy (module definition); the excess kurtosis of the 5-40 Hz band-passed waveform; a 2-1000 Hz, 1 Hz-bin PSD (mean and p1-p99 over 1 s segments); time fields; QC fields; sha256.
- Time: footer 'First Data' (with its n/65536 s field), minus the clock error interpolated linearly between the metadata clock sets (convention A).

## Validation gate (passed)
The module's 8 March background (B) sets (25 / 47 / 27 records for 3376 / 3274 / 3250) were taken from this run's outputs. All 99 files are **byte-identical** (sha256) to the package files. Maximum absolute differences against `noise_bands.csv` and `noise_per_recording.csv`, over all 7 bands (tolerance 0.5 dB):

| logger | max_abs_d_p50_1s | max_abs_d_p50_welch | n_rec | max_abs_per_record_diff |
|---|---|---|---|---|
| 3250 | 0.035 | 0.005 | 27 | 0.005 |
| 3274 | 0.03 | 0.005 | 47 | 0.005 |
| 3376 | 0.035 | 0.004 | 25 | 0.005 |

The 1 s differences come from float16 storage of the 1 s levels; the Welch levels reproduce to rounding. Full table: validation_gate_8march.csv.

## QC

| logger | site | records | days | qc_pass | out_of_water | dc_fault | nonfinite | clipped_kept | overwritten_kept |
|---|---|---|---|---|---|---|---|---|---|
| 3250 | Scott Reef | 23418 | 247 | 23374 | 8 | 36 | 10 | 20 | 12 |
| 3274 | Portland | 34522 | 360 | 31714 | 2774 | 34 | 0 | 28 | 55 |
| 3376 | Perth Canyon | 32637 | 341 | 32588 | 0 | 49 | 11 | 14 | 0 |

DC fault = |mean counts − logger median| > 200 counts. In normal records the DC drifts by tens of counts over a year; every faulty record departs by more than 1,000 counts (jumps of ~29-32 k counts, or all-zero records).

## Results
### Where 8 March 2014 sits: 5-40 Hz band SPL (dB re 1 µPa)
Day-window rank = percentile rank of the window median among the medians of the same clock window on every other day with ≥ 80 % record coverage. This controls for the diel cycle. Record rank = rank of the window median in the pooled per-record distribution.

| Site | Window | n records | Window median (dB re 1 µPa) | Day-window rank, deployment (%) | n days | Day-window rank, March (%) | n March days | Record rank, deployment (%) | Record rank, March (%) | Deployment median | March median |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Scott Reef | W1 | 32 | 108.63 | 63.9 | 241 | 33.3 | 30 | 66.8 | 41.4 | 103.54 | 110.76 |
| Scott Reef | W2 | 39 | 112.84 | 84.0 | 243 | 66.7 | 30 | 77.2 | 58.1 | 103.54 | 110.76 |
| Scott Reef | W3 | 96 | 113.2 | 86.0 | 242 | 63.3 | 30 | 78.0 | 59.5 | 103.54 | 110.76 |
| Portland | W1 | 33 | 102.97 | 63.0 | 330 | 10.0 | 30 | 54.1 | 13.8 | 102.62 | 105.47 |
| Portland | W2 | 41 | 103.38 | 68.6 | 328 | 16.7 | 30 | 58.3 | 19.5 | 102.62 | 105.47 |
| Portland | W3 | 96 | 103.54 | 68.4 | 329 | 13.3 | 30 | 60.0 | 21.7 | 102.62 | 105.47 |
| Perth Canyon | W1 | 32 | 96.38 | 28.5 | 337 | 0.0 | 30 | 25.3 | 5.2 | 99.54 | 102.99 |
| Perth Canyon | W2 | 40 | 99.02 | 44.4 | 338 | 0.0 | 30 | 46.1 | 19.5 | 99.54 | 102.99 |
| Perth Canyon | W3 | 96 | 100.08 | 58.3 | 338 | 13.3 | 30 | 53.8 | 26.8 | 99.54 | 102.99 |

Readings:
- **Perth Canyon**: W1 is the quietest 00:00-08:00 UTC window of all 31 March days (rank 0 of 30 others) and sits at the 28th percentile of the deployment. March to May is the loud season here: monthly medians are 103.0-104.7 dB against 94.5-97.7 dB from Nov to Feb. The narrow 18-70 Hz peaks in the March-May spectra are consistent with the known seasonal whale chorus at this site (interpretation). W1 also falls in the local-day diel trough (07:40-15:40 local solar time).
- **Portland**: W1 is low for March (rank 10 %) and above the middle of the deployment (63 %). Diel modulation is weak (March hourly-median range 1.3 dB, Kruskal-Wallis p = 0.2).
- **Scott Reef**: W1 is mid-March (33 %) and upper-middle of the deployment (64 %). The site is highly variable and impulsive. Median 2-5 Hz levels rise from 88-98 dB re 1 µPa²/Hz (Oct-Feb) to 104-113 dB (Mar-Jun), which is likely flow or tidal pseudo-noise at 216 m (interpretation; below the 8 Hz corner).

### W1 rank among March day-windows, by band (mean PSD levels)
| band (mean PSD) | Perth Canyon | Portland | Scott Reef |
|---|---|---|---|
| 2-5 Hz | 93.3 | 46.7 | 66.7 |
| 5-10 Hz | 26.7 | 20.0 | 40.0 |
| 10-20 Hz | 3.3 | 6.7 | 43.3 |
| 20-40 Hz | 3.3 | 3.3 | 66.7 |
| 40-80 Hz | 0.0 | 36.7 | 60.0 |
| 80-160 Hz | 6.7 | 93.3 | 66.7 |
| 160-240 Hz | 16.7 | 90.0 | 46.7 |
| 5-40 Hz | 0.0 | 10.0 | 33.3 |

Perth Canyon W1 is low in every band from 10 to 160 Hz (ranks 0-7 %), and Portland W1 is low from 10 to 40 Hz but high from 80 to 240 Hz (90-93 %).

### Diel cycle, March 2014 (5-40 Hz SPL, local mean solar time)
| logger | site | hourly_median_range_db | peak_hour | trough_hour | kruskal_H | p_value |
|---|---|---|---|---|---|---|
| 3250 | Scott Reef | 7.88 | 20 | 15 | 55.3 | 0.0002 |
| 3274 | Portland | 1.32 | 13 | 16 | 28.4 | 0.2 |
| 3376 | Perth Canyon | 5.28 | 5 | 13 | 328.4 | 8e-56 |

Deployment-wide monthly hourly-median ranges: Perth Canyon 1.0-5.9 dB, Portland 0.9-6.3 dB, Scott Reef 3.7-29.2 dB (diel_amplitude_by_month.csv).

### Impulsiveness (excess kurtosis of the 5-40 Hz waveform)
| site | window_median | deployment_median | record_rank_deployment |
|---|---|---|---|
| Perth Canyon | 0.14 | 0.92 | 20.1 |
| Portland | 0.21 | 0.16 | 55.7 |
| Scott Reef | 25.4 | 25.3 | 50.1 |

### Monthly median 5-40 Hz SPL (dB re 1 µPa)
| month | Perth Canyon | Portland | Scott Reef |
|---|---|---|---|
| 2013-10 |  |  | 98.74 |
| 2013-11 | 96.54 |  | 98.2 |
| 2013-12 | 95.41 | 103.1 | 99.95 |
| 2014-01 | 95.51 | 104.08 | 104.82 |
| 2014-02 | 97.66 | 106.61 | 103.71 |
| 2014-03 | 102.99 | 105.47 | 110.76 |
| 2014-04 | 103.79 | 103.77 | 110.91 |
| 2014-05 | 104.71 | 103.18 | 111.33 |
| 2014-06 | 101.12 | 101.86 | 107.68 |
| 2014-07 | 101.34 | 101.19 |  |
| 2014-08 | 99.19 | 99.72 |  |
| 2014-09 | 98.09 | 99.13 |  |
| 2014-10 | 94.93 | 99.38 |  |
| 2014-11 | 94.51 | 100.06 |  |

## Implications for detection work
- The module's 8 March background sets come from a window that is quiet for March at Perth Canyon and Portland. Detection thresholds derived from them are therefore not conservative relative to typical March noise; for 8 March itself they are representative.
- For any detector that calibrates against the deployment, use the same-clock-window distribution (diel-controlled), not the pooled distribution.

## Spectrogram cube (deskstar only)
`/home/pete/imos-noise/cube/<logger>/<yyyymmdd>.npz` on ssh:deskstar: 948 files, **13.78 GB** (3376 4.97 GB / 341 files; 3274 5.25 GB / 360; 3250 3.56 GB / 247). Each file holds `psd_db` (n_rec × 613 × 124, float16, dB re 1 µPa²/Hz, 2-125 Hz at 1 Hz, 0.5 s step, 1 s Hann on the 500 Hz series), `files`, `start_utc_unix` (corrected), `f_hz`, `t_offset_s` (frame centres from record start). Also on deskstar: `/home/pete/imos-noise/out/<logger>/{rows,psd,hist,lev1s}` (2.99 GB): per-record 2-1000 Hz PSD statistics, daily 1 s histograms and 1 s band-level series. Code: `/home/pete/imos-noise/imos_deploy_noise.py`, `agg.py`.

## Files
- imos_deployment_noise_per_record.parquet / .csv.gz: per-record table, 90,577 × 80, with QC flags.
- spectra_<logger>.npz: monthly, deployment and W1 percentile spectra; across-record (`rec_pct`) and pooled 1 s (`s1_pct`); per-frequency W1 ranks.
- march8_window_ranks.csv, monthly_band_level_percentiles.csv, diel_5_40Hz_by_local_hour.csv, diel_amplitude_by_month.csv, validation_gate_8march.csv, hist_exclusion_log.csv.
- Figures: noise_spectra_by_month_<logger>.png, noise_5_40Hz_deployment_timeseries.png, noise_5_40Hz_diel_cycle.png.
