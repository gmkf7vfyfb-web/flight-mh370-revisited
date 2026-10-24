# Next steps from the source survey: results (24 October 2026)

Follows [impact-and-other-sources-synthesis-2026-10-23.md]({{artifact:48dfdd44-634e-41de-b4e4-aa73cc442e08}}). Status: exploratory. Nothing here returns a likelihood to the composer. Every rejection or upper limit carries both standing caveats:

1. The propagation model fails the frequency-slope check against the 2001 airguns (+10 dB/octave at H01W, +7 dB/octave at H08S), although levels pass.
2. Detection probability is a proxy unless it is measured on real data.

## 1. Open IMS hydrophone background for March (2015-2019 as a stand-in for 2014)

Note: [ims-open-march-background-note.md]({{artifact:e9733f9c-2599-488e-b0ae-29ceff0d1564}}). Tables: [ims-march-false-alarm-rates.csv]({{artifact:da30fe9e-42df-4120-a725-af8b348d18fd}}), [ims-march-noise-percentiles.csv]({{artifact:5934eb83-a597-4e84-b6e2-68eb0b60e8b2}}), [ims-march-noise-vs-references.csv]({{artifact:59ff8cbc-7e16-452a-9072-65ea9adc2d5f}}), [ims-open-availability.csv]({{artifact:648befdb-52d8-49c7-8e23-00b209984bf2}}), [h01w-array-calibration.json]({{artifact:076cefbe-3cb6-4831-8495-2149f256d05a}}).

- **Data used.** EarthScope serves IMS hydrophone data openly from 2015, not for 2014, and none for H08N. The track used the 00:00-04:00 UTC block of every open March day: 115 station-days at H01W and 153 at H08S, 2015-2019. The sandbox link speed (about 1.1 MB/s) forced this cut.
- **Noise (5-40 Hz median in the arrival-window hours).**
  - H01W: 103.6 dB re 1 µPa. That is +2.0 dB above Blackman 2003 and **+7.4 dB above the stand-in the module has used** (registry D06).
  - H08S: 98.0 dB re 1 µPa. That is +2.5 dB above Blackman 2003 and +1.8 dB above the stand-in.
  - **Consequence:** detection estimates at H01W built on the stand-in are optimistic by about 7 dB.
  - **Corroboration from 2014:** the H01W levels digitised earlier from Royer's 2014 spectrogram (about 101.7 dB) and from Kadri's Fig. 9 trace (103.1 dB) agree with the proxy to within about 2 dB. The stand-in, which is the IMOS 3376 5-40 Hz level of 96.2 dB, is therefore the outlier.
- **H01W bearing bias.** Bearings computed from the published element positions are biased by a median of +5.2°, and by up to +12° inside the arc sector. An array calibration on 41 catalogue earthquakes corrects this: left-out error -0.04°, robust standard deviation 0.66°. Any project bearing at H01W computed from element positions needs this check.
- **False-alarm background.** The rate counts coherent arrivals from the 7th-arc sector (20-40 S) in the 2014 clock-time windows that pass the registered 5-40 Hz detector, per hour, with day-bootstrap 90 % intervals.

  | | screen (p < 0.3) | mark (p < 0.1) | report (p < 0.05) |
  |---|---|---|---|
  | H01W | 0.139 (0.086-0.194) | 0.125 | 0.086 |
  | H08S | 1.00 (0.72-1.32) | 0.43 | 0.36 |

  The p floors are 1/27,850 (H01W) and 1/39,173 (H08S). The expected count in one arrival window at the screen level is about 0.27 at H01W and about 2.1 at H08S.
  - At H08S, 298 of the 316 arc-direction passes come from 148-163.5°. That is the 35-40 S part of the arc, which is also the direction of Antarctic ice and the ridge to the south. Bearing alone cannot separate an impact there from those sources.
- **8 March 2014 was worse than a typical proxy day at H08S.** In the proxy years, airgun trains fill 30 % or more of the window on 49 of 153 days, all from 108-114°. The 35° train seen on 8 March 2014 never appears.
- **Declared limits:**
  - The class rules were tuned on the 8 March full days.
  - The comparison of window hours against the rest of the day rests on 9 full days.
  - Other years are a proxy for 2014.

## 2. Island seismometers and Royer's located events

Note: [island-seismic-check-note.md]({{artifact:9ae64caf-24b6-46c7-acba-2581971e2d79}}). Tables: [royer-events-labelled-set.csv]({{artifact:5e1deaae-9dd2-4279-8994-29772ef4f0ea}}), [island-seismic-associations.csv]({{artifact:70e0a47c-95b3-4d08-b968-64aaa9c9eb94}}), [island-impact-window-unexplained.csv]({{artifact:4ea60c55-82b9-444a-985d-182c20f60c7c}}), [island-seismic-detections.csv]({{artifact:b5bbb22d-15d8-40e2-864b-2ea7161a9c79}}).

- **Coverage.** 24 stations, 6-10 March 2014, 20,484 detections.
- **Detection level.** Island stations record T-phases mainly from M 4.5 and above within about 1,500 km (14 of 16 events). At 1,500-3,000 km they record 2 of 18. Below M 4.5 the rate is no better than chance.
- **Royer event 16 is confirmed as an earthquake.** Four stations record P and S. The seismic location is 8.14 S 107.88 E, depth about 35 km, origin 01:15:23.05 UTC. That is 30 km from Royer's position and 24.9 s earlier than his origin.
  - The event explains the Curtin H08S detection at 01:58:55 from 93°: predicted 01:59:19.8 at back-azimuth 93.3°.
- **The other 19 Royer events are not tested with useful power.** This includes events B, D1 and D2 near the arc, where the largest SNR is 3.17 or less, at chance level.
- **Impact windows: no significant detection with limited power.**
  - 23 stations and 46 windows gave 312 unexplained detections: 6 at screen, 3 at mark and 1 at report level. The p floor is 0.008-0.014.
  - The single report-level candidate (AU.XMI 00:57:41, SNR 19.6, p 0.0127) is a local transient. The co-located AU.XMIS, 5.2 km away, stays at SNR 1.12 or less.
  - One mark-level candidate remains: II.COCO 02:13:02, SNR 4.9, p 0.062, peak 18 Hz. Cocos has no second sensor to check it against.
- **Royer labelled set built.** It has 840 rows: 20 events × 42 receivers, with source class. Royer's 143 listed arrivals fit the 1.48 km/s rule with median -3.1 s and standard deviation 8.6 s. The module can now use it as a real-arrival calibration set.

## 3. Antarctic moorings (AADC Casey 2014, South Kerguelen 2014)

Note: [aadc-moorings-note.md]({{artifact:89a81868-64bc-4cb3-aff6-a5027d7e868e}}). Table: [aadc-2014-access.csv]({{artifact:a6d7b7be-a00b-41c4-97b2-493569d6da04}}).

- **Access.** All 12 hourly files (12 kHz, continuous) for 7 Mar 18:00 - 8 Mar 06:00 UTC exist at both sites. Download is behind an email request form, with no account; AADC then sends a link. This is a request, so under Pete's rule it was not submitted. About 0.5 GB covers 00:00-03:00 UTC at both sites.
- **They are a weak test of an impact on the arc.** Both hydrophones sit near the seabed, far below the polar surface duct. At South Kerguelen no refracted-only path from the arc reaches 2,000 m. At Casey only 16-36 % of the refracted angle band reaches 2,700 m, and none of the low-angle energy.
- **They would be a strong independent check on Royer's southern events.** For all 10 Royer events south of 50 S, a mooring is closer than Royer's nearest receiver: 260-1,427 km against 1,150-3,572 km. The moorings are also south of the events, while all of Royer's receivers are north or west. Example: icequake A is 693 km from South Kerguelen, with a predicted arrival at 00:24:17.
- **Calibration to Pa** also needs the ADC full-scale voltage, which is held in the gated sidecar files.

## 4. Still running

- **Metz close-range records.** The track is waiting on approval for `www.jamstec.go.jp`.
- **Swissair 111 seismic record.** The track is waiting on approval for `earthquakescanada.nrcan.gc.ca`.

## 5. Decisions for Pete

1. Submit the AADC email request (free, no account) for the 8 March 2014 Casey and South Kerguelen files? It is the only way to check Royer's southern icequake locations independently.
2. Replace the module's IMS noise stand-in (D06) with the 2015-2019 March percentiles, declared as a proxy? This moves H01W about 7 dB louder.
3. Apply the H01W array bearing calibration to the module's H01W bearing work?
4. Still open from 23 Oct: the AMSA March 2014 AIS click-through, and a Global Fishing Watch token.
