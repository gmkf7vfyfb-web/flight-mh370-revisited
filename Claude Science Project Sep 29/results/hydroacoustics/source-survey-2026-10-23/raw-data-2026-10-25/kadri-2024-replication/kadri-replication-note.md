# Replication of Kadri (2024) aircraft-crash panels on raw IMS data, and reconciliation (track 4)

Hydroacoustics module, 25 Oct 2026. Pre-registered windows and statistics: {{artifact:0e9cad65-8030-4b8a-8f04-6528e5abbbfd}} (saved before any waveform was downloaded).
Parts marked EXPLORATORY or POST-HOC were not pre-registered. No MH370 quantity is inferred from anything here. No coupling value is derived in this track (no energy or transmission-loss inversion), so no `db_coupling_value.csv` rows are written.

## Deviations and limits (read first)
1. **Citation.** The paper is *Sci. Rep.* **14:10102** (2024), doi 10.1038/s41598-024-60529-1 (not 14:10178; checked in the repo text and PMC copy).
2. **AirAsia 8501, H01W:** open EarthScope data cover only 2014-12-27 22:00:00 – 2014-12-28 00:00:00 UTC (probes: 204 at 21:00, 00:05, 00:30, 02:00, 06:00, 12:00 on 28 Dec; 200 from 29 Dec). The pre-registered water window (00:02:58–00:06:28) is **not testable**; the last minute of Kadri's panel (00:00–00:01) is missing.
3. **AB Aviation 1103:** no official accident report found; impact time 09:30–09:40 UTC from ASN/press (12:30/12:40 EAT); position from Kadri S1 (not verified).
4. **Transair 810:** ditching position from Wikipedia (NTSB final-report coordinates not read); time 11:45:18 ± 60 s from the NTSB docket (ADS-B end 11:45:17.902; 'about 0145 HST').
5. **F-35A:** impact time 10:26:30 UTC from Kadri S1 / JASDF and position from the module working point (Metz 2023); not re-verified (track 1 owns F-35A).
6. **Processing deviation (declared):** the pre-registered 5 % cosine taper (and obspy's default 5 % response-removal taper) damped up to 6 min at the end of the 2-h H01W record and 18 min at the ends of 6-h records; both were capped at 30 s and the edge exclusion widened from 20 s to 60 s; 1-sample chunk-join holes are interpolated instead of zero-filled (zero fill made spikes). Results after the fix differ from the first run by ≤ 0.04 in p except QZ8501 H01W Kadri box (p 0.109 → 0.047, because the box lay inside the damped end).
7. **D1 STA/LTA** is computed on the triad-mean energy (module definition STA 2 s / LTA 30 s otherwise unchanged). **M1b matched filter not run** (its template bank is built for the MH370 ranges; not adapted). **Likelihood ratios not defined** (no calibrated per-case signal model).
8. **Reproduction figure** uses the single element with the highest zero-lag envelope correlation (display choice, not pre-registered).
9. **Bearings at H08S (SJ182, Jan 2021):** elements H08S1/H08S2 are 15–20 dB noisier than H08S3 at 2–20 Hz; triad bearing unreliable. AB1103 box: element delays incoherent; no bearing.
10. **Kadri's panel boxes, traces and levels** are digitised from the publisher's full-resolution PNGs (≈0.78 s/px; trace clipped at the frame). Kadri's Lion Air 904, Yemenia, AF447, Asiana panels are pre-2015 (no open data) and not in scope.
11. Three script artifacts (cases.py, geometry.py, water_route.py) were saved as version 2 of existing same-name project artifacts (likely another track's); earlier versions are retained.

## 1. What Kadri reports (quoted)
Methods: "a high pass Butterworth IIR filter was used (in addition to the CTBTO high pass filter) below 5 Hz. Moreover, a 2–40 [Hz] band-pass filter was applied in general." Panels: "Signals from past aircraft crashes were presented around the middle of a 10 min time window". S1 speed range (MH370 section): "an average speed between 1,450 m/s and 1,570 m/s".
For the crash panels Kadri gives **no numeric signal time, amplitude or bearing**; the claim is the box in each figure. Per case (full quotes in {{artifact:41d9a266-fbed-4cb9-ac7e-4f8e9bd84c42}}, column `kadri_claim`):
* **F-35A** (Fig. 4a; H11N after 10:58, H11S after 10:59): "a distinctive, sharp, and rapid (6 s) signal following the supersonic impact"; S1 impact "10:26:30 UTC", "about 3, 340 km".
* **Sriwijaya 182** (Fig. 4c; H08S after 08:06): "the signal of interest is sharp and clear"; S1 "07:40 UTC", range "4, 694 km" — Fig. 2 map gives "3,772 km, 89.32°".
* **Transair 810** (Fig. 5b; H11N after 12:28, H11S after 12:27): "there appears to be a double signal, potentially indicating a ditching event, an engine that was detached, or signal arrival from different locations"; S1 "around 11:46 UTC".
* **AB Aviation 1103** (Fig. 6a; H08S after 09:36): Fig. 6 "signal dispersion is most pronounced"; S1 "around 09:30 UTC"; Fig. 2 "3,186 km, 258.47°".
* **AirAsia 8501** (Fig. 6b; H01W only, after 23:51): "distorted with noise (possibly due to airgun shots ...), and the magnitude of the pressure induced by the aircraft crash is not clear"; S1 "December 28, 2014 ... around 07:37 UTC"; Fig. 2 "3,523 km, 351.52°".
Digitised box limits (min after panel start): F-35A H11N 4.26–5.69, H11S 4.38–5.81; SJ182 4.58–6.01; TA810 H11N 4.24–5.68, H11S 4.20–5.65; AB1103 4.62–6.09; QZ8501 4.10–5.73 ({{artifact:ef2da099-bf3b-4d6f-9b5d-ebcc9bbb3a6f}}); agree with the project's earlier 669-px reads within 0.06 min.

## 2. Impact times and positions (primary sources) vs Kadri
* QZ8501: KNKT final report "The last data recorded by FDR was at 2320:35 UTC" (27 Dec), radio altitude 118 ft. The project table's "2014-12-28 ~07:37" (from Kadri S1) is **not supported**; Kadri's own panel (23:51) implies he used a ~23:2x time. Kadri's S1 position is 286.6 km from the KNKT site; his Fig. 2 range (3,523 km) is close to our KNKT-site range (3,492.1 km).
* SJ182: KNKT "At 07:40:28 UTC, the FDR stopped recording"; last FDR coordinate 5°57'56.21"S 106°34'24.86"E. Kadri's S1 coordinate is 60.6 km east of this and 11.0 km from the Lion Air 610 first-debris point; his S1 range 4,694 km equals his Fig. 2 Lion Air 904 range (4,695 km) to within 1 km; his Fig. 2 range 3,772 km matches our 3,771.9 km. None of these moves the predicted arrival by more than ~40 s.
* JT610: KNKT "DFDR stopped recording at 23:31:54" (28 Oct 2018).
* TA810: NTSB "about 0145 HST" (11:45 UTC); S1 position 13.2 km from ours.
* F-35A: S1 position is 64.0 km from Misawa, the module point 134.8 km (Metz/Kadri text say ~135 km); range difference 50 km (34 s).

## 3. Method (pre-registered; {{artifact:0e9cad65-8030-4b8a-8f04-6528e5abbbfd}})
Raw data: IM.EDH, all three elements, impact −2 h to +4 h, EarthScope dataselect ({{artifact:46ed83df-a1ea-4f20-8a66-27239d3de795}}); StationXML responses (1,839–1,871 counts/Pa at 10 Hz). Processing K = response removal to Pa, Butterworth HP 5 Hz + BP 2–40 Hz (order 4, zero-phase). Statistic: triad-mean 1-s RMS maximum per window; p from same-length non-overlapping windows in the 6-h record with exclusions; SNR against panel and day medians; D1 STA/LTA; plane-wave back-azimuth from 3 element pairs (validated on the F-35A: 323.7° / 325.8° vs geodesic 320.8° / 322.3°, apparent speed 1.45 km/s, closure ≤ 0.002 s).
Predictions ({{artifact:c776ab57-73d2-44dc-a88b-4af7b03dbea0}}, {{artifact:2f804617-6500-4806-8620-d42104814fc0}}, {{artifact:a29958dd-60a5-43f7-bdf7-5be5587b8cd0}}): WGS84 geodesic from the triad centroid; GEBCO 2026 profile every 1 km; shortest all-water route on a 0.05° grid (deepest cell per block, so permissive) for minimum depths 1–1,000 m. **Water paths:** F-35A and Transair geodesics are clear (Transair shallow only within 16 km of the source). AB1103: geodesic crosses Anjouan and the Saya de Malha bank; a ≥1,000 m route exists (+168.7 km). **Java Sea cases (SJ182, JT610, QZ8501): no route exists at ≥50 m depth**; routes exist only through 30–44 m bottlenecks (SJ182 via the Sunda Strait shelf, 199 km < 200 m; JT610 257 km < 200 m; QZ8501→H01W via the Bali Strait and the WA margin, +399.5 km, 1,601 km < 200 m; QZ8501→H08S 647 km < 200 m). For 5–20 Hz such water is below the first-mode cut-off for typical seabeds, so these are effectively land/shelf-coupled paths; we therefore also pre-registered a crustal envelope (shallow part at 3–8 km/s).

## 4. Results
![Raw recordings reproduce Kadri's Pacific panels]({{artifact:d0653932-94f4-418e-9897-f777016608af}})
![Raw recordings reproduce two of three Indian Ocean panels]({{artifact:16d85475-c7ec-46bd-919f-e7c64f5a4d34}})
![Timelines with pre-registered windows]({{artifact:75882a56-a33b-4c88-8651-be693939586b}})

| Case | Station | Kadri box (UTC) | Reproduction of printed panel | Our signal in Kadri box (peak, 1-s RMS, SNR day, p, back-azimuth) | Expected back-azimuth | Our pre-registered windows | Consistent with crash site? |
|---|---|---|---|---|---|---|---|
| F35A | H11N | 11:02:15-11:03:41 | time and shape match (r 0.76, +1.6 s); level −8.1 dB | 11:03:05, 0.246 Pa, SNR 15.0 dB, p 0.021, 324° | 321° | water p 0.03 | Yes |
| F35A | H11S | 11:03:22-11:04:48 | time and shape match (r 0.71, +1.6 s); level −8.1 dB | 11:04:07, 0.188 Pa, SNR 14.6 dB, p 0.017, 326° | 322° | water p 0.03 | Yes |
| TA810 | H11N | 12:32:14-12:33:40 | time and shape match (r 0.52, +0.8 s); level −7.0 dB | 12:32:56, 0.104 Pa, SNR 6.9 dB, p 0.350, 156° | 81° | water p 0.67 | No: +392 s late, from 156° |
| TA810 | H11S | 12:31:12-12:32:39 | time and shape match (r 0.53, +0.8 s); level −6.6 dB | 12:31:42, 0.122 Pa, SNR 9.0 dB, p 0.025, 153° | 79° | water p 0.67 | No: +288 s late, from 153° |
| SJ182 | H08S | 08:10:35-08:12:00 | time and shape match on element 3 (r 0.72, +0.8 s); level −4.2 dB | 08:11:20, 0.415 Pa, SNR 5.1 dB, p 0.349, 141° | 91° | water p 0.55; crustal p 0.54 | No: 742 s early; bearing unreliable |
| AB1103 | H08S | 09:40:37-09:42:05 | time and shape match (r 0.61, +2.4 s); level −4.0 dB | 09:41:10, 0.172 Pa, SNR 10.5 dB, p 0.028, 187° | 255° | water p 1.00 | No: 1,594 s early; no bearing |
| QZ8501 | H01W | 23:55:06-23:56:44 | not reproduced (r ≤ 0.13); boxed burst present | 23:55:43, 0.269 Pa, SNR 7.5 dB, p 0.047, 220° | 351° | water: not covered; crustal p 0.42 | No: from 220°; water window untestable |
| QZ8501 | H08S | — | no Kadri panel | — | 91° | water p 0.84; crustal p 0.89 | No claim; no significant detection with limited power |
| JT610 | H08S | — | no Kadri panel | — | 91° | water p 0.49; crustal p 0.46 | No claim; no significant detection with limited power |

p floors are 1/(n+1) = 0.004–0.06 per row (n in {{artifact:f0206674-f20c-4423-8612-f763af61a21b}}). Even the F-35A arrival (SNR 15 dB) ranks 5th–6th of 241 windows in its 6-h record (p 0.017–0.021): larger transients occur in the same day, so p ≈ 0.02 is close to the best this test can give for one impact.

### 4.1 Reproduction of Kadri's printed panels ({{artifact:81d34df0-13f4-4896-937a-04edba60c6ea}})
| Panel | Best element | Envelope r (best lag) | Lag (s) | r at 0 s | Median printed vs ours (dB) | Printed box peak (Pa) | Our box peak (Pa) |
|---|---|---|---|---|---|---|---|
| AB1103_H08S | H08S2 | 0.61 | +2.4 | 0.45 | -4.0 | 0.46 | 0.40 |
| F35A_H11N | H11N1 | 0.76 | +1.6 | 0.40 | -8.1 | 1.21 | 0.88 |
| F35A_H11S | H11S1 | 0.71 | +1.6 | 0.20 | -8.1 | 1.05 | 0.99 |
| QZ8501_H01W | H01W1 | 0.07 | -78.7 | 0.06 | -3.1 | 0.99 | 0.79 |
| SJ182_H08S | H08S3 | 0.72 | +0.8 | 0.55 | -4.2 | 1.04 | 1.08 |
| TA810_H11N | H11N2 | 0.53 | +0.8 | 0.49 | -7.0 | 0.50 | 0.28 |
| TA810_H11S | H11S2 | 0.53 | +0.8 | 0.50 | -6.6 | 0.47 | 0.38 |

Time base agrees within +0.8 to +2.4 s (best element) in six of seven panels. Under the pre-registered rule all six are 'partial' only because the printed level differs by more than ±3 dB. Kadri's printed noise floor is 3–8 dB above ours in every panel. EXPLORATORY diagnosis ({{artifact:2f683444-86b3-4379-a027-07330e74a7a2}}, {{artifact:64ea311a-ef21-4f2f-a806-473aca60355d}}): over the four matched panels, his stated chain gives mean r 0.53 and mean level -5.5 dB; a 4 Hz high-pass without the 40 Hz low-pass gives mean r 0.50 and -1.7 dB. His plotted trace is therefore consistent with the 40 Hz low-pass not being applied to the pressure plot (perhaps only to the 0–40 Hz spectrogram), or with a ~5 dB gain difference; our data cannot tell which. This does not change any timing or bearing result.
**AirAsia 8501:** at the labelled time the raw H01W envelope does not match the printed panel (r ≤ 0.13 at any lag within ±90 s, both filter phases); the printed panel's periodic impulses are absent at 23:51. A slide over the whole 2-h open record finds two near-equal best matches at 22:26:10 (r 0.44) and 23:09:22 (r 0.42) on all three elements (99th percentile 0.25–0.27) — not unique, so the printed panel's origin is unresolved ({{artifact:b76cedbe-0455-4fc7-806f-71e5e5aba2ca}}). The boxed burst itself is present in the raw data at 23:55:44.

### 4.2 Timing against Kadri's own speed range and against our model ({{artifact:cc09266b-3427-40cb-9cbd-594c1bf78a39}})
| Panel | Kadri box | Kadri's own 1.45–1.57 km/s window | Box inside? | Our box peak minus our water-path centre | Implied speed (km/s) | D13 (exploratory) |
|---|---|---|---|---|---|---|
| F35A_H11N | 11:02:15-11:03:41 | 11:01:57-11:04:53 | yes | +3 s | 1.480 | -2.0 |
| F35A_H11S | 11:03:22-11:04:48 | 11:01:57-11:04:53 | yes | +2 s | 1.481 | 3.0 |
| SJ182_H08S | 08:10:35-08:12:00 | 08:20:02-08:23:21 | no | -742 s | 2.076 | -706.0 |
| TA810_H11N | 12:32:14-12:33:40 | 12:24:56-12:28:09 | no | +392 s | 1.279 | 345.0 |
| TA810_H11S | 12:31:12-12:32:39 | 12:25:24-12:28:40 | no | +288 s | 1.329 | 255.0 |
| AB1103_H08S | 09:40:37-09:42:05 | 10:03:49-10:06:37 | no | -1594 s | 5.004 | not in D13 |
| QZ8501_H01W | 23:55:06-23:56:44 | 23:57:58-00:01:04 | no | -517 s | 1.845 | not in D13 |

### 4.3 Bearings (POST-HOC robustness, {{artifact:b829d53a-42ab-4f8c-8882-fe44d9a3ff34}}) and alternative sources (EXPLORATORY, {{artifact:b543fd63-7458-4055-b775-13ffd33ded15}})
Stable across 5–15, 15–40, 20–40 Hz and 20/60-s segments: F-35A 323.6–325.8°; TA810 H11S 151.7–152.7° (v_app 1.44 km/s, closure ≤ 0.04 s); QZ8501 H01W 219.8° (v_app 1.60 km/s). TA810 H11N 149.5–155.9° (5–15 Hz). SJ182 141–195° (unreliable; 15–40 Hz 171.8–174.8°). AB1103 incoherent. At TA810 H11S, 5 of the 20 loudest background transients in the 6-h record come from within 5° of 153°; at QZ8501 H01W, 3 of 20 within 5° of 220°. No catalogued USGS event (M ≥ 3.5, ≤ 12,000 km, −5 h) predicts a 1.482 km/s arrival within ±5 min of any box with a matching bearing (one Saipan M4.7 at −146 s for QZ8501 has back-azimuth 35.5°). Uncatalogued small events cannot be excluded.

## 5. Reconciliation (full table: {{artifact:41d9a266-fbed-4cb9-ac7e-4f8e9bd84c42}})
* **F-35A (H11N, H11S): reproduced and consistent.** Kadri's box contains the arrival; our raw-data peak is +3.3 s / +2.3 s from the 1.482 km/s prediction; bearing +2.9° / +3.5°; p 0.021 / 0.017.
* **Transair 810: panels reproduced in time; boxed signals not consistent with the ditching site under a sound-channel arrival.** H11S box transient is real (p 0.026, SNR 9.0 dB) but arrives +288 s late from 153° (Oahu bearing 79°); H11N box p 0.35, 156°. Our pre-registered water windows: no significant detection with limited power (p 0.67 both). Track 2 owns the full Transair analysis.
* **Sriwijaya 182: panel reproduced (element 3); boxed transient not consistent with the crash site under water or crustal-envelope paths.** It is 742 s before the water-route centre and outside Kadri's own 1.45–1.57 km/s window; not significant against the day (p 0.35); bearing unreliable. Predicted windows: no significant detection with limited power.
* **AB Aviation 1103: panel reproduced in time; boxed transient (p 0.028) not consistent with a water arrival from the crash under impact 09:30–09:40 UTC** (it is 1,594 s early; would need impact ~09:03–09:05 UTC). Water window: no significant detection with limited power (p 1.00).
* **AirAsia 8501 (H01W): printed panel not reproduced at its labelled time; boxed burst present (p 0.047) but from 219.8°, not 341–4°.** Water window not testable (no open data). H08S (not claimed by Kadri): no significant detection with limited power.
* **Lion Air 610 (out-of-sample, H08S): no significant detection with limited power** in water, crustal or wide-crustal windows (p 0.46–0.57).
Wording: these are 'not consistent with the crash site under assumption Y' or 'not reproduced'; they do not show that Kadri erred. Possible causes on both sides are listed per row in the CSV (e.g., ours: unmodelled crust/shelf paths, unverified AB1103 time and TA810 position, bearing bias at H11 of ~+3°, single-element display, permissive routing; Kadri's: a different source in the panel, panel timing or element, S1 transcription of times/ranges).

## 6. Change from the earlier exploratory check (registry D13)
D13 (straight path, one speed, S1 inputs) said "NOT evidence that Kadri's panel times are wrong". With raw data, primary times/positions and a path check: F-35A unchanged (−2/+3 → +3/+2 s). SJ182 persists (−706 → −742 s; a crustal path on the 238 km shallow part saves at most 2.2 min; the observed time would need ~1,260 km at 8 km/s). Transair persists and is firmer (+345/+255 s assumed → +392/+288 s measured, with bearings 156°/153° vs 81°/79°). AB1103 (−1,594 s) and QZ8501 H01W (−517 s vs water route; bearing 220°) are new. D13's label still applies in spirit: these remain 'not consistent under our path model', now pre-registered and on raw data, with the causes listed above unresolved.

## 7. Standing caveats
(1) The module propagation model failed the frequency-slope check against the 2001 airguns (+10 dB/octave at H01W, +7 at H08S) although levels passed. This track uses no transmission-loss model; its results neither change nor depend on that caveat. (2) Detection probability is a proxy unless measured on real data; none is measured here, so every non-detection is 'no significant detection with limited power'.

## 8. What would resolve the open rows
Official AB1103 report (impact time); NTSB ditching coordinates; full H01W data for 27–28 Dec 2014 and Kadri's element and plotting filter; an independent bearing at H08S (H08N not open for these dates) or IMS seismic stations; a modelled crust/shelf (T-phase) path from the Java Sea; injection-recovery on these records to measure detection probability.

## Scripts
{{artifact:3dfa8b7f-f68c-4971-987e-f50ac0b82c33}} cases.py · {{artifact:c80aa303-575f-4551-ad7b-b721c3e52e94}} geometry.py · {{artifact:b513ee39-67b3-4c50-b718-181b09a42fcd}} water_route.py · {{artifact:34a55a9d-ddc8-4a1c-a918-4d74cbc30662}} download.py · {{artifact:effa0ccf-72fc-46c7-9e67-5d61b0e8d135}} measure.py · {{artifact:0a5b5f9d-5fee-48af-bc52-d5db980e0bb5}} digitise_panels.py · {{artifact:343c1d8e-2310-43cf-ba6a-f044d988d288}} analyse.py · {{artifact:379beac3-6c8b-4ae9-bade-6c1553629cfc}} figures.py
