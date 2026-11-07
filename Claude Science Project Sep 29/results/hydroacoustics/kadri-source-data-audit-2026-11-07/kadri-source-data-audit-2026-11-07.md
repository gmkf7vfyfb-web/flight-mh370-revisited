# Kadri source data: what we hold, what the 8 March run used, what is not yet used

Date: 7 Nov 2026. Scope: every Kadri document held by the project, checked page by page against the digitised tables in hydro_data.sqlite and against the input of the combined-detector run on the 8 March 2014 data (6 Nov). Tables: `kadri-source-data-inventory.csv` (19 items) and `kadri2017_atsb_fig3_h01w_detections.csv` (27 detections, new).

Documents checked:
- Kadri (2024) Sci. Rep. 14:10102, with Supplementary S1.
- Kadri et al. (2017) Sci. Rep. 7:13949.
- Kadri (2019) Sci. Rep. 9:912.
- Kadri, Crivelli and Parsons (2017), "Analysis of data revisited: inverse problem approach", the report to the ATSB dated 8 Feb 2017.
- The SnT 2025 poster P1.4-254.

Two files were opened and excluded: "Usama Kadri Sep 11.pdf", which is the project's own presentation, and "ctbto.pdf", which is the CTBTO IDC infrasound report, not Kadri material.

## 1. What the run used: complete

- **Kadri 2024 Fig. 9 pressure traces.** All five panels, 44,051 vertices. This matches the database count exactly.
  - Cape Leeuwin: 00:27–00:57 UTC.
  - Diego Garcia South: 01:00–01:20 UTC.
  - The run's looks cover 00:27:15–00:56:45 and 01:00:15–01:19:40. Each end loses only half a 30-s window.
- **Kadri 2024 Table 1.** All 19 Cape Leeuwin transients, used as seeds. Their bearings are now corrected under ruling B1 (thread rerun, commit ca4eb652).

## 2. Kadri data held or published but not used

1. **Diego Garcia South, 00:00–02:00 UTC (Kadri 2019, Fig. 4).**
   - Content: hour panels with the pressure trace, the cross-correlation level and a bearing-versus-time image. Panel "12.00 UTC" is 00:00–01:00 and "1.00 UTC" is 01:00–02:00; the paper uses 12-hour labels, as its Table 3 notes confirm.
   - Status: not digitised.
   - Why it matters: Figure 9 covers Diego Garcia South only from 01:00 to 01:20. Arrivals from impacts between 00:19:38 and 00:55:00 reach Diego Garcia South between 00:56:34 and 01:42:18 UTC (primary sound speed, unblocked grid points within 150 NM). So 00:56–01:00 and 01:20–01:42 have not been tested.
   - Limits: the figure is a raster at about 20 s per pixel in time and 0.8° per pixel in bearing, with no colour scale. It gives an envelope and directions only, not absolute level.
2. **Figure 9 spectrograms (Kadri 2024).**
   - Content: all five panels have a spectrogram beside the trace. Cape Leeuwin is 0–40 Hz; Diego Garcia South is 0–60 Hz and 0–40 Hz; the colour scale is 70–110 dB re 1 µPa²/Hz.
   - Resolution: about 0.8 s and 0.15 Hz per pixel, JPEG-compressed.
   - Status: the colours were read once, for noise level only. That reading is about 15 dB low and is flagged.
   - Use: a relative spectral-shape check at candidate times. No detection run has used these spectrograms.
3. **Cape Leeuwin detection list, 00:00–02:00 UTC (report to the ATSB, Fig. 3).**
   - Content: 27 labelled detections, each with a minute and a bearing. The text is vector, so the values are exact.
   - Status: extracted now; it was not in the database before.
   - 15 detections fall inside the span in which an arc impact could arrive (00:33–01:33 UTC, widest speed bounds). None points into the arc sector, with or without the array correction.
   - The one arc-sector bearing (01:35, 301.4°) is Kadri's 2017 candidate E1. It arrives after the latest possible arrival.
4. **Scott Reef picks (report to the ATSB, Fig. 6).**
   - Content: three picks in records the project holds.
   - On the corrected time base the picks are at 00:48:49, 01:16:34 and 01:32:51 UTC.
   - Kadri's titles use logger time, which is 15.1 s late against corrected UTC. The database applies each logger's measured clock error.
   - The run tested the first two as its own seeds. The third was never tested.
5. **Diego Garcia South, 7 March 17:49–19:10 UTC (Kadri 2024, Fig. S1 a–c).**
   - Status: digitised but unused.
   - Use: it is the same station, the same day and the same plot form as Figure 9d–e. It can serve as an independent background for the Diego Garcia South null. The 6 Nov run built that null from the 8 March trace itself.
6. **Diego Garcia South shot-train directions (Kadri 2019, Fig. 1).**
   - Content: 309° from 23:00 to 03:10 UTC and 219° from 23:10 to 02:10 UTC.
   - Status: not digitised.
   - Use: labelling the airgun shots.
7. **Kadri 2017 candidates E1 and E2.**
   - Status: digitised but unused as seeds.
   - E2 (00:50:00, 234.6°) is in effect Table 1 00:49:41 (234.67°).
   - E1 (01:34:40, 301.4°) lies outside the impact window of the pre-registration.

## 3. The 2017 and 2024 Cape Leeuwin lists differ

- The two analyses use the same Cape Leeuwin data, but their detection lists for 00:38–00:56 differ.
  - Only one detection matches: 00:50 at 234.6° (2017) against 00:49:41 at 234.67° (2024).
  - In minute 00:54 the 2017 list gives 29.6°. The 2024 list gives 306.18° at 00:54:30.
  - In minutes 00:47, 00:48 and 00:52 the 2017 bearings (149.7°, 205.2°, 190.6°) are far from the 2024 bearings in the same minutes.
- The 2017 list has minute resolution, so detections in the same minute may be different arrivals. The 2024 table may also be restricted to bearings towards the arc.
- Our check does not reconcile the two lists. The cause is not known; it can be our error.
- The 2017 minute 00:52 (190.6°) coincides with Royer's marks at 00:51:57–00:51:59. This may give a direction for that onset, but minute resolution cannot confirm the match.

## 4. Spectrograms in the Kadri documents, by period

| Document | Station | Period | Frequency range |
|---|---|---|---|
| Kadri 2024 Fig. 9 | Cape Leeuwin | 8 Mar 00:27–00:57 | 0–40 Hz |
| Kadri 2024 Fig. 9 | Diego Garcia South | 8 Mar 01:00–01:20 | 0–60 / 0–40 Hz |
| Kadri 2024 Fig. S1 | Diego Garcia South, Wake | 7 Mar 17:49–19:51 | 0–40 Hz |
| Report to ATSB Fig. 6 | Scott Reef | 8 Mar, three 307-s records | 0–100 Hz (raw held) |
| Kadri 2017 Fig. 7 | Cape Leeuwin | 7 Mar, one event | — |

Kadri 2019 Fig. 4 holds bearing-versus-time images, not frequency spectrograms.

## 5. Next steps (each under 1.5 h of clock time)

1. Digitise Kadri 2019 Fig. 4. Score Diego Garcia South 00:56–01:00 and 01:20–01:42, and the arc direction at Diego Garcia South (about 1–1.5 h).
2. Rebuild the Diego Garcia South envelope null from Fig. S1 a–c and re-score (about 0.5 h).
3. Add the 27 detections and the shot-train directions to hydro_data.sqlite as labels (about 0.5 h).
4. Test the third Scott Reef pick (01:32:51) at the other sites (about 0.3 h).
5. Read the Figure 9 spectrogram rasters as relative spectra at the candidate times (about 1 h).
