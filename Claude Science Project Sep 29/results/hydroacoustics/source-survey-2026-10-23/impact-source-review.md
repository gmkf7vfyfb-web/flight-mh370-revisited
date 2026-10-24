# Acoustic source of an aircraft (or large object) ocean impact: review of coupling and source characteristics

Hydroacoustics module, track "impact source", 23 October 2026. Companion tables: `impact-source-parameters.csv` (56 rows, one row per event or study and quantity) and `coupling-prior-range.csv` (16 rows: the recommended coupling-efficiency priors and every contributing value, each tagged by definition and by the propagation relation it must be paired with; section 4b).

**Status: literature and held-data synthesis. No waveform data were processed.** Values marked *digitised* come from earlier project digitisation of published figures. Values marked *own arithmetic* are my calculations from published numbers. Values marked *second-hand* were read in a source that cites the primary. Every value in the table states whether I read it in the primary source.

## Deviations and limits (read first)

1. Many classic primaries are paywalled and not held. I read them at abstract level only: Leslie 1964, Franz 1959, Orr & Schoenberg 1976, Turner 2007, Chapman 1985/1988, Gaspin & Shuler 1971, Truscott et al. 2014, Lu et al. 1990, Yang et al. 2026. Where I looked is in section 10.
2. Several open-access primaries were read only through search extracts, not in full: Glowacki & Deane 2020, Liu et al. 2021, Li et al. 2021, Soloway & Dahl 2014, Harben et al. 2000, Shukla et al. 2018 (snippet).
3. The Duncan & Dall'Osto lay-language text could not be re-read. acoustics.org returned HTTP 403. I used the held figures (Fig. 3, Fig. 5) and the ASA abstract.
4. To fit the budget, I did not search each named accident separately. TWA 800, EgyptAir 990/804, Ethiopian 409, Adam Air 574, Columbia, Falcon stages and Chelyabinsk-type ocean bolides were not searched one by one. I searched Swissair 111, Germanwings 9525, MILS/re-entry vehicles, Space Shuttle SRB and Titan. Brown 2026 covers bolides.
5. I did not re-derive any project number. F-35A coupling, envelope, exposure and source-spectrum numbers are quoted from `results/hydroacoustics-metz-f35a-anchor.md` (22 Oct 2026). That note has registry status **PENDING_RULING**.
6. I added two columns to the requested CSV schema: `quantity` and `notes`.

---

## 1. Measured aircraft cases

### 1.1 F-35A, Misawa, 9 April 2019 (Metz, Obana & Fukao 2023; read in full)

Metz et al. is the only peer-reviewed long-range detection of an aircraft impact with ground truth. I read all nine pages and looked at Figs. 2 and 3 again.

- **Impact.** The aircraft descended steeply at near-supersonic speed, about 300 m/s (Metz p. 1343, citing JASDF 2019b). Radar lock was lost below 300 m altitude at 10:26:30 UTC. Metz give no impact angle, mass or energy. Brown et al. 2026 (Icarus 455:117106; p. 17 of the held author accepted manuscript) give 900 ± 200 MJ from the accident report's speed and the mass bounds. That implies a mass of about 16–24 t (own arithmetic, m = 2E/v²).
- **Location and time.** Origin time is 10:26:32 ± 9 s. The 90 % ellipse is 844 km² (36.8 × 7.3 km). It lies within 8 km of the 135 km range circle from Misawa. With IMS triplet data alone, the semi-major axis of the solution exceeds 1500 km (p. 1349). The near-field cabled stations were essential to the fix.
- **Near field (180–255 km; seafloor at 2124–3428 m; DSOH, KSP1–3).** The onset is well defined and broadband. Except at KSP2 it extends beyond the 50 Hz Nyquist. Peak 1-s RMS is up to 20 dB above ambient at DSOH and KSP1 (p. 1346). My approximate read of Fig. 2E–H: about 120–125 dB re 1 µPa at DSOH/KSP1 and 105–110 dB at KSP2/3 (4–40 Hz). The envelopes stay above ambient for about 5–15 s. Most spectral energy is below about 15 Hz. **These are the only published near-field records of an aircraft ocean impact that I found. The project has not digitised them.**
- **Far field (H11N 3249 km, H11S 3341 km; SOFAR-axis triplets at 727/739 m).** Metz describe the arrivals as "6–8-s-long transients". At H11N the onset is emergent ("overture") and the drop-off is clear ("finale"). At H11S the envelope is less distinct, which Metz attribute to bottom interaction or mooring height. The back azimuth is stable to ±0.1° (H11N) and ±0.05° (H11S) over the whole transient.
  - Spectrum: energy lies "well below 25 Hz". No energy above background near 20 Hz is seen at any station, near or far. Because the 20 Hz gap is present at 180 km and at 3300 km, I read it as a source or source-site feature, not a long-path effect (my interpretation).
  - Project digitisation of Fig. 3C/D: peak 1-s RMS 109.9–111.3 dB (0.31–0.37 Pa) at H11N and 106.1–108.7 dB (0.20–0.27 Pa) at H11S, 12–16 dB above background. The −6 dB width is 3.5 s / 2.5 s. The 5–95 % energy span is 4.8 s / 3.4 s. Exposure in 4–64 Hz is 0.270 Pa² s (SEL 114.3 dB re 1 µPa² s) at H11N and 0.090 Pa² s (109.5 dB) at H11S.
  - Brown's 0.7 Pa is about twice the 1-s RMS peak. It is therefore consistent with an instantaneous peak. Brown does not state its band.
- **What Metz do not give:** impact energy, source level, coupling efficiency, epicentre coordinates (only a cross in Fig. 1E), and any sub-event structure.
- **Held-data correction.** In `ground-truth-cases.csv`, row F35A-H11N still says "Metz2023 full text not read (closed)". That is stale. Metz is held (artifact 7e4d336f) and has been read.
- **Site discrepancy.** Kadri S1 gives the crash site as 40°30′10″N 142°04′37″E. That point is 64 km from Misawa (own arithmetic), not the 135 km that Metz and Kadri both state. The module's working point (40.64 N 142.96 E) is 134 km from Misawa and agrees with Metz.

### 1.2 Kadri 2024 and S1 cases (held; read earlier, key passages re-read)

| case | impact speed (S1) | attitude (S1) | station(s) | timing vs water path (project check) | grade |
|---|---|---|---|---|---|
| F-35A | 300 m/s | steep | H11N/S | consistent | A (Metz) |
| AF447 (A330) | 78 m/s (282 km/h) | belly first | H10S | +6.5 min | C |
| Yemenia 626 (A310) | 133 m/s (480 km/h) | nose first | H08N/S | +9.0 / +5.7 min | C |
| Sriwijaya 182 (B737-500) | not stated | — | H08S | −12.1 min | C |
| Transair 810 (B737-200F) | 60 m/s (215 km/h) | ditching | H11S/N | +4.2 / +5.8 min | C |
| Lion Air 904 (B737-800) | 67 m/s (240 km/h) | low-energy undershoot | H01W/H08S | consistent; H01W amplitude 15 dB too high | C |
| AirAsia 8501 (A320) | 76 m/s (274 km/h) | nose down | H01W | not assessed | C |
| Asiana 991 (B747-400F) | 123 m/s (442 km/h) | in-flight fire, mid-air separation | H11 | not assessed | C |

- Kadri describes the F-35A signal as "sharp, and rapid (6 s)". He states that the AF447 pressure reached 75 % of the F-35A value at 2200 km, and that Transair 810 shows a "double signal".
- The amplitudes in the ground-truth table were digitised from Kadri's 2–40 Hz panels by an earlier session. Kadri publishes no residuals, false-alarm rate or candidate count. An earlier project check found SNR < 2 on Kadri's own figures for AF447 and Yemenia 626.
- Kadri's energy argument (p. 9) has a flaw. He gives 200 t at 200 m/s = 4 GJ ("956 kg TNT, magnitude 3.2"), and concludes that a 7th-arc crash would be "highly unlikely" to leave no signature. This treats kinetic energy as if it were radiated acoustic energy. The coupling efficiency (section 4) spans more than six decades. Without it, the inference does not follow.
- **Tank experiments (Kadri et al. 2017, read in full, Drive copy).** Hollow steel spheres were filled with wax (specific gravity about 0.92): 150, 203 and 305 mm, 1.6, 4.0 and 13.4 kg. They were dropped by hand from three heights (values not given in the text) into 2.0 m of water. The hydrophone was 1.7 m deep and about 20 m away, with a 10 Hz–200 kHz band. There were 18 tests.
  - The signature has three phases: (I) impact, (II) cavitation, (III) reverberation or secondary impact.
  - The model is a cylinder of radius R and height ζ that enters the surface in time τ. Its far-field bottom-pressure envelope is set by a J₁ Bessel term.
  - No absolute level, energy or efficiency is given.
  - The first acoustic-mode cut-off of a 2 m tank is about 190 Hz (own arithmetic). The tank "AGW" signatures therefore do not scale in frequency to the 0.06–0.13 Hz ocean cut-off.

### 1.3 Duncan & Dall'Osto 2023 (ASA abstract read; lay-paper figures held)

- They compare propagation from the F-35A site to H11 with propagation along the Curtin 301.6° bearing from HA01. They also consider "possible differences in source levels due to different assumptions about impact parameters". The held material has no values for that part.
- My read of lay Fig. 3: modelled relative received level near 3000 km is about −120 to −130 dB for the F-35A and about −150 to −160 dB for MH370. That is about 20–30 dB worse for MH370.
- Their mechanism: at the F-35A site the channel axis is shallow (Fig. 3 lower panel: it rises towards about 300 m at the source) and the seabed slopes down. Along the MH370 path the axis is about 1000 m deep over abyssal water (Fig. 5).
- Their conclusion (lay text, quoted in a search extract): detection of MH370 is "much less likely than that of the F35".
- The project's own test of the shallow-channel argument found +2.9 dB, below the pre-registered 3 dB rule. Duncan & Dall'Osto's 20–30 dB therefore comes mostly from the near-source bathymetry and from geometry, not from axis depth alone. That is my inference from the two results.

### 1.4 Curtin CMST 2014-30 (held; source-assumption sections re-read)

- Signal of interest: peak-energy arrival at RCS (Perth Canyon seabed logger, 450 m) at 01:33:44 ± 4 s, and at HA01 at 01:34:50 ± 3 s. HA01 bearing 301.6° ± 0.75°. The most probable source is at 5.93 S 77.22 E. The spectrograms are in dB relative to their maximum, so no absolute level is given.
- **Source assumptions.** CMST assume no source level and no energy. Their only source model is qualitative:
  - A near-surface source radiates mostly at steep angles. It couples into the deep channel only over a seabed that slopes down toward the receiver, best where the seabed meets the axis (800–1200 m).
  - An implosion in the upper ~100 m follows the same rule.
  - A deeper implosion couples efficiently whatever the bathymetry (Fig. 14).
  - TL was computed with RAMGeo for a 20 Hz source "30 m below the water surface" (WOA05, silt seabed). The plot titles read "Zs=1100m, Zr=30m", so the labels are inconsistent. The Chagos–Laccadive Ridge on 302.36° (minimum depth about 1000 m) cuts TL by 20 dB.
- **Paired control on the same night.** The TGS seismic survey shooting over the continental slope in 260 m of water was detected at HA08S. The Woodside survey over a flat seabed in about 1000 m of water was not.
- If the source were on the 7th arc, its time would be 01:16:19. That is 25 min after the latest ATSB impact time (00:51). CMST allow a delayed implosion of sinking debris as one explanation.

### 1.5 Other aircraft and object impacts found

- **Swissair 111 (MD-11), 2 Sep 1998 (TSB A98H0003, held, read for these items).** Seismographs at Halifax and Moncton recorded a seismic event at 01:31:18 UTC, the time of impact. Impact data: 300 kn (154 m/s), 20° nose down, 110° right bank on the standby indicator (structure: about 20° nose down, bank > 60°), longitudinal deceleration ≥ 350 g. Weight was about 230 t; take-off weight was 241,100 kg and no fuel was dumped. The seabed was about 55 m deep. Kinetic energy was about 2.7 GJ (own arithmetic).
  - **This is the best-documented airliner ocean impact with a geophysical record.** It is in MH370's energy class, but at a 55 m shelf site. No hydroacoustic record was found. The seismic waveforms may exist in Canadian network archives; I did not search for them.
- **Germanwings 9525 (A320), 2015, land impact.** A Sismalp station 12 km away recorded the impact (secondary source). Impact speed was about 700 km/h. This is a land analogue only.
- **Missile and re-entry-vehicle impacts.** MILS, SMILS, BOA-MILS (which used the SOFAR channel), HITS and KMISS exist to locate RV splashes acoustically; HITS timing accuracy is ±2.6 ms (DTIC ADA219996). **I found no published RV source levels or efficiencies.** These data are request-only (US DoD).
- **Space Shuttle SRB water entry.** Vertical speed was 20–26 m/s. NASA reports describe cavity-collapse pressure loads on the casing. I found no far-field acoustic data.
- **Ditching.** US Airways 1549 conditions (NASA TM-2020-5006941) were 64 m/s forward, 3.8 m/s vertical and 9.5° nose up. The slam energy is small. No acoustic data.
- **Titan (2023).** A US Navy detection exists (not public). The NTSB report MIR-25-36 covers the hull failure. No quantitative acoustic publication was found.
- **Claims not counted as evidence.** Lyne (2022–2025, ResearchGate preprints) claims a MH370 ditching sound at HA01 (01:10.8 UTC, 278.8°) and an implosion at about 4300 m. These are not peer reviewed and use non-water paths.

---

## 2. Physics of water entry and its sub-events

The order of events and the acoustic character of each:

1. **First-contact slam (von Kármán/Wagner phase).** The wetted contact edge moves faster than sound for a short time. This radiates a short shock-like pulse (Franz 1959; drop-impact literature). For low-velocity entry Franz measured dipole radiation, because the free surface is pressure-release. At small scale this phase is energetically minor. Li et al. 2021 (steel balls) find the bubble-pulsation sound energy **3–5 orders of magnitude larger** than the initial-impact sound. Leslie 1964 (bullets) puts most of the acoustic energy into "a single bubble during the first 2 ft of travel".
2. **Cavity formation, surface seal or deep seal, pinch-off** (Truscott et al. 2014). Pinch-off and collapse radiate the main pulse. The trapped volume then rings at its volume resonance (Grumstrup et al. 2007 and Yu et al. 2023, via an arXiv review; Springer 2026 study of hydrophobic spheres).
3. **Air entrainment and bubble-cloud oscillation.** A bubbly region oscillates collectively at frequencies far below those of its single bubbles (Lu, Prosperetti & Yoon 1990; Loewen & Melville 1994). **Own arithmetic (Minnaert, γ = 1.4):** air pockets of radius 0.5, 1, 2 and 5 m at the surface resonate at 6.5, 3.2, 1.6 and 0.65 Hz. A 5 m pocket carried to 10 m depth resonates at about 1.2 Hz; at 100 m, at about 4.8 Hz. Airliner-scale cavities therefore radiate mostly **below the 4–64 Hz band used for the F-35A**, and near or below the IMS response roll-off (−47 dB at 0.1 Hz relative to 10 Hz). This is provisional, but it bears directly on detectability.
4. **Break-up and multiple sub-impacts.** An airliner fragments within tenths of a second (Swissair ≥ 350 g; Germanwings modelling, Chen et al. 2017, secondary). Engines, wings and fuselage sections may enter as separate bodies over about 0.1–1 s. No measurement of this sequence exists. The F-35A far-field envelope cannot resolve it: the channel's dispersion sets its length (project pulse check: misfit changes only 0.4 dB over τ = 0.05–10 s).
5. **Implosions of trapped volumes while sinking.** The available energy is P·V. For 1 m³ (own arithmetic) it is 0.6 MJ at 50 m, 1.1 MJ at 100 m, 10 MJ at 1000 m and 40 MJ at 4000 m. The radiated fraction is about 18 % for brittle glass spheres (Orr & Schoenberg 1976, 96–5000 Hz) but about 0.2–0.6 % for ductile metallic shells (Shukla et al. 2018). Chamberlin et al. 2014 bound it at ≤ 6 % (second-hand).
   - Own check: 18 % of P·V for a 43.2 cm sphere at 3 km gives 53.6 dB re 1 J. Orr & Schoenberg report about 53 dB re 1 J. The two agree.
   - **Comparison:** the F-35A radiated about 2 MJ in total at η = 2.26 × 10⁻³, or about 1.1 MJ in band. One deep (> 1 km) implosion of about 1 m³ at 0.2–18 % gives 0.02–7 MJ. It could match the F-35A impact acoustically, and it would couple well below the axis (CMST Fig. 14). Shallow implosions (< 100 m) give ≤ 0.2 MJ, and that energy couples poorly (Blackman 2001: a sphere detected at 680 m was missed at 320 m).
   - Whether any sealed volume survives an airliner impact intact to depth is **unknown**.
6. **Seabed strike.** Sinking speeds are of order 5–10 m/s; Lyne's 7.08 m/s is a claim. A 10 t section at 5–10 m/s carries 0.1–0.5 MJ (own arithmetic). With impact-type efficiencies this is a weak source. It sits on the abyssal floor, below the channel axis, where coupling to IMS is poor except via slopes. I found no measured case.

**Kadri's model (2017, 2019; AGW theory).** The source is a cylinder that enters the surface in time τ; the elastic seabed is added in 2019. This model gives mode structure and dispersion. It contains no radiated-energy or efficiency term. Kadri's far-field analyses high-pass at 5 Hz, so they lie in the SOFAR band, not the AGW band.

---

## 3. Analogue sources with known energy

- **Shallow explosions.** The Arons (1954) peak-pressure law P = 52.4 × 10⁶ (R/W^1/3)^−1.13 Pa (via Brown Eq. 2) was derived for source and receiver in the channel. Brown finds that it over-predicts for shallow sources.
  - SUS source levels: Chapman 1985/1988 (0.82 kg at 18.3/91/183 m, 1/3-octave 5–630 Hz, standard deviation within 1 dB); Gaspin & Shuler 1971; Gaspin et al. 1979. For 0.82 kg at 18.3 m the bubble period is about 0.12 s (about 8 Hz) (DOSITS). Shallow-explosion bubble frequencies therefore fall in the same few-Hz to 10 Hz band as the F-35A energy.
  - Energy partition: about 45–50 % of the explosive energy is left for the bubble after the shock (Taylor 1942; Arons & Yennie 1948; both second-hand). Soloway & Dahl 2014 give the SEL scaling.
- **Known-yield charges at IMS (Brown Table A.4; ground-truth table).** Arons-relative coupling (Arons-equivalent in-channel yield ÷ declared yield):

| source | ratio |
|---|---|
| San Juan calibration charge (102 kg, ~33 m), H10N | 5 × 10⁻³ |
| San Juan calibration charge, H04S | 4 × 10⁻⁴ |
| 39 kg charges at H11N | 1.5 × 10⁻³ – 1.3 × 10⁻² |
| FSST 2016 (6759 kg) | 0.10–0.34 |
| FSST 2021 (18,000 kg) | 0.13–1.7 |

  The ratio spans about 3.5 decades. Within one FSST site it varies by a factor of about 13.
- **Submarine losses.** San Juan: 139 dB re 1 µPa peak at H10N (6035 km). The acoustic energy release is about 428 kg TNT equivalent (Heyburn et al. 2020, via Vergoz 2021). The source was a doublet with 13 secondary arrivals. Scorpion: 19 signals over about 91 s (grey literature). Titan: no numbers. Kursk: about 4–5 t TNT, seismic only.
- **Imploding spheres as calibration sources.** Harben et al. 2000/2001 used a 22 L glass flask at about 700 m. Source level was about 200 dB re 1 µPa at 10 Hz (Dabob Bay) and about 205 dB at 200 Hz (San Diego), nominally equivalent to 1–5 lb of explosive (snippet).
- **Large, slow, blunt impacts.** Iceberg blocks: η = 8 × 10⁻⁷ ± 60 % below 100 Hz (Glowacki & Deane 2020), and 5.16 × 10⁻¹⁰ in an earlier analysis with cylindrical spreading (Glowacki et al. 2015). Large calving: source SEL 259–279 dB re 1 µPa² s (JASA 151:6, 2022). Pile driving: 0.12–2.1 % of hammer energy (Scottish Government review).
- **Airbursts.** Clarke 1996 gives about 10⁻⁵ (1 kT at 1 km); Kamegai & White 1994 about 10⁻⁴ (40 m burst height); Sakurai 1969 about 10⁻³ transmittance (all via Brown). Brown's fireball upper limit is ≤ 10⁻¹⁰.

---

## 4. Coupling efficiency: all values found, with definitions

| source | η | numerator / denominator / band | read in primary |
|---|---|---|---|
| Glass sphere implosion, 3 km (Orr & Schoenberg 1976) | ~0.18 | radiated acoustic energy 96–5000 Hz / P·V | abstract |
| Explosion, bubble share (Arons & Yennie 1948; Taylor 1942) | ~0.45–0.5 left to bubble | energy partition near source | second-hand |
| Bullet entry (Leslie 1964) | ~10⁻² ("order of 1 %"); Brown quotes 0.1–1 % | near-field acoustic energy at the impact site / KE (not coupling into the deep channel) | abstract |
| Pile driving (review) | 1.2 × 10⁻³ – 2.1 × 10⁻² | water-column energy / hammer energy | web page |
| F-35A, project route A (anchor) | 2.26 × 10⁻³ (spread 2.8 × 10⁻⁴ – 5.4 × 10⁻²) | total radiated energy (one-pole f⁻² source, normalised 1–500 Hz, z_s 10 m, RAM TL) / 900 MJ | project analysis of Metz |
| F-35A, project route B | 1.2 × 10⁻³ (lower bound) | in-band 4–64 Hz radiated energy / 900 MJ | project analysis |
| Metallic implosions (Shukla et al. 2018) | 2 × 10⁻³ – 6 × 10⁻³ | acoustic / P·V | snippet |
| F-35A, Brown 2026 | ~10⁻⁴ (project quotes 2.1 × 10⁻⁴) | Arons-equivalent in-channel TNT energy / KE (end-to-end, path-blind) | yes |
| Shallow charges at IMS (Brown Table A.4) | 4 × 10⁻⁴ – 1.7 | Arons-equivalent yield / declared yield | yes (Brown) |
| Small raindrops (Liu et al. 2021) | ~10⁻⁵ | radiated (bubble + impact) / KE | partial |
| Airburst (Clarke; Kamegai & White) | 10⁻⁵ – 10⁻⁴ | in-channel equivalent / burst energy | second-hand |
| Iceberg impact (Glowacki & Deane 2020) | 8 × 10⁻⁷ | source energy below 100 Hz / block KE | partial |
| Iceberg impact (Glowacki et al. 2015) | 5 × 10⁻¹⁰ | below 200 Hz, cylindrical-spreading TL | abstract |
| Fireballs (Brown 2026) | ≤ 10⁻¹⁰ | in-channel Arons-equivalent / fireball energy | yes |

Reading:

- Definitions differ in three ways:
  1. Source radiation only, or source plus coupling into the channel toward one receiver.
  2. Total band or a stated band.
  3. Energy integral versus an Arons peak-pressure equivalent.
- Only Orr & Schoenberg, Leslie, Liu, Glowacki, pile driving and project route A/B are "source radiated energy ÷ input energy". Brown's numbers and Table A.4 are end-to-end path-blind ratios. They bundle the site term (CMST, Northrop: 15–20 dB) with the source term.
- For impacts alone, the like-for-like values range from 10⁻⁹ (slow blunt ice) to 10⁻² (fast slender bullet). The F-35A, at 10⁻³, lies at the upper end, as its high speed would suggest.
- **A 777 impact could plausibly lie anywhere from about 10⁻⁶ (slow, flat, ditching-like) to about 10⁻² (fast, steep).** The project's log-uniform prior on η from 10⁻⁶ to 10⁻² matches this spread. The evidence above supports keeping it.

### 4b. Coupling-efficiency prior range for downstream use (added at the request of the per-degree detectability thread)

**Citation correction.** Brown, McFadden, McCormack, Adams & Vida (2026) is a peer-reviewed paper: *Icarus* 455, 117106 (1 September 2026), doi 10.1016/j.icarus.2026.117106. It was accepted on 14 April 2026. The repo copy is the author accepted manuscript (arXiv 2604.12723), and its footnote states the acceptance. All citations of Brown in both tables now use the Icarus reference.

**Brown's F-35A value, checked against the held text.**
- Highlight: an energy-transfer efficiency "for surface ocean impacts into the SOFAR channel of 10⁻⁴".
- Body (pp. 17–18): impact energy 900 ± 200 MJ, observed peak pressure 0.7 Pa at H11, range 3300 km, Arons relation (Eq. 2).
- Brown also warn that the channel at the crash site is only 500–700 m deep (Chu & Fan 2024). The value "may be a higher efficiency than in the open ocean and again should be taken as an upper bound".
- Own reproduction: W = 0.0447 kg TNT, so η = 2.08 × 10⁻⁴ (1.7–2.7 × 10⁻⁴ for 700–1100 MJ). This agrees with the other thread's 0.045 kg → 2.1 × 10⁻⁴.
- Sensitivity to the peak definition: if the digitised 1-s RMS peaks (0.31–0.37 Pa) are used in the same relation, η is 2.4–3.8 × 10⁻⁵, nearly a decade lower.

**Leslie 1964.** The abstract says "on the order of 1 %" of the available kinetic energy was converted to acoustic energy. Brown paraphrase this as 0.1–1 % transferred "into hydroacoustic energy" at the impact site. This is near-field acoustic energy. It is not coupling into the deep sound channel. I found no legitimate free copy. I looked at the ASA site (paywalled), DTIC/NOL reports, Drive (title and full text "Leslie", "bullet", DOI fragment 1.1919174), the artifact store and ~/Downloads. A purchased or inter-library copy is needed.

**Project value.** The 2.26 × 10⁻³ is not published. It is the project's inversion of the F-35A recording through its own propagation chain at an assumed source depth of 10 m. It depends mainly on that depth: 5.4 × 10⁻² at 2 m and 3.4 × 10⁻⁴ at 30 m (22 Oct re-derivation with measured exposure and RAM). The "about 10⁻⁴ at 30 m" quoted by the other thread is the 9 Oct KRAKEN-only calibration (2 × 10⁻², 8 × 10⁻⁴ and 1 × 10⁻⁴ at 2, 10 and 30 m). The two calibrations differ by about a factor of 3 at 30 m.

**Definition classes.** Every value in `coupling-prior-range.csv` carries one of these tags:

| class | numerator / denominator | examples | must be paired with |
|---|---|---|---|
| D1 model-inverted | total source-radiated acoustic energy (one-pole f⁻² spectrum, normalised 1–500 Hz) / KE, at a stated source depth | F-35A 2.26 × 10⁻³ at 10 m (22 Oct); 8 × 10⁻⁴ at 10 m (9 Oct) | the same chain it was inverted through: explicit source depth (surface image) + KRAKEN (+ RAM for 22 Oct) along each path, exposure-based scoring |
| D2 Arons-equivalent | Arons-equivalent in-channel TNT energy / KE (path-blind, peak pressure) | F-35A ~10⁻⁴ (Brown), 2.1 × 10⁻⁴ reproduced; shallow charges 4 × 10⁻⁴ – 1.7 | Arons 1954 only, P_peak at range R; no TL model; peak (not RMS, not exposure) |
| D3 near-field measured | radiated acoustic energy near the source / KE (or P·V for implosions), in a stated band | Leslie ~10⁻²; piles 10⁻³–2 × 10⁻²; raindrops 10⁻⁵; ice 8 × 10⁻⁷ (< 100 Hz) | an explicit source model (spectrum, depth, directivity) plus a full TL; band must be matched |
| D4 in-band | source-radiated energy in a stated band / KE | F-35A 1.2 × 10⁻³ (4–64 Hz) | band-by-band TL of the module |

**Values do not carry over between propagation relations.** The iceberg case shows this directly. The same kind of event gives 5 × 10⁻¹⁰ with cylindrical spreading (2015) and 8 × 10⁻⁷ with Bellhop TL plus terminus reflection (2020). That is about 3 decades from the propagation relation alone. Likewise, Brown's D2 value already contains the favourable F-35A site term. Using it together with a path TL model would count the path twice, or the wrong path.

**Recommended priors.**

1. **PRIOR-A (module likelihood; use this):** η_D1 log-uniform from 10⁻⁶ to 10⁻², four decades, at the module convention z_s = 10 m. It must be used with the module's propagation chain (D1 pairing).
   - Upper bound: Leslie's near-field ~1 %, the pile-driving range up to 2 %, and the F-35A anchor (2.26 × 10⁻³) 0.65 decades below the top.
   - Lower bound: blunt, slow impacts (raindrops 10⁻⁵, ice 8 × 10⁻⁷).
   - If z_s is sampled rather than fixed, scale both bounds by η_F35(z_s) / 2.26 × 10⁻³ (×24 at 2 m, ×0.15 at 30 m), so the F-35A stays calibrated at every depth. η and z_s must never be sampled independently.
   - Sensitivity variant: 10⁻⁷ to 3 × 10⁻².
2. **PRIOR-B (Arons screening only, e.g. a per-degree detectability check that uses Arons):** η_D2 log-uniform from 10⁻⁸ to 2 × 10⁻⁴, about 4.3 decades.
   - Upper bound: the F-35A at a favourable site (Brown's own reading).
   - Lower bound: Duncan & Dall'Osto's modelled 20–30 dB lower received level along the MH370 path maps to a factor of 450–9600 in Arons yield (P ∝ W^0.377). That gives 2.2 × 10⁻⁸ – 4.7 × 10⁻⁷ for an F-35A-like impact (own arithmetic), rounded down to 10⁻⁸.
   - Because D2 is path-blind, the 7th-arc site penalty must sit inside η. PRIOR-B must therefore not be used with any TL model, and PRIOR-A must not be used with Arons.
3. **Implosions (separate source branch):** radiated fraction of P·V, log-uniform from 2 × 10⁻³ to 0.18 (Shukla 2018; Orr & Schoenberg 1976). It must be paired with a deep-source TL (source below or near the axis).

All three priors are provisional. Every bound rests on abstracts, partial reads or one aircraft case.

---

## 5. Propagation-side effects that change the received character

- **Surface image (Lloyd's mirror).** A source at depth d under a pressure-release surface radiates as a vertical dipole when kd ≪ 1. Low-angle energy is suppressed roughly as (2kd sin θ)². At 10 Hz, kd = 0.08 / 0.42 / 1.26 for d = 2 / 10 / 30 m (own arithmetic). This is why the F-35A η moves by a factor of 160 between assumed depths of 2 m and 30 m. **After η itself, the effective source depth is the most important unknown.** It is set by cavity depth and pinch-off depth, which grow with speed and size.
- **Downslope conversion.** Northrop et al. 1968, Carey 1986 and Dosso & Chapman 1987 measured it (peak-amplitude effects of about 15 dB). CMST show 20 dB over a ridge. The TGS/Woodside pair on the MH370 night is a natural control.
- **T-phase-like spreading.** Metz contrast the 6–8 s aircraft transient with T-phases lasting tens of seconds to minutes. Coupling over a rough slope or an extended area would lengthen an impact arrival in the same way. CMST reported "very similar durations" at HA01 and RCS but gave no number.
- **AGW.** The first-mode cut-off c/4H is about 0.06–0.13 Hz. It is far below every band used for aircraft analyses (Kadri high-passes at 5 Hz). IMS (−47 dB at 0.1 Hz) and IMOS (8 Hz analogue high-pass) are not suited to it. No far-field AGW detection of an impulsive surface source is verified (project literature review).

---

## 6. What the project already holds, and what is new here

**Held and already analysed** (results notes and the 37-row ground-truth table):

- F-35A, Metz figures digitised: anchor 2.26 × 10⁻³; real-arrival matched-filter penalty +4 to +9.5 dB; τ not identifiable (`hydroacoustics-metz-f35a-anchor.md`, `-f35a-eta-calibration.md`).
- Kadri 2024 panels digitised and timing checked (`-kadri-package-v2.md`, `-kadri-table1-test.md`, `-digitised-sources.md`).
- Blackman airgun, SUS and sphere validation (`-blackman-validation.md`, `-air9-ew0112-source-reference.md`).
- San Juan, FSST and 2008 charges as table rows (via Brown).
- AGW scenarios (`-agw-scenarios.md`).
- Literature review and critique.

**New in this note:**

- The Metz near-field cabled-observatory records (Fig. 2): the only near-field aircraft-impact data, not yet digitised.
- The 20 Hz gap is common to near and far stations, so it is a source or site feature.
- Swissair 111 as an airliner-energy seismic ground-truth case (held report).
- Leslie 1964 (~1 %), Li 2021 (bubble ≫ slam), Liu 2021, Glowacki 2015/2020, pile-driving ECF, Orr & Schoenberg 18 % vs Shukla 0.2–0.6 %, Harben source levels and Heyburn's 428 kg TNT for San Juan: these give the first cross-mechanism η comparison with stated definitions.
- Minnaert arithmetic: airliner-scale cavities ring at 0.5–5 Hz.
- Implosion P·V arithmetic: a deep 1 m³ implosion could rival the F-35A acoustically.
- The Kadri S1 F-35A coordinate discrepancy (64 km vs 135 km from Misawa).
- The CMST TL plot label inconsistency (Zs 1100 m vs 30 m).
- Kadri 2017 tank parameters, and the tank cut-off (~190 Hz) that blocks frequency scaling to the ocean.

---

## 7. Source parameters for a Boeing 777-200ER impact

| parameter | status | basis |
|---|---|---|
| Impact time window | well constrained (by the end-of-flight module, not acoustics) | BTO/BFO and end-of-flight PDF |
| Mass at impact | well constrained (fuel model) | project fuel and performance model |
| Kinetic energy | constrained conditionally on the descent scenario (about 4–9 GJ for an unarrested descent, earlier sessions) | ½mv²; speed is scenario-dependent |
| Impact speed, angle, attitude | poorly constrained (scenario-dependent: high-speed dive vs controlled ditching) | end-of-flight hypotheses |
| Coupling efficiency η | poorly constrained: 10⁻⁶ – 10⁻² plausible; one aircraft calibration point (F-35A, 19 t-class, steep, ~300 m/s) | section 4 |
| Effective source depth (cavity / pinch-off depth) | unknown; dominates η inversion (factor of 160 over 2–30 m) | section 5 |
| Source duration τ and sub-event sequence (slam, cavity, break-up, engines) | unknown; not identifiable from far-field envelopes | project pulse check; no measurements |
| Source spectrum | poorly constrained: the F-35A implies −6 to −7 dB/octave over 5–40 Hz with a gap near 20 Hz; cavity resonances for a 777 likely 0.5–5 Hz (Minnaert) | project route 2; own arithmetic |
| Directivity | unknown; near-surface dipole expected; no aircraft measurement | Franz 1959; image theory |
| Received duration at IMS | moderately constrained by the propagation model (dispersion-dominated, a few seconds for a compact source); longer if coupling is extended | Metz; project pulse check |
| Implosions during sinking: number, volumes, depths | unknown | section 2 item 5 |
| Seabed strike | unknown; probably weak | own arithmetic |
| Site coupling (downslope, axis depth) | computable per path; along 7th-arc paths likely 20–30 dB worse than the F-35A site | Duncan & Dall'Osto 2023; CMST 2014 |

## 8. Main disagreements in the literature

1. **Size of coupling.** Brown gives "~10⁻⁴, upper bound". The project gives 2.26 × 10⁻³ for its own source-radiation definition. Leslie gives ~10⁻². Iceberg studies give 10⁻⁷–10⁻⁹. Most of the spread comes from definitions and from scale and speed (section 4).
2. **Whether the F-35A is an upper bound.** Brown says yes, because of the shallow channel. Duncan & Dall'Osto say the site is favourable (shallow axis plus downslope seabed). The project's counterfactual for axis depth alone gives only +2.9 dB. The seabed-slope term has not been isolated.
3. **Detectability of MH370.** Kadri 2024 says it is "highly unlikely" that a 7th-arc crash would leave no signature. Duncan & Dall'Osto 2023 say detection is "much less likely than" for the F-35A. CMST say a near-surface source needs a favourable slope.
4. **Validity of Kadri's historical detections.** Kadri presents ten crashes as detections. Project checks find six of eight inconsistent in timing by 4–12 min and SNR < 2 for two of them. No independent group has reproduced them.
5. **Non-water (land or seafloor) paths.** Kadri (San Juan at H03S) and Lyne argue for them. CTBTO analyses (Nielsen 2021; Vergoz 2021) do not report them.
6. **Which sub-event dominates the sound.** Kadri's model and Franz's emphasis put weight on impact and penetration (phase I). Leslie and Li et al. find bubble or cavity oscillation dominant by orders of magnitude.
7. **Implosion efficiency.** Glass spheres give ~18 %. Ductile metal structures give 0.2–0.6 % (≤ 6 % bound).
8. **Arons relation for shallow sources.** Brown says it over-predicts. Dall'Osto, Dahl & Chapman 2023 (Acoustics Today, via a Springer chapter extract) call the peak-pressure relation robust over many conditions. The two statements concern different source depths.
9. **What CMST's signal could be.** CMST think a natural event is most likely, but allow a delayed implosion. Lyne claims an MH370 implosion at about 4300 m.

## 9. Recommendations for the module (short)

1. Keep η as a declared alternative over at least 10⁻⁶–10⁻². Report the source-depth dependence separately from η.
2. Add a source branch below about 5 Hz for entrained-cavity resonance. Score it against each station's real low-frequency response before any claim.
3. Add a delayed-implosion source with an explicit P·V × efficiency prior (0.2–18 %) and a depth prior. Deep implosions couple below the axis.
4. Digitise Metz Fig. 2 (near field) to test the source spectrum and duration with little path distortion.
5. Use PRIOR-A (section 4b) in the module and PRIOR-B only for Arons-based screening. Never mix definition classes.
6. Look for Swissair 111 seismic waveforms (Canadian network) as a second airliner-class ground-truth case.

## 10. Not held, and where I looked

| source | status | where looked |
|---|---|---|
| Leslie 1964 JASA 36:1138 | not held (paywalled); abstract read; no legitimate free copy exists online that I could find | ASA site, DTIC/NOL search, artifact store (filename/DOI search), Drive title/full text "Leslie", "bullet", "bullet entry", DOI fragment, ~/Downloads |
| Franz 1959 JASA 31:1080 | not held; abstract read | artifact store, Drive "splashes as sources of sound", ~/Downloads |
| Truscott et al. 2014 | not held; author copy on ResearchGate not fetched | artifact store, Drive "water entry of projectiles" |
| Orr & Schoenberg 1976; Turner 2007 | not held; abstracts | artifact store, Drive "implosions of spherical cavities", "implosion of glass spheres" |
| Chapman 1985/1988; Gaspin & Shuler 1971 (DTIC AD0734381 is open access, not read); Gaspin et al. 1979 | not held | Drive "source levels of shallow explosive", artifact store |
| Arons 1954 | not held; equation via Brown | Drive title "Arons" (none) |
| Soloway & Dahl 2014; Glowacki & Deane 2020; Liu 2021; Li 2021; Harben 2000 (OSTI) | open access; not downloaded (extracts read) | publisher/OSTI pages |
| Yang et al. 2026 JASA 159:1930 | not held (paywalled) | artifact store, Drive |
| Shukla et al. 2018 Exp Mech | not held; snippet | — |
| Prario et al. 2023; Heyburn et al. 2020; Prior et al. 2011; Dall'Osto 2019 | not held | Drive "Prario" (none); artifact store; ledger lists them "not retrieved" |
| Duncan & Dall'Osto 2023 lay text | held figures only; web text blocked (403) | acoustics.org; repo papers folder |
| Dall'Osto & Duncan 2023 "Revisiting" (abstract 1pAO1) | title only | CrossRef |
| Clarke 1996; Kamegai & White 1994; Sakurai 1969; Cole 1948 | not held; via Brown or secondary | — |
| NASA SRB cavity-collapse reports | titles/abstracts only | NTRS |
| JASDF F-35A accident report (Japanese) | not read | — |
| **Request-only:** CTBTO vDEC waveforms (all IMS cases); US Navy Titan detection; MILS/KMISS RV impact data; Royer/Kadri raw data; Canadian seismic archive for Swissair 111 (may be open archive; not checked); Dall'Osto & Dahl 2014 APL report (cited by Kadri; not searched) | request-only or not searched | — |

Drive searches run: Franz, Truscott, Leslie, Orr, Turner, Arons, Chapman, Dall'Osto (query failed), "aircraft surface impacts", Kadri 2017, ditching, implosion, water impact + acoustic, slamming, Prario, Vergoz, Minnaert, Soloway, Titan + implosion, missile impact + hydrophone. New held items found: Kadri et al. 2017 PDF (Drive id 1X8-6GeaQH1Lr8zZQoFe7hCkcAol9WC-U); Kadri, Crivelli & Parsons 2017 report to ATSB, "Important Kadri_ATSB_8_Feb_2017.pdf" (read via the Drive text tool for the HA01 bearing and method; it gives no source level).
