# Unused Kadri data for 8 March 2014: extraction and tests

Date: 7 November 2026. Scope: the four items left open by the 7 November source audit (kadri-source-data-audit-2026-11-07). Folder: `Claude Science Project Sep 29/results/hydroacoustics/kadri-unused-data-2026-11-07/` on branch `claude-science-sep29`.

## Summary (ASD-STE100)

- We read Kadri (2019) Fig. 4 for Diego Garcia South (IMS station H08S), 00:00 to 02:00 UTC. We read the pressure trace, the cross-correlation level and the bearing-time image.
- No transient points towards the 7th arc (20-41 S) between 00:56:34 and 01:42:18, when an arc impact can arrive. This is true with a 6 degree margin.
- At 01:09:55-01:11:30 no event is visible. The 309 degree airgun shot train is the strongest direction for all of that time.
- We found an error in the project database. The pressure scale of Kadri (2024) Fig. 9 panels d and e (Diego Garcia South) was digitised wrongly. Panel c (Cape Leeuwin) also has a smaller error.
- Because of this error, the background level stepped up by 8 dB at 01:10:00, where two figure panels join. This step made the 6 November peak at 01:10:15.
- With the scale read again from the tick labels, 01:10:15 is an ordinary look. Its in-sample p is 0.59 (rank 138 of 234). Against the 7 March background its p is 0.02-0.43.
- Thus the Diego Garcia South member of the 6 November candidates at 01:10:15 is withdrawn. This is our error, not an error in Kadri's paper.
- The third Scott Reef pick (01:32:51 UTC) is a real, strong, short broadband pulse. Its energy is highest at 50-63 Hz. It does not have the impact shape.
- Inside the project grid, only impacts at 32-34 S between 00:51:30 and 00:55:00 fit its time. Those paths have large attenuation. No other site shows a matching event in the predicted spans.
- The relative spectra from the Fig. 9 spectrograms show no clear impact-shaped excess at the seven candidate times. 00:51:50 comes nearest, but its slope (-4.0 +- 1.1 dB per octave) is shallower than the -7 dB per octave expected.
- All values come from published figures, except the Scott Reef record, which is raw. Weak features are listed, not discarded.

## 1. Sources and reuse

- Reused from the audit folder: `kadri-source-data-inventory.csv` and `kadri2017_atsb_fig3_h01w_detections.csv` (27 Cape Leeuwin detections from the report to the ATSB, Fig. 3).
- Kadri (2019) Sci. Rep. 9:912, open-access PDF, page 5 image (1650 x 1613 px, lossless FlateDecode). Panels used: 7 March 23:00-24:00 (label "11.00 UTC"), 8 March 00:00-01:00 ("12.00 UTC") and 01:00-02:00 ("1.00 UTC"). The paper uses 12-hour labels; the times of the signals in its Table 3 confirm this (Section 2.1).
- Kadri (2024) Sci. Rep. 14:10102, page 9 (Fig. 9): five embedded JPEG spectrograms and their colour bars; tick labels read from a 400 dpi render. Kadri (2024) Supplementary S1, page 5 (Fig. S1), whose tick labels are text.
- hydro_data.sqlite (read-only): Fig. 9 and Fig. S1 vertex tables, Table 1, site, known_event.
- 6 November code and outputs (bundle hydro_detector_code_2026-11-07): kadrienv.py (envelope statistic), network14.py (window calibration), run14v5_final/station_point_series.csv, grid_ext_paths_wide.csv, path_speed_bounds_woa23.csv.
- Raw IMOS 250 Hz cache for logger 3250 (Scott Reef), clock-corrected start times.

## 2. Item A: Kadri (2019) Fig. 4, Diego Garcia South, 00:00-02:00 UTC

### 2.1 Calibration and resolution

Axes were calibrated by a least-squares fit to the centres of the tick-label glyphs (3-8 labels per axis). Table `kadri2019_fig4_axis_calibration.csv`.

| Quantity | Pixel resolution | Calibration residual | Effective uncertainty |
|---|---|---|---|
| Bearing-time image, time | 10.41 s/px (00:00 panel), 10.81 s/px (01:00 panel), 10.60 s/px (23:00 panel) | <= 0.33 px (<= 3.6 s) | transient width 54 s (full width at half maximum) |
| Bearing-time image, bearing | 0.576-0.577 deg/px | <= 0.43 px (<= 0.25 deg) | shot-line width 1.73 deg; transient width 3.5 deg; reference offset 2.58 +- 0.51 deg (below) |
| Bearing-time image, intensity | CIELAB L* per pixel, 0.0-70 above background | none (no colour bar) | relative only; smallest visible step about 1-2 L* units |
| Pressure trace, time | 15.0 s/px (01:00), 15.6 s/px (00:00), 15.0 s/px (23:00) | <= 0.61 px (<= 9.4 s) | -19 s alignment to Fig. 9; correlation within 0.02 of best over -35 to 0 s |
| Pressure trace, pressure | 0.0292 Pa/px (01:00), 0.0317 Pa/px (00:00), 0.0148 Pa/px (23:00) | <= 0.002 Pa | +-1 px at each envelope edge (antialiasing) |
| Cross-correlation RMS | 0.0029-0.0035 per px | <= 0.0008 | +-1 px |

Bearing reference. The image bearings run above the values Kadri states in the text by a constant amount (`kadri2019_fig4_bearing_reference_checks.csv`):

| Kadri value | Image reading | Difference |
|---|---|---|
| Table 3, 23:57, 247 deg | 23:56:53, 249.30 deg | +2.30 |
| Table 3, 00:11, 170 deg | 00:11:04, 173.48 deg | +3.48 |
| Table 3, 01:58, 241 deg | 01:58:45, 243.49 deg | +2.49 |
| Fig. 1, 309 deg shot train | 311.30 deg | +2.30 |
| Fig. 1, 219 deg shot train | 221.35 deg | +2.35 |

Mean +2.58 deg, standard deviation 0.51 deg (n = 5). All bearings below are "Kadri-referenced": image reading minus 2.58 deg. The cause of the offset is not known (a half-bin plotting convention is possible). The bearing bias of the Diego Garcia South array itself is not calibrated by anyone; this offset is only a reading convention.

Amplitude cross-check. The Fig. 4 envelope (01:00-01:20) agrees in shape with the re-calibrated Fig. 9 trace (correlation 0.86 of the half peak-to-peak envelopes; Fig. 4 amplitude 0.74 x Fig. 9, median). The two papers may show different hydrophones or filters. The gap at 00:15-00:18 in the 00:00 panel is missing data in the source.

Not digitised: the bearing-scatter panels (dots about 13 deg wide; no information beyond the image).

### 2.2 (i) 01:09:55-01:11:30 UTC

- The dominant bearing in every column is the 309 deg shot train (L* excess 39-49). Its intensity dips at 01:10:28-01:11:12.
- No transient above the detection threshold occurs at any other bearing.
- A weak feature lies at 172.2-172.8 deg, 01:10:39-01:11:01 (L* excess 1.7-2.1). It is outside the arc sector (114.5-168.6 deg) but inside the 6 deg margin. In the background hours (23:00-00:56), 3-7 % of columns reach this level in the arc sector. The same direction carries two earlier signals that precede any possible arc arrival: 00:11:04 at 170.9 deg (Kadri Table 3, HA_31) and 00:24:49 at 172.7 deg. We label the feature as that recurring 170-173 deg source. We do not exclude it.
- The Fig. 4 envelope is low here: excess -3.0 to -0.85 dB relative to its ring, p 0.85-0.98 against the pre-arrival background.

### 2.3 (ii) Transients 00:56-01:42

Detection: connected pixels more than 4 L* above a 31-column running median of the same row (`kadri2019_fig4_dgs_bearing_transients.csv`, all panels; 2 px annotation circles masked).

- 00:56:34-01:00:00 (00:00 panel): no transient.
- 00:56:34-01:42:18 in total: 53 transients. 31 lie within 5 deg of the two shot-train lines (labelled as shots). The other 22 are at recurring bearings:
  - 34.7-38.9 deg, 6 (01:02:33, 01:09:45, 01:20:45, 01:28:26, 01:29:34, 01:41:51); a faint persistent band at this bearing runs through all three hours;
  - 246.6-246.8 deg, 5 (01:19:07, 01:28:51, 01:31:07, 01:35:02, 01:37:50); the same bearing as Kadri's HA_30 signal at 23:57;
  - 284.6-288.7 deg, 4 (01:27:54, 01:32:11, 01:38:59, 01:40:07);
  - 316.6-334.6 deg, 5 (01:08:19, 01:13:02, 01:13:56, 01:14:38, 01:27:14); the three at 01:12:38-01:14:59 coincide with the envelope rise at 01:12:33-01:15:33;
  - 276.4 deg (01:28:51) and 224.6 deg (01:35:09), single pixels.
- None of the 53 points into the arc sector, with or without the 6 deg margin.
- Sub-threshold features in the arc sector (`kadri2019_fig4_dgs_weak_arc_sector_features.csv`), L* excess 1.5-2.2:
  - 01:10:39-01:11:01, 172.2-172.8 deg (above);
  - 01:13:21-01:13:54, 136.5-137.1 deg (arc about 30.4 S); it occurs at the same time as the 316.6 deg transient, 179.6 deg away;
  - 01:28:08-01:28:40, 156.6-157.2 deg (arc about 37.8 S).
  In the background hours 3.8 % of columns reach 2.0 L* in the arc sector; in the arrival span 1.2 % do (3 of 248 columns). These features are not significant. We keep them on the list.
- Envelope episodes with p < 0.01 against the pre-arrival background (453 columns, so the smallest possible p is 0.0022): 01:03:33-01:04:03 (excess 3.0 dB; combined with cross-correlation, p 0.026) and 01:12:33-01:15:33 (up to 5.2 dB; combined p 0.0022). The second is the shot-train rise.

### 2.4 (iii) Shot trains

| Kadri (2019) Fig. 1 | Image line (Kadri-referenced) | Visible in Fig. 4 |
|---|---|---|
| 309 deg, 23:50-03:10 | 308.7 deg | 23:52:26 to 01:55:20; fades after about 01:45 |
| 219 deg, 23:10-02:10 | 218.8 deg | 23:10:34 to 01:58:46 (end of panel) |

Correction to the audit note: Fig. 1 gives 23:50, not 23:00, as the start of the 309 deg train. Shots are labels only (ruling); the shot-line intensities per column are in `kadri2019_fig4_dgs_bearing_columns.csv`.

### 2.5 (iv) Directions to the 7th arc

`dgs_bearings_to_7th_arc_20_41S.csv` (from grid_ext_paths_wide.csv, station H08S): 114.96 deg at 20 S to 167.85 deg at 41 S on the arc; 114.47-168.56 deg over +-150 NM. Assumed bearing uncertainty 6 deg: reading 1 deg, reference offset 0.5 deg, and up to 5 deg array-position bias. The bias allowance is by analogy with Cape Leeuwin, where the array correction (ruling B1) moved bearings by up to 4.4 deg. The Diego Garcia South bias is not calibrated.

## 3. Item B: out-of-sample null and re-score of 01:10:15

### 3.1 A digitisation error in the Fig. 9 traces

The project database table of Kadri (2024) Fig. 9 holds pressures whose scale does not match the figure tick labels (`kadri2024_fig9_pressure_scale_audit.csv`):

| Panel | Station | Database scale, zero | Tick-label scale, zero | Effect on database pressure |
|---|---|---|---|---|
| a | Cape Leeuwin | 32.65 pt/Pa, 93.72 pt | 32.44 pt/Pa, 93.76 pt | -0.7 % (negligible) |
| b | Cape Leeuwin | 32.65 pt/Pa, 198.22 pt | 32.71 pt/Pa, 198.17 pt | +0.2 % (negligible) |
| c | Cape Leeuwin | 32.65 pt/Pa, 300.85 pt | 29.63 pt/Pa, 299.09 pt | 10 % low, +0.054 Pa offset |
| d | Diego Garcia South | 16.33 pt/Pa, 404.72 pt | 10.87 pt/Pa, 404.61 pt | 33 % low (factor 1.50) |
| e | Diego Garcia South | 8.16 pt/Pa, 511.70 pt | 7.25 pt/Pa, 508.00 pt | 11 % low, +0.454 Pa offset |

Tick-label fit residuals are <= 0.0075 Pa. The median vertex height of every panel equals the tick-label zero within 0.08 pt, which confirms the tick-label zeros. The database used the panel a scale for panel c and wrong values for d and e. The re-calibrated vertices are in `kadri2024_fig9_panels_cde_recalibrated_vertices.csv`. Per-point resolution after re-calibration: 0.031 Pa/pt (a, b), 0.034 Pa/pt (c), 0.092 Pa/pt (d), 0.138 Pa/pt (e). The Fig. S1 a-c digitisation matches its text tick labels exactly (15.03, 18.39, 14.74 pt/Pa).

Consequence. In the database values the median |pressure| per 30 s steps from 0.18 Pa to 0.47 Pa (8.2 dB) exactly at the panel join, 01:10:00. With the tick-label scale it is 0.26-0.29 Pa on both sides (`dgs_fig9_panel_join_check.csv`). The Fig. 9 spectrogram shows no step either: median 72.3 dB in the last minute of panel d, 71.7 dB in the first minute of panel e (2-40 Hz). The 6 November statistic compares a 30 s window with a ring of 180 s on each side. For windows just after 01:10:00 the ring lies partly in panel d, so the step raised the band energy there. That is the 01:10:15 peak.

### 3.2 Re-score

Statistic: the 6 November envelope statistic without change (band energy E over the ring median; envelope persistence; Fisher combination; reproduced to 4e-16). Out-of-sample background: Fig. S1 a-c, Diego Garcia South, 7 March 17:49-17:59, 18:44-18:54, 19:00-19:10 (349-355 looks, 30 min). Four background variants handle the different vertex density of Fig. S1 (25-86 vertices/s against 14.9/s on 8 March). Table `dgs_envelope_null_rescore_0110.csv`.

| Input | Background | E at 01:10:15 | Per-look p | Window p, 4 / 6 / 8 / 10 min (within segment) |
|---|---|---|---|---|
| database (6 Nov) | same trace (6 Nov method) | 5.75 dB | 0.0085 (rank 1/234) | 0.265 / 0.460 / 0.697 / 0.993 |
| database | 7 Mar, as digitised | 5.75 dB | 0.0056 | < 0.0002 at all lengths (beyond the background) |
| database | 7 Mar, 1 s envelope bins | 3.55 dB | 0.0084 | 0.419 / 0.615 / 0.676 / 0.666 |
| re-calibrated | same trace (6 Nov method) | 4.10 dB | 0.590 (rank 138/234) | 0.501 / 0.845 / 0.991 / 0.570 |
| re-calibrated | 7 Mar, as digitised | 4.10 dB | 0.037 | 0.332 / 0.495 / 0.647 / 0.669 |
| re-calibrated | 7 Mar, thinning lag fixed at 9 bins | 4.10 dB | 0.020 | < 0.0002 (window maximum set by 01:08:15, not 01:10:15) |
| re-calibrated | 7 Mar, thinned to 14.9 vertices/s (10 seeds) | 4.10 dB | 0.379 (0.329-0.426) | 0.354 / 0.528 / 0.330 / 0.333 |
| re-calibrated | 7 Mar, 1 s envelope bins | 4.29 dB | 0.028 | 0.688 / 0.953 / 1.000 / 1.000 |

Block-bootstrap window p (2 min blocks) and the Bonferroni bounds are in the table; they agree with the within-segment values to within about 0.2.

Reading:
- With the correct scale, 01:10:15 is not the top look under any background. The top looks are 01:14:15 (in-sample p 0.0043) and 01:08:15, both in the shot-train rise.
- The comparison asked for (per-look 0.0085, window 0.749) is superseded: per-look 0.59 in-sample and 0.02-0.43 out-of-sample; window 0.33-1.0, except one variant where another look sets the window maximum.
- The 7 March background is not fully comparable. On 8 March the shot trains keep E above the 7 March maximum (3.35 dB) in 175-191 of 234 looks (46 with thinning). So small out-of-sample p values describe the 8 March shot noise, not a transient.
- Window p values below about 1/7 (4 min) or 1/3 (10 min) are beyond what 30 min of background can resolve. Values printed as < 0.0002 are draw floors, not probabilities.

Fig. 4 envelope (Section 2.3) gives an independent view of the same hour and shows a local low at 01:10.

## 4. Item C: Scott Reef third pick, 01:32:51 UTC

Data: raw record of logger 3250, sequence 6, start 01:29:44.9 UTC after the logger clock correction (logger 15.1 s late), 307 s, 250 Hz, 8 Hz hardware high-pass. Figure `fig_scott_reef_0132_pick.png`.

- Detector score (6 November combined detector, `scott_reef_record_0130_detector_looks.csv`): p 0.0138 at 01:32:49.9 and 0.0153 at 01:32:54.9; winning clutter class "earthquake". 2.4 % of all looks of this logger on 8 March reach p <= 0.0153. The record minimum is p 0.00044 at 01:33:59.9.
- The record contains two strong pulses: 01:32:40.5-01:32:45.6 (8-40 Hz band energy +21.9 dB over the record median, the record maximum) and 01:32:47.7-01:32:53.8 (+20.1 dB), which contains the pick.
- Spectra (`scott_reef_0132_transient_spectrum.csv`): the first pulse is narrow, +21 to +27 dB at 20-40 Hz and at most +2.2 dB at or below 16 Hz, like the calls at 20-45 Hz that repeat through the record (whale-like). The pulse at the pick is broadband, +17.6 to +32.1 dB from 10 to 100 Hz, highest at 50-63 Hz, slope +1.7 dB per octave over 20-100 Hz. It does not have the impact shape (-7 dB per octave). A further broadband pulse at about 01:33:05 is followed by raised 5-30 Hz noise. Source not identified.
- Possible label: the Halmahera earthquake (mb 3.93, 01:13:09 UTC, 2,115 km) could arrive at 01:30-01:37 under mixed seismic and water paths. This is a timing label only; it is not verified.

Arc points and impact times consistent with 01:32:51 +- 10 s (`scott_reef_0132_consistent_arc_points.csv`), impact window 00:19:38-00:55:00:

| Speed model | Points (project grid, to 34 S) | Impact time |
|---|---|---|
| Kadri 1.45-1.57 km/s | 33S +125 NM, 33S +150 NM, 34S +150 NM | 00:52:31-00:55:00 |
| WOA23 March path bounds (slow side / 1.05) | 32S +125/+150 NM, 33S +125/+150 NM, 34S +150 NM | 00:51:30-00:55:00 |

All these paths are classed "large attenuation". The project grid for this logger stops at 34 S. South of 34 S the geodesic from Scott Reef passes within about 0-60 km of North West Cape (114.1 E, 21.8 S); those points (35-41 S, impact 00:37:57-00:55:00 at Kadri speeds) are listed as "path not assessed" and are provisional.

Predicted arrival spans at the other sites, for the in-grid points (`scott_reef_0132_predicted_spans_other_sites.csv`):

| Site | Span (WOA23 bounds) | What the data show |
|---|---|---|
| Cape Leeuwin | 01:14:04-01:19:32 | Fig. 9 ends at 00:57. The report to the ATSB (Fig. 3) lists 01:14 at 183.0 deg and 01:18 at 188.4 deg (corrected); the arc directions are 271.9-279.4 deg. No match. |
| Diego Garcia South | 01:28:08-01:35:20 | Fig. 4: no transient at 135-152 deg (arc 141.0-146.1 deg with margin); maximum excess 0.11 L*; envelope minimum p 0.095. |
| Perth Canyon 3315 | 01:15:06-01:20:40 | 260 s recorded; minimum p 0.245. |
| Perth Canyon 3376 | 01:15:06-01:20:41 | 25 s recorded; minimum p 0.918. |
| Portland 3274 | 01:40:02-01:47:53 | 160 s recorded; minimum p 0.279. |
| Portland 3275 | 01:40:01-01:47:52 | not recorded (duty cycle). |

The Kadri-speed spans are slightly narrower (same table). No site supports the pick.

## 5. Item D: relative spectra from the Fig. 9 spectrograms

Raster calibration (`kadri2024_fig9_spectrogram_calibration.csv`): 754-762 x 272-277 px per 10 min panel; 0.785-0.791 s/px; 0.141 Hz/px (0.211 Hz/px in the 0-60 Hz panel); lowest row 1.8-1.9 Hz. Tick-fit residual <= 1.3 px (time) and <= 0.33 px (frequency). Colour to level: nearest colour in each panel's colour bar, 0.17-0.19 dB per colour-bar row; colour-bar label fit residual <= 0.03 dB; panel c colour bar runs to 109 dB, the others to 112-114 dB. Median colour distance of the JPEG pixels to the colour bar is 15-18 RGB units (JPEG chroma subsampling). The absolute reading remains about 15 dB low (earlier flag); only differences are used.

Method: mean power in one-third-octave bands, event window -3 to +12 s (sensitivity -2 to +5 s) against columns 20-90 s before and 30-100 s after, same panel. Reference distribution: 400 random times per panel. Signal slope: fit of 10 log10(P_event - P_background) over 3-40 Hz bands with positive excess. Tables `kadri2024_fig9_relative_spectra_summary.csv` and `..._bands.csv`.

| Time | Broadband excess (p) | Bands above the 95 % reference (p) | Shape | Signal slope, dB/octave | Reading |
|---|---|---|---|---|---|
| CL 00:36:07 | +3.2 dB (0.06) | 4 (0.03) | band 10-25 Hz, peak 16 Hz; nothing below 8 Hz | -4.4 +- 6.4 | not impact-like (no low-frequency energy); whale-like or distant source; earlier earthquake label stands |
| CL 00:47:04 | +2.3 dB (0.06) | 4 (0.002) | flat to rising, 3 Hz and 25-31.5 Hz | +1.6 +- 1.1 | not impact-like; broadband, airgun-like or ship-like; earlier earthquake label stands |
| CL 00:49:58 | -0.8 dB (0.64) | 0 | none | n/a | not visible in the spectrogram |
| CL 00:51:50 | +1.9 dB (0.19) | 3 (0.012) | 4-10 Hz | -4.0 +- 1.1 | low-frequency; nearest to impact or earthquake shape, but slope 2.8 standard errors shallower than -7; not significant in the 7 s window |
| CL 00:54:30 | +2.7 dB (0.05) | 3 (0.012) | peak 3.15 Hz, plus 8 Hz and 20-25 Hz | -1.4 +- 1.3 | low-frequency peak with broadband excess; earthquake-like more than impact-like |
| CL 00:55:07 | -0.2 dB (0.45) | 1 | none | n/a | not visible |
| DGS 01:10:15 | +0.6 dB (0.24) | 2 (0.15) | 5-6.3 Hz only | not constrained | no significant excess |

Seven times and two windows are tested, so a p of 0.01-0.05 is not significant after allowance for multiplicity. The DGS 01:10:15 result agrees with Section 3: nothing is there.

## 6. Effect on earlier results

- 6 November candidate 6 (Kadri 00:49:58 with Diego Garcia South 01:10:15, 38-39 S): its Diego Garcia South member is withdrawn (Section 3). 00:49:58 itself shows no spectral excess.
- 6 November candidate 1 (already withdrawn on 7 November): it also used 01:10:15.
- The 6 November Cape Leeuwin envelope stream used panel c with a 10 % scale error and a 0.054 Pa offset. A check at the six Cape Leeuwin candidate times shows small changes only: 00:47:05 moves from p 0.014 to 0.0056; the others change by 0.003-0.085 (00:55:05 moves from 0.40 to 0.48).
- Recommendation: correct the Fig. 9 tables in hydro_data.sqlite (panels c-e) and re-run the Cape Leeuwin and Diego Garcia South envelope streams of the combined detector. We did not modify the database (read-only use).

## 7. Key assumptions and modelling choices

| Item | Choice | Status |
|---|---|---|
| Impact window | 00:19:38-00:55:00 UTC; 7th arc 20-41 S, +-150 NM | Pete's ruling |
| Diego Garcia South arrival span | 00:56:34-01:42:18 (1.465-1.520 km/s, 2 % detour, unblocked points) | project convention (6 Nov run) |
| Sound speeds for Scott Reef | Kadri 1.45-1.57 km/s; WOA23 March path bounds, slow side / 1.05 | Pete's ruling |
| Airgun shots | label and interference test only, never exclusion | Pete's ruling |
| Time coincidence with Royer | label only | Pete's ruling |
| Cape Leeuwin bearings | corrected bearings primary (ATSB detections table) | Pete's ruling (B1) |
| Kadri (2019) Fig. 4 hour labels | 12-hour labels: "12.00 UTC" = 00:00, "1.00 UTC" = 01:00 | audit finding, confirmed by Table 3 signal times |
| Bearing reference | image reading minus 2.58 deg | own choice (from 5 checks) |
| Diego Garcia South bearing uncertainty | 6 deg margin (1 + 0.5 + up to 5 deg bias) | own choice; bias not calibrated; not agreed by Pete |
| Fig. 4 trace time alignment | -19 s, from cross-correlation with Fig. 9 | own choice |
| Transient threshold | 4 L* above a 31-column running median; shot sector +-5 deg | own choice |
| Fig. 9 pressure scale | tick-label calibration replaces the database values for panels c-e | own choice; correction of a project error; not yet agreed by Pete |
| Envelope statistic | unchanged from 6 Nov (kadrienv.py) | project convention |
| Out-of-sample background | Fig. S1 a-c, four variants for vertex density | own choice |
| Fig. 4 envelope null | 23:00-00:55:34 columns (before the earliest arrival, 60 s margin) | own choice |
| Spectrogram reading | nearest colour-bar colour; relative levels only | own choice; absolute reading flagged low (earlier finding) |
| Spectral windows | -3 to +12 s (primary), -2 to +5 s; background 20-100 s either side | own choice |
| Impact spectral shape | about -7 dB/octave above 3 Hz; corners 0.2-2.7 Hz | project convention (source model families) |
| Scott Reef pick tolerance | +-10 s | own choice |
| Scott Reef grid | project grid to 34 S; 35-43 S added with geodesic distances, path not assessed | own choice; provisional |
| Clock | IMOS times corrected by the measured logger clock error (3250: 15.1 s) | project convention |

## 8. Deviations and limits

- All Cape Leeuwin and Diego Garcia South values come from published raster or vector figures, not from raw IMS data.
- The Fig. 4 bearing-scatter panels were not digitised (dots about 13 deg wide).
- The 7 March background covers 30 min only; window p values below about 0.15-0.3 cannot be resolved, and the 8 March shot noise makes that background not fully comparable.
- Thinning (variant V3) uses 10 random seeds; the other variants are deterministic.
- The Scott Reef grid points south of 34 S lack path classification; their result is provisional.
- The DGS 01:10:15 spectral and envelope results rest on the re-calibration in Section 3.1, which Pete has not yet reviewed.

## 9. Files

Tables:
- `kadri2019_fig4_axis_calibration.csv` - axis fits, resolutions, residuals (Fig. 4).
- `kadri2019_fig4_bearing_reference_checks.csv` - five checks of image bearings against Kadri text values.
- `kadri2019_fig4_dgs_bearing_columns.csv` - per image column: dominant bearing, non-shot bearing, intensities, arc-sector maximum, shot-line intensities (00:00, 01:00 and 23:00 panels).
- `kadri2019_fig4_dgs_bearing_transients.csv` - all detected transients with labels.
- `kadri2019_fig4_dgs_weak_arc_sector_features.csv` - sub-threshold features in the arc sector, 00:56-01:42.
- `kadri2019_fig4_dgs_trace_xcorr_columns.csv` - per 15 s column: envelope, cross-correlation, excess and p values.
- `dgs_bearings_to_7th_arc_20_41S.csv` - bearings and distances from Diego Garcia South to the arc.
- `kadri2024_fig9_pressure_scale_audit.csv` - database against tick-label scale, all five panels.
- `kadri2024_fig9_panels_cde_recalibrated_vertices.csv` - re-calibrated vertices, panels c-e.
- `dgs_fig9_panel_join_check.csv` - 30 s levels across the panel join.
- `dgs_envelope_null_rescore_0110.csv` - re-score of 01:10:15, all inputs and backgrounds.
- `scott_reef_record_0130_detector_looks.csv`, `scott_reef_0132_transient_spectrum.csv`, `scott_reef_0132_consistent_arc_points.csv`, `scott_reef_0132_predicted_spans_other_sites.csv` - Scott Reef test.
- `kadri2024_fig9_spectrogram_calibration.csv`, `kadri2024_fig9_relative_spectra_summary.csv`, `kadri2024_fig9_relative_spectra_bands.csv` - spectral reading.

Figures (working version with footnotes; Journal of Navigation version as `-word.png` at 600 dpi, `-jon.pdf`, `-proof.png` with caption, `-caption.txt`):
- `fig_dgs_kadri2019_fig4_0000_0200` - Diego Garcia South 00:00-02:00 from Fig. 4.
- `fig_dgs_0110_panel_join_rescore` - the panel-join error and the re-score of 01:10:15.
- `fig_scott_reef_0132_pick` - Scott Reef record at the third pick.
- `fig_kadri2024_fig9_relative_spectra` - relative spectra at seven candidate times.

Code: `kadri_unused_data_2026-11-07.py` (the analysis as run, exported from the session).
