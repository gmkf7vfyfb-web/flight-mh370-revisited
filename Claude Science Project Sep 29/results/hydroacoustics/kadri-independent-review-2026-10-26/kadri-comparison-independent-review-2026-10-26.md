# Independent review: why our results differ from Kadri (2024), and whether the difference is defensible

Review date: 26 October 2026. Reviewer: a fresh session that did not write the replication tracks.
Scope: the comparison of Kadri, *Sci. Rep.* 14:10102 (2024), doi 10.1038/s41598-024-60529-1, Figs. 4–6, with open raw IMS hydrophone data for the five cases that have open data.
Material reviewed: the replication note, the pre-registration, the reconciliation tables, the wave-3 verifier report and errata, the F-35A raw-ridge note, Kadri's main text (PMC) and S1 text.
New checks (all POST-HOC, not pre-registered): station geometry rebuilt from EarthScope FDSN metadata, travel-time brackets that include Kadri's own land-crossing speeds, a test of arrival order between the two Wake triads, and the AB Aviation 1103 timeline. Script and tables are listed at the end.

Limit on independence: the reviewer is the same kind of model as the track authors, and it re-used the box times that the track digitised from Kadri's figures. The box times are checked indirectly, because the raw waveforms match Kadri's printed traces to within 0.8–2.4 s in six of seven panels.

## 1. Short answer

1. We cannot say for sure that the errors are in Kadri's work and not in ours. For some cases we can say something narrower that holds up.
2. The disagreement is not a calibration or time-base error on our side. Our raw data reproduce Kadri's printed traces in time (6 of 7 panels). They reproduce the F-35A arrival time, bearing and order between triads. Our absolute levels match Metz et al. (2023) to within 0.2–0.8 dB.
3. The differences come from one step: whether the boxed signal can be **attributed** to the crash. Kadri shows a transient near the expected time. We add three tests that his crash panels do not report: travel time, bearing, and rank against the same day's background.
4. Two cases pass a strict test. For Transair 810 and Sriwijaya 182, the boxed signals cannot be arrivals from the accident sites under any water path. The same holds under the land-crossing speeds that Kadri himself uses. AB Aviation 1103 is conditional on an unofficial impact time. For AirAsia 8501 the comparison is not valid, because the printed panel was not found in the open data.
5. One of our own claims is wrong in its current form. The "517 s early" timing argument for AirAsia 8501 does not hold under Kadri's land-crossing framework. Only the bearing argument is left, and it applies to a burst that may not be the one Kadri plotted.
6. "Kadri is wrong" is not defensible. "Kadri's boxed signals in Figs. 5b and 4c are not arrivals from those accident sites" is defensible for Transair 810 and Sriwijaya 182, with the stated assumptions. This finding concerns attribution in the crash panels only. It does not test his MH370 candidate (306°, 00:52–00:54 UTC).

## 2. Where the differences come from

| Possible source of the difference | Checked how | Result | Could it explain the disagreement? |
|---|---|---|---|
| Our time base or data differ from Kadri's | Raw envelope against Kadri's printed trace | Lag +0.8 to +2.4 s, r 0.52–0.76, in 6 of 7 panels | No. Same data, same clock |
| We read the boxes wrongly | Digitised at ≈0.78 s/px; boxes sit at 4.1–6.1 min of each 10-min panel, as Kadri states | Agrees with an earlier independent read within 0.06 min | No (error ≈1 s) |
| Station element positions (FDSN) | Rebuilt here; H11 bearing bias +3°, H01W +5° before calibration | Bias of 3–5° | No. Disagreements are 50–130° in bearing and 5–25 min in time |
| Our absolute pressure calibration | Raw F-35A against Metz (2023) digitised | +0.2 to +0.8 dB | No. Kadri prints about 5 dB higher in every panel. That is in his plotting chain and does not affect time or bearing |
| Our water-route lengths | Verifier erratum 2 | Routes 1–4 % too long. Offsets become −716 s (SJ182) and −1,510 s (AB1103) | Changes the numbers, not the conclusion |
| Our path model is narrower than Kadri's | **New check, section 3** | Kadri allows long land paths at 3.55 km/s. Our "crustal envelope" allowed crust only on the shallow part | Yes, for AirAsia 8501. No, for Sriwijaya 182 and AB 1103 |
| Impact time and position | Primary sources (KNKT, NTSB); press for AB 1103 | SJ182 and QZ8501 firm; TA810 firm in time; AB1103 unofficial | Yes, possibly, for AB 1103 only |
| We apply a speed window that Kadri did not apply to crash panels | Kadri gives 1.45–1.57 km/s in the MH370 section only. For the crash panels he gives no time, speed or bearing | This is our inference about his intent | It affects the wording, not the physics |
| Kadri's selection method | His text: panels "around the middle of a 10 min time window"; no bearing or background rank for the crash panels | The F-35A ranks only 5th–6th of 241 windows in its own 6-h record. Large transients are common | This is the most likely cause on Kadri's side. It is an inference, not a proven error |

## 3. New checks (post-hoc)

### 3.1 Travel-time brackets, including Kadri's own land-crossing speeds
Kadri (2024) proposes that signals cross land, and uses 3.55 km/s over about 1,900 km for the ARA San Juan path to H03S. Our replication tested water routes and a crustal envelope on the shallow part of each path only. I recomputed brackets on the WGS84 geodesic with ETOPO1 bathymetry. Every path segment shallower than a threshold (0, 200 or 1,000 m) is given a fast speed (3.55 km/s, or 8 km/s as an upper limit). The rest is given water speed (1.48 km/s, or Kadri's upper value 1.57 km/s). Full table: review_mixed_path.csv.

| Case | Range (km) | Kadri box (s after impact) | Water only, 1.57–1.45 km/s (s) | Most generous mixed path: 8 km/s where shallower than 1,000 m, 1.57 km/s elsewhere (s) | Box end minus most generous prediction | Fast-path length needed / available |
|---|---|---|---|---|---|---|
| Sriwijaya 182 → H08S | 3,772 | 1,807–1,892 | 2,402–2,601 | 2,283 | −391 s | 997 km needed at 8 km/s; 236 km shallower than 1,000 m exists |
| AB Aviation 1103 → H08S | 3,190 | 637–725 (impact 09:30) | 2,032–2,200 | 1,865 | −1,140 s | Not reachable even with the whole path at 3.55 km/s |
| AirAsia 8501 → H01W | 3,492 | 2,071–2,169 | 2,224–2,408 | 1,664 | +505 s (box is later than the earliest arrival) | 484 km needed at 3.55 km/s; 786 km shallower than 200 m exists |

Result: Sriwijaya 182 is too early by at least 6.5 min, even with an unrealistically generous path. To fit, about 1,000 km of a path that is mostly abyssal ocean would have to carry the signal at 8 km/s. AB Aviation 1103 cannot fit at any physically reasonable speed if the impact time is 09:30 UTC. For AirAsia 8501, a path through the Java Sea shelf and Java at Kadri's 3.55 km/s reaches H01W at about 2,051 s. That is just before the boxed burst. **The timing of the AirAsia 8501 burst is therefore consistent with Kadri's framework.** Our "−517 s" (against an all-water route through the Bali Strait) should not be used as evidence against him.

### 3.2 Arrival order between the two Wake triads (needs no processing of ours)
H11S lies 137 km south of H11N. A source at the Transair 810 ditching site (bearing about 80°) reaches H11N 29.8 s before H11S. Kadri's own boxes in Fig. 5b put H11S **first**, by 62 s. Our raw peaks put H11S first by 74 s. A plane wave from 152.6° predicts +74.5 s (verifier check T2). For the F-35A the same test agrees: predicted −62.6 s, Kadri's boxes −67 s, raw peaks −61 s.

This test uses only Kadri's box times and the station positions. It does not depend on our bearing code, impact time or speed. A position error in Mamala Bay changes the predicted value by less than 1 s. The two boxed signals in Fig. 5b therefore cannot be one water-borne wave from the ditching site. Kadri's own caveat ("signal arrival from different locations") remains open for a second source, but the bearing of both boxed pulses is 152–156°, not about 80°.

### 3.3 AB Aviation 1103 impact time
No official report was found. The operator's statement gives departure from Moroni at 11:50 local (UTC+3); one database gives 11:55. Last contact was about 12:30 local, 2.5 km from Mohéli airport (other press reports give 12:40). The hop is about 100 km. A Caravan could cover it in 20–25 min, so an impact near 12:05–12:10 local (09:05–09:10 UTC) is not physically impossible. That is the time the boxed signal needs for a water arrival. The AB 1103 result therefore depends on the press reports of last contact. It is the weakest of the three timing cases. Kadri himself calls AB 1103 "a small aeroplane" and puts it in his most uncertain class (Fig. 6).

## 4. Verdict per case

| Case | Our current wording | Does it hold? | What it depends on | Our possible errors | Defensible wording for the paper |
|---|---|---|---|---|---|
| F-35A (H11N, H11S) | Agrees | Yes | Nothing contentious | Bearing bias +3° (element coordinates) | Reproduced in time, bearing and triad order |
| Transair 810 (H11N, H11S) | Real sound; time and direction disagree | **Yes, strongly.** Three independent lines: bearing at two triads (verified with separate code), arrival order between triads (model-free), and +285 to +388 s delay | Station positions only | Ditching position from Wikipedia (immaterial). The triad-order test is post-hoc | "The boxed pulses arrive from 152–156°, not from the ditching site at about 80°, and reach H11S before H11N, which a source at the ditching site cannot do" |
| Sriwijaya 182 (H08S) | Real sound; time disagrees | **Yes, for timing.** Holds under Kadri's own water speeds and under his land-crossing idea | KNKT impact time and position (firm); no long oceanic-crust leg | Bearing unreliable (noisy elements), so it rests on time alone. The boxed transient is ordinary for that day (p 0.35, rank 81 of 231) | "The boxed transient precedes the earliest water-borne or land-assisted arrival by at least 6.5 min, and is not unusual against the same day's background" |
| AB Aviation 1103 (H08S) | Real sound; time disagrees | **Conditional** | Impact time from press only; the fit needs an impact 20–25 min before reported last contact | Our S1-based bearing (erratum 3, immaterial); no coherent bearing to test | "Not consistent with the reported accident time; consistent only if impact occurred near 09:05–09:10 UTC" |
| AirAsia 8501 (H01W) | Real sound; time and direction disagree | **No, not as stated.** Timing fits a land-assisted path. Printed panel not reproduced at its labelled time (r ≤ 0.13). Open data end at 00:00 UTC | Whether the burst we tested is the one Kadri plotted | Our "−517 s" uses an all-water route, which Kadri does not assume | "The printed panel could not be matched to the open data; a burst inside the box arrives from 220°, not from the north; the comparison is unresolved" |

## 5. Specific corrections to our own wording

1. "His other aircraft signals are real sounds." This is literally true; there is energy in each box. But for Sriwijaya 182 the boxed transient is ordinary for the day (p 0.35). For AirAsia 8501 we cannot show that we found Kadri's sound. Replace with "a transient is present in each box in the raw data".
2. "Their time or direction does not agree with the crash sites under our model." Name the model and give the bracket. For Sriwijaya 182 and AB 1103 the result now holds under Kadri's model too, which is stronger and should be said. For AirAsia 8501 remove the timing claim.
3. Report offsets as ranges with the route-length correction (Sriwijaya 182 about −700 s against the geodesic at 1.48 km/s, ≥ −391 s against the most generous bracket), not as −742 s.
4. The table column "Kadri's own 1.45–1.57 km/s window" applies a window from his MH370 section to the crash panels. Say so. He gives no window for the crash panels.
5. The triad-order test, the land-crossing brackets and the bearing robustness are post-hoc. Label them in the paper. The pre-registered parts (windows, statistics, plane-wave bearing) remain the main result.

## 6. Is it publishable?

Yes, as a replication and attribution test with this scope:
- "Using open raw IMS data we reproduced six of seven printed panels from five cases. We confirm the F-35A arrival. For Transair 810 and Sriwijaya 182 the boxed signals cannot be arrivals from the accident sites under water-borne or land-assisted propagation at the speeds used by Kadri (2024). For AB Aviation 1103 the same holds under the reported accident time. The AirAsia 8501 panel could not be matched to the open data."
- Consequence for this project: of the published aircraft cases with open data, only the F-35A can calibrate coupling or detectability. That is already the project's position (memory: Kadri set is a comparison set).

Not publishable as stated: "errors in Kadri's work". We do not know how he chose his windows. The most likely failure mode is attribution: choosing a salient transient near an expected time without a travel-time and bearing test. That is an inference. It is not a demonstrated error.

Before submission:
1. Send Kadri the per-case table and script, consistent with the collaboration package as a give. Ask how the crash-panel windows and the AirAsia 8501 panel were made. A formal comment route (e.g. Sci. Rep. Matters Arising) normally expects this contact first; check the current journal policy.
2. Get the official AB 1103 report (Comoros, or the BEA if it assisted) or ATC/radar times.
3. Read the NTSB final-report coordinates for Transair 810 (immaterial, but tidy).
4. Test the H08S time base and bearing on a located event in Jan 2021 or Feb 2022 (an earthquake T-phase), as was done for H01W with 41 earthquakes.
5. Search all three H01W elements on 26 and 29 Dec 2014 at 23:51 for the AirAsia 8501 panel, to test a date error on either side.
6. Keep the MH370 candidate separate. Nothing here tests the 306° signal at 00:52–00:54 UTC.

## Files
- kadri_review_checks.py: reproduces every number in section 3 from public services (EarthScope FDSN, NOAA ERDDAP ETOPO1, obspy TauP iasp91).
- review_geometry.csv: ranges, expected bearings, water, land, P and S times, box times and implied speeds.
- review_mixed_path.csv: land-crossing brackets.
- review_inter_triad.csv: arrival order between H11N and H11S.

Assumptions in all new tables: WGS84 geodesic from the triad centroid; ETOPO1 sampled every 2 km at 2-arcmin grid stride; fast speed applied to all segments shallower than the threshold, which is generous to Kadri; primary impact times (KNKT FDR end for SJ182 07:40:28 and QZ8501 23:20:35; NTSB for TA810 11:45:18; press for AB1103 09:30); box times as digitised by the replication track.
