# Haixun 01 37.5 kHz contacts (4-5 Apr 2014): beacon physics, geometry test and B_H

Leg: pre-registration Q5 (`../preregistration.md`, committed 18 Oct 2026 before any statistic). Hydroacoustics module, high-frequency branch, separate from the sound-channel (H01W/Kadri) work.
Date: 18 Oct 2026. Status: **provisional physics**; result is a **prior-free likelihood ratio**. It uses no run J weights and does not depend on the 00:19 option or on Kadri branch T or C. (The Haixun position is the same in both branches; only the implied source time differs, 00:34:24 T / 00:36:51 C, which this leg does not use.)

Script `haixun_beacon.py` (seed 20261018, about 20 s), inputs in `inputs/`, outputs `bh_summary.json`, `geometry_test.json`, `pdet_vs_offset.csv`, `tl_vs_offset.csv`, `profile.csv`.

## 1. Result in one paragraph

A working Dukane DK100 beacon on the sea floor at the Haixun 01 position (4,577 m, GEBCO 2020) is 4,575 m from a hand-held hydrophone on a 2 m pole even directly overhead, which is beyond the receiver's stated practical range (2,000 m) and beyond ATSB's "about 4,500 m in favourable conditions". The direct path loses 107 dB (73 dB spreading, 34 dB absorption at 37.5 kHz). The probability that the boat team detects a transmitting beacon directly overhead is 0.08 (first-principles sonar equation), 0.02 (calibrated to ATSB's favourable-conditions range) or 2 x 10^-4 (calibrated to the manufacturer's practical range). These figures are means over the unknown parameters. Refraction is not the limit, because direct rays reach 31 km. A single fixed beacon can produce two contacts 2-3 km apart, the second weaker, only if the overhead signal excess is at least +2.9 to +3.8 dB. The probability of that is 0.03-0.04 under the first-principles calibration and ≤ 0.001 under the other two. The Bayes factor for "MH370's recorders lie within 2 km of 25.975 S 101.461 E", over contacts plus the failed reacquisitions, is **B_H = 0.59 (ln B = -0.53) first principles, 0.48 (ln -0.74) ATSB favourable, 0.45 (ln -0.80) maker's range; headline mix of the first and third 0.52 (ln -0.66)**. The 5-95 % sensitivity range is 0.31-2.1 (ln -1.15 to +0.75). The contacts themselves carry almost no weight (factor 1.0-1.45), because a genuine detection from 4.6 km down is less probable than a plausible false contact. The weak negative comes from HMS Echo, the submarine and the sonobuoys not reacquiring the signal. That term is judgement-based (section 6).

## 2. Sources (grades: A primary read with pages; B official cited, not read; C online/community)

| Item | Value | Source | Grade |
|---|---|---|---|
| ULB model | Dukane DK100 on both recorders | ATSB 2017 *Operational Search* p.36 fn 19 (printed; Drive text read 18 Oct); ATSB June 2014 *Definition of Underwater Search Areas* p.11 | A |
| ULB model per SIR | "DK-100/DK-120"; FDR ULB S/N SC26210, battery expired Dec 2012; CVR ULB battery due June 2014 | Malaysian SIR 2018 pp.134-137, 364-365 (read 17 Oct, `../../evidence-sweep-2026-10-17/research-beacons-tpl-simulator-barnacles.md`) | A (prior session) |
| Frequency, pulse, rate | 37.5 ± 1 kHz; 10 ms ± 10 %; ≥ 0.9 pulse/s; ≥ 30 days | Dukane DK100/120/130/140 Technical Manual 03-TM-0037 Rev 13 (13 Apr 2004) p.6; ATSB June 2014 p.11 | A |
| Source level | 1060 dyn/cm² = 160.5 dB re 1 µPa @ 1 m initial; 700 dyn/cm² = 157.0 dB after 30 days; rated over 80 % of sphere | DK100 manual p.6 | A |
| Manufacturer detection range | "2000 to 4000 yards (1800 to 3600 meters)", depending on sea state, boats, marine animals | DK100 manual p.15 | A |
| Battery life | manufacturer predicted 40 days maximum | ATSB 2017 p.36 fn 20 | A |
| Nominal ULB detection range | 2,000-3,000 m; about 4,500 m in favourable conditions; 1 km for a robust search | ATSB June 2014 p.11 | A |
| Haixun 01 equipment | Benthos pinger locator, 5-80 kHz, practical ULB detection range 2,000 m | ATSB June 2014 p.11-12 fn 11; ATSB 2017 p.39 | A |
| Haixun method | hydrophone on a pole from a rescue boat, rotated through directions | ATSB 2017 p.37 | A |
| Unit identity | Teledyne Benthos DPL-275 diver pinger locator (Teledyne VP quoted from photographs) | press via wfoster2011 blog, 6 Apr 2014 | C |
| DPL-275 receiver | 5-80 kHz, 2 kHz bandwidth, hydrophone directivity typically 30° between 3 dB limits | Teledyne Benthos locator catalogue (2012, third-party mirrors) | C |
| Comparable unit | RJE DPR-275: 1 kHz bandwidth, 25° beam at 37.5 kHz, 1,200 m on a 162.5 dB 37 kHz source (diver) | RJE / ndiver datasheets | C |
| Contacts | 4 Apr, 25.975 S 101.461 E, depth about 4,500 m, 37.5 kHz pulsed once per second, 15 min; 5 Apr, 3 km west, 90 s, much weaker | ATSB 2017 p.38 | A |
| Contact detail | first operator heard ≥ 200 pings over about 3 min before alerting others; pole about 2 m; a change of head angle lost the signal; first contact about 16:34 local; second contact "within 2 km" | Xinhua/CCTV via metabunk and Global Times, 5-8 Apr 2014 | C |
| Follow-up | HMS Echo 6 and 8 Apr unsuccessful; judged unlikely from depth, surface noise and the 2,000 m practical range; a submarine also unable | ATSB 2017 p.39; June 2014 p.13 | A |
| Echo's system | hull-mounted, designed for 27-30.5 kHz transponders, retuned to 37.5 kHz | ATSB 2017 p.38 | A |
| Submarine identity | HMS Tireless | UK MoD 24 Apr 2014 (via globalsecurity) | C |
| Sonobuoys | hydrophone at 300 m; ULB detection up to 4,000 m; about 3,000 km² per sortie; 6-17 Apr, "where depths were favourable", including Haixun area; nothing ULB-related | ATSB 2017 p.41; June 2014 p.13 (June 2014 lists Ocean Shield and the H01 bearing, not Haixun) | A |
| Ocean Shield TPL | worked near 21 S 104 E, not at the Haixun site; max effective 3 km, pinger max transmission 10 km | ATSB 2017 pp.39-42; June 2014 Fig. 12 | A |
| Depth | 4,577 m at the contact; 4,570-4,609 m within 3 km; 4,461 m at the Kadri arc crossing 25.732 S 101.369 E | GEBCO 2020 via OpenTopoData | A (data) |
| T/S | WOA23 decav 1°, March monthly (0-1,500 m) + Jan-Mar seasonal below, mean of 25.5 S and 26.5 S cells, 101.5 E | NCEI THREDDS | A (data) |
| Wind | ERA5 10 m, 3.6 m/s mean 04-12 UTC 4 Apr, 2.8 m/s 5 Apr, no precipitation | Open-Meteo ERA5 archive, grid cell 25.975 S 101.508 E | A (data) |

## 3. Sonar equation (Q5 items 1-3)

- **Source level on the day.** Linear between the specification points: 157.3 dB on day 27.3 (4 Apr 08:34 UTC, with immersion taken as 8 Mar 00:30 UTC), 157.2 dB on day 28.3. Unit spread −3/+2 dB. With probability 0.2, an extra 3-15 dB loss, because rated output covers only 80 % of the sphere. With probability 0.25, an extra 0-20 dB loss from partial shielding or burial. P(at least one ULB transmitting at day 27-28 | wreck at the site) is 0.7-0.9, from the Metron/BEA 0.8 per ULB and the FDR battery being past expiry.
- **Propagation.** Direct up-going ray in the WOA23 profile (surface 23.2 °C, 1,530.7 m/s; minimum 1,484 m/s at 1,000 m; bed 1,531.5 m/s), with ray-tube spreading and Francois-Garrison absorption at 37.5 kHz along the ray. Absorption is 7.2 dB/km at the surface, peaks at about 9.2 dB/km near 500-800 m and falls to 5.2 dB/km at the bed. The path mean is 7.4 dB/km, so absorption takes 34.0 dB on the vertical path and TL overhead is 107.2 dB. Direct rays reach the surface out to 31 km, so there is no refraction shadow within the geometry of interest. ±5 % 1-sigma on absorption.
- **Noise.** APL-UW wind noise at 3.6 m/s gives 32.6 dB re 1 µPa²/Hz at 37.5 kHz; thermal noise is 16.5. Receiver self-noise is 20-35 and boat or mother-ship noise 20-40, power-summed.
- **Receiver.** DI 13-18 dB (25-30° cone). Effective band 100-2,000 Hz, log-uniform (from the aural critical band up to the 2 kHz receiver band). DT 0-10 dB. Pointing: with probability 0.3-0.8 the hydrophone is aimed downward (0-3 dB loss); otherwise it is aimed near horizontal while searching (10-25 dB loss off-axis at the 45-90° depression of a sea-floor source). Fluctuation sigma 2-5 dB; P = P_tx · Φ(SE/σ).
- **Three calibrations of receiver performance.** A: the first-principles equation above. B: SE = 0 at the manufacturer's practical range (2.0-3.6 km, uniform), for a new 160.5 dB source, near-surface absorption 7.9 dB/km and reference wind 5-8 m/s. C: SE = 0 at ATSB's favourable-conditions range (4.0-5.0 km), with reference wind 2-4 m/s. In B and C the site adds 0-6 dB of surface noise against the reference.

| Calibration | SE overhead (dB), 5/50/95 % | Same, losses removed | P(detect) overhead, mean | P at 2 km / 3 km |
|---|---|---|---|---|
| A first principles | −37.1 / −14.9 / +2.2 | −12.4 / −2.7 / +6.8 | 0.081 | 0.037 / 0.011 |
| C ATSB favourable | −39.4 / −18.3 / −3.1 | −12.9 / −6.1 / +0.6 | 0.023 | 0.0059 / 0.00082 |
| B maker's range | −53.5 / −31.1 / −13.8 | −28.8 / −18.9 / −9.5 | 2.4 x 10^-4 | 3.1 x 10^-5 / 2.2 x 10^-6 |

(Values at 2 and 3 km are read from `pdet_vs_offset.csv`.) Only calibration A, with all losses removed and the receiver at its best, gives a positive median-to-upper signal excess overhead. The manufacturer's own range statement places the overhead signal 10-29 dB below threshold.

![Water column]({{artifact:art_3f52be83-f18b-48b7-b587-8a74a9794c66}})

![Detection against horizontal offset]({{artifact:art_fc455a0f-8dad-4537-bebf-402670d1f354}})

Artifact links: figures haixun-water-column.png (version 4bf8a8bb-fab7-4067-818f-5f4784b8ed12), haixun-detection-vs-offset.png (8d576cd3-54d6-45a4-9090-c2ab389feaf6), haixun-bayes-factor-sensitivity.png (10895d1d-22a1-469e-aa2b-e0f3398ec9f2).

## 4. Geometry test (Q5 item 4)

- **Hard-limit reading.** With the practical range taken as a hard slant-range limit (2,000 m, or ATSB's 4,500 m), no beacon position at 4,577 m depth can produce even the first contact, since the minimum slant range is 4,575 m. To produce both contacts with the second weaker by at least 3 dB, the receiver must reach a slant range of 4,908 m (contacts 2 km apart; beacon 0.22 km from the first contact) or 5,006 m (3 km apart; beacon 0.97 km from the first contact).
- **Probabilistic reading.** The overhead signal excess must be at least +2.9 dB (2 km separation) or +3.8 dB (3 km separation). The probability of that is 0.041 / 0.031 under calibration A, 0.0013 / 0.0006 under C and 0.000 under B (no draws in 200,000).
- **Duration.** A boat drifting at 0.1-0.3 m/s moves 90-270 m in 15 min, which changes TL by less than 0.1 dB near overhead. A 15-min contact is therefore consistent with a fixed source if the source is above threshold at all. The reported loss of signal when the head angle changed matches a directional receiver aimed at a source nearly straight below. It matches equally a nearby source in the beam.

Answer: a single fixed beacon is geometrically possible only in the upper tail of the first-principles calibration, and it is excluded under the manufacturer's and ATSB's range statements.

## 5. Follow-up searches and P(miss | beacon present) (Q5 item 5)

| Search | Date (day) | Equipment / range | P(miss given a transmitting beacon), used | Basis |
|---|---|---|---|---|
| HMS Echo | 6 and 8 Apr (29.3, 31.3) | hull-mounted positioning system, 27-30.5 kHz design, retuned to 37.5 kHz | 0.2-0.7 | Out-of-band response and ship self-noise against a large array gain. No track or detection range is published: **not assessed at this depth** beyond the range. |
| Submarine (HMS Tireless, C) | about 6-8 Apr | not published | 0.2-0.8 | Unknown sensor coverage at 37.5 kHz. |
| AP-3C sonobuoys | 6-17 Apr | 300 m hydrophone, up to 4,000 m | 0.5-0.95 | Computed: from the bed to 300 m is 4,277 m slant with 31.5 dB absorption. Calibrated to SE = 0 at 4,000 m for a new source, SE is −5.5 dB on day 29 and −5.7 dB on day 31. Drop positions are unpublished. |
| Ocean Shield TPL | not at site | max effective 3 km | 1 (not applicable) | Towed near 21 S 104 E only. |
| Battery stop between day 28 and 29-31 | — | — | 0.05-0.3 | 30-day minimum, 40-day predicted maximum; FDR battery past expiry. |
| Chinese vessels Donghaijiu 101 and navy 999 (8 Apr, 432 km²) | 8 Apr | not published | not used | Equipment unknown; **not assessed**. |

The joint factor P(no reacquisition | recorders within 2 km) has mean 0.45. It is a judgement range, not a measurement, and it dominates B_H.

## 6. B_H and sensitivity (Q5 item 7)

- **Operational hypothesis.** H_H is read as "MH370's recorders lie on the sea floor within 2 km (uniform disc) of 25.975 S 101.461 E". The data are the two reported contacts (the second 2-3 km west and weaker) and the failed follow-ups. The pre-registration wording ("the contact came from a beacon") assumes the outcome, so it cannot give a likelihood ratio (deviation 1).
- **Likelihood.** Under H_H, with the beacon transmitting, each contact is a true detection (p from section 3) or a false contact (f). The pair is "much weaker" with probability logistic((SE1 − SE2 − 3)/2) if both contacts are true, and 0.5 otherwise. With no beacon (or the beacon not transmitting), the contacts are false (f1 for the first; f2 = 0.1-0.7 for a repeat on the next day) and there is no reacquisition.
- **False-contact rate.** f1 = 0.02-0.5 per listening day, log-uniform. Empirical anchor: all three surface or towed assets listening near 37.5 kHz in April 2014 (Echo 2 Apr, Haixun 4-5 Apr, Ocean Shield 5-10 Apr) reported unconfirmed contacts within days, and none was from MH370 at those sites. Shared nuisance parameters are marginalised in numerator and denominator alike; 100,000 draws.

| Calibration | B_H (ln) | 5/50/95 % of B(θ) | Contacts only | Follow-up misses only | Losses removed (upper) |
|---|---|---|---|---|---|
| A first principles | 0.586 (−0.53) | 0.32 / 0.48 / 2.11 | 1.45 | 0.45 | 0.98 |
| C ATSB favourable | 0.475 (−0.74) | 0.31 / 0.46 / 0.73 | 1.09 | 0.45 | 0.58 |
| B maker's range | 0.448 (−0.80) | 0.31 / 0.45 / 0.59 | 1.00 | 0.45 | 0.45 |

Headline (mean of A and B, as pre-registered physics and manufacturer bounds): **B_H = 0.52, ln B_H = −0.66**. Sensitivity range over everything above: **0.31-2.1** (ln −1.15 to +0.75). On the f1 × q grid of calibration A the range is 0.38-3.62. B_H exceeds 1 only if the follow-up searches were nearly blind (joint miss ≥ 0.4) and false contacts were rare (f1 < 0.05).

**Prior-free statement.** B_H is P(data | H_H)/P(data | not H_H). It contains no prior on where the aircraft is. To obtain P(H_H | data), multiply the prior odds of the 2-km disc (from run J or another flight posterior, labelled by run and 00:19 option, computed in the flight leg) by B_H. Because B_H is between about 0.3 and 2, the Haixun contacts can move any prior by at most a factor of about 2-3 in either direction. They cannot make the site credible if the flight prior gives it little mass, and they do not exclude it.

![Bayes factor sensitivity]({{artifact:art_8c8336b5-383c-4e5f-a57b-da1703b82209}})

## 7. Alternative explanations (Q5 item 6) — qualitative, no recordings

1. **Own equipment.** 38 kHz is a standard echo-sounder and Doppler-log frequency and lies inside the ULB tolerance of 37.5 ± 1 kHz. A 2 kHz receiver band admits it. A sounder in a shallow range setting can ping at about 1 per second. Haixun 01's fitted sonar suite is not published (**not assessed**). A test pinger in the locator kit is a further candidate.
2. **Sperm whales.** Usual clicks have inter-click intervals of about 0.5-1 s, in trains lasting minutes, with broadband energy that reaches tens of kHz. Source levels are very high, so they are audible through a 37.5 kHz receiver at kilometres (literature values, grade B, not read in this session). ATSB 2017 p.37 lists marine life as a cause of false detections.
3. **Other 37.5 kHz sources.** Aircraft-dropped datum buoys are radio, not acoustic. The sonobuoys started on 6 April, after the contacts. Animal-tracking tags use 69 or 180 kHz and are detectable only to about 400 m (ATSB 2017 p.40). None fits.
4. **Doppler and aliasing.** Boat motion of 0.5 m/s shifts 37.5 kHz by about 12 Hz, which is negligible against a 2 kHz band. The DPL-275 is an analogue heterodyne receiver, so sampling aliasing does not apply. An image response is possible but unquantified.
5. **Operator expectation.** The crew was listening at the expected frequency for a 1 pulse/s train. A tuned receiver reports the dial frequency, so "37.5 kHz" is not an independent measurement. This is why the contact features carry little discriminating power (f2 and the feature probability are the same under both hypotheses).

## 8. COVERAGE

- **(a) Feasible set.** A recorder beacon anywhere in the 2-km disc on a bed of 4,570-4,610 m (GEBCO 2020 within 3 km). Either ULB may be transmitting (CVR in date; FDR past expiry). Any receiver aim. Contact separations of 2-3 km (press 2 km, ATSB 3 km).
- **(b) Model reach.** Direct path only. Bed-reflected and scattered paths are not modelled: they are negligible for a source on the bed, but local terrain shadowing by bed slope is not modelled (gap: needs AusSeabed / OI 2018 bathymetry at metre scale). The receiver is fixed at 2 m depth; surface-image interference is set to 0 dB (directional receiver aimed down; ±3 dB not carried, a reach gap). There is a single beacon; two simultaneous beacons, each weaker, are not modelled (gap, small effect on B_H because both would be loud only together).
- **(c) Proposal coverage.** Monte Carlo over all nuisance ranges: 200,000 draws for the sonar curves and 100,000 for B_H, with the beacon uniform in the disc and the separation uniform 2-3 km. No posterior weights, so ESS is not applicable. Monte Carlo noise in B_H is below 0.01.
- **Parameter bounds and sources.** Source level: DK100 manual. Ranges: DK100 manual, ATSB 2014/2017. DI and bandwidth: grade C datasheets. Follow-up miss probabilities, false-contact rate, pointing mix and shielding: **judgement, no source**. These are the declared gaps; they are carried as wide ranges and shown as sensitivity (figure panel a).

## 9. Open issues

1. The ATSB and Phoenix TPL logs, the Haixun 01 audio (CCTV footage only) and the sonobuoy drop positions are not public. Each would replace a judgement range.
2. The DPL-275 manual (sensitivity, self-noise, band) has not been read from a primary Teledyne document; grade C only.
3. HMS Echo's search tracks and system response at 37.5 kHz are unpublished. FOI or UK MoD request.
4. Haixun 01's own sonar and echo-sounder frequencies are not known.
5. Malaysian 2015 interim report and SIR 2018 ULB pages are cited from the 17 Oct read; not re-read in this session.
6. Composition: B_H enters once, as an acoustic-beacon term at the 2-km disc around 25.975 S 101.461 E. It must not be folded into the searched-areas module's seabed or sonobuoy coverage (the same follow-up searches would be counted twice).

**Hydro caveats travel with this number:** the high-frequency beacon term is independent of the sound-channel propagation slope misfit and the coupling uncertainty, which apply only to the H01W/Kadri legs.
