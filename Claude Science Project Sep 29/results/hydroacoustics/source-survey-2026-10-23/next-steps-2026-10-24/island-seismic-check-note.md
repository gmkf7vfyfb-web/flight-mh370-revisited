# Island and coastal seismometers as an independent public check, and Royer's located events as a labelled set

Hydroacoustics module, exploratory track. 24 October 2026.
Status: EXPLORATORY. Nothing in this note returns a likelihood to the composer. No impact duration is inferred from any received signal.

## 0. Deviations and limits (read first)

1. **Stations not reached.** MR.MRIV (Mauritius) and S1.AUCAR (Carnarvon) return no data for 6–10 March 2014 at EarthScope, GEOFON or RESIF. GE.HMDM (Maldives, north) returns no data. No Rodrigues alternative was needed, because G.ROCAM returned HHZ from RESIF. The EPOSFR alias was not live, so I used the RESIF name.
2. **Sampling rate limits the band.** The GE stations have no HHZ archived for 2014, so I used BHZ at 20 sps. At 20 sps only the 2–8 Hz band can run. The 3–12 Hz band runs only at the 40–100 sps stations: II.COCO, II.DGAR, II.MSEY, II.PALK, AU.XMIS, AU.XMI, AU.GIRL, IU.NWAO, IU.MBWA, G.ROCAM, PF.RER and S1.AUALB. 100 sps data were decimated to 50 sps.
3. **Gaps and substitutions.** PF.RER has 4 of 5 days (6 March is missing). IU.NWAO 10.HHZ was 99.4 % gaps, so I replaced it with 10.BHZ (40 sps). II.DGAR uses location 10 (40 sps), not the held location 00 (20 sps). The held 12-hour zip was superseded by fresh 5-day downloads, 6–10 March 2014, 00:00–24:00 UTC.
4. **Response: scalar sensitivity, not full deconvolution.** A full StationXML deconvolution moved the time base of six GE stations by −47 to −49 s. The stations are GE.CISI, JAGI, KAAM, MMRI, MNAI and SOEI; their metadata are from GEOFON, and the FIR phase is the likely cause. All other stations moved by 0.1 s or less ([fullresponse_time_shift_check.csv]({{artifact:503f5fe5-c044-456e-b41b-c2d36ec9be37}})). I found this on Royer event 16. All detections were then re-run with scalar sensitivity. Peak frequency comes from a signal/pre-noise spectral ratio, so the response cancels. RMS velocities (nm/s) are scalar approximations.
5. **T window is a priori, not calibrated per station.** The per-station T offset could not be calibrated. Only 22 first-pass matches were clean, and their spread was set by chance matches (1.4826 × MAD = 123 s). The final rule is therefore offset 0 s and ±150 s, about 3.3 × the 46 s SD of the 1.48 km/s rule against IDC T arrivals. The calibration table is kept only as a diagnostic ([station_T_calibration.csv]({{artifact:8cc6a821-6168-4ffe-84ef-49a448871d94}})).
6. **Catalogue scope.** Earthquakes come from the known-events table (region box 6–10 March, plus global M ≥ 4 or IDC-located events from 7 Mar 12:00 to 8 Mar 06:00). I added 82 USGS global M ≥ 4.5 events (5 Mar 12:00 – 11 Mar) that were not already in the table. Magnitude types are mixed (mb, mb1, MLv, ML, MS, Mw).
7. **Arc and latitude limit.** I used the project's 7th-arc definition from `registry/data_db/arc_line_of_sight.py`: a small circle, centre 0.570 N 64.252 E, radius 44.501°, fitted to the 00:19:29 positions. I did not check it against a separately defined sea-level arc. The arc is sampled at 0.5° from 20 S to 40 S. I did not locate the 99th-percentile prior contour, so latitudes north of 20 S are not covered.
8. **Bathymetry and path rule.** I used GEBCO_2026 15″ from Pete's Downloads folder (read only), not ETOPO via ERDDAP. The classes are those of the project screen (blocked, large attenuation, clear), and the screen is geometric only. The water/land conversion point is the first point deeper than 1,000 m, counted from the station, and the seismic leg is taken at 6 km/s. The land leg is not penalised, so inland stations (IU.MBWA, IU.NWAO, AU.GIRL) count as "clear" with long land legs.
9. **Horizontals not used.** No polarisation back-azimuths were measured. Direction comes only from the Réunion array test (section 1, finding 6).
10. **The event-16 relocation is simple.** It uses 4 stations (7 picks), iasp91 and no station corrections. The uncertainty box is the formal Δχ² ≤ 4 region at the best depth.
11. **Réunion network.** The PF/G network was downloaded only for 01:20–01:35 UTC, 8 March.
12. **No likelihood ratio.** I computed none, because there is no signal amplitude model for island stations. The column says this.
13. **Background bias.** Background windows had only catalogue sources removed; no Royer-type located set exists for them. They therefore hold more unexplained transients than the 8 March window, so the p-values are conservative (biased high).
14. **Not saved.** The raw waveforms (606 MB) and the 1-s SNR series (53 MB) were not saved as artifacts. Scripts 01, 01b, 01c and 03 regenerate them.
15. **CMST time.** The H08S detection "00:11–00:12" was entered as 00:11:24 UTC (0.19 h).
16. **Conflict rule and detection-level counts.** The conflict rule prefers the claim with the lowest p_chance. That favours P/S claims, because their windows are narrow, and it can mis-assign: II.DGAR 2014-03-10 14:00:45 goes to a Fiji P although a Java T fits. The detection-level counts are pair-level: a pair counts as "seen" when its T window holds a detection at p_chance < 0.05, whatever the assignment. The shifted-time control is treated the same way.

## 1. Main findings

All counts and values below come from the saved tables. They rest on the a priori ±150 s window and on scalar-response detections. The impact-window results are exploratory.

1. **What the island stations can see.** I ran an STA/LTA detector over 5 days at 24 island and coastal seismometers. It gave 20,484 detections (13,887 in 2–8 Hz; 6,597 in 3–12 Hz). Of these, 1,522 are assigned to a known source (781 P, 333 S, 408 T).
2. **T phases are real but the stations have low sensitivity.** Real predicted times give 437 T matches at coincidence probability < 0.05. Predicted times shifted by ±25 and ±50 min give 358.5 per shift. As a control on clock and method, P matches are 637 against 341.5.
3. **Empirical detection level** (open path, distance > 600 km, p_chance < 0.05; [detection levels]({{artifact:58341fe1-96c0-479b-8b66-4143bc04d0d8}})):

   | Magnitude | Distance | T seen | Shifted-time control rate |
   |---|---|---|---|
   | M ≥ 4.5 | 600–1,500 km | 14 of 16 | 0.06 |
   | M ≥ 4.5 | 1,500–3,000 km | 2 of 18 | 0.03 |
   | M ≥ 4.5 | > 3,000 km | 4 of 53 | 0.05 |

   For M < 4.5 the seen rates do not differ from the control. The rule of thumb is that island seismometers see T phases from about M 4.5 within about 1,500 km. The longest-range example is II.DGAR, which recorded an arrival matching the T phase of the Java mb 4.7 (EV162) at 4,055 km: SNR 13.1, residual +11 s, p_chance 0.0007. This one is ambiguous. The same detection matches the P of a Fiji mb 4.9 (depth 302 km) at 11,662 km with residual −7 s, and the conflict rule assigns it to that P (deviation 16). The arc is 900–3,000 km from Cocos and Christmas Island and 3,000–4,500 km from Diego Garcia. At those ranges these stations would see only a source with the T-phase energy of an earthquake of about M 4.5 or larger.
4. **Royer event 16 is a real earthquake, confirmed seismically.** Royer gives it as Java, 01:15:48.0, 8.052 S 107.622 E, and it is not in any public catalogue. GE.CISI (65 km), GE.UGM (292 km), AU.XMIS (356 km) and AU.XMI (351 km) record clear P and S. The relocation is 8.14 S 107.88 E, best depth 35 km, origin 01:15:23.05 UTC, χ² = 2.58 for 7 picks, with P residuals of 0.4 s or less. That is 30 km east-south-east of Royer's position (25–36 km over the Δχ² ≤ 4 box) and 24.9 s earlier than Royer's origin. Royer's formal errors (0.067° × 0.024°, 4.7 s) are smaller than these differences. A sound-based origin marks when sound enters the water, so a later time is expected; the size of the difference is not tested here. This is an independent public check, and it **supports** event 16 as a real earthquake near Royer's position ([Fig. 3]({{artifact:bd1ff318-5cb2-479d-b059-78e422bbeb73}})).
5. **The CMST H08S detection at 01:58:55 from 93° is explained by Royer event 16.** From the seismic hypocentre, the predicted H08S arrival is 01:59:19.8 (observed − predicted −24.8 s), at back-azimuth 93.3° on a clear path. From Royer's origin the prediction is 01:59:25.7 (−30.8 s). This replaces the catalogue track's "unresolved" status for that detection.
6. **The other 19 Royer events are not tested with useful power.** For events 1–15 and 17–20 there were 308 open-path island pairs. Five matches are assigned at p_chance < 0.05, against 15 expected by chance. No significant detection with limited power; this is not evidence against Royer's locations.
   - Events B (35.224 S 99.922 E), D1 and D2 lie on or near the arc corridor. Their largest island SNR in the T window is 3.17 at Cocos and 3.13 at Diego Garcia for B, and 2.67 at Cocos for D1/D2. All are at chance level.
   - C2/C3 (26.5 S 81.0 E) has the strongest isolated match: G.RER and PF.RER at 01:26:14, SNR 18.4 and 11.3, p_chance 0.001, residual −48 s. That one arrival serves both C2 and C3. A Réunion network test (33 stations) shows the summit stations are not earlier than the coastal stations (mean lag +2.2 s against +1.4 s). That argues against a summit volcanic source. The back-azimuth is not resolved, however (bootstrap 95 % range 57–260°, against 108° expected for C2). Weak support only.
7. **CMST detections along their bearings (exploratory).** I scanned each bearing every 10 km from 50 to 6,000 km. H01W 01:34:50 (301.6°), H08S 00:11:24 (168.05°) and H01W 04:59:21 (210.2°) give **zero** ranges where two or more stations agree on unexplained arrivals. Shifted-time controls give 23, 60.5 and 9 such ranges on average. H08S 01:58:55 (93°) and H01W 05:14:28 (208.5°) each give one contiguous cluster (23 and 37 ranges), against control means of 7.5 and 10.75 and a control maximum of 17 and 43. Each cluster pairs unrelated arrivals: a GE.PLAI local transient (SNR 39.7) with a marginal IU.NWAO match, and an AU.GIRL arrival 341 s off with II.DGAR/G.ROCAM arrivals at 06:10. The island stations add no support to any CMST detection beyond the known sources ([summary]({{artifact:ac694836-7a4c-4d10-bbd8-a7e30d17dd44}})).
8. **Impact windows: no significant detection with limited power (exploratory).** I tested 23 stations with open paths from the arc (GE.MMRI has none) in 46 station-windows, with impact 00:15–01:05 and tail 01:05–02:00. That gave 312 unexplained detections: 302 below screen, 6 at screen (p ≤ 0.3), 3 at mark (p ≤ 0.1) and 1 at report (p ≤ 0.05). Background windows number 73–121 per station; the p floor is 0.008–0.014.
   - The one report-level candidate is AU.XMI at 00:57:41, SNR 19.6, p = 0.0127 (at the p floor). It is a spike of about 10,000 nm/s lasting about 2 s. The co-located AU.XMIS, 5.2 km away, stays at SNR ≤ 1.12. It is a local or instrumental transient, not an ocean arrival.
   - Both mark-level XMI candidates (00:32:25, SNR 9.0; 01:05:06, SNR 7.9) also fail the partner check.
   - The remaining mark is II.COCO 02:13:02 (tail window), SNR 4.9, p = 0.062, peak frequency 18 Hz. No second Cocos sensor was archived for 2014.
   - The screen-level candidates are II.DGAR 02:11:10 (SNR 4.2, p = 0.170; seen on both DGAR sensors, 2–8 Hz SNR 2.40 and 2.26), II.MSEY 01:44:30 (p = 0.116), G.ROCAM 02:43:52 (p = 0.130) and GE.PLAI 01:59:49 and 02:24:18 (p = 0.256, 0.135, 0.270).
   - Across 46 windows about 2.3 window-level p ≤ 0.05 results are expected by chance; 1 was observed, and it fails the partner check. [Fig. 4]({{artifact:5876ed85-71ff-4bf2-afef-1aca2a38f308}}).
9. **Royer labelled set built.** [royer-events-labelled-set.csv]({{artifact:5e1deaae-9dd2-4279-8994-29772ef4f0ea}}) has 840 rows: 20 events × 42 receivers. The receivers are H01W, H08S, H08N, the five IMOS loggers, Royer's 7 OHASISBIO sites, the H01W1–3 elements and 24 seismometers. Each row carries source class, path class and predicted arrival, plus Royer's observed arrival where Royer lists one. Against Royer's 143 listed arrivals, the 1.48 km/s geodesic rule gives observed − predicted median −3.1 s, SD 8.6 s, range −22.2 to +24.7 s. The set is ready for the module as real-arrival calibration events.

## 2. Royer 2016 Table 4 events: island check summary

From [royer-events-island-check-summary.csv]({{artifact:680f3215-aacb-4343-b274-faa38af1795d}}). Predicted arrivals use Royer's location and origin at 1.48 km/s. "Open" is the number of island stations with a clear or large-attenuation path.

| # | label | class | lat, lon | origin (UTC) | pred H01W | pred H08S (path) | open | island result |
|---|---|---|---|---|---|---|---|---|
| 1 | | icequake | −55.400, 88.173 | 23:47:46.2 | 00:21:50 | 00:49:26 (clear) | 20 | not tested with useful power |
| 2 | | uncertain | −64.510, 127.048 | 00:13:09.3 | 00:51:32 | 01:38:49 (blocked) | 0 | no open path |
| 3 | A | icequake | −57.300, 88.965 | 00:16:29.4 | 00:51:40 | 01:20:35 (clear) | 20 | not tested with useful power |
| 4 | B | uncertain | −35.224, 99.922 | 00:21:30.6 | 00:36:07 | 01:08:10 (clear) | 22 | not tested with useful power |
| 5 | | uncertain | −49.755, 133.114 | 00:28:51.5 | 00:54:19 | 01:50:48 (large att.) | 12 | not tested with useful power |
| 6 | | uncertain | −66.090, 127.043 | 00:32:49.2 | 01:13:03 | 01:59:28 (blocked) | 0 | no open path |
| 7 | C1 | uncertain | −3.445, 74.087 | 00:33:43.5 | 01:34:33 | 00:39:19 (clear) | 17 | not tested with useful power |
| 8 | | uncertain | −60.844, 78.097 | 00:36:21.8 | 01:19:48 | 01:43:03 (blocked) | 0 | no open path |
| 9 | | uncertain | −48.671, 97.477 | 00:37:52.4 | 01:01:01 | 01:35:31 (clear) | 20 | not tested with useful power |
| 10 | | icequake | −57.967, 92.050 | 00:56:45.5 | 01:31:03 | 02:02:26 (clear) | 19 | not tested with useful power |
| 11 | C2 | uncertain | −26.469, 80.952 | 00:57:32.4 | 01:34:40 | 01:23:05 (clear) | 21 | isolated match at Réunion (weak) |
| 12 | C3 | uncertain | −26.539, 80.979 | 00:57:33.5 | 01:34:38 | 01:23:12 (clear) | 21 | same Réunion arrival as C2 |
| 13 | C4 | uncertain | −55.719, 87.615 | 00:59:55.3 | 01:34:33 | 02:01:50 (clear) | 20 | not tested with useful power |
| 14 | D1 | uncertain | −25.404, 93.567 | 01:04:39.1 | 01:29:51 | 01:38:12 (clear) | 20 | not tested with useful power |
| 15 | D2 | uncertain | −27.856, 93.460 | 01:06:05.4 | 01:29:52 | 01:41:30 (clear) | 22 | not tested with useful power |
| 16 | | earthquake | −8.052, 107.622 | 01:15:48.0 | 01:50:06 | 01:59:26 (clear) | 16 | **supported: seismic P/S, 30 km, −24.9 s** |
| 17 | | icequake | −57.950, 95.354 | 01:37:39.5 | 02:10:32 | 02:44:18 (clear) | 19 | not tested with useful power |
| 18 | | icequake | −52.635, 80.389 | 01:49:33.0 | 02:26:49 | 02:46:19 (clear) | 19 | not tested with useful power |
| 19 | | icequake | −51.322, 117.339 | 01:58:14.2 | 02:19:00 | 03:09:42 (clear) | 15 | isolated match, not significant |
| 20 | | earthquake | −27.149, 67.307 | 02:02:31.7 | 02:53:21 | 02:27:37 (clear) | 21 | isolated match, not significant |

"Not tested with useful power" means no island T at p_chance < 0.05 on the open paths: no significant detection with limited power. Given the empirical level (finding 3), these non-detections place only weak limits on event size.

## 3. Method

1. **Data.** I downloaded vertical channels for 6–10 March 2014 from FDSN (EarthScope, GEOFON, RESIF), together with StationXML. The 24 stations are II.COCO, II.DGAR, AU.XMIS, AU.XMI, G.AIS, G.PAF, G.CRZF, G.ROCAM, G.RER, PF.RER, II.MSEY, GE.KAAM, II.PALK, GE.MNAI, GE.CISI, GE.UGM, GE.JAGI, GE.PLAI, GE.SOEI, GE.MMRI, S1.AUALB, AU.GIRL, IU.NWAO and IU.MBWA.
2. **Detector** (`detect.py`). The steps are:
   - divide by scalar sensitivity, then decimate to 40–50 sps or less;
   - band-pass (Butterworth, 4 poles, zero phase) at 2–8 Hz, and at 3–12 Hz where fs ≥ 40;
   - take a 1-s RMS envelope;
   - STA = mean energy over 10 s; LTA = median energy over the 600 s ending 20 s before the STA window; SNR = √(STA/LTA);
   - trigger on at SNR ≥ 2.0, off below 1.4, minimum duration 8 s, merge gaps of 10 s or less.

   Each detection records onset, end, duration, peak time, peak SNR, peak frequency (peak of the signal/pre-noise Welch ratio, 1 Hz to 0.9 Nyquist), band RMS and a high/low-frequency ratio.
3. **Predictions** (`02_predict.py`, `geom.py`).
   - T: WGS84 geodesic; GEBCO class on the water leg; water leg at 1.48 km/s plus land leg at 6 km/s.
   - P and S: TauP iasp91, for catalogue earthquakes and the relocated event 16 only.
   - Hydrophones: geodesic at 1.48 km/s.
4. **Association** (`04_associate.py`, `05_tables.py`).
   - Windows: T ±150 s, P −10/+20 s, S −20/+40 s.
   - Coincidence probability p_chance = 1 − exp(−rate(SNR ≥ matched) × window). The rate comes from the station's own 5-day list in the same band.
   - A detection claimed by several sources goes to the lowest p_chance, then P/S before T, then the smallest residual.
   - Event 16 is represented by its seismic relocation. An assignment carries over to the overlapping detection in the other band.
   - Control: the same association with all predictions shifted by ±1,500 s and ±3,000 s.
5. **Detection level.** Seen fraction against the shifted-time control rate, binned by magnitude and distance, for open paths beyond 600 km.
6. **Event-16 relocation** (`06_roy16_relocate.py`). AIC picks in windows set by eye. Grid search at 0.02° over depths 5–70 km. Weights 0.5 s for P and 2 s for S.
7. **Impact windows** (`10_impact_windows.py`).
   - Window = impact window + the minimum to maximum travel time over open-path arc points, ±150 s.
   - Candidates are unassigned merged detections.
   - p = (1 + number of background windows whose maximum unexplained SNR ≥ the candidate's) / (n + 1), with background windows tiled over 6–10 March, excluding 7 Mar 23:00 – 8 Mar 04:00.
   - Screen 0.3, mark 0.1, report 0.05. Rank is by SNR within the window.
   - Co-located partner check for XMI/XMIS and G.RER/PF.RER.
8. **CMST bearing scan** (`09_cmst_scan.py`). The source is placed along each bearing (50–6,000 km, in water deeper than 200 m) and island arrivals are predicted. I counted ranges where two or more stations agree on unexplained detections, against shifted-time controls.

## 4. Standing caveats (apply to every rejection, upper limit and non-detection here)

1. The project propagation model fails the frequency-slope check against the 2001 airguns (+10 dB/octave at H01W, +7 dB/octave at H08S), although the levels pass. This note uses only travel times and geometric path classes, not that model's levels.
2. Detection probability is a proxy unless measured on real data. Here the level is measured on real catalogued earthquakes at these stations. Its transfer to an aircraft-impact source (spectrum, duration, coupling) is not measured. For impacts it remains a proxy.

Wording throughout: "no significant detection with limited power", never "absence of signal".

## 5. Files

Tables:
- [island-seismic-detections.csv]({{artifact:b5bbb22d-15d8-40e2-864b-2ea7161a9c79}}) — 20,484 detections, with assignment and competing claims.
- [island-seismic-associations.csv]({{artifact:70e0a47c-95b3-4d08-b968-64aaa9c9eb94}}) — 6,648 event × station rows (T, P, S).
- [royer-events-labelled-set.csv]({{artifact:5e1deaae-9dd2-4279-8994-29772ef4f0ea}}) — 840 rows; summary in [royer-events-island-check-summary.csv]({{artifact:680f3215-aacb-4343-b274-faa38af1795d}}).
- [island-impact-window-unexplained.csv]({{artifact:4ea60c55-82b9-444a-985d-182c20f60c7c}}) — 312 candidates, with rank, p, p floor, SNR, level, partner check, and the LR column marked "not computed".
- [island-impact-windows.csv]({{artifact:cc8a4401-945f-4cca-b1fa-8a4360c91c72}}) — 46 station-windows plus one no-path row.
- [island-impact-arc-paths.csv]({{artifact:87231983-178a-48d0-a15e-9f5aebd36806}}) — 984 station × arc-point paths.
- [island-seismic-detection-levels.csv]({{artifact:58341fe1-96c0-479b-8b66-4143bc04d0d8}}).
- [island-seismic-cmst-summary.csv]({{artifact:ac694836-7a4c-4d10-bbd8-a7e30d17dd44}}) and [island-seismic-cmst-bearing-scan.csv]({{artifact:0a4b81ca-2112-4ff8-b22e-8d7990a10f37}}).

Figures:
- [Fig. 1, map]({{artifact:847c0c69-045b-444f-a263-a9dfa9bd8f3d}})
- [Fig. 2, detection level]({{artifact:cc601eec-3c89-4179-bc7f-dc657752e9c3}})
- [Fig. 3, Royer event 16]({{artifact:bd1ff318-5cb2-479d-b059-78e422bbeb73}})
- [Fig. 4, impact windows]({{artifact:5876ed85-71ff-4bf2-afef-1aca2a38f308}})

Auxiliary data:
- [stations.csv]({{artifact:feba4ae4-7d93-4f3b-b611-db3d02c82b91}})
- [events_all.csv]({{artifact:f1296512-27ae-47b9-a3c3-4bf0e38671c3}})
- [pred_arrivals.csv]({{artifact:bec08bcf-6e50-4cda-8414-beac81da0cfc}})
- [roy16_relocation.json]({{artifact:16e2856a-a0a7-4189-a6ec-98ff5e9d871f}})
- [reunion_array.json]({{artifact:836af34b-cda6-4a99-af98-55e569cc5f16}}) and [reunion_array_lags.csv]({{artifact:6e7b435a-0faf-4a5e-95e9-5bfbc37a7743}})
- [second_sensor_check.csv]({{artifact:5e49de7c-63bb-4312-a4f5-ab1673ef48f2}})
- [fullresponse_time_shift_check.csv]({{artifact:503f5fe5-c044-456e-b41b-c2d36ec9be37}})
- [download_log.txt]({{artifact:3720857c-7af7-494a-83c9-ab4e4b760628}})
- [USGS M ≥ 4.5 list]({{artifact:1b3d4bb6-b628-4af0-8349-1923fe66b24d}})

Scripts (run in order, env `mh370-hydro`):
- [geom.py]({{artifact:e306fb7e-e553-4451-b04f-2b80490d581d}})
- [detect.py]({{artifact:66fb56ff-7dab-40d6-92be-5587bd39139b}})
- [01_download.py]({{artifact:97bc9719-11dd-48c9-8d5b-efcf9ba4b5d8}}), [01b]({{artifact:b9d8829f-c650-43e9-ab21-32fb05679fa3}}), [01c]({{artifact:446d9bf5-4f76-4b06-855d-1f5779a8ee56}})
- [02_predict.py]({{artifact:4202e16b-afe3-4445-98ad-c04a3217d29b}})
- [03_run_detect.py]({{artifact:bcf6df9c-c848-4a10-a51c-746dab2d7225}})
- [06_roy16_relocate.py]({{artifact:7a02932d-bb7e-4600-8882-e1c841e50078}})
- [02b_add_roy16_seismic.py]({{artifact:142f23d0-b695-40da-9517-7f182ce85447}})
- [04_associate.py]({{artifact:64a27ada-5db6-408a-bf4c-f3f5c0207f6d}})
- [05_tables.py]({{artifact:766338a5-5807-4ffa-ad30-a2fe82295660}})
- [07_reunion_array.py]({{artifact:26b48d05-5fe2-4104-8214-c4aacebdc51d}})
- [08_royer_set.py]({{artifact:84419723-65ac-48a7-aba7-5deb5694c685}})
- [09_cmst_scan.py]({{artifact:721e9d8c-5e1d-4615-b94f-abcbf6f4bf9b}})
- [10_impact_windows.py]({{artifact:c00eb688-d15d-4214-9901-1f8ebb59c648}})
- [11_figures.py]({{artifact:cbf20113-7886-444d-b4d5-db70ec42d435}})

Inputs used:
- hydro_data.sqlite v6d525329. The Royer and site tables are identical to v7a31618e, which only adds `arc_path`.
- known-events-6-10mar2014.csv vdf0f8673.
- Royer 2016 LDO PDF: Table 4 checked against the database table.
- GEBCO_2026 grid (Downloads, read only).
