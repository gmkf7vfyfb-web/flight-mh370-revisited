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

## 4. Metz et al. 2023 F-35A close-range records (180-255 km)

Note: [metz-nearfield-note.md]({{artifact:71f9f592-ca1a-4388-9dff-cf5d55128c74}}). Tables: [metz-nearfield-derived.csv]({{artifact:817bdb0f-4188-44a5-add8-92402b7a054b}}), [metz-nearfield-eta.csv]({{artifact:5a8fd3a5-3aa0-4202-a560-1633d6f9d2e7}}), [metz-source-slope.csv]({{artifact:36fce763-909c-4e20-97db-40fff3772877}}), [metz-geometry.csv]({{artifact:3018d01d-c250-4727-a1dc-cf7c7e5f7d60}}).

- **Correction to the 23 Oct survey.** The project had already digitised Metz Fig. 2 (module branch, prepare/digitise_metz_2023.py), so "not digitised" was stale. An independent re-digitisation agrees: envelope peaks to 0.002 dB, spectrogram pixels to a median of 0.10 dB. It also reproduces Metz's stated reading errors (5.62 s at KSP2 against 5.7 s; 1.38 s at H11S1 against 1.4 s).
- **Raw waveforms are not open.** The JAMSTEC cabled-observatory data centre now shows a notice that access is partly suspended. Download was for registered users only.
- **Source duration.** The 5-95 % energy span is 7.1-10.5 s at close range and 3.3-5.0 s at Wake Island. Propagation cannot shorten a signal, so the source energy span, at the angles the sound channel holds, is at most about 3.3 s. Most of the close-range length comes from seabed and slope reverberation. The close-range onset is sharp (10-90 % rise 0.76-0.84 s, which equals the 1-s window limit). The emergent onset at Wake is therefore a path effect.
- **Sub-event hint.** At close range, 25-40 Hz energy arrives first and stops within about 2-2.5 s, while 4-10 Hz energy continues to 8-13 s. This fits a short broadband entry phase followed by low-frequency energy, but path dispersion can produce the same pattern. It is not resolved.
- **The ~20 Hz gap is at all four close-range and both far stations.** It does not move with range, so it is not a surface-image notch at source depths of 30 m or less. It is a source feature or a common processing feature.
- **Source spectrum is steeper than the module model.** After the module's propagation loss is removed, the implied source energy spectrum falls at about -12 dB/octave (5-40 Hz) at close range and -10 dB/octave at Wake. The project's one-pole f⁻² source (-6 dB/octave) does not fit; an f⁻⁴-like source does. Caveat: the module propagation loss fails the 2001 airgun frequency-slope check, so these slopes may be biased steep by a similar amount. The close-range-versus-far comparison of received spectra does not depend on the model and is not affected.
- **Coupling (D1).** The close-range values are 0.106 (2 m), 4.43e-3 (10 m) and 6.79e-4 (30 m): 4.2 × the far-field value at every depth (2.4 × without KSP2). The close-range level depends mostly on the seabed model; a soft bottom changes it by about × 200. **The close-range records do not narrow the trade-off between coupling and source depth.**
- **Geometry.** The point consistent with Metz's ranges (40.4496 N 142.9237 E) is 21.4 km from the module's working point. Kadri S1's site is 64 km from Misawa, against Metz's 135 km.
- **Data-file finding.** The module-branch Fig. 2 spectrogram files keep frame and tick pixels at about 110 dB. The far-field Fig. 3 files show 13-17 % saturated edge pixels. These lie mostly outside the arrival windows; the effect is probably small but was not quantified.

## 5. Swissair 111 (MD-11, 3 September 1998 01:31:18 UTC) as an airliner-energy case

Note: [airliner-seismic-cases-note.md]({{artifact:444bf62f-94a5-4323-87d4-45c1540e5459}}). Tables: [swissair111-seismic.csv]({{artifact:652b61c4-60b1-4683-a229-801904a9b121}}), [airliner-ocean-impacts-seismic-cases.csv]({{artifact:4aa5cc0f-1e6d-484f-b548-da60aed3ffcf}}), [swissair111-energy-sensitivity.csv]({{artifact:20e3cf81-6c68-4733-b2c0-8288f79d7873}}).

- **Date correction.** The impact was on 3 September 1998 UTC (TSB report, footnote 1), not 2 September as in the survey.
- **Catalogued.** Earthquakes Canada event 19980903.0131003: origin 01:31:17.0, location fixed at the wreck, magnitude MN 0.57, classed as "mining explosion". ISC and USGS ComCat have no event.
- **Recorded.** Station CN.LMN (Caledonia Mountain, 173.4 km) shows clear P and S; implied origin time within -1.4 to +0.9 s of 01:31:18; SNR 17.3; p 0.022, at the p floor (44 noise windows). Peak ground velocity is 40.5 nm/s (three components). The 44-64 s signal length comes mostly from the path and must not be used as an impact duration. The Halifax record the TSB mentions is not in the open archive (metadata start in 2003).
- **Magnitude and energy.** Scaling against five land events at LMN gives MN 0.74 ± 0.15 (1-15 Hz) and 0.58 ± 0.13 (3-15 Hz). Kinetic energy is 2.74 GJ (2.39-2.92). Radiated seismic energy is 1.5e3-3.7e4 J measured directly, or 3.2e4-8.1e5 J from magnitude.
- **New coupling class S1** (land-recorded seismic energy / impact kinetic energy): 5e-7 to 3.4e-4. It is provisional and spans about three decades. It must not be mixed with the hydroacoustic classes D1-D4.
- **No hydroacoustic record** exists in the open literature or the TSB report.
- **Nine other airliner sea impacts** (Alaska 261, Flash 604, EgyptAir 990 and 804, Lion Air 610, Sriwijaya 182, TWA 800, Adam Air 574, Ethiopian 409) give no detection that holds: no significant detection with limited power. The coastal stations are too noisy, or the archives have no data. AF447, Yemenia 626 and AirAsia 8501 were not scanned.

## 6. Decisions for Pete

1. Submit the AADC email request (free, no account) for the 8 March 2014 Casey and South Kerguelen files? It is the only way to check Royer's southern icequake locations independently.
2. Replace the module's IMS noise stand-in (D06) with the 2015-2019 March percentiles, declared as a proxy? This moves H01W about 7 dB louder.
3. Apply the H01W array bearing calibration to the module's H01W bearing work?
4. Should the module's source spectrum move from the one-pole f⁻² model to an f⁻⁴-like declared alternative, given that the Metz close-range and far-field records both imply about -10 to -12 dB/octave (with the propagation-slope caveat)?
5. Add Swissair 111 to the ground-truth cases table as a seismic (S1) airliner case?
6. Still open from 23 Oct: the AMSA March 2014 AIS click-through, and a Global Fishing Watch token.
