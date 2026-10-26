# Noise caveat fixes C1-C3 (26 October 2026)

Status: UNCHECKED. No independent verifier has checked these numbers yet (RULE 4). Do not quote them as CURRENT.
Instruction: Pete, 26 Oct 2026, "(3) please check on and fix the items noted in caveats" (relayed by the coordinating session 8b907e71).
Pre-registration: [PREREGISTRATION.md](PREREGISTRATION.md) (written before the final numbers; amendment 1 before any C1 row).
Database: hydro_data.sqlite stage 4 (`build_noise_fixes.py`) on `hypothesis/hydroacoustics`. Rows are added. No row is deleted.
Code and ratio tables: module `results-data/noise-caveat-fixes-2026-10-26/` and `prepare/noise_caveat_*.py`.
Tables here are exports of the database tables of the same name.

## Check table (each input, its registry id, its definition as quoted from its source, and a second source)

| input | registry id | definition (quoted) | second source |
|---|---|---|---|
| Kadri 2024 Fig. 9 vertex tables (`dg_data_kadri_fig9_digitised_*`) | hydro.in.hydro_data_db (dataset kadri2024_fig9_h01w / _h08s) | dataset caveat: "Envelope resolution only: PDF vector vertices of the plotted trace, about 14.5 vertices/s; not CTBTO samples. Element not stated." | Royer 2016 H01W2 spectrogram band table (same hours); open raw H01W/H08S March 2015-2019 |
| Kadri processing | (attribute author_processing) | "Butterworth IIR high-pass below 5 Hz (in addition to the CTBTO high-pass) and a 2-40 Hz band-pass 'applied in general'. The Fig. 9 caption does not name the filter." | filter variants in the ratio k (spread 0.03 dB H01W, 0.07 dB H08S) |
| H08S airgun shots (`pick` kind 'airgun shot') | hydro.in.hydro_data_db (dataset h08s_airgun_shots) | 110 shots 01:00:03-01:19:09 UTC (check C16: all inside the Fig. 9 panels) | Kadri Fig. 9 panel d/e trace (shots visible every ~10 s) |
| Ratio k = 1-s peak-to-peak / 1-s RMS | hydro.res.noise_caveat_fixes_2026_10_26 | "k = median over 1-s windows of PP/RMS on raw IMS records, 5-40 Hz" (noise_caveat_calibration.py) | k on held Dec 2014 H01W and 2014-2022 H08S records: 5.17-5.23 (March: 5.18 H01W, 5.14 H08S) |
| IMOS band levels (`noise_estimate`, note.imos_noise) | hydro.note.imos_noise | prepare/imos_noise.py line 117: `cal = 10 ** ((Gi(f) + L["sens_db"]) / 10)`; line 118: `pu = p / cal`; line 127 (1-s): `p1u = p1 / (10 ** ((Gi(f1) + L["sens_db"]) / 10))` | own recompute of 6 records with the module reader: max difference 0.005 dB |
| CMST 2014 Fig. 1 (digitised) and IMOS 3315 531A728A envelopes | hydro.in.hydro_data_db (cmst2014_fig1_imos3315) | dataset caveat: "Raster envelope (561x420 px): 0.69 s per pixel column." | module overlay result of 22 Oct 2026 (cmst_fig1_vs_imos3315.json: -0.69 / -0.42 dB), reproduced from the tables |
| Royer 2016 spectrogram band tables (`psd_db_5_40`) | hydro.in.hydro_data_db (royer2016_spectrograms_*) | digitise_royer_2016.py: "Mean dB over 5-40 Hz and 10-15 Hz against time"; "Colour -> dB uses ... 'jet' over 70-100 dB (the printed colour bar)" (+/-1.5 dB) | Royer Table 3 station sensitivities (dg_royer_2016_royer_sensitivity) |

## C1. 8 March 2014 IMS levels from the published pressure traces

Method. The vertices are mostly local extrema (78 %). So their RMS is not the signal RMS. The 1-s peak-to-peak range PP is kept. RMS = PP / k.
k is measured on raw IMS records (EarthScope, response removed, 5-40 Hz zero-phase 4-pole) of 8 March 2015, 2017, 2019 (H01W, 00:27-00:57 UTC) and 8 March 2015-2019 (H08S, 01:00-01:20 UTC).
H01W k = 5.176. H08S k = 5.145. Statistic: median over quiet seconds of the 1-s RMS level.

| station, span | seconds | median 5-40 Hz level (dB re 1 uPa) | 1 sigma (dB) | second estimator (dB) |
|---|---|---|---|---|
| H01W panels a-c, 00:27-00:57 (preferred) | 1692 | 104.28 | 0.34 | 103.49 |
| H01W panel a / b / c | | 104.55 / 104.38 / 103.85 | 0.36 / 0.34 / 0.34 | |
| H08S panel d, 01:00-01:10, between shots (preferred) | | 100.43 | 0.40 | 99.27 |
| H08S panel d, all seconds (shots included) | | 102.33 | 0.37 | |
| H08S panel e (not pooled: +8.8 dB step at the panel join) | | 103.54 | 0.39 | |

- The 1-sigma value has three parts: sampling (30-s block bootstrap, 0.06 dB at H01W), the spread of k (0.03 dB) and the plotting rate (0.33 dB; k after decimation to 80 samples/s is 4.79).
- The second estimator (vertex RMS divided by the vertex-RMS/RMS ratio of a min/max decimation) is 0.8 dB lower at H01W and 1.2 dB lower at H08S. The 1-sigma value does not include this difference. Treat about 1 dB as the method uncertainty.
- The axis scale of the published panels is not re-checked. The three H01W panels agree within 0.7 dB.
- The expected order was 102-103 dB (earlier readings 103.1 and 102.4). The result is 1.2-1.9 dB higher. The earlier 102.4 came from column extremes divided by about 3.5. The measured k (5.18) shows that ratio was too small.
- Second sources (see C3 ii): open raw H01W March 2015-2019 103.63 dB; Blackman 2003 101.64 dB.
- Preference. v_noise_8mar2014 and v_noise_summary now carry `preferred_8mar2014` and `preference_reason`. At H01W and H08S the trace rows are preferred. The spectrogram-colour rows are kept with their own caveat (biased low).

## C2. IMOS logger gain

The IMOS band levels already include the frequency-dependent logger gain. imos_noise.py divides every Welch and 1-s periodogram bin by the gain of that bin (lines 117, 118, 127; quoted above) before the band average. build_noise_coupling.py copies the values unchanged (lines 180, 197-198).
Recompute (pre-registered pass: within 0.05 dB): 6 records, 7 bands, maximum difference 0.005 dB. PASS. No correction is made.
If a flat 100 Hz gain had been used, the 10-20 Hz levels would be lower by 5.32 (3250), 2.63 (3274), 4.40 (3275), 4.42 (3315) and 3.23 dB (3376). All bands are in `noise_fix_result.csv`.

## C3. Absolute level checks

(i) IMOS 3315 against CMST 2014 Fig. 1. Pass criterion (pre-registered): within 2 dB.

| quantity (1-120 Hz) | measured (Pa) | CMST figure (Pa) | difference (dB) | result |
|---|---|---|---|---|
| peak abs(p) | 1.310 | 1.418 | -0.69 | PASS |
| 99th percentile of abs(envelope) outside 205-245 s | 0.628 | 0.660 | -0.42 | PASS |

In 5-40 Hz the measured values are 2.0 and 6.0 dB lower. CMST does not state the band of the figure. That comparison is for information only.

(ii) H01W and H08S 5-40 Hz levels from every held source (view `v_ims_noise_5_40_compare`, file `noise_compare_5_40.csv`).

| station | source | period | level (dB re 1 uPa) |
|---|---|---|---|
| H01W | Kadri 2024 Fig. 9 trace (C1) | 8 Mar 2014, 00:27-00:57 | 104.28 +/- 0.34 |
| H01W | open raw IMS (EarthScope) | March 2015-2019, arrival-window hours | 103.63 |
| H01W | Blackman et al. 2004 (traced) | May-June 2003 | 101.64 |
| H01W | Royer 2016 H01W2 colour (raw reading) | 8 Mar 2014, 00:27-00:57 | 98.48 |
| H01W | Kadri 2024 Fig. 9 colour (1/3 octaves, 4.45-44.9 Hz) | 8 Mar 2014, panel b | 86.29 |
| H08S | Kadri 2024 Fig. 9 trace (C1), between shots | 8 Mar 2014, 01:00-01:10 | 100.43 +/- 0.40 |
| H08S | open raw IMS (EarthScope) | March 2015-2019, arrival-window hours | 98.04 |
| H08S | Blackman et al. 2004 (traced) | May-June 2003 | 95.49 |
| H08S | Kadri 2024 Fig. 9 colour | 8 Mar 2014, panels d / e | 83.37 / 82.92 |

(iii) OHASISBIO by transfer calibration via H01W2.
Offset = C1 H01W level minus the Royer H01W2 colour level for the same 30 minutes = +5.81 dB (10-min panels: +6.01, +6.12, +5.24).
Pre-registered decision: |offset| <= 6 dB means Royer's colour scale is calibrated at every station (hypothesis A). Under hypothesis B (counts) the offset would be near +52.6 dB. Result: A. The pooled offset is close to the 6 dB line, and two of the three 10-min offsets are above it. The decision between A and B is clear (5.8 against 52.6 dB). The size of the colour-reading bias is not explained here. It includes the mean-of-dB statistic and the 70 dB colour floor.

| station | span | level by transfer (dB re 1 uPa) | 1 sigma (dB) |
|---|---|---|---|
| SSEIR | 00:27-00:57 | 104.45 | 1.61 |
| SSEIR | 00:00-02:00 | 104.79 | 1.61 |
| SWAMS3 | 00:27-00:57 | 103.96 | 1.61 |
| SWAMS3 | 00:00-02:00 | 104.22 | 1.61 |

1 sigma = C1 0.34, colour digitisation 1.50 and the spread of the three offsets 0.48 dB, in quadrature. It assumes the same colour bias at the three stations.
Caveat on every row: Royer 2016 reports that powerful seismic-survey shots obscured much of the OHASISBIO data that day.
Royer Table 3 (sensitivity) gives 52.6 dB re 1 uPa per count for H01 and 33.5 dB for OHASISBIO. A counts-based scale would need -19.1 dB more at an OHASISBIO station. The H01W2 offset rules this out.

## Deviations from the pre-registration
1. Amendment 1 (written before any C1 row): k from the same season and clock time (8 March 2015-2019), not only the held December 2014 record; term (c) replaced (as first written it was zero by construction).
2. C3 (iii) spread: the pre-registration says "half-hour spread". Only one 30-min span overlaps the Kadri trace. The spread of the three 10-min offsets is used.
3. The vertex excess kurtosis of Kadri's trace (-1.1) is not reproduced by a min/max decimation of the March records (H01W +0.18, H08S -0.62). The plotting reduction of the published figure is therefore not fully known. This is the main reason to treat about 1 dB as the method uncertainty of C1.

## Files
- [PREREGISTRATION.md](PREREGISTRATION.md), `noise_fix_result.csv`, `noise_compare_5_40.csv`, `absolute_level_check.csv`, `noise_fix_input.csv`, `noise_preference.csv` (exports of the database tables), `manifest.json`.
