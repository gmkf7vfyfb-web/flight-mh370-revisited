# Combined weak-signal detector on 8 March 2014: results, version 3 (7 Nov 2026)

Replaces version 2 ({{artifact:2123893d-3b94-430e-b617-6b35e13ac404}}). Pre-registration: {{artifact:0e0d28e4-a73d-408e-a9d6-878ed158bfa8}}. Independent review: {{artifact:351db6d4-f6c5-424e-b713-7f8510b7c81a}}.

## Summary (plain)
- The final network search finds no impact time and place that stands out from chance. The global chance is 0.95 (primary speeds) and 0.93 (wide speeds).
- A fault in the noise calibration made some noise looks seem very rare. We fixed it. The earlier top weak candidates near 00:54 at Scott Reef were partly caused by this fault.
- Kadri's bearings now carry the Cape Leeuwin array correction (ruling B1). With the correction, no seeded test confirms a source (smallest p 0.26 at primary speeds).
- Weak signals remain and are shown in full. These are timing coincidences only, not detections:
  - Cape Leeuwin 00:36:07, Portland 2 01:07:44 and Diego Garcia South 01:10:15 fit one impact at 30–32° S, 125–150 NM south-east of the arc, about 00:20:48–00:22:07, but only at the wide speeds.
  - Kadri's Cape Leeuwin 00:49:58 and the Diego Garcia South 01:10:15 peak fit one impact at 38–39° S, 125–150 NM south-east, about 00:23:20–00:25:51, at the primary speeds.
- The Portland 2 burst at 01:07:44 has the impact spectral shape. It lasts 5 s, and only one logger recorded it.
- Above 8 Hz the three impact types have the same spectral shape. A spectrum therefore cannot tell a dive from a ditching at the IMOS loggers.

## 1. What changed since version 2
1. **Tail-map fix (imos_calib.py, {{artifact:a98df159-483a-4035-b136-067c95a35506}}).** Persistence saturates at the noise maximum in 6.6 % of Scott Reef and 2.2 % of Perth Canyon 2 noise looks. The fitted tail gave those looks p of about 1e-7, and these values then distorted the Fisher combination. Now p is the empirical rank, with ties, up to the sample maximum; the fitted tail applies only beyond it. The calibration file was rebuilt with earthquake windows and fault records removed.
2. **Kadri bearings corrected** for the H01W array-position bias (calibration from 144 earthquakes; corrections −4.4 to −13.8°), with published bearings as the sensitivity case (ruling B1, 26 Oct). Table: {{artifact:997f9bb4-1b28-47c4-ba49-89b3763f8867}}.
3. **Final run run14v5_final:** {{artifact:7ce37b10-b640-498c-9d20-82348394b54f}} (global), {{artifact:04c940c5-32dd-4b69-8364-eb244453be67}} / {{artifact:f92d7211-62b9-4243-b82e-6b6020d5df23}} (seeded tests), {{artifact:c0658ab6-e1cf-4182-a92d-98e02114a3d4}} (split half).

## 2. Final network result
| Speed model | Best evidence (−log10 p) | Global chance | Global level 5 / 20 / 50 % |
|---|---|---|---|
| Primary 1.465–1.520 km/s, 2 % detour | 1.42 | 0.945 | 3.41 / 2.85 / 2.33 |
| Wide 1.40–1.56 km/s, 5 % detour | 1.16 | 0.931 | 3.06 / 2.53 / 2.03 |

Seeded tests: 57 of 65 seeds testable (primary), smallest p 0.255, smallest q 0.974; wide speeds smallest p 0.083, q 0.999. Split half: noise calibration holds at 5 % (0.045–0.056) except Portland 2 (0.074 at 5 %, 0.034 at 1 %), which is calibrated on its own day and is optimistic. Figure: {{artifact:9ec43911-8bc1-435e-8e73-1f281613716c}}. Ranked network candidates: {{artifact:c3b02ba8-24d0-49ad-8b20-911839df7f59}}. The top primary entry (34° S, +150 NM, 00:53:38) is carried by Scott Reef alone (p 0.0035), on a path with large attenuation and in a record with the airgun-type shot train.

## 3. Sensitivity (injection test version 3, final calibration)
- Pure-noise check: false-alarm rate 0.059 at a nominal 5 % and 0.19 at 20 % (200 noise cases per logger).
- One logger, known time, 50 % detection, 8–40 Hz SNR: −9.4 to +0.9 dB at 5 % per look; −20.0 to −3.6 dB at 20 % per look.
- Two independent sites at equal SNR: 1.5–11.3 dB at global 5 %; −0.2 to 6.2 dB at 20 %; −2.5 to 3.4 dB at 50 %. A third station with only noise adds 1.0–3.6 dB. The Portland 1 + Scott Reef pair is now the weakest (9.4–11.3 dB at 5 %) because the tail fix removed false sensitivity at Scott Reef.
- Figure: {{artifact:a7a2e8cf-6828-42b9-aed0-ae015e588a1c}}. Tables: {{artifact:5988669e-6b91-41ac-b4ce-9a5a3cba7ff8}}, {{artifact:9d74bcf8-b201-4954-aa3f-5d3062d6381d}}, {{artifact:5c7f5669-ab98-4c36-b5b8-f617178e0f39}}, {{artifact:9b5131ac-f953-4722-9f29-a8f4d5afbe4d}}, {{artifact:f768f5fa-d8a0-4b9e-af33-a772b957a568}}.

## 4. Candidate pages (Cape Leeuwin and Diego Garcia South, top 10)
PDF {{artifact:8f81acae-b0be-4321-9969-f7ecac43a57f}} (55 pages), table {{artifact:97d5079a-6e5d-499b-9469-8f2f8fde4c62}}. Each candidate has a primary-site page and one page per other site with an open path. Each site page shows: the expected arrival time (all allowed speeds, dotted; primary speeds, shaded) in the title; a strip of expected arrival time by arc latitude; the spectrogram; raw 1 s 8–60 Hz power over the band-energy score, so the time alignment can be checked; and the correlation and combined scores. The scores use 30 s windows with a ±20 s lag search, so one short sound gives a flat-topped step about 70 s wide centred on it. This was checked at Scott Reef (raw peak 00:47:52.4, plateau centre 00:47:49.9) and Portland 2 (01:07:58.4 against 01:07:57.9).

### 4.1 Arrival-time convention and latitude bounds without a bearing
Arrival span (7 Nov 2026). Our screening times are onset picks on the digitised envelope; Kadri (2024) does not state whether his Table 1 times are onsets or peaks. In the top ten candidates the envelope peak lies between 8 s before and 20 s after the pick; when the peak comes first, the span ends at the pick. Royer's (2016) own Cape Leeuwin figure pick bars sit 7.7–16.6 s after his Table 5 picks (five figures), and up to 23.4 s for one array element of event B. Our envelope onsets match his figure bars for events A and B within 1.5 s. The 20 s offset covers this difference between the two pick conventions. The timing therefore uses an arrival span from the onset minus 20 s to the envelope peak. The earliest implied impact uses the start of the span with the slowest speed; the latest uses the end of the span with the fastest speed. The candidate pages mark the onset (solid red line), the peak (dashed line) and the span (red band).
- Cape Leeuwin 00:36:07 (onset; peak 00:36:20): at 1.56 km/s and impact no earlier than 00:19:38, the source is no more than 1,563 km from Cape Leeuwin. That equals the distance to the nearest on-arc point (28° S). The arc line itself is therefore reachable only at that point, only at the limit (impact 00:19:38, 1.56 km/s, arrival at the envelope peak). At the primary maximum speed of 1.52 km/s the limit is 1,523 km, and only points south-east of the arc fit. Fitting points: 22–33° S at 25–150 NM south-east, plus 28° S on the arc at the limit; impact 00:19:38–00:22:36 ({{artifact:c746341d-6266-412b-8a12-1a8da1a3f0f3}}).
- Diego Garcia South 01:10:15: every latitude 20–41° S fits; the impact window depends on latitude ({{artifact:482720d9-34d9-4bff-aade-c95526cb1ee7}}).

Time coincidences with Royer (2016) picks are shown as labels only. The 00:36:07 onset coincides with Royer's figure pick for his event B (association 0.94, below the 0.95 removal level). Royer's event locations rest on his own association of picks across stations, which is not independently verified. A label therefore does not move or remove a candidate.

### 4.2 Timing coincidences (label only)
- Candidate 1 ({{artifact:93a35009-279f-464c-aa1e-ee0d0ed538e6}}): with the arrival spans, Cape Leeuwin 00:36:07 and Portland 2 01:07:44 fit 30–33° S at the wide speeds only. Adding Diego Garcia South 01:10:15 narrows this to 30–32° S, 125–150 NM south-east, impact 00:20:48–00:22:07. No arc point fits at the primary speeds. The wide-speed network scored these hypotheses 0.39–0.57 (−log10 p), against a global 50 % level of 2.03. The Diego Garcia window covers most of its 19-min trace, so that station adds almost no timing constraint. The 4 Nov check found Cape Leeuwin quiet (−0.4 to +0.5 dB) where an arc source of the Portland burst would arrive at the primary speeds (00:39:57–00:41:26).
- Candidate 6 ({{artifact:4f0158e0-07ca-4803-a9f9-3f4418d78cc5}}): Kadri 00:49:58 (corrected 246.8°) with Diego Garcia South 01:10:15 fits at the primary speeds at 38° S −125/−150 NM and 39° S −150 NM, impact 00:23:20–00:25:51 (with arrival spans). The Diego Garcia peak is the strongest look in its trace (per-look p 0.0085). The window p of 0.749 says only that the in-sample envelope test cannot judge it, because the window spans almost the whole trace. The peak lies just before the broad 01:12–01:16 rise of the airgun shot train. Under the airgun rule this is a label, not an exclusion. The 5 Nov shot-population test found no significant shot cycle.

### 4.3 Spectra against the impact families
Figure: {{artifact:b288bbc3-7a43-4538-8dac-e754ebf1a9ee}}. All slopes are fitted on 1/3-octave bands over 10–40 Hz. The impact families give about −7 dB/oct there, because their corner frequencies lie below 3 Hz.
| Signal | Duration | Slope (dB/oct) | Reading |
|---|---|---|---|
| Scott Reef 00:44:56–00:48:39 low-frequency event | ~4 min | +10.4 | not impact-like; excess +20 dB at 3 Hz; no USGS event of any size fits |
| Scott Reef pulses 00:44:45 record | — | +7.7 | airgun-type train (envelope period 8.1 s) |
| Scott Reef pulses 00:59:46 record | — | +13.4 | airgun-type train (envelope period 8.4 s) |
| Portland 2 01:07:43.9–01:07:48.9 | 5 s | −4.8 | impact-like shape; also typical of earthquake sound (54–86 % of real quakes class as impact-like) |
| Portland 2 01:20:30–01:20:42 | 12 s | +8.5 | not impact-like; peak near 40 Hz |

Portland 1 did not record at either Portland time (its records run 00:59:59–01:05:06 and 01:14:59–01:20:06). For candidate 6 the 01:07:44 burst comes about 24 s before the earliest physically allowed arrival (01:08:08), so it cannot belong to that candidate. For candidate 1 it lies inside the all-speeds window (00:59:54–01:09:23) but after the primary span (01:01:51–01:05:24).

**Correction to earlier statements.** The value −12.8 dB/oct for the Portland 2 burst came from a fine-bin fit with clipped negative bins and was wrong. The burst does not fall faster than an impact; its shape agrees with the impact families. The earlier statement that the irregular Scott Reef pulses rule out an airgun train was also wrong: the background has a regular 8.1–8.4 s envelope period.

## 5. Sound-speed ranges
- Primary: 1.465–1.520 km/s, path detour 0–2 % (pre-registration item B5). This is the range of speeds implied by Royer (2016) Table 5 picks on 8 March 2014: 1.4667–1.5184 km/s over 143 picks at 10 receivers (array elements counted separately), 20 events (5–95 %: 1.4725–1.4998). The values depend on Royer's origins and pick associations.
- All allowed: 1.40–1.56 km/s, path detour 0–5 % (sensitivity). Its derivation is not documented in the project record; it is wider than the Royer-implied range on both sides. Kadri (2024) uses 1.45–1.57 km/s.

## 6. Open limits
- No raw Cape Leeuwin or Diego Garcia South waveforms exist for 8 March 2014; only the digitised Kadri envelopes. Requesting the raw IMS data from CTBTO is the largest possible gain.
- Portland 2 and Perth Canyon 2 are calibrated on their own day (in-sample).
- No received-level model yet links SNR to source level, so these results cannot exclude any impact energy.
