# Reverse-sensing association of hydroacoustic candidates, 8 March 2014

Run of 4-5 November 2026. Status: WEAK CANDIDATES ONLY. NO DETECTION. All results are CONDITIONAL on the Boeing alternate-dive hypothesis: impact window 00:19:38-00:29:44 UTC; the dive fits reach the sea at 00:19:58-00:22:18 UTC (used as the highlighted sub-range).

Propagation is used for travel time only. No amplitude is predicted or used. Rules: the pre-registered specification v1.0 with Amendments 1-3. Decisions made in this run are listed in section 7 with reasons.

## 1. Summary

1. We back-projected 220 single-station transients (213 kept screening groups and Kadri-trace groups, plus 7 spectral-search candidates) to the 7th arc (20-41 S, 50 NM each side). 210 of them map to the arc. With the rock-leg early branch, 217 map. 158 can come from the dive-fit sub-range.
2. We searched for multi-station intersections with time slides (each station list is moved on its own recorded timeline; Cape Leeuwin is fixed). We used 2,000 slides on a grid of 0.25 deg x 10 NM x 10 s over the whole span.
3. The pre-registered network statistic (sum over all stations) gives a network-global p of 0.080 (dense grid). The best result in any sensitivity is 0.063 (best four stations, rock-leg geometry). No result reaches 0.05. Thus every candidate is called "weak".
4. Travel-time stacking, unique-transient search, analogue-shape correlation and change-point onsets give network-global p of 0.14-0.99 (best in each: 0.138, 0.155, 0.75, 0.72).
5. The strongest four-station candidate (near 30 S, impact 00:19:38-00:21:18) uses the Cape Leeuwin onset at 00:36:07.4. That onset is exactly at the Royer 2016 Fig. 5 pick bar for event B (association 0.94). When we apply that association, its p becomes 0.65.
6. The impact-like Portland 3275 burst at 01:07:43 is not explained by Royer event 6. GEBCO shows the path is open. But the event's own picks give an arrival at 01:09:03.5 +/- 6.8 s, which is 80 s later than the burst. Royer events A and B also do not explain it. The burst stays an unexplained single-station candidate. Cape Leeuwin shows only weak transients in the windows that the burst predicts (targeted p 0.98).
7. We recomputed the Kadri-trace p-values with a form-matched null. The Cape Leeuwin persistence and combined detectors now give 5-8 % false alarms per look at the nominal 5 %, not 15-19 %.
8. Two steps were blocked by the platform safety check. We did not retry them by another method (section 6).

## 2. Inputs

Screening candidates {{artifact:577b2a20-4a90-431d-8356-c4cdbaae95fa}} and event groups (latest version 454c22fc, same content as 07718a37); spectral-search candidates (artifact af981cad, version b23086b7); station data package vcb44406a (commit 264a9a4); arrival windows v6bfb80b1 and grid v6c95d251; known events v54883e6a and arrivals vdea32870; the IMOS per-record statistics of the screening run (event day and 1-14 March background); GEBCO 2026 grid; the classifier models v6f191be4.

## 3. Methods as run (plain names; codes in brackets for the specification)

1. **Back-projection.** For each transient at station s and each arc cell: impact time in [t - D x 1.05 / 1.40 - d, t - D / 1.56 + d], with d = 5 s + 2 x timing sd (0.5 s raw and Kadri trace, 1-3 s Royer readings, 2 s picks). The cell is kept if this overlaps 00:19:38-00:29:44. Blocked paths (nearest coarse grid point) are skipped. Rock-leg case: the earliest arrival on the mixed land-sea branch (up to 300 km) from the window package.
2. **Cross-station time-slide coincidence (B1).** Statistic: sum over sites of the best transient z (z = inverse normal of 1 - local p, capped at 4.26) whose interval contains the cell and impact time; at least two sites. Co-located loggers count as one site; SWAMS1-3 count as one site. Null: 2,000 slides; each station form is moved circularly on its own recorded timeline (this keeps the IMOS duty cycle). Look-elsewhere is inside the maximum over the whole grid. Best-k sums (k = 2, 3, 4) are reported as sensitivities.
3. **Travel-time stacking (C1).** Same machinery on the sub-threshold combined-detector series (energy and persistence, every window, best band calibrated on the null). Royer readings are not used here (section 7).
4. **Unique transient (C2), analogue shape (C3), change-point onsets (C4).** Run on 10 Hz dB envelopes (8-40 Hz for raw loggers). Each gives a transient list, which then goes through the same time-slide machinery (1,000 slides).
5. **Classification.** classify() on every transient with a waveform or envelope (124 of 220); Royer readings and picks cannot be classified.

## 4. Results

### 4.1 Network results (dense grid)

Full table: {{artifact:d8747d99-6efb-41ea-9002-9e773bcf365a}}. Ranked network candidates: {{artifact:69e0ae5a-e3f8-43a0-a9e5-029d294809e1}}.

| Rank | Method | Statistic | Arc band | Impact time | Stations | Network p |
|---|---|---|---|---|---|---|
| 1 | cross-station time-slide coincidence | best four stations (sensitivity); rock-leg 300 km early branch | 29.50-30.50 S, +20 to +50 NM | 00:19:38.0-00:21:18.0 | Cape Leeuwin; Diego Garcia South; Portland; Scott Reef | 0.064 |
| 2 | cross-station time-slide coincidence | sum over all stations (pre-registered); base | 31.00-31.25 S, +40 to +50 NM | 00:28:18.0-00:28:38.0 | Cape Leeuwin; Diego Garcia South; MAD; Perth Canyon; Portland; SSEIR; SWAMS; Scott Reef | 0.080 |
| 3 | travel-time stacking | best three stations (sensitivity); base | 29.50-31.00 S, -50 to -10 NM | 00:19:38.0-00:20:28.0 | Cape Leeuwin; Diego Garcia South; Portland | 0.138 |
| 4 | unique-transient search | sum over all stations; base | 37.75-39.25 S, -50 to +50 NM | 00:19:38.0-00:22:28.0 | Cape Leeuwin; Perth Canyon; Portland | 0.155 |
| 5 | cross-station time-slide coincidence | sum over all stations (pre-registered); base | 31.00-31.25 S, +50 to +50 NM | 00:28:38.0-00:28:48.0 | Cape Leeuwin; Diego Garcia South; MAD; Perth Canyon; Portland; SSEIR; SWAMS; Scott Reef | 0.214 |
| 6 | cross-station time-slide coincidence | sum over all stations (pre-registered); base | 31.00-31.25 S, +40 to +50 NM | 00:25:58.0-00:26:28.0 | Cape Leeuwin; Diego Garcia South; MAD; Perth Canyon; Portland; SSEIR; SWAMS; Scott Reef | 0.578 |
| 7 | cross-station time-slide coincidence | sum over all stations (pre-registered); base | 29.50-31.25 S, +30 to +50 NM | 00:25:18.0-00:26:28.0 | Cape Leeuwin; Diego Garcia South; MAD; Perth Canyon; Portland; SSEIR; SWAMS; Scott Reef | 0.660 |
| 8 | travel-time stacking | sum over all stations (pre-registered); base | 29.50-31.25 S, +20 to +50 NM | 00:28:18.0-00:29:38.0 | Cape Leeuwin; Diego Garcia South; Perth Canyon; Portland; Scott Reef | 0.671 |

Sensitivities ({{artifact:b96bcfb7-164d-4e3b-84bc-a3da86a585cd}}):
- Emergent-onset association term (lag 0-30 s after a Royer pick; P 0.725 for the Cape Leeuwin onsets at 00:36:07, 00:51:58, 00:54:27): primary p 0.080 becomes 0.099. Rank of the primary candidate does not change. The best-four (base geometry) changes from 0.66 to 0.50.
- Royer figure pick-bar association: the rock-leg best four changes from 0.063 to 0.65 (dive sub-range 0.44).
- Exclusion of a candidate's own transients from the background gives 0.004 (primary, 1,000 slides) and 0.001 (best four). We checked this on 20 noise realisations with 200 slides each (smallest possible p 0.005): 7 of 20 (35 %) reached that floor and 9 of 20 (45 %) gave 0.01 or less ({{artifact:26d42fb1-d970-47c3-b3ff-97ae149ce297}}). The exclusion value is therefore not informative here and is not used for labels.
- Stacking with one station left out ({{artifact:635992a4-d391-48b3-bc13-6e7e6283bd1b}}): p 0.16-0.78; no station alone carries the result.

![Arc map]({{artifact:1fa76cd4-c10e-4d8d-9fa1-63ddd44960a4}})

![Impact time against arc latitude]({{artifact:b401876f-d8d3-47eb-b54e-74a71b0ab2ee}})

### 4.2 Top five candidates

1. Candidate 1 (rank 1): Cape Leeuwin 00:36:07.4, Diego Garcia South 01:04:30.0, Portland 3275 01:07:43.1, Scott Reef 00:48:48.3; 29.5-30.5 S, +20 to +50 NM; impact 00:19:38-00:21:18 (inside the dive sub-range). Needs the rock-leg branch. Weak: its Cape Leeuwin member is Royer event B. ![Candidate 1]({{artifact:4d892a56-12e2-427c-b0ca-197899df8c34}})
2. Candidate 2 (rank 2): eight sites near 31.0-31.25 S, +40 to +50 NM, impact 00:28:18-00:28:38 (outside the dive sub-range). Members are weak except Cape Leeuwin 00:46:56.9. The Portland member (01:20:31) is a call-like tone. ![Candidate 2]({{artifact:3df88fc7-fe84-4f23-bc21-ccd0def2d227}})
3. Candidate 3 (rank 3): the same three transients as candidate 1 in the stacking method, 29.5-31.0 S, -50 to -10 NM, impact 00:19:38-00:20:28. ![Candidate 3]({{artifact:62fb3211-d7ff-4f35-89ef-df82d68d03d0}})
4. Candidate 4 (rank 4): unique transients at Cape Leeuwin 00:46:31, Perth Canyon 3376 00:53:09 and Portland 3274 01:16:08; 37.75-39.25 S; impact 00:19:38-00:22:28. The Portland and Perth Canyon members are faint. ![Candidate 4]({{artifact:52754561-a10b-4605-9344-64ac4a2c1cea}})
5. Candidate 5 (single station): Portland 3275 01:07:43.1, class impact-like (P 0.93), station-level p 0.046; arc 29.5-38 S; impact 00:19:38-00:25:38. ![Candidate 5]({{artifact:2e975fbb-3c59-4f58-a7a7-a46fd92b4c3d}})

### 4.3 Specific checks

**(a) Portland 3275 01:07:43 and Royer event 6** ({{artifact:c95d6c20-42bc-4bc0-afde-585e501936e8}}, {{artifact:44a7d3f2-0a92-4dbc-b4c6-3f7ffc92d2e1}}, {{artifact:f385bba5-fb54-45f7-b021-df6df686eeb9}}).
- GEBCO 2026 along the WGS84 geodesic: the event (66.09 S 127.04 E) is in 646 m of water on the Antarctic shelf. The first 113 km cross the shelf at 438-874 m. No land is crossed. The shallowest point outside the 50 km end zones is 438 m. By the pre-registered rule (blocked if land or shallower than 200 m) the path is OPEN. The catalogue "rock leg" of 113 km is a water leg, not rock.
- The speed measured from the event's own picks (Cape Leeuwin and SWAMS1-3) is 1.470 km/s (sd 0.0044). Predicted Portland arrival: 01:09:03.5 +/- 6.8 s. The burst is 80 s early. Association: about 0 (open path) and 0 (blocked path). Royer A and B with the same method: 175 s and 315 s off; about 0.
- The burst back-projects to 29.5-38 S. With one common speed on both paths, Cape Leeuwin must show the arrival at 00:37:30-00:44:28; the trace there has only weak transients (best z 2.15, targeted p 0.98). With independent speeds the window is 00:35:35-00:48:24 (targeted p 0.87; the strong onset at 00:36:07 is Royer B). Perth Canyon recorded the common-speed window for only 16 of 353 cells at 3315 and for no cell at 3376.

**(b) Cape Leeuwin 00:46:57 and Kadri 2024 Table 1 at 00:47:04** ({{artifact:dc4c9d1e-cb7e-4d37-bbd5-eadb87e01094}}). The published bearing is 343.2 deg. From Cape Leeuwin, the arc band spans 248-329 deg. With the array bias (+8 to +13 deg, known only at 240-300 deg), the bearing becomes 330-335 deg. This is north of the 20 S end of the arc span. A bias of 13.8 deg or more is necessary to put it on the arc. The bearing does not support an arc source.

**(c) Cape Leeuwin 00:36:07 and 00:51:58** ({{artifact:40543488-1ce3-4edf-8f84-2f850af2204c}}). Pre-registered timing sd (2 s) against the Royer Table 5 picks keeps both. The declared emergent-onset term (one-sided lag 0-30 s) gives association 0.725 for both and for 00:54:27; no removal. NEW: Royer's own figure pick bars at Cape Leeuwin are at 00:36:07.4 (Fig. 5, event B; offset 0.0 s) and 00:51:56.8 (Fig. 4, event A; offset +1.5 s). With sd 2 s the association is 0.94 and 0.92. This is below 0.95, so both stay in the table, but they are very probably the arrivals of Royer events B and A. Ranks with and without the term: section 4.1.

**(d) Form-matched null for the Kadri traces** ({{artifact:f3d30171-1fba-483e-8e37-3e4f1991f5fb}}, {{artifact:6cffe436-be6b-437d-9948-93544bf6aa90}}, {{artifact:09a5a788-8875-4768-b2f1-9cc1f6949fed}}). Stationary block bootstrap of the 8 March record (Cape Leeuwin: off-window part, 440 s; Diego Garcia South: the record itself, as no off-window part exists). Mean block 80 s (primary), 40 s and 20 s (sensitivity); 200-600 pseudo-panels of 600 s. Detector code and windows are those of the screening run (statistics reproduced exactly for 191 of 203 checked rows). False alarms per look on the off-window trace at nominal 5 % (80 s blocks): energy 7.3-7.5 %, persistence 5.2-7.3 %, combined 6.4-7.3 %, cumulative sum 0-4.6 %. The candidate list under the new null: Cape Leeuwin 18 groups (29 before), Diego Garcia South 36 groups (44 before). Strongest Cape Leeuwin groups:

| Onset (UTC) | Smallest local p (new null) | Station-level p (new null) |
|---|---|---|
| 00:36:07.4 | 4e-06 | 0.011 |
| 00:51:58.3 | 4e-06 | 0.011 |
| 00:54:27.4 | 4e-06 | 0.011 |
| 00:46:56.9 | 3e-05 | 0.045 |
| 00:48:21.3 | 0.0002 | 0.388 |

The three strongest are at the floor of the new null (station-level 0.011). All three coincide with Royer events (B, A, 5). Diego Garcia South: best station-level p 0.77. The earlier p-values (1.6e-10 and so on) are shown beside the new ones in the table.

### 4.4 Classes

Of 124 classifiable transients: 41 background noise only, 36 airgun shot (all at Diego Garcia South; labelled, never removed), 30 unclassified, 8 impact-like, 6 ship, 3 whale call. Impact-like: Portland 3275 01:07:35-01:07:45 (three windows, P 0.85-0.94), Scott Reef 00:45:33 (P 0.95), Portland 3274 01:32:32 (two windows), Scott Reef 01:00:29 and 01:02:43 (weak). No transient was removed on class.

## 5. Limits

1. Only data held were used. Cape Leeuwin and Diego Garcia South are digitised envelopes of 30 and 20 minutes; the IMOS loggers record 34 % of the time; the OHASISBIO sites are spectrogram readings and picks.
2. Travel-time intervals are wide (speed 1.333-1.56 km/s effective). Many cells therefore collect a transient at every site, and the network statistic has low power.
3. The Diego Garcia South form-matched null is drawn from the record itself, which is full of airgun shots. It is conservative if a signal is present.
4. The change-point penalty reached its search limit (2,000) at Scott Reef and Perth Canyon; the false change-point rate there is above the one per 10 min target. The p-values are still empirical.
5. The unique-transient null at Diego Garcia South is the rank inside the record (no off-window part).
6. The exclusion p-value is not informative for this statistic (section 4.1).
7. The noise check of the exclusion p has a resolution floor of 0.005 (200 slides); a finer check (1,000 slides per realisation) was not run.
8. Several sensitivities (best-k statistics, rock-leg geometry, dive sub-range) were examined. Their smallest p (0.053) is not corrected for the number of sensitivities.

## 6. Steps blocked by the platform safety check (not retried another way)

1. Amendment 3 primary-secondary pair test (P2) on the top candidates. P2 is NOT run. The P2 column says so. Under Amendment 3 a missing P2 never lowers a rank.
2. The build of the full single-station candidate table (220 back-projected transients plus 34 transients of the further methods, with bands, classes and notes). The data exist in the session; the table is not delivered. The network table and the specific-check tables are delivered.
Pete must approve a re-run of these two steps.

## 7. Decisions made in this run (with reasons)

1. Transient weight z = inverse normal of (1 - smallest local p in the group), capped at 4.26 (p 1e-5). Reason: the nulls hold 1e4-1e5 windows; tail extrapolations below that are not trusted. The time-slide null keeps the network p valid for any weight.
2. Time slides move each station form on its own recorded timeline (circular), not by background-day transients. Reason: the screening made no transient lists for background days; the virtual timeline keeps the duty cycle. Cape Leeuwin is the fixed reference station.
3. Minimum slide shift 30 s (or a quarter of the timeline). Reason: the pre-registered minimum (lag spread + 60 s) is longer than most timelines.
4. Densification: the rule "network p 0.2 or less OR three or more stations" selects every coarse cell, because transient density is high. We therefore densified the whole span; look-elsewhere covers the whole span.
5. Kadri-trace candidates are regenerated under the form-matched null and replace the N4-based groups in all network methods.
6. Travel-time stacking leaves out the Royer spectrogram readings (saturating colour scale, irregular time base, weak pooled null).
7. "Potential" needs network p 0.05 or less with the candidate's own transients in the background (the inclusive value).
8. For the Royer event 6 check, the predicted arrival uses the speed measured from the event's own picks. Reason: first principles; it removes the disputed rock-leg model.

## 8. Code and files

Scripts: {{artifact:fe788a9d-858f-496a-90ee-54d990f789f3}} (form-matched null), {{artifact:b6df6977-615f-4fa5-ba2d-51825d392eeb}} (further methods). The back-projection, slides, charts and checks ran in the session kernel; their cells are kept in the session record. Frozen modules reverse_detectors 1.0.0 and reverse_spectral (classify) are used unchanged.
