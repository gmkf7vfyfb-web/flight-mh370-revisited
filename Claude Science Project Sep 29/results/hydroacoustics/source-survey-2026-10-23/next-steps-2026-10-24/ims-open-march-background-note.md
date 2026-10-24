# Open IMS hydrophone records for March 2015-2019: same-season noise and false-alarm background

Hydroacoustics module. 24 October 2026. **Status: EXPLORATORY.** Nothing here returns a likelihood to the composer. No 8 March 2014 IMS waveform was available, so every number here is a **same-season proxy**, taken from other years.

## 0. Deviations and limits (read first)

1. **Volume cut, as the brief allowed.** The sandbox network gave about 1.1 MB/s in total. A PyPI download in parallel gave only 0.27 MB/s, so the limit is the network, not EarthScope. Full days for 1-15 March (about 150 station-days, about 15 GB) would have taken more than 4 h, and requests for full days stalled with 300-s read timeouts. So I kept:
   - **00:00-04:00 UTC of every open March day, 1-31 March, 2015-2019, all three elements.** That is 273 station-days requested and 268 processed: H01W 115 days, H08S 153 days. Five blocks had no data: H01W 2018-03-08, 03-09, 03-13 and 03-21, and H08S 2016-03-23. This block contains both arrival windows. It is the primary data set for the noise in the window and for all detections and rates.
   - **Complete days for 8 March only**, for the time-of-day comparison: H01W 2015, 2017, 2018 and 2019, and H08S 2015-2019. H01W 2018-03-08 has 69 % coverage and no data in 00:00-04:00.
   - So the "rest of day" comparison rests on these 9 days only (provisional). It is not based on 1-15 March.
2. **H01W 2016 has no open data on 1-15 March.** It has only 12 March days (18-31 March), and those were used.
3. **H08N: no open data.** All 1,437 probed element-days returned 404: 465 March element-days and the February and April days in 2015-2019, plus the selected dates in 2010-2014 and 2020-2025. H08N is not analysed. It is blocked from the arc anyway (project result).
4. **No open data before 2015 for any station.** That includes March 2014: probes on 1, 8 and 15 March 2010-2014 at all 9 elements returned 404. H08S has open data on probed dates in 2020-2025, but those years were not processed because the brief set 2015-2019.
5. **The FDSN availability service is retired.** fdsnws/availability and irisws/availability both returned 404 "retired". I mapped availability by probes instead: two 30-s requests per element-day, at 00:30 and 12:00 UTC. A day with data only between the probe times would be missed.
6. **H01W bearings needed an empirical array calibration** (not planned; see section 3.3). On the FDSN element positions the bearings were biased by a median of +5.2°, and by up to +12° at 260-280°, which is inside the arc sector. All H01W sector results use the calibrated bearings. H08S uses the FDSN geometry.
7. **The 2014 stand-in null is used for D1 and M1b only.** It is the run-J IMOS 3376 window-maximum file, `null_3376.npz` (n = 6,574). The 2-8 Hz statistic has no stand-in analogue.
8. **Rough classes are labels, not exclusions.** The thresholds of the periodicity rule were set after looking at the 8 March full days (section 3.4).
9. **The catalogue association does not check path blockage.** The chance level was measured with a time-shift control (section 3.5).
10. **A pandas 3 timestamp-unit bug was found and fixed before any reported number.** The bug converted microseconds as nanoseconds and produced zero catalogue matches. All reported values come from the corrected run.
11. **ObsPy warned "computed and reported sensitivities differ by more than 5 %".** I checked all 11 channel epochs: computed and stated sensitivity agree to 0.0 dB at 10 Hz. So the absolute levels are not affected.
12. **No registrations, no requests to people or agencies.** All data came from anonymous FDSN services: EarthScope dataselect and station, USGS ComCat and the ISC Bulletin.

## 1. Main findings

**Noise in the arrival windows** (5-40 Hz band SPL, dB re 1 µPa, element-minutes pooled over the 3 elements):

| station | March 2015-2019, window: median (5-95 %) | 2003 Blackman median | stand-in (IMOS 3376) | March − 2003 | March − stand-in |
|---|---|---|---|---|---|
| H01W (00:25-02:20) | 103.6 (100.9-107.8), n = 37,825 | 101.6 | 96.2 | **+2.0 dB** | **+7.4 dB** |
| H08S (00:45-02:50) | 98.0 (93.6-106.9), n = 57,366 | 95.5 | 96.2 | **+2.5 dB** | **+1.8 dB** |

- Most of the excess over 2003 is at 5-12.5 Hz. In the third-octave mean PSD, March is +5.0 to +5.9 dB above 2003 at H01W and +4.7 to +6.4 dB at H08S. At 16-25 Hz the difference is within ±1.5 dB at both stations.
- **The stand-in under-states the H01W noise by about 7 dB** (registry D06). Any H01W detection probability or upper limit built on the stand-in is therefore optimistic by about that much in noise terms. This is provisional, because it is a proxy year.
- **Time of day** (8 March full days only, provisional): the window is louder than the rest of the day by +0.8 dB at H01W (103.98 against 103.14) and +0.4 dB at H08S (97.61 against 97.24). Within the 115/153-day 00:00-04:00 blocks, the window and the rest of the block differ by less than 0.1 dB.

**False-alarm background: coherent arrivals from the bearing sector of the 7th arc, 20-40 S, inside the 2014 arrival clock windows** (statistic D1, 5-40 Hz STA 2 s / LTA 30 s, registered run-J definition; rate per hour; brackets give the 90 % day-bootstrap interval of the mean):

| station, window | level | p from same-season null | p from 2014 stand-in null |
|---|---|---|---|
| H01W 00:25-02:20 (115 days, 208 h) | screen p < 0.3 | **0.139** (0.086-0.194) | 0.072 (0.037-0.112) |
| | mark p < 0.1 | **0.125** (0.072-0.179) | 0.024 (0.009-0.043) |
| | report p < 0.05 | **0.086** (0.048-0.130) | 0.010 (0.000-0.020) |
| H08S 00:45-02:50 (153 days, 315 h) | screen p < 0.3 | **1.00** (0.72-1.32) | 0.36 (0.23-0.53) |
| | mark p < 0.1 | **0.43** (0.28-0.62) | 0.13 (0.07-0.21) |
| | report p < 0.05 | **0.36** (0.23-0.52) | 0.054 (0.016-0.105) |

p floors: 1/27,850 (H01W) and 1/39,173 (H08S) for the same-season null; 1/6,575 for the stand-in null.

- **Expected count in one window:**
  - H01W (1.92 h): about 0.27 arc-sector arrivals at the screen level and about 0.17 at the report level.
  - H08S (2.08 h): about 2.1 at the screen level and about 0.74 at the report level.
- **The rate varies strongly from day to day.** Most days have none. The 95th percentile of the daily rate is 1.05/h at H01W and 3.30/h at H08S (screen level). Yearly means range from 0.03 to 0.24/h at H01W and from 0.11 to 1.91/h at H08S.
- **At H08S the background is concentrated where the impact is most likely.**
  - 298 of the 316 arc-sector screen-level passes come from the 35-40 S part of the sector (148.3-163.5°): 0.945/h, against 0.057/h for 20-35 S.
  - That bearing also points to the Antarctic margin and the ridge to the south, so bearing alone cannot separate them at H08S.
- **At H01W the arc-sector background is split.** It is 0.082/h for 20-35 S (263.6-327.9°) and 0.058/h for 35-40 S (248.9-263.5°), at the screen level.
- **Other statistics** (arc sector, clock window, same-season null; screen / mark / report):
  - H01W: registered M1b 0.086 / 0.038 / 0.014; D1 at 2-8 Hz 0.173 / 0.149 / 0.101.
  - H08S: M1b 0.97 / 0.74 / 0.49; D1 2-8 Hz 0.56 / 0.35 / 0.27.
- **The registered M1b detector runs on these data without change**: the 18-template bank from `templates_raw.npz`, on the 5-40 Hz 10 Hz envelope. Defect D05 (model-template mismatch) still applies.
- **Coherent arrivals from any direction** (screen level, clock window): 7.4/h at H01W and 14.6/h at H08S.
  - At H01W, 2,937 of the 3,223 coherent screen-level windows in the blocks (91 %) come from the Antarctic sector (140-224°).
  - At H08S, 6,340 of 8,513 (74 %) are periodic 5-15 s trains, at about 108-114°.

![Noise spectra in the arrival windows]({{artifact:6f1baa3c-a0c4-4d6c-b567-a59a59308c73}})

![5-40 Hz level through 8 March]({{artifact:f9b484ae-1b50-4deb-9565-1f612ed15710}})

![Direction of coherent arrivals]({{artifact:bab41ab1-d022-44fd-b280-eecb30c4bbbd}})

![Rate of arrivals from the arc direction]({{artifact:2c9fc689-d56d-444a-a4e2-932a9cf697f1}})

## 2. What differs on 8 March 2014 (the proxy limits)

Other years are a proxy for 8 March 2014. Surveys, ice and whales were different. Points from the survey tables and the hydro database:

1. **H08S, 2014.** CMST 2014 (Table 4; digitised Fig. 7, 389 iteration-1 detections inside 00:45-02:50, all at about 35° and about 113°, none in the arc sector) shows **two airgun trains across the whole window**.
   - In 2015-2019 a periodic 5-15 s train filled at least 30 % of the window on 49 of 153 days: 6 days in 2015, 20 in 2016, 23 in 2017, none in 2018-2019. All of those trains were at 108-114°.
   - **No train at about 35° (Bay of Bengal) occurs in the proxy years.** The 2014 H08S window was therefore noisier and more masked than a typical proxy day. The proxy also does not model a 35° train.
   - The 113° train lies about 1.9° outside the arc sector (114.9°). Within one hour of a train, the robust SD of the H08S bearing has a median of 0.07° (interquartile range 0.04-1.6°, 145 train-hours). Train shots therefore stay out of the sector in the proxy. A 2014 train at 113.0-113.6° would behave the same.
2. **H01W, 2014.** Royer 2016 (hydro_data.sqlite, `dg_royer_2016_royer_arrivals`, H01W1) has 17 arrival rows inside 00:25-02:20, about 13 distinct times.
   - Three of these arrivals have a location option whose bearing lies inside the arc sector: 00:35:54 (264.3°), 01:29:42 (286-292°) and 01:34:31 (277° or 301°). That is about 1.6 per hour. The proxy gives 0.139/h at the screen level.
   - CMST 2014 (digitised Fig. 5) has 55 detections inside the window (28.7/h). Fifty-four of them are at 120-210° and one is in the arc sector.
   - Royer's located arrivals are not from the same detector, and their bearings come from locations, not from the triplet. The comparison is therefore only indicative. It suggests that the 2014 window held more arc-direction arrivals than a typical proxy day.
3. **Season.** Early March is the iceberg-noise maximum (survey review). The proxy covers all of March, so it brackets this.
4. **Earthquakes.** The 2014 window had the south-of-Java mb 4.04 event (23:52:17), whose predicted H01W arrival falls just before the window. The proxy days have their own catalogue events instead.

## 3. Method

### 3.1 Data and response

- Data: IM.H01W1-3 and H08S1-3, channel EDH, 250 Hz, from EarthScope FDSN dataselect (anonymous).
- Response: the full StationXML response (level=response) was removed with ObsPy (output DEF = Pa; pre-filter 0.3/0.5/110/120 Hz; taper 0.05 % of each segment). 60 s at each gap edge was set to NaN.
- Element positions: from FDSN. These are single epochs from 2004 (H01W) and 2002 (H08) onward, so they are the same for 2015-2019.
- Raw miniSEED was deleted after each station-day was processed. Only the derived products are kept.

### 3.2 Noise

- Welch PSD for each element-minute: Hann window, 4 s, 50 % overlap, 0.25 Hz bins. These were averaged to 1-Hz bins centred on 1-100 Hz.
- Also computed: third-octave band SPL and band-mean PSD (base-10 centres 2-80 Hz), and the 5-40 Hz SPL.
- Percentiles 5/25/50/75/95 were taken over element-minutes, per element and pooled.
- 2003 reference: recomputed from the QC-passed Blackman panels in `blackman_noise_curves.npz` (23 H01W, 19 H08S). The recomputed 5-40 Hz medians are 101.6 and 95.5 dB; the module note gives 101.7 and 95.6 dB.
- Stand-in: the IMOS 3376 5-40 Hz SPL of 96.2 dB re 1 µPa (`blackman_noise_offsets.json`). It is drawn as a flat PSD of 80.8 dB re 1 µPa²/Hz.
- Below 3 Hz the response correction is large (−15 dB at 1 Hz relative to 10 Hz).

### 3.3 Detection, bearing and calibration

**Statistics.**

- D1_540: 5-40 Hz band-pass to 100 Hz; energy STA 2 s / LTA 30 s, hop 0.1 s. This is the registered run-J D1 on the IMOS path.
- M1b: the registered envelope matched filter, copied verbatim from `prepare/searches_run_j/detectors.py`. It uses the 18-template bank (ranges 1,800-3,703.5 km × τ 0.1/1/10 s, `templates_raw.npz`).
- D1_28: 2-8 Hz band-pass to 25 Hz, STA/LTA as above (not registered).
- Window score = the maximum in each 55-s window from 32 s after 00:00 (registered rule). A window is invalid if any NaN lies in [start − 35 s, end + 60 s].

**p-values.**

- Same-season null: all valid windows of that station and statistic in the 00:00-04:00 blocks of every March day, so the null has the same clock hours as the search. p = k/n, leave-one-out.
- Stand-in null: p = (k + 1)/(n + 1) against `null_3376.npz`.
- For any bearing, the same-season rates at a level are fixed by construction: 0.3, 0.1 or 0.05 × 65.5 windows per hour. The information is in the sector, clock-window and day-to-day results.

**Bearing.**

- Cross-correlation of the band-passed elements at the time of the window maximum: a 6-s segment for 5-40 Hz, 10 s for 2-8 Hz.
- Parabolic sub-sample lag, corrected for fractional sample offsets.
- Least-squares plane wave on the three pairs. A synthetic test recovers bearing to 0.003° and speed to 1.48 km/s.
- "Coherent": minimum CC ≥ 0.3, |lag closure| ≤ 0.02 s, apparent speed 1.3-1.9 km/s.

**H01W array calibration** ([h01w-array-calibration.json]({{artifact:076cefbe-3cb6-4831-8495-2149f256d05a}})).

- Problem: against catalogue T-phases the raw H01W bearings were biased by a median of +5.2° (robust SD 2.5°), and the apparent speed depended on azimuth (1.35-1.61 km/s). A timing-only model did not remove the bias.
- Fit: a 7-parameter model (scale/speed, two timing offsets, two horizontal position offsets), fitted robustly to 41 catalogue-matched events, one per event, CC ≥ 0.5, azimuths 120.7-343.8°, two iterations.
- Result: leave-one-out residual median −0.04°, robust SD 0.66°, maximum 6.4°. Fitted element offsets are about 180 m (element 2) and 400 m (element 3); they are absorbed jointly with timing and scale and are not a survey result.
- H08S on the FDSN geometry: residual median −0.2°, robust SD 1.3° (108 events, CC ≥ 0.5). Not corrected.

**Sectors** ([bearing-sectors.csv]({{artifact:dbaf8a48-93ea-4a79-99be-ce0c045ddeb4}})).

- WGS84 geodesic azimuths from the FDSN triplet centroid to the official FL400 7th-arc line.
- 20-40 S: H01W 248.9-327.9°, H08S 114.9-163.5°.
- The earlier "248-298°" covers only the southern part. Its rates are reported separately (H01W screen 0.096/h in the window).
- Antarctic sector (55-66 S, 30-150 E): H01W 140.3-224.4°, H08S 144.8-207.3°. At H08S this overlaps the arc sector at 144.8-163.5°.

### 3.4 Features and rough classes

Features at each window maximum:

- SNR: 1-s power, peak within ±3 s over the median of the preceding 60 s.
- Duration: the time above +3 dB.
- Peak excess frequency over 2-100 Hz, 6 s against the preceding 60 s.
- Envelope periodicity: autocorrelation of the detrended log envelope over ±300 s, interior peak at 5-15 s and at 40-200 s, with its prominence.

The periodicity rule: within each (station, day, UTC hour, statistic), the modal lag bin must hold at least 30 % of windows; a window counts as periodic if its prominence is at least 0.3 and its lag is near the mode. The fixed 0.15 prominence threshold first tried was at the noise median and was replaced by this rule before any rate was computed.

Classes, in this order:

1. catalogue T-phase;
2. periodic 5-15 s (airgun train or fin whale);
3. periodic 40-200 s (whale song or other repeating source);
4. Antarctic sector (ice likely);
5. Antarctic and arc sectors overlap;
6. T-phase-like (duration ≥ 20 s, peak frequency < 15 Hz);
7. bearing not resolved;
8. unknown.

Bearing-only likelihood ratio (exploratory, a label only): impact bearing uniform over the arc sector with a 2° Gaussian error, divided by the smoothed empirical bearing density at that station.

### 3.5 Catalogue association

- Catalogues: USGS ComCat (box 75 S-30 N, 15-180 E, M ≥ 2.5; plus global M ≥ 5.0) and the ISC Bulletin (same box), 28 Feb-31 Mar 2015-2019. Merged with a 60 s / 150 km rule; M ≥ 3.0 kept (12,063 events, [catalogue-events-march-2015-2019-m3.csv]({{artifact:6940f49f-ba3c-4b0c-a5e2-de4cdf9d9e27}})).
- Predicted arrival: geodesic distance / 1.48 km/s. A match needs |Δt| ≤ 120 s and |Δbearing| ≤ 15°.
- Control, with catalogue times shifted by ±600 s and ±1,200 s ([catalogue-association-control.csv]({{artifact:9ebb7e7c-e9b1-4db6-a944-1151751b04b4}})):
  - H01W: 139 matches against 13-24 by chance, so most H01W matches are real.
  - H08S: 672 matches against 290-387 by chance, so about half are chance.

## 4. Standing caveats

These figures are not a rejection, upper limit or Bayes factor. Any later use of them in one carries the two standing caveats:

1. The propagation model fails the frequency-slope check against the 2001 airguns (+10 dB/octave at H01W, +7 dB/octave at H08S), although the levels pass.
2. Detection probability is a proxy unless it is measured on real data.

Wording for any later use: "no significant detection with limited power".

## 5. Files

**Tables**

- [ims-open-availability.csv]({{artifact:648befdb-52d8-49c7-8e23-00b209984bf2}}): the probe map (Feb-Apr 2015-2019 and selected 2010-2014 and 2020-2025 dates, 9 elements) plus the hours downloaded per element-day.
- [ims-march-noise-percentiles.csv]({{artifact:5934eb83-a597-4e84-b6e2-68eb0b60e8b2}}): 1-Hz PSD, third-octave and 5-40 Hz percentiles, by source, station, element and subset (window, block, rest of day, hour).
- [ims-march-noise-vs-references.csv]({{artifact:59ff8cbc-7e16-452a-9072-65ea9adc2d5f}}): dB differences from Blackman 2003 and from the stand-in.
- [ims-march-detections.csv]({{artifact:06cb7199-6852-4efd-b6b4-dc12bb1ea67f}}): all windows with p < 0.1 (24,159 rows). Each row has rank, p (same-season and stand-in), SNR, bearing-only likelihood ratio, bearing, speed, CC, duration, peak frequency, periodicity, class and catalogue match.
- [ims-march-detections-screen-level.csv.gz]({{artifact:c8a699a1-95c5-4220-9180-060c478b2eeb}}): the same columns for all windows with p < 0.3.
- [ims-march-false-alarm-rates.csv]({{artifact:da30fe9e-42df-4120-a725-af8b348d18fd}}): rates by station, statistic, p basis, level, time subset and bearing condition. Each row has the day-bootstrap and Poisson 90 % intervals, daily 5/50/95 %, per-year rates and the p floor.
- [processed-coverage.csv]({{artifact:3a84ca01-81c6-4e19-97d5-598d28c476c8}}): station-days processed per year.

**Derived products and code**

- [ims-march-derived-products.zip]({{artifact:118db893-a961-4b66-bbe2-e435da80adb8}}): per station-day per-minute noise arrays (`*_noise.npz`) and per-window statistics and features (`*_windows.pkl.gz`), with the download logs and the raw probe file.
- [ims-march-scripts.zip]({{artifact:41cd5ffd-1027-4ece-8356-ec08d6d29333}}): `probe_availability.py`, `sectors.py`, `ims_proc.py`, `m1b_bank.py`, `run_days.py`, `catalogues.py`, `array_cal.py`, `analyse.py` and `figures.py`.
- Inputs read from the module branch `hypothesis/hydroacoustics` at d88d48e (read-only): `results-data/blackman_noise/*`, `prepare/searches_run_j/{detectors,preregistration}.py` and `registry/REGISTRY.json` (D05, D06, D26). Inputs read from ~/Downloads/mh370-exchange: `run-j-weak-signal/templates/templates_raw.npz` (sha256 59a8798b…) and `run-j-searches/null/null_3376.npz` (sha256 0bd6bdc1…).
