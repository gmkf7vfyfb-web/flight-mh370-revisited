# End of flight: points for the paper (data, method, results, figures)

7 November 2026. Final end-of-flight run of 7 November 2026. Each section gives ASD-STE100 points first, then one technical paragraph. Numbers come from the run tables. In-text citations use the Harvard style of the Journal of Navigation; the full references are in Section 6 and in the project citation ledger.

## 1. Data and evidence

### 1.1 Points (ASD-STE100)

- We start from the flight model at 00:10:59 UTC. It gives each path its position, speed, heading, height, mass and fuel in each tank (Davey et al., 2016).
- We use two route models. The main model is the Davey model with the fuel model and the radar data. The second model uses waypoints; only this model includes a planned descent.
- We use the satellite data at 00:19. The aircraft asked to log on at 00:19:29. The ground station answered, and the aircraft sent a second message at 00:19:37 (Ashton et al., 2015; Davey et al., 2016).
- Each message gives a timing value (BTO) and a frequency value (BFO). The timing values are 18,400 µs and 18,380 µs. The frequency values are 182 Hz and −2 Hz.
- The 18,380 µs value includes the correction for the second message type, derived from Davey et al. (2016).
- We use the time from a loss of power to a log-on request. The auxiliary power unit needs about 60 s, and the satellite unit needs about 60 s more (ATSB, 2015; Malaysian ICAO Annex 13 Safety Investigation Team, 2018).
- We use Holland's study of the frequency at start-up. It shows that the frequency can be offset for a period after the unit starts (Holland, 2018).
- We use ten Boeing 777 engineering-simulator runs of the end of flight. Six runs have normal electrical power and four runs have alternate power (Boeing, 2016; ATSB, 2016).
- We use 42 real accidents in which a large commercial jet aeroplane dived or descended fast. They occurred from 1974 to 2022. The investigation reports give the data (Table 1).
- The 42 aeroplanes come from eight manufacturers. 35 have two engines, four have three engines and three have four engines.
- We put the accidents in three groups: 12 push-overs, 18 roll-offs or upsets, and 12 steady descents or stalls.
- Twelve accidents give measured values for the start of the dive. The four Boeing alternate-power runs give values of the same quantities. Together they make the dive prior (Section 2).
- We compare all 42 accidents with the 00:19 data. We do not remove an accident because it does not fit. Removal would bias the result.
- We use the Boeing 777-200ER mass, wing area and speed limits from type documents (FAA, 2025; Boeing Commercial Airplanes, 2024).
- We use the structural limits on load factor in the certification rules (EASA, 2023; FAA, 2016).
- We use the standard atmosphere (ISO, 1975) and the ERA5 winds at each path position (Hersbach et al., 2020).
- We do not use the break-up of the aircraft in this stage. Break-up belongs to the settling stage.

**What to call the aeroplanes.** We recommend "large commercial jet aeroplanes". In ICAO terms they are large aeroplanes (maximum certificated take-off mass above 5,700 kg) used in commercial air transport (ICAO Annexes 6 and 8; not yet in the citation ledger). All are turbofan aeroplanes certificated to transport-category standards: 14 CFR Part 25, CS-25, or the national equivalent (AP-25 for the An-148; the earlier Soviet standards for the Tu-154). "Transport-category aeroplanes" is accurate for the western types but not strictly for the two Soviet-certified types, so "large commercial jet aeroplanes" with this note is the safer term. The set includes twins (35), trijets (4: B727 ×2, Tu-154, DC-10) and quadjets (3: B747SP, B747, BAe 146). Two flights carried cargo only (Atlas Air 3591, West Air Sweden 294).

### 1.2 Technical paragraph

The end-of-flight stage takes the core filtering distribution at 00:10:59 UTC as its prior, so every path carries its own position, velocity, mass and per-tank fuel, and the core evidence. Its own data are the two 00:19 bursts — the log-on request at 00:19:29 (BTO 18,400 µs, σ 63 µs; BFO 182 Hz) and the log-on acknowledge at 00:19:37 (BTO 18,380 µs after correction, σ 43 µs; BFO −2 Hz), with the BFO noise 4.32 Hz as in the core — and the fact of the log-on itself, whose timing after a loss of main AC power follows the APU and SDU start-up times. Dynamics are informed by three sources: the ten Boeing 777 engineering-simulator scenarios of April 2016, the published accident record (42 cases, 1974–2022), and type-certificate and certification data for the Boeing 777-200ER. Twelve accident cases and the four alternate-power simulations carry measured build-up values (largest 8-s mean downward acceleration, 15 values; time from descent onset to 15,000 ft/min, 11; delay from first flame-out to onset, 6); all 42 are compared with the 00:19 descent rates, without exclusion.

### 1.3 Why Air France 447 was not used to fit the dive model

- We did use Air France 447. It is case 36 in the table, in the group of steady descents and stalls.
- We compared it with the 00:19 data, as for all 42 cases. Its peak descent was about 10,900 ft/min. It cannot reach the descent rate that the 00:19:37 frequency needs.
- We did not use it to fit the dive model. The dive model needs a dive build-up to 15,000 ft/min. Air France 447 stalled with the nose up and never reached 15,000 ft/min, so it has no value for the build-up quantities.
- Its descent began with crew inputs (nose-up), not with a loss of power. So it gives no value for the delay from power loss to the dive.
- It informs other stages: the water impact and break-up (intact at impact, about 1,000 floating parts; settling) and the search method (Stone et al., 2014; searched areas).

## 2. Methodology

### 2.1 Points (ASD-STE100)

- Each path continues from 00:10:59 to the sea. We use three families: no pilot after fuel exhaustion, a pilot after fuel exhaustion, and a planned descent (waypoint model only).
- The fuel model gives the time of each engine flame-out. The electrical configuration gives the time of the power loss. The power loss starts the log-on clock.
- With no pilot and alternate power, a new dive model flies the descent. It is a point-mass model with speed, flight-path angle and heading as states.
- In the dive model, the downward acceleration grows from the start of the dive until the descent rate is 15,000 ft/min. The bank grows with it. After that, nobody moves the controls.
- The model includes drag, a drag rise near Mach 1, the stall limit and the structural limits on load factor.
- The model can pull out of the first dive, as the Boeing runs did. The height, load factor and bank of the pull-out come from the Boeing runs.
- A fitted prior gives the three dive quantities: the strength of the build-up, its duration and the delay before it. The prior is fitted to the real accidents and the Boeing runs, in two classes: no effective crew input, and crew input.
- We wrote the two tests before we ran them. Test A: we remove each case in turn and predict it. Test B: we remove each Boeing run in turn and predict its descent.
- Test A passed: 0 of 15, 1 of 11 and 0 of 6 values fell outside the central 95 %. Test B passed: 15 of 16 values fell inside the central 90 %.
- A normal-power glide replays one of the six normal-power Boeing runs. A piloted descent uses the push-over prior of the earlier runs: descent rate 6,500–40,000 ft/min, load-factor floor −1.0 to 0.8 g, hold 0–300 s.
- We aim the dives at the 00:19 data by importance sampling. Exact weights remove the effect of the aiming. No case is chosen because it fits.
- We score each path against the 00:19 data in nine ways (Table 2). We compare the evidence only between treatments that use the same data.
- We use 16 seeds for the Davey model and 24 seeds for the waypoint model. We give 90 % intervals from the spread between seeds.
- The method follows the Bayesian search for Air France 447 in one respect: each stage passes weighted samples to the next (Stone et al., 2014).
- An independent review checked the code before the production run. It found one blocking defect and six major issues. We corrected or declared all of them.
- We flag a result as provisional when fewer than 500 effective no-pilot paths support it.

### 2.2 Technical paragraph

Equation (12) continues each core path from its hand-off epoch to impact under a descent family H_E and an electrical configuration K, weighted by the 00:19 likelihood of equations (13)–(15). For the no-pilot alternate-configuration family, the descent is a three-degree-of-freedom point-mass model (A9) whose build-up law (A10) carries two case-informed quantities, the build-up acceleration a8 and the time T15 from onset to 15,000 ft/min, with Lock's fourth-power drag rise, a Mach-dependent stall limit and the CS 25.337 load-factor limits (A11), and an optional arrest with Boeing-derived pull-out parameters (A12); the equations of motion follow Hull (2007) and the drag rise follows Gur et al. (2010). The three build-up quantities have a hierarchical lognormal prior over two classes of crew input (A13), fitted by random-walk Metropolis sampling (Metropolis et al., 1953; Hastings, 1970; Gelman et al., 2013), and checked by a pre-registered leave-one-out probability-integral-transform test (A14; Dawid, 1984). Dives are aimed at the 00:19 window by importance sampling with exact weights (A15; Robert and Casella, 2004), effective sample sizes follow Kong et al. (1994), low-weight rows are thinned by unbiased Russian roulette (Kahn, 1955), and evidence is pooled over seeds (A16) and compared only within a data group. ERA5 winds (Hersbach et al., 2020) move each path.

## 3. Results

### 3.1 Points (ASD-STE100)

- The impact latitude does not depend much on the use of the 00:19 data. The median is 36.4° S to 36.8° S for the Davey model and 36.8° S to 37.2° S for the waypoint model, in every treatment.
- When we use both 00:19 frequencies, every path descends faster than 10,000 ft/min at 00:19:37. The median descent rate is about 15,000 ft/min (frequencies as recorded) or 19,500 ft/min (Holland offset).
- The aircraft then hits the sea about 1.4–1.9 min after 00:19:29 (median, by treatment).
- With both frequencies, 88 % (as recorded) to 93 % (Holland offset) of impacts are within 25 NM of the 7th arc for the Davey model, and 86 % to 90 % for the waypoint model.
- With the timing values only, the median impact is about 17–18 min after 00:19:29, and only 73 % of impacts are within 25 NM.
- The frequencies make the impact area smaller. The 90 % region falls from about 128,000 km² (timings only) to about 54,000 km² (Holland offset) for the Davey model. This is a factor of 2.4. For the waypoint model the factor is 2.3.
- Holland's start-up offset fits the 00:19 data better than the frequencies as recorded: log evidence +0.31 (90 % interval +0.18 to +0.46) for the Davey model and +0.23 (+0.04 to +0.39) for the waypoint model. This is weak evidence.
- An offset on the second frequency only fits worse than the frequencies as recorded: −0.43 (−0.60 to −0.27) and −0.49 (−0.68 to −0.30).
- When we use both frequencies, all no-pilot weight is in the alternate electrical configuration.
- The data do not decide whether a pilot was present. The no-pilot share is 0.52 with the timing values only and 0.70 with the Holland offset. With the Holland offset it changes from 0.63 to 0.71 under our alternative assumptions.
- When we use both frequencies, 72 % to 86 % of impacts have a kinetic energy of 4 GJ or more. The median is about 9.2 GJ. This is at or above the top of the Boeing range (6.4–9.0 GJ), so we report energy as a sensitivity.
- The planned descent keeps 1.8 % to 2.7 % of the weight when we use both frequencies, and 16.8 % when we use no data after 00:11.
- Three results are provisional because they rest on few effective no-pilot paths: frequencies as recorded (Davey model, 156 paths; waypoint model, 261) and an offset on the second frequency only (Davey model, 489).

### 3.2 The most important results, in order, and why

1. **If the 00:19 frequencies come from the aircraft, the aircraft was in a fast descent at 00:19:37 and hit the sea within about two minutes, close to the 7th arc.** Every path is descending faster than 10,000 ft/min at 00:19:37 under every treatment that uses both frequencies, and 88–93 % of impacts lie within 25 NM of the arc (Davey model). This is the result that sets the width of the search area, and it holds for both route models and for every interpretation of the frequencies we tested. It is conditional on the frequencies being aircraft-generated.
2. **The along-arc position is set by the flight before 00:11, not by the 00:19 data.** The median impact latitude moves by less than 0.5° across all nine treatments. The search length therefore does not depend on how the 00:19 data are interpreted, and the disagreement over those data does not move the area along the arc.
3. **Using the frequencies shrinks the 90 % impact region by a factor of about 2.3–2.4** (Davey model, 128,000 to 54,000 km²; waypoint model, 95,000 to 41,000 km²), because it removes the long glides that carry the aircraft 50–150 NM from the arc. This is the practical value of the 00:19 data for search planning.
4. **The data favour Holland's start-up offset, but only weakly** (+0.2 to +0.3 nat), and they disfavour an offset on the second frequency only (about −0.45 nat, so about 0.7 nat below Holland). The evidence is too weak to choose an interpretation, so the paper reports the results under each interpretation.
5. **The data cannot tell whether a pilot was present at the end.** For the Davey model the no-pilot share moves with the assumptions (0.44–0.72 across treatments and variants). This is a negative result, but it is important: it prevents an over-claim, and it shows that the impact area does not depend much on the answer.
6. **High-energy impact is likely if the frequencies are used** (72–86 % at 4 GJ or more), which supports fragmentation and is the input to the debris, settling and hydroacoustic stages. The energy level itself is at the top of the Boeing range and is reported as a sensitivity.

Other results: the planned descent becomes small once the 00:19 data are used (1.8–2.7 %); all no-pilot weight moves to the alternate configuration under the frequencies; without the frequencies the impact comes about 17–18 min after the log-on and the 95 % distance from the arc is about 70 NM.

### 3.3 Technical paragraph

Across the nine headline treatments the median impact latitude is 36.42–36.82° S (Davey model with the fuel model) and 36.77–37.22° S (waypoints), with 90 % seed intervals of about ±0.15°. Using both BFOs forces a descent of at least 14,400 ft/min at 00:19:37 in every path (5th percentile; as recorded) or about 16,200 ft/min (Holland offset), an impact 1.4–1.9 min after 00:19:29 (median), and a 95 % distance from the 7th arc of 31–38 NM (Davey model), against 69 NM with the BTOs alone, compared with the 25 NM corridor of the underwater search (ATSB, 2017). Within the both-frequency group, Holland's start-up offset has ln B = +0.31 (+0.18 to +0.46) against the as-recorded values; the R1200-only offset has −0.43 (−0.60 to −0.27). The no-pilot share is 0.52 (as recorded; provisional, ESS 156) to 0.70 (Holland; ESS 1,672), and 0.63–0.71 across eight variants under the Holland offset. The 90 % HPD area is 54,165 km² (Holland) against 127,598 km² (BTOs only) for the Davey model, after a 0.1° Gaussian smoothing of the impact density.

## 4. Tables for the paper

Table 1. Real accident cases. Group as in the master case table. 'Used in the dive prior' lists the build-up quantities that the case supplies (a8: largest 8-s mean downward acceleration; T15: time from onset to 15,000 ft/min; delay: first flame-out to onset). All 42 cases are compared with the 00:19 descent rates.

| No. | Flight | Aircraft | Manufacturer | Engines | Year | Group | Used in the dive prior | Investigation report |
|---|---|---|---|---|---|---|---|---|
| 1 | EgyptAir 990 | B767 | Boeing | 2 | 1999 | push-over | a8, T15 | NTSB (2002a) |
| 2 | Atlas Air 3591 | B767F | Boeing | 2 | 2019 | push-over | a8, T15 | NTSB (2020) |
| 3 | SilkAir 185 | B737 | Boeing | 2 | 1997 | push-over | a8 | NTSC (2000) |
| 4 | flydubai 981 | B737 | Boeing | 2 | 2016 | push-over | a8 | IAC (2019a) |
| 5 | Tatarstan 363 | B737 | Boeing | 2 | 2013 | push-over | — | IAC (2015) |
| 6 | West Air Sweden 294 | CRJ200F | Bombardier | 2 | 2016 | push-over | — | SHK (2016) |
| 7 | Saratov 703 | An-148 | Antonov | 2 | 2018 | push-over | a8 | IAC (2019b) |
| 8 | Lion Air 610 | B737 MAX | Boeing | 2 | 2018 | push-over | — | KNKT (2019) |
| 9 | Ethiopian 302 | B737 MAX | Boeing | 2 | 2019 | push-over | — | EAIB (2022) |
| 10 | Qantas 72 | A330 | Airbus | 2 | 2008 | push-over | a8 | ATSB (2011) |
| 11 | PSA 1771 | BAe 146 | British Aerospace | 4 | 1987 | push-over | — | NTSB (1989) |
| 12 | Gulf Air 072 | A320 | Airbus | 2 | 2000 | push-over | — | Civil Aviation Affairs, Bahrain (2002) |
| 13 | TWA 841 | B727 | Boeing | 3 | 1979 | roll-off or upset | a8, T15 | NTSB (1981) |
| 14 | China Airlines 006 | B747SP | Boeing | 4 | 1985 | roll-off or upset | T15, delay | NTSB (1986) |
| 15 | Adam Air 574 | B737 | Boeing | 2 | 2007 | roll-off or upset | a8, T15, delay | NTSC (2008) |
| 16 | AirAsia 8501 | A320 | Airbus | 2 | 2014 | roll-off or upset | a8, T15 | KNKT (2015) |
| 17 | China Eastern 5735 | B737 | Boeing | 2 | 2022 | roll-off or upset | a8, T15 | CAAC (2022) |
| 18 | Lauda Air 004 | B767 | Boeing | 2 | 1991 | roll-off or upset | a8 | Aircraft Accident Investigation Committee, Thailand (1993) |
| 19 | Sriwijaya Air 182 | B737 | Boeing | 2 | 2021 | roll-off or upset | — | KNKT (2022) |
| 20 | Gol 1907 | B737 | Boeing | 2 | 2006 | roll-off or upset | — | CENIPA (2008) |
| 21 | Northwest 6231 | B727 | Boeing | 3 | 1974 | roll-off or upset | — | NTSB (1975) |
| 22 | USAir 427 | B737 | Boeing | 2 | 1994 | roll-off or upset | — | NTSB (1999) |
| 23 | Birgenair 301 | B757 | Boeing | 2 | 1996 | roll-off or upset | — | JIAA (1996) |
| 24 | Tarom 371 | A310 | Airbus | 2 | 1995 | roll-off or upset | — | Ministry of Transport, Romania (2000) |
| 25 | Air India 855 | B747 | Boeing | 4 | 1978 | roll-off or upset | — | Government of India (n.d.) |
| 26 | Flash Airlines 604 | B737 | Boeing | 2 | 2004 | roll-off or upset | — | Ministry of Civil Aviation, Egypt (2006) |
| 27 | Kenya Airways 507 | B737 | Boeing | 2 | 2007 | roll-off or upset | — | CCAA (2010) |
| 28 | Ethiopian 409 | B737 | Boeing | 2 | 2010 | roll-off or upset | — | Ministry of Public Works & Transport, Lebanon (2012) |
| 29 | Austral 2553 | DC-9 | McDonnell Douglas | 2 | 1997 | roll-off or upset | — | CIADA (n.d.) |
| 30 | Copa 201 | B737 | Boeing | 2 | 1992 | roll-off or upset | — | Dirección de Aeronáutica Civil, Panama (n.d.) |
| 31 | Germanwings 9525 | A320 | Airbus | 2 | 2015 | steady descent or stall | — | BEA (2016) |
| 32 | LAM 470 | E190 | Embraer | 2 | 2013 | steady descent or stall | — | DAAI (2016) |
| 33 | EgyptAir 804 | A320 | Airbus | 2 | 2016 | steady descent or stall | — | EAAID (2024) |
| 34 | Alaska Airlines 261 | MD-83 | McDonnell Douglas | 2 | 2000 | steady descent or stall | — | NTSB (2002b) |
| 35 | Helios 522 | B737 | Boeing | 2 | 2005 | steady descent or stall | — | AAIASB (2006) |
| 36 | Air France 447 | A330 | Airbus | 2 | 2009 | steady descent or stall | — | BEA (2012) |
| 37 | Pinnacle 3701 | CRJ200 | Bombardier | 2 | 2004 | steady descent or stall | — | NTSB (2007) |
| 38 | Pulkovo 612 | Tu-154 | Tupolev | 3 | 2006 | steady descent or stall | — | IAC (2007) |
| 39 | West Caribbean 708 | MD-82 | McDonnell Douglas | 2 | 2005 | steady descent or stall | — | JIAAC (2010) |
| 40 | Turkish Airlines 981 | DC-10 | McDonnell Douglas | 3 | 1974 | steady descent or stall | — | Secrétariat d'État aux Transports (1976) |
| 41 | Aeroflot 593 | A310 | Airbus | 2 | 1994 | steady descent or stall | — | Aircraft Accident Investigation Commission, Russia (n.d.) |
| 42 | Air Algerie 5017 | MD-83 | McDonnell Douglas | 2 | 2014 | steady descent or stall | — | Mali Commission of Inquiry (2016) |
| B3, B4, B6, B10 | Boeing 777 simulations, alternate power | B777-200ER | Boeing | 2 | 2016 | no pilot input | a8, T15, delay | Boeing (2016); ATSB (2016) |
| B1, B2, B5, B7, B8, B9 | Boeing 777 simulations, normal power | B777-200ER | Boeing | 2 | 2016 | no pilot input | — (glide replay) | Boeing (2016); ATSB (2016) |

Table 2. Treatments of the 00:19 data.

| Treatment | Data used |
|---|---|
| No data after 00:11 | none (reference) |
| Log-on event only | the log-on and its timing; no 00:19 value |
| Both timings | both BTOs |
| Both timings + first frequency | both BTOs, BFO at 00:19:29 as recorded |
| Both frequencies as recorded | both BTOs, both BFOs as recorded |
| Both frequencies, Holland offset | both BTOs, both BFOs with a start-up offset of 17–136 Hz (00:19:29) and 17–130 Hz (00:19:37) |
| Holland offset, zero floor | as above, offsets from 0 Hz |
| Offset on the second frequency | both BTOs, BFO at 00:19:29 as recorded, offset of 17–130 Hz on 00:19:37 only (Ashton premise) |
| Offset on the second frequency, zero floor | as above, offset from 0 Hz |

## 5. Figures to choose from (Journal of Navigation form)

All files are greyscale, 127 mm wide, with no title and no notes on the image; panel labels are letters only; each has a caption text and a proof with the caption beneath. The PNG is 600 dpi for Word; the PDF is vector.

| Section | Figure | Word PNG | PDF | Recommendation |
|---|---|---|---|---|
| Data and evidence | Build-up of real dives and Boeing simulations against the 00:19 descent rates (your chosen chart, 7 Nov) | [PNG]({{artifact:9b6eed78-93b7-4c50-81a8-7ddcaa6bdd31}}) | [PDF]({{artifact:99babcdf-6299-4a4f-8c3b-0ecffbb6c10f}}) | Recommended: main text |
| Data and evidence / Methodology | Case values and the fitted dive prior | [PNG]({{artifact:1d9a45d5-7a1c-4eef-9203-adb40b9ffd85}}) | [PDF]({{artifact:b366ef3c-de99-41cb-86ca-dcf7b71c0784}}) | Recommended: appendix or supplement |
| Methodology | Leave-one-out check of the dive model against each Boeing alternate-power simulation | [PNG]({{artifact:9e98533f-c799-4db3-b6c8-a698fd59317c}}) | [PDF]({{artifact:81bc6a43-7076-4a03-a78a-1c1f1766304e}}) | Recommended: main text if space allows, else appendix |
| Results | Impact regions 50/90/99 %, Davey model with the fuel model, six treatments | [PNG]({{artifact:8ae974db-62d2-48b3-b9ae-60cf1b5ddb23}}) | [PDF]({{artifact:864d5c1f-28f4-4863-bf80-df033b2f1a07}}) | Recommended: main results figure |
| Results | Impact regions 50/90/99 %, waypoint model, six treatments | [PNG]({{artifact:1fffb7f1-6aa9-41ac-9419-373912eab2d4}}) | [PDF]({{artifact:3dc76bdc-775f-4afd-b15c-6266ad595872}}) | Supplement, or pair with the Davey map |
| Results | Impact regions of three treatments overlaid, Davey model with the fuel model | [PNG]({{artifact:4b9c037e-3ad2-41dc-af75-ace7f70182ba}}) | [PDF]({{artifact:c2de879a-c7b9-4948-831c-6cf7348e45aa}}) | Alternative to the six-panel map when space is short |
| Results | Impact regions of three treatments overlaid, waypoint model | [PNG]({{artifact:13794a15-9b14-44c3-9267-1fcac199dd2b}}) | [PDF]({{artifact:2542e1cf-38b7-42ab-88e1-2d808364e050}}) | Supplement |
| Results | Distance from the 7th arc at impact (both route models) | [PNG]({{artifact:108c0401-2663-4e71-814f-2b4bc83126b4}}) | [PDF]({{artifact:8ac9ee68-0863-4073-844d-e815bdb05136}}) | Recommended: main text (search width, 25 NM) |
| Results | Descent rate at 00:19:37 under four treatments | [PNG]({{artifact:fb0d07e6-c450-45cb-ad2c-53ee678b3bcd}}) | [PDF]({{artifact:3917eff8-1433-4e12-90aa-3b88c3a66916}}) | Recommended: main text (first result) |
| Results | Impact latitude, median and central 90 %, every treatment | [PNG]({{artifact:d702922c-9571-4493-9c37-1e2ea2de12a5}}) | [PDF]({{artifact:088ef15b-d8e9-4d3a-9e90-e632e09aa4fe}}) | Recommended: main text (second result) |
| Results | Log evidence of the frequency interpretations | [PNG]({{artifact:cb43aa71-53dc-4465-9164-8b9d01ffcd9e}}) | [PDF]({{artifact:f82a94fb-6124-4324-94b5-d765d3a65cc5}}) | Main text or a table |
| Results | Impact latitude density and impact time | [PNG]({{artifact:187bffe2-1081-43b6-88b3-47438d5b1547}}) | [PDF]({{artifact:f13c1450-79e2-476b-a77a-c1536c258868}}) | Supplement |
| Results | No-pilot and piloted shares under each assumption | [PNG]({{artifact:79d7e0c1-31fb-459d-94dd-72b8db43215f}}) | [PDF]({{artifact:77be046b-c99e-4b39-8eeb-a211ea1c02da}}) | Supplement (conditional result) |
| Results | Impact kinetic energy and distance from the arc by energy | [PNG]({{artifact:ccdad021-a89b-4110-88d2-7f3b61149737}}) | [PDF]({{artifact:ce539771-ebcc-47ef-a7f4-b76230dd6cf4}}) | Supplement (declared sensitivity) |

Impact maps for every scenario, one PDF each (18 files: 9 treatments × 2 route models), with an index of the 50/90/99 % areas: [eof-impact-hpd-all-scenarios.zip]({{artifact:344ab974-1aaf-4b9e-845c-22e5fc2e0994}}), [index]({{artifact:e64e1a38-8e3b-4298-8cf6-26ee72c5d9a4}}).

Not offered: the earlier chart of power-loss timing against build-up time carries panel headings and a column heading on the image, so it does not meet the Journal rule; it needs letter-only labels before use.

## 6. References

All entries are in the project citation ledger (commit 779def9, `paper/references.bib`). 45 of the 59 entries added on 7 November were verified against the document or its registry record; 10 are partly verified and 4 are marked 'not retrieved – ask Pete' (Tarom 371, Air India 855, Austral 2553, Kish 1965). The China Eastern 5735 entry cites the CAAC preliminary notice, because no final report exists.

- Air Accident Investigation & Aviation Safety Board, Hellenic Republic. (2006). Aircraft Accident Report: Helios Airways Flight HCY522, Boeing 737-31S, at Grammatiko, Hellas, on 14 August 2005. Report 11/2006. Athens. November 2006. https://www.faa.gov/sites/faa.gov/files/2022-11/Helios737_AccidentReport.pdf. Accessed 7 November 2026.
- Aircraft Accident Investigation Bureau, Federal Democratic Republic of Ethiopia. (2022). Investigation Report on Accident to the B737-MAX8 Reg. ET-AVJ Operated by Ethiopian Airlines, 10 March 2019. Report AI-01/19. Addis Ababa. 23 December 2022. https://bea.aero/fileadmin/user_upload/ET_302__B737-8MAX_ACCIDENT_FINAL_REPORT.pdf. Accessed 7 November 2026.
- Aircraft Accident Investigation Commission (Russian Government Commission). (n.d.). Report on the investigation into the crash of A310-308, registration F-OGQS, on 22 March 1994 near the city of Mezhdurechensk (English translation). Moscow.
- Aircraft Accident Investigation Committee of Thailand. (1993). Lauda Air Luftfahrt Aktiengesellschaft Boeing 767-300ER Registration OE-LAV, Dan Chang District, Suphan Buri Province, Thailand, 26 May B.E. 2534 (A.D. 1991). Bangkok. Approved 21 July 1993. https://www.faa.gov/sites/faa.gov/files/LaudaAccidentReport_0.pdf. Accessed 7 November 2026.
- Ashton, C., Shuster Bruce, A., Colledge, G. and Dickinson, M. (2015). The search for MH370. *The Journal of Navigation*, **68**(1), 1–22. https://doi.org/10.1017/S037346331400068X
- ATSB (2016). *MH370 – Search and Debris Examination Update*, AE-2014-054, 2 November 2016. Canberra: Australian Transport Safety Bureau.
- Australian Transport Safety Bureau. (2011). In-flight upset, 154 km west of Learmonth, WA, 7 October 2008, VH-QPA, Airbus A330-303. ATSB Transport Safety Report, Aviation Occurrence Investigation AO-2008-070, Final. Canberra. Released 19 December 2011. https://www.atsb.gov.au/investigations/ao-2008-070. Accessed 7 November 2026.
- Australian Transport Safety Bureau. (2015). MH370 - Definition of Underwater Search Areas. ATSB Transport Safety Report AE-2014-054, 3 December 2015. ATSB, Canberra. https://www.atsb.gov.au/sites/default/files/2022-12/AE-2014-054_MH370-Definition%20of%20Underwater%20Search%20Areas_3Dec2015.pdf
- Australian Transport Safety Bureau. (2017). The Operational Search for MH370. ATSB Transport Safety Report AE-2014-054, 3 October 2017. ATSB, Canberra.
- Boeing Commercial Airplanes (2024). *777-200/-200ER/-300 Airplane Characteristics for Airport Planning*, D6-58329 Rev. E. Seattle, WA: Boeing.
- Bureau d'Enquêtes et d'Analyses pour la sécurité de l'aviation civile. (2012). Final Report on the accident on 1st June 2009 to the Airbus A330-203 registered F-GZCP operated by Air France flight AF 447 Rio de Janeiro - Paris. Le Bourget. Published 5 July 2012. https://www.bea.aero/docspa/2009/f-cp090601.en/pdf/f-cp090601.en.pdf. Accessed 7 November 2026.
- Bureau d'Enquêtes et d'Analyses pour la sécurité de l'aviation civile. (2016). Final Report: Accident on 24 March 2015 at Prads-Haute-Bléone (Alpes-de-Haute-Provence, France) to the Airbus A320-211 registered D-AIPX operated by Germanwings. Report BEA2015-0125. Le Bourget. Published 13 March 2016. https://bea.aero/uploads/tx_elydbrapports/BEA2015-0125.en-LR.pdf. Accessed 7 November 2026.
- Cameroon Civil Aviation Authority. (2010). Technical Investigation into the Accident of the B737-800 Registration 5Y-KYA Operated by Kenya Airways that Occurred on the 5th of May 2007 in Douala. Yaoundé. Released 28 April 2010.
- Centro de Investigação e Prevenção de Acidentes Aeronáuticos (CENIPA), Command of Aeronautics, Brazil. (2008). Final Report A-022/CENIPA/2008: PR-GTD and N600XL, B-737 8EH and EMB-135 BJ Legacy, 29 September 2006. Brasília. https://sistema.cenipa.fab.mil.br/cenipa/paginas/relatorios/rf/en/RF_PR-GTD_N600XL_29_09_06_Eng..pdf. Accessed 7 November 2026.
- Civil Aviation Administration of China, Office of Aviation Safety. (2022). Guanyu '3·21' Donghang MU5735 hangkongqi feixing shigu diaocha chubu baogao de qingkuang tongbao [Notice on the preliminary report of the investigation into the '3·21' China Eastern MU5735 aircraft accident] (in Chinese). Beijing. 20 April 2022. https://www.caac.gov.cn/XXGK/XXGK/TZTG/202204/t20220420_212895.html. Accessed 7 November 2026.
- Civil Aviation Affairs, Kingdom of Bahrain. (2002). Accident Investigation Report: Gulf Air Flight GF-072, Airbus A320-212, Reg. A40-EK, on 23 August 2000 at Bahrain. Manama. https://bea.aero/fileadmin/documents/docspa/2000/a40-ek000823a/htm/a40-ek000823a.html. Accessed 7 November 2026.
- Comisión Investigadora de Accidentes de Aviación, Dirección Nacional de Aviación Civil e Infraestructura Aeronáutica, Uruguay. (n.d.). Informe final de accidente de aviación: McDonnell Douglas DC-9-32, Austral Líneas Aéreas Cielos del Sur S.A., LV-WEG, Nuevo Berlín, R.O.U., 10 de octubre de 1997 (in Spanish). Montevideo.
- Commission d'enquête sur les accidents d'aviation civile, Ministère de l'Équipement, des Transports et du Désenclavement, République du Mali. (2016). Final Report: Accident on 24 July 2014 near Gossi (Mali) to the McDonnell Douglas DC-9-83 (MD-83) registered EC-LTV operated by Swiftair S.A.. Bamako. 22 April 2016. https://bea.aero/fileadmin/uploads/tx_elydbrapports/ec-v140724.pdf. Accessed 7 November 2026.
- Davey, S., Gordon, N., Holland, I., Rutten, M. and Williams, J. (2016). *Bayesian Methods in the Search for MH370*. SpringerBriefs in Electrical and Computer Engineering. Singapore: Springer. https://doi.org/10.1007/978-981-10-0379-0
- Dawid, A. P. (1984). Present Position and Potential Developments: Some Personal Views: Statistical Theory: The Prequential Approach. Journal of the Royal Statistical Society. Series A (General), 147, 278-290. https://doi.org/10.2307/2981683
- Dirección de Aeronáutica Civil, Republic of Panama. (n.d.). [Final report, in Spanish:] Copa Flight 201 Boeing 737-204 Advanced - 6 June 1992 - near Tucuti, Darien - Republic of Panama. Panama City. https://data.ntsb.gov/Docket?ProjectID=15961. Accessed 7 November 2026.
- Directorate of Aircraft Accident Investigations, Republic of Namibia. (2016). Civil Aircraft Accident Report: Aircraft C9-EMC, Embraer 190, Bwabwata National Park, 29 November 2013. Windhoek. Released 15 April 2016.
- Egyptian Aircraft Accident Investigation Directorate, Ministry of Civil Aviation. (2024). [Final investigation report: accident to the Airbus A320-232 SU-GCC, EgyptAir flight MS804, Mediterranean Sea, 19 May 2016]. Cairo. Published 29 October 2024. https://bea.aero/en/investigation-reports/notified-events/detail/accident-to-the-airbus-a320-registered-su-gcc-and-operated-by-egyptair-on-05-19-2016-in-cruise-off-the-egyptian-coast-investigation-led-by-aib-egypt/. Accessed 7 November 2026.
- European Union Aviation Safety Agency. (2023). Certification Specifications and Acceptable Means of Compliance for Large Aeroplanes (CS-25), Amendment 28. ED Decision 2023/021/R, 19 December 2023. https://www.easa.europa.eu/en/document-library/certification-specifications/cs-25-amendment-28
- FAA (2025). *Type Certificate Data Sheet T00001SE, Revision 48: Boeing 777*. Washington, DC: Federal Aviation Administration.
- Federal Aviation Administration. (2016). 14 CFR 25.337 Limit maneuvering load factors. Code of Federal Regulations, Title 14, Part 25. https://www.ecfr.gov/current/title-14/section-25.337. Accessed 7 November 2026.
- Gelman, A., Carlin, J. B., Stern, H. S., Dunson, D. B., Vehtari, A. and Rubin, D. B. (2013). Bayesian Data Analysis. 3rd edn. Chapman and Hall/CRC, Boca Raton, FL. https://doi.org/10.1201/b16018
- Government of India, Court of Inquiry (Justice M. N. Chandurkar). (n.d.). [Report of the Court of Inquiry into the accident to Air India Boeing 747 VT-EBD 'Emperor Ashoka' off Bombay on 1 January 1978]. New Delhi.
- Gur, O., Mason, W. H. and Schetz, J. A. (2010). Full-Configuration Drag Estimation. Journal of Aircraft, 47, 1356-1367. https://doi.org/10.2514/1.47557
- Hastings, W. K. (1970). Monte Carlo sampling methods using Markov chains and their applications. Biometrika, 57, 97-109. https://doi.org/10.1093/biomet/57.1.97
- Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A., Muñoz-Sabater, J., Nicolas, J., Peubey, C., Radu, R., Schepers, D., Simmons, A., Soci, C., Abdalla, S., Abellan, X., Balsamo, G., Bechtold, P., Biavati, G., Bidlot, J., Bonavita, M., De Chiara, G., Dahlgren, P., Dee, D., Diamantakis, M., Dragani, R., Flemming, J., Forbes, R., Fuentes, M., Geer, A., Haimberger, L., Healy, S., Hogan, R. J., Hólm, E., Janisková, M., Keeley, S., Laloyaux, P., Lopez, P., Lupu, C., Radnoti, G., de Rosnay, P., Rozum, I., Vamborg, F., Villaume, S. and Thépaut, J.-N. (2020). The ERA5 global reanalysis. Quarterly Journal of the Royal Meteorological Society, 146, 1999-2049. https://doi.org/10.1002/qj.3803
- Holland, I. D. (2018). MH370 burst frequency offset analysis and implications on descent rate at end-of-flight. *IEEE Aerospace and Electronic Systems Magazine*, **33**(2), 24–33. https://doi.org/10.1109/MAES.2018.170048
- Hull, D. G. (2007). Fundamentals of Airplane Flight Mechanics. Springer, Berlin, Heidelberg. https://doi.org/10.1007/978-3-540-46573-7
- Interstate Aviation Committee, Air Accident Investigation Commission. (2015). Okonchatel'nyi otchet po rezul'tatam rassledovaniya aviatsionnogo proisshestviya: Boeing 737-500 (53A) VQ-BBN, Kazan International Airdrome, 17.11.2013 [Final report on the results of the investigation of the aviation accident: Boeing 737-500 (53A) VQ-BBN, Kazan, 17 November 2013] (in Russian). Moscow. Investigation completed 23 December 2015. https://mak-iac.org/upload/iblock/ba0/report_vq-bbn.pdf. Accessed 7 November 2026.
- Interstate Aviation Committee, Air Accident Investigation Commission. (2019a). Final Report: Boeing 737-8KN A6-FDN, fatal accident at Rostov-on-Don aerodrome, Rostov Region, Russian Federation, 19 March 2016 (English translation; the Russian original is the text of reference). Moscow. November 2019. https://mak-iac.org/upload/iblock/1e8/report_a6-fdn_eng.pdf. Accessed 7 November 2026.
- Interstate Aviation Committee, Air Accident Investigation Commission. (2019b). Okonchatel'nyi otchet po rezul'tatam rassledovaniya aviatsionnogo proisshestviya: samolet An-148-100V RA-61704, Moskovskaya oblast', Ramenskii raion, 11.02.2018 [Final report on the results of the investigation of the aviation accident: An-148-100V RA-61704, Moscow Region, 11 February 2018] (in Russian). Moscow. Investigation completed 11 June 2019. https://mak-iac.org/upload/iblock/560/report_ra-61704.pdf. Accessed 7 November 2026.
- Interstate Aviation Committee, Technical Commission. (2007). Okonchatel'nyi otchet po rezul'tatam rassledovaniya aviatsionnogo proisshestviya s samoletom Tu-154M RA-85185 aviakompanii 'Pulkovo' 22.08.2006 v raione n.p. Sukhaya Balka Konstantinovskogo raiona Donetskoi oblasti, Ukraina [Final report on the investigation of the accident to Tu-154M RA-85185 of Pulkovo Airlines, 22 August 2006, Donetsk Region, Ukraine] (in Russian). Moscow. Investigation completed 12 February 2007. https://mak-iac.org/rassledovaniya/tu-154-ra-85185-22-08-2006/. Accessed 7 November 2026.
- ISO (1975). *Standard Atmosphere*, ISO 2533:1975. Geneva: International Organization for Standardization.
- Junta Investigadora de Accidentes Aéreos, Dirección General de Aeronáutica Civil, Dominican Republic. (1996). Final Aviation Accident Report: Birgenair Flight ALW-301, Puerto Plata, Dominican Republic, February 6, 1996. Santo Domingo. https://www.faa.gov/sites/faa.gov/files/Birgenair301_Accident_Report.pdf. Accessed 7 November 2026.
- Junta Investigadora de Accidentes de Aviación Civil, República Bolivariana de Venezuela. (2010). Informe Final Caso West Caribbean HK4374X, vuelo WCW708, Machiques, Estado Zulia, 16 de agosto de 2005 (in Spanish). Expediente JIAAC-9-058-2005. Caracas. Delivered 16 August 2010.
- Kahn, H. (1955). Use of Different Monte Carlo Sampling Techniques. RAND Paper P-766. RAND Corporation, Santa Monica, CA. https://www.rand.org/pubs/papers/P766.html
- Kish, L. (1965). Survey Sampling. John Wiley and Sons, New York.
- Komite Nasional Keselamatan Transportasi. (2015). Aircraft Accident Investigation Report: PT. Indonesia Air Asia, Airbus A320-216; PK-AXC, Karimata Strait, Coordinate 3°37'19"S - 109°42'41"E, Republic of Indonesia, 28 December 2014. Final. Report KNKT.14.12.29.04. Jakarta. December 2015. https://bea.aero/uploads/tx_elydbrapports/Final_Report_PK-AXC-reduite.pdf. Accessed 7 November 2026.
- Komite Nasional Keselamatan Transportasi. (2019). Final KNKT.18.10.35.04 Aircraft Accident Investigation Report: PT. Lion Mentari Airlines, Boeing 737-8 (MAX); PK-LQP, Tanjung Karawang, West Java, Republic of Indonesia, 29 October 2018. Jakarta. October 2019.
- Komite Nasional Keselamatan Transportasi. (2022). Final KNKT.21.01.01.04 Aircraft Accident Investigation Report: PT Sriwijaya Air, Boeing 737-500; PK-CLC, Kepulauan Seribu District, DKI Jakarta, Republic of Indonesia, 9 January 2021. Jakarta. November 2022. https://knkt.go.id/Repo/Files/Laporan/Penerbangan/2021/KNKT.21.01.01.04-Final-Report.pdf. Accessed 7 November 2026.
- Kong, A., Liu, J. S. and Wong, W. H. (1994). Sequential Imputations and Bayesian Missing Data Problems. Journal of the American Statistical Association, 89, 278-288. https://doi.org/10.1080/01621459.1994.10476469
- Malaysian ICAO Annex 13 Safety Investigation Team for MH370 (2018). *Safety Investigation Report: MH370 (9M-MRO)*, MH370/01/2018. Putrajaya: Ministry of Transport Malaysia.
- Metropolis, N., Rosenbluth, A. W., Rosenbluth, M. N., Teller, A. H. and Teller, E. (1953). Equation of State Calculations by Fast Computing Machines. The Journal of Chemical Physics, 21, 1087-1092. https://doi.org/10.1063/1.1699114
- Ministry of Civil Aviation, Arab Republic of Egypt. (2006). Final Report of the Accident Investigation: Flash Airlines Flight 604, January 3, 2004, Boeing 737-300 SU-ZCF, Red Sea off Sharm El-Sheikh, Egypt. Cairo. 25 March 2006. https://bea.aero/docspa/2004/su-f040103a/pdf/su-f040103a.pdf. Accessed 7 November 2026.
- Ministry of Transport, Romania, Administrative Investigation Commission. (2000). [Final report on the accident to the Airbus A310-324 YR-LCC, TAROM flight ROT 371, Balotești, 31 March 1995]. Bucharest.
- National Transportation Safety Board. (1975). Aircraft Accident Report: Northwest Airlines, Inc., Boeing 727-251, N274US, near Thiells, New York, December 1, 1974. Report NTSB-AAR-75-13. Washington, DC. 13 August 1975. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR7513.pdf. Accessed 7 November 2026.
- National Transportation Safety Board. (1981). Aircraft Accident Report: Trans World Airlines, Inc., Boeing 727-31, N840TW, near Saginaw, Michigan, April 4, 1979. Report NTSB-AAR-81-8. Washington, DC. 9 June 1981. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR8108.pdf. Accessed 7 November 2026.
- National Transportation Safety Board. (1986). Aircraft Accident Report: China Airlines Boeing 747-SP, N4522V, 300 Nautical Miles Northwest of San Francisco, California, February 19, 1985. Report NTSB/AAR-86/03. Washington, DC. 29 March 1986. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR8603.pdf. Accessed 7 November 2026.
- National Transportation Safety Board. (1989). Aviation Investigation Final Report: British Aerospace BAe-146-200, N350PS, Pacific Southwest Airlines, San Luis Obispo, California, December 7, 1987. Accident number DCA88MA008. Washington, DC. Original publication 4 January 1989. https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/15893/pdf. Accessed 7 November 2026.
- National Transportation Safety Board. (1999). Aircraft Accident Report: Uncontrolled Descent and Collision with Terrain, USAir Flight 427, Boeing 737-300, N513AU, near Aliquippa, Pennsylvania, September 8, 1994. Report NTSB/AAR-99/01. Washington, DC. Adopted 24 March 1999. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR9901.pdf. Accessed 7 November 2026.
- National Transportation Safety Board. (2002a). Aircraft Accident Brief: EgyptAir Flight 990, Boeing 767-366ER, SU-GAP, 60 Miles South of Nantucket, Massachusetts, October 31, 1999. Report NTSB/AAB-02/01. Washington, DC. Adopted 13 March 2002. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAB0201.pdf. Accessed 7 November 2026.
- National Transportation Safety Board. (2002b). Aircraft Accident Report: Loss of Control and Impact with Pacific Ocean, Alaska Airlines Flight 261, McDonnell Douglas MD-83, N963AS, about 2.7 Miles North of Anacapa Island, California, January 31, 2000. Report NTSB/AAR-02/01. Washington, DC. Adopted 30 December 2002. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR0201.pdf. Accessed 7 November 2026.
- National Transportation Safety Board. (2007). Aircraft Accident Report: Crash of Pinnacle Airlines Flight 3701, Bombardier CL-600-2B19, N8396A, Jefferson City, Missouri, October 14, 2004. Report NTSB/AAR-07/01. Washington, DC. Adopted 9 January 2007. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR0701.pdf. Accessed 7 November 2026.
- National Transportation Safety Board. (2020). Rapid Descent and Crash into Water, Atlas Air Inc. Flight 3591, Boeing 767-375BCF, N1217A, Trinity Bay, Texas, February 23, 2019. Aircraft Accident Report NTSB/AAR-20/02. Washington, DC. Adopted 14 July 2020. https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR2002.pdf. Accessed 7 November 2026.
- National Transportation Safety Committee, Department of Communications, Republic of Indonesia. (2000). Aircraft Accident Report: SilkAir Flight MI 185, Boeing B737-300, 9V-TRF, Musi River, Palembang, Indonesia, 19 December 1997. Final Report. Jakarta. 14 December 2000.
- National Transportation Safety Committee, Republic of Indonesia. (2008). Aircraft Accident Investigation Report: PT. Adam SkyConnection Airlines (AdamAir) Flight DHI 574, Boeing 737-4Q8, PK-KKW, Makassar Strait, Sulawesi, Republic of Indonesia, 1 January 2007. Report KNKT/07.01/08.01.36. Jakarta. Released 25 March 2008.
- Republic of Lebanon, Ministry of Public Works & Transport. (2012). Investigation Report on the Accident to Ethiopian 409, Boeing 737-800, Registration ET-ANB, at Beirut, Lebanon, on 25th January 2010. Beirut. 17 January 2012.
- Robert, C. P. and Casella, G. (2004). Monte Carlo Statistical Methods. 2nd edn. Springer, New York. https://doi.org/10.1007/978-1-4757-4145-2
- Secrétariat d'État aux Transports, Commission d'enquête. (1976). Turkish Airlines DC-10 TC-JAV: Report on the accident in the Ermenonville Forest, France on 3 March 1974. Translation of the report published by the French Secretariat of State for Transport. Accidents Investigation Branch, Department of Trade, Aircraft Accident Report 8/76. AIB Aircraft Accident Report 8/76. London: HMSO. February 1976 (translation title page). https://assets.publishing.service.gov.uk/media/5422eedde5274a1317000247/8-1976_TC-JAV.pdf. Accessed 7 November 2026.
- Statens haverikommission (Swedish Accident Investigation Authority). (2016). Final report RL 2016:11e: Accident in Oajevágge, Norrbotten County, Sweden on 8 January 2016 involving the aeroplane SE-DUX of the model CL-600-2B19, operated by West Atlantic Sweden AB. RL 2016:11e (file no. L-01/16). Stockholm. 12 December 2016. https://shk.se/download/18.2d6f089b18faca29dc81cffa/1700491384504/RL-2016_11e.pdf. Accessed 7 November 2026.
- Stone, L. D., Keller, C. M., Kratzke, T. M. and Strumpfer, J. P. (2014). Search for the Wreckage of Air France Flight AF 447. Statistical Science, 29, 69-80. https://doi.org/10.1214/13-STS420
- The Boeing Company (2016). End-of-flight engineering-simulator exports, ten cases (B1-B10), supplied via the ATSB; unpublished data set. Published description: Australian Transport Safety Bureau (2016). MH370 - Search and debris examination update. ATSB Transport Safety Report AE-2014-054, 2 November 2016. ATSB, Canberra.
