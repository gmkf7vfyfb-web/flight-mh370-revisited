# Aircraft ocean-impact sound, other underwater sound sources, and online catalogues: synthesis

Hydroacoustics module. 23 October 2026. Status: literature and held-data review, plus catalogue queries run in code. No hydrophone waveform was processed. All values carry their source in the companion files.

## Companion files

| topic | review note | table |
|---|---|---|
| Impact source and coupling | [impact-source-review.md]({{artifact:3c9965ef-dbcc-4199-9726-6a37c9c3303d}}) | [impact-source-parameters.csv]({{artifact:8eea74d5-7197-4449-b80d-36c2de3b5e61}}) (56 rows); [coupling-prior-range.csv]({{artifact:56e7a807-0844-4e46-a57e-a4355c70753a}}) (16 rows) |
| Other sources | [hydroacoustics-other-sources-review.md]({{artifact:454fe998-d67f-4b92-9363-d7bac28d15d8}}) (v2, Brown citation corrected) | [other-source-characteristics.csv]({{artifact:46f64144-9ba1-4d9a-8f95-dab690399fae}}) (41 rows) |
| Catalogues | [hydro-known-sources-catalogue-review.md]({{artifact:7970a3be-d55f-4973-8614-908bdb96b7dc}}) | [source-catalogues.csv]({{artifact:d02397a5-874c-4d63-86bc-8574a9e1e151}}) (45 databases); [known-events-6-10mar2014.csv]({{artifact:df0f8673-f306-41ef-9b41-11e2230e3f70}}) (298 rows) |
| Raw returns | [returned-records-catalogues.zip]({{artifact:a67afdbc-0eaf-42c2-9f2b-99fa59c88386}}); [returned-waveforms-12h.zip]({{artifact:fe96bfde-27f9-40c8-8a61-d211e76deccf}}) (island seismic stations, primary window) | |

## 1. Impact source: what is known

1. **Only one aircraft ocean impact has a peer-reviewed long-range record with ground truth.** It is the F-35A off Misawa, 9 April 2019 (Metz, Obana & Fukao 2023). At H11N and H11S, 3,249-3,341 km away, the arrivals are 6-8 s transients. The onset is emergent and the end is clear. The energy is mostly below 15-25 Hz, with no energy near 20 Hz at any station, near or far. Peak 1-s RMS is 0.31-0.37 Pa (H11N), 12-16 dB above background. The 5-95 % energy span is 3.4-4.8 s. Metz give no energy, source level or coupling.
2. **Metz also give near-field records (180-255 km, cabled seabed stations).** These are the only near-field records of an aircraft ocean impact that were found. The project has not digitised them. They are the best available test of source spectrum and duration with little path distortion.
3. **The 20 Hz spectral gap is in both near and far records.** It is therefore a source or site feature, not a long-path effect (track interpretation).
4. **Kadri 2024 claims of other aircraft are weak evidence.** Six of the eight cases checked are 4-12 min off the water-path time in an exploratory straight-path, one-speed check (registry D13: this is not evidence that Kadri erred), and AF447 and Yemenia 626 have SNR below 2 on Kadri's own figures. No other group has reproduced them. Kadri's energy argument treats kinetic energy as if it were radiated sound.
5. **Swissair 111 (MD-11, 1998, about 2.7 GJ, 55 m water) is a new airliner-energy case.** Land seismographs recorded the impact. No hydroacoustic record was found.
6. **The physics of water entry puts most of the sound in the cavity and bubble phase, not the first slam.** Leslie 1964 (bullets) and Li et al. 2021 (steel balls) agree on this; Kadri's model emphasises the entry phase. Minnaert arithmetic gives 0.5-6.5 Hz resonance for air pockets of 0.5-5 m radius. Airliner-scale cavities may therefore radiate largely below the 4-64 Hz band used for the F-35A, and near the IMS response roll-off. This is provisional.
7. **Implosions of trapped volumes while the wreck sinks are a separate source.** The radiated fraction of P·V is about 18 % for glass spheres and 0.2-0.6 % for ductile metal shells. One deep (more than 1 km) implosion of about 1 m³ could match the F-35A impact in radiated energy. Whether any sealed volume survives an airliner impact is unknown.
8. **Duncan & Dall'Osto 2023 model the MH370 path 20-30 dB weaker than the F-35A path.** Their path is the Curtin 301.6° bearing, not the core region near 37 S.

**Coupling efficiency.** Published and project values span 10⁻¹⁰ to 1. Most of that spread comes from different definitions, not from physics. The track sorted every value into four definition classes:

- D1: inverted through the project's propagation model at a stated source depth.
- D2: Arons-equivalent yield in the sound channel, path-blind.
- D3: measured near the source.
- D4: in one frequency band.

| quantity | value | definition |
|---|---|---|
| Brown et al. 2026 (*Icarus* 455:117106, peer-reviewed), F-35A | about 10⁻⁴; reproduced 2.08 × 10⁻⁴; 2.4-3.8 × 10⁻⁵ if the 1-s RMS peak is used | D2; Brown call it an upper bound because the sound channel at Misawa is 500-700 m deep |
| Project F-35A inversion (22 Oct, RAM-corrected) | 5.4 × 10⁻² (2 m), 2.26 × 10⁻³ (10 m), 3.4 × 10⁻⁴ (30 m) | D1; not adopted (pending Pete's ruling) |
| Leslie 1964, bullet entry | about 10⁻² | D3, near-field; abstract only |
| Pile driving | 1.2 × 10⁻³ to 2.1 × 10⁻² | D3 |
| Iceberg block impacts | 8 × 10⁻⁷ (ray-traced TL); 5 × 10⁻¹⁰ (cylindrical spreading) | D3; shows a 3-decade effect from the propagation relation alone |
| Known-yield shallow charges at IMS | 4 × 10⁻⁴ to 1.7 | D2 |

The track recommends three log-uniform priors (provisional):

- **PRIOR-A**, for the module likelihood: 10⁻⁶ to 10⁻² (D1, at the 10 m source-depth convention).
- **PRIOR-B**, for Arons-only screening: 10⁻⁸ to 2 × 10⁻⁴ (D2).
- **Implosions**: 2 × 10⁻³ to 0.18 of P·V.

A value carries over only with the propagation relation it came from. Coupling and source depth must be sampled together.

**Boeing 777-200ER source parameters** (track section 7):

- Well constrained (by other modules): impact time window and mass.
- Constrained conditionally on the descent scenario: kinetic energy.
- Poorly constrained: speed, angle and attitude, coupling, and spectrum.
- Unknown: effective source depth, the sub-event sequence and duration, directivity, and the number and depth of implosions.

## 2. Other sources: how they differ

| class | duration | band | envelope | repetition | bearing |
|---|---|---|---|---|---|
| Surface impact (expected) | short source; seconds to tens of seconds after the path | broadband | impulsive, no harmonics, no bubble pulse | single, then possible implosions over minutes | fixed, toward the 7th arc |
| Baleen whale song | units 3-50 s | narrow tones 17-108 Hz | emergent, tonal | strict: 40-200 s | local, slow drift |
| Fin whale 20 Hz pulse | about 1 s | 15-28 Hz | downsweep | 7-26 s for hours | slow drift |
| Iceberg tremor | minutes to 30 min | 4-10 Hz plus harmonics | emergent, gliding | clustered | Antarctic sector (158-209° at H01W) |
| Iceberg break-up, icequake | tens of seconds to about 20 min | broadband, under 40 Hz at range | impulsive to emergent | swarms | Antarctic sector |
| Earthquake T-phase | tens of seconds to minutes | 1-40 Hz, peak 1-5 Hz | emergent "cigar" | Poisson, clusters | ridge or trench |
| Airgun survey | seconds at range | 10-100 Hz | sharp onset | about 10 s for hours | constant |
| Explosion | short | broadband | impulsive with bubble pulses | single or series | fixed |

The nearest published discriminants are cepstral bubble-pulse detection, the Talandier-Okal duration-amplitude criterion, spectral fall-off, and recent IMS machine-learning catalogues (Fauvel et al. 2026; Raumer et al. 2026). None was built for aircraft impacts.

**On 8 March 2014 the arrival windows were not quiet:**

- **H01W (00:25-02:20 UTC):** Royer 2016 located 20 events between 23:45 and 02:05 UTC. About 12 of them arrive at H01W inside the window: four icequakes, one Java earthquake, and the rest "uncertain". That is about six located transients per hour. March is the seasonal maximum of iceberg noise.
- **H08S (00:45-02:50 UTC):** two airgun trains, at 35° and 113°, cover the whole window.
- **IMOS loggers:** pygmy blue whale song at Perth Canyon. At 3250, Bryde's whale calls, the Chagos song and Omura's whale.

## 3. Online catalogues: how many exist

The catalogues track tested or assessed **45 databases** in code:

| group | count |
|---|---|
| (i) open download (or held) and covers March 2014 | 29 |
| (ii) free registration needed | 3 (ISC-GEM, Global Fishing Watch, Copernicus CDS ERA5) |
| (iii) request-only or paid | 6 (IMS hydrophone waveforms 2014, IDC REB/SEL/SLSD, OHASISBIO raw data, WWLLN, GLD360, IMS infrasound) |
| (iv) no 2014 or no regional coverage, or retired | 4 |
| (v) coverage not determined | 3 |

Of the 29 in group (i), the AMSA March 2014 AIS file needs a copyright click-through, which the track did not accept for you.

**What the catalogues show for the windows:**

1. **No catalogued earthquake has both an open deep-water path and a predicted arrival inside either window.** The arrival rule (great-circle distance at 1.48 km/s) was checked against 24 IDC-observed T arrivals at H01W1 and H08S1 on 6-10 March. The median residual is +10 s and the standard deviation is 46 s.
2. **The main earthquake confound is south of Java:** mb 4.04 at 23:52:17 UTC on 7 March (ISC, USGS). Its predicted arrival is 00:24:34 at H01W, 26 s before the window opens, at back-azimuth 347°. At H08S it is 00:36:53. Its coda can reach into both windows.
3. **No IDC-associated arrival at H01W1 or H08S1 falls inside the windows.** The unassociated IDC detections are request-only.
4. **Four NOPTA 3D seismic surveys overlap 6-10 March.** Huzzas and Centaurus were known. Fortuna (Northern Carnarvon Basin) and Nerites (Bight Basin, about 1,635 km east of H01W) are new candidates. NOPTA dates are acquisition spans, so shooting on 8 March is not confirmed.
5. **Other sources in the windows:**
   - Bolides: no CNEOS fireball on 6-10 March.
   - Icebergs: all large ones are at 64.8-68.2 S; the northernmost small iceberg is at 55.3 S.
   - Whales: the OHASISBIO Antarctic blue whale Z-call file (SEANOE) has 78 detections between 00:25 and 02:50 UTC on 8 March.
   - Volcanoes: Heard and McDonald were active, at back-azimuth about 225° from H01W.
6. **Weather:** ERA5 mean 10 m wind over 20-40 S, 88-110 E was 8.7-8.9 m/s, with significant wave height 3.2-3.3 m. Near H08S the wind was only 2.1-3.5 m/s.
7. **Public catalogues miss many sources that H01W records.** The two high-SNR Curtin clock cross-check arrivals (04:59 and 05:14 UTC, from about 209°) are in no catalogue. A clean catalogue window is therefore weak evidence of a quiet source field.

## 4. Points reconciled across the tracks

1. **Brown et al. 2026 is peer-reviewed** (*Icarus* 455:117106, doi 10.1016/j.icarus.2026.117106). Labels calling it an arXiv preprint are out of date.
2. **The project F-35A coupling at 30 m source depth is 3.4 × 10⁻⁴** on the 22 Oct derivation. The "about 10⁻⁴" figure is the 9 Oct KRAKEN-only calibration.
3. **The CMST H08S detection at 01:58:55 from 93° has no public-catalogue match.** The only candidate, a Banda Sea ML 3.8 event, is 9 min off. Royer's own located event 16 (Java, 01:15:48) predicts 01:59 at H08S. The detection is therefore explained by a Royer-located event that is not in any public catalogue.
4. **The ground-truth table row F35A-H11N still says Metz is closed and not read.** That is stale: Metz is held and has now been read.
5. **Kadri S1 gives an F-35A site 64 km from Misawa, not 135 km.** The module's working point agrees with Metz (134 km).

## 5. Gaps that held or downloadable data can close (no requests to people or agencies)

1. Digitise Metz Fig. 2, the near-field F-35A records.
2. Use the open IMS March records for 2015-2018 on EarthScope to measure a same-season false-alarm rate. The 8 March 2014 records themselves return no data.
3. Use the island seismic waveforms already downloaded (II.DGAR, II.COCO, G.AIS and others) as an independent public T-phase check on H01W and H08S.
4. Use Royer's 20 located events as a labelled set of real arrivals for the H01W false-alarm model.
5. Two items need a decision from you before use:
   - the AMSA March 2014 AIS click-through;
   - a free Global Fishing Watch token.
6. Two possible new datasets need a check first:
   - AADC Casey and South Kerguelen 2014 mooring recordings: check the duty cycle and band.
   - Swissair 111 seismic waveforms from the Canadian national archive: check whether they are open.
7. Leslie 1964, Franz 1959 and several classic papers on explosion and implosion source levels are paywalled and not held. Each track note lists where it looked.
