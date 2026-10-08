# Hydroacoustics module: literature review of the state of the art

Brief: `Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md` (27,457 B, branch `claude-science-sep29`), deliverable §10 item 2(a). Inbox `coordination/HYDROACOUSTICS.md` read (entries to 2026-10-08). Companion files: `hydroacoustics-prior-work-critique.md`, `hydroacoustics-bibliography.csv` (keys used below), `ground-truth-cases.csv` (37 rows).

**Status: literature synthesis, not analysis.** No hydroacoustic data were processed for this document. Two items are my own arithmetic on published numbers (timing checks of Kadri's historical cases in §1.3; the look-elsewhere numbers in §5), and they are labelled as such. Values that the previous session read off published figures are labelled DIGITISED and are never treated as measurements.

**Reading depth.** Full texts read: Kadri2024 + S1, KadriPoster2025, Kadri2017, Kadri2019, CMST2014, Brown2026, Blackman2004UCRL (key sections), Vergoz2021, Nielsen2021 (key passages), Stone2014 (key passages), DuncanDallOsto2023lay. Read through abstracts, snippets or secondary sources only (marked in the CSV `read_level`): Metz2023, Prario2023, Heaney2017, Prior2011, Koper2001, the Scorpion and Titan sources, and most of the theory papers in §4. **No load-bearing claim below rests on an abstract alone unless it says so.**

---

## 1. Acoustic-loss cases weighted by ground truth

Brief §1 asks for most weight on cases where a later ground truth exists. I sort the evidence into three grades (column `evidence_grade` in `ground-truth-cases.csv`):

- **A**: known source position and time, analysed by more than one group or in a controlled experiment.
- **B**: known source, a single analysis, or a grey-literature account.
- **C**: a claimed detection with no independent check of timing or amplitude.

### 1.1 Controlled sources: the only ground truth for propagation and for source-to-channel coupling

- **Blackman 2001/2003, Indian Ocean** [Blackman2004UCRL]. Airgun sites air1–air9, SUS charges and imploding glass spheres were recorded at H01, H08 and H04. Arrival times fell within a few seconds of a 1.49 km/s geodesic prediction. Azimuths were within 1–2° when SNR was high, which gives a location uncertainty of 5–15 km. Two results matter most here:
  - air9, about 116 km from the 7th arc, was the only airgun site clearly seen in the low-frequency band at H01 (1,665 km).
  - air8 was not detected at H01. Blockage there was not thought significant, noise was similar to the air9 period, and the authors could not explain the miss.
  - Two depth effects were also recorded. A 320 m sphere implosion was missed where a 680 m one at the same site was detected. The air7 shots, fired over a west-dipping slope, coupled poorly toward H01.
  - The authors also report that long, topographically scattered arrivals produced unacceptably large location errors in some cases. **Arrival complexity, not SNR alone, limits timing.**
- **ARA San Juan calibration charge, 1 Dec 2017** (Mk 54, 102–108 kg TNT equivalent, about 30–33 m depth) [Nielsen2021; Vergoz2021]. It was detected at H10N (5,995 km) and H04S (7,779 km). The CTBTO located it 39 km from the declared drop point, with a 90% ellipse of 37,212 km².
- **US Navy full-ship shock trials 2016 and 2021** (6,759 kg and 18,000 kg TNT) and **39 kg explosions in 2008**. All were detected at 3,000–8,200 km [Brown2026 Table A.4, citing Heyburn2018, Bittner 2024, Prior2011; those primaries not read].
- **TGS Huzzas versus Woodside Centaurus surveys, on the MH370 night itself** [CMST2014].
  - HA08S detected the TGS survey, shooting over the continental slope in about 260 m of water. The bearing track matched the survey navigation with a mean offset of 0.6°.
  - HA08S did not detect the Woodside survey over a flat seabed in about 1,000 m of water.
  - This is a **natural paired positive/negative control for site coupling**: same night, similar sources, different seabed.
- **Basin-scale controlled propagation.** These establish that geodesic travel-time models need path-specific corrections over thousands of kilometres:
  - Heard Island 1991, from the southern Indian Ocean [Munk1994].
  - Perth–Bermuda 1960 shots, from the HA01 source region [Shockley1982; Heaney1991]. Heaney1991 explains the paths with horizontal refraction (adiabatic modes) rather than great circles.

**What the known-yield explosions say about coupling.** Brown2026 converts each received peak pressure into an "Arons-equivalent in-channel yield" using the Arons relation (Arons1954), which was derived for source and receiver both in the SOFAR channel. Dividing that by the declared yield gives an empirical "shallow source to SOFAR channel" factor:

| source | declared yield | station, range | Arons-equivalent yield | ratio |
|---|---|---|---|---|
| 2017 San Juan calibration charge, ~30 m | 102 kg | H10N, 5,995 km | 0.5 kg | ~5×10⁻³ |
| same | 102 kg | H04S, 7,779 km | 0.04 kg | ~4×10⁻⁴ |
| 2008 explosions | 39 kg | H11N, 3,000 km | 0.06–0.5 kg | 1.5×10⁻³–1.3×10⁻² |
| FSST 2016, five shots | 6,759 kg | H10N, ~8,150 km | 650–2,325 kg | 0.10–0.34 |
| FSST 2021, three shots | 18,000 kg | H10N, ~8,130 km | 2,325–30,000 kg | 0.13–1.7 |

The ratio spans **about 3.5 decades** across sites. Even shots at the same FSST site vary by a factor of about 13. Brown2026 notes that the Arons relation consistently over-predicts pressure for shallow sources and treats it as an upper limit for them. Nielsen2021 cautions that a louder received signal cannot be read as a more energetic source when source depth and path environment are uncertain.

### 1.2 Accidental losses with a later wreck or site

- **ARA San Juan, 15 Nov 2017** [Nielsen2021; Vergoz2021]. This is the strongest case. The impulsive event was detected at H10N (6,035 km, peak 139 dB re 1 µPa) and H04S (7,760 km).
  - The CTBTO hydrophone-only location was 19.8 km from the wreck found a year later, with a 90% ellipse of 33,659 km². Adding the regional seismic station TRQA shrank the ellipse to 748 km² but moved the point only to 19.0 km.
  - Vergoz2021 identified 13 secondary arrivals reflected or refracted by seamounts, islands and the continental slope, and inverted jointly with the calibration charge. That gave a location 3.5 km from the wreck, with 95% bounds of ±29 km × ±15 km and origin time 13:51:05 ± 9 s.
  - The Rio Grande Rise attenuated the H10N path by about 20 dB at 7 Hz.
  - **Lessons:**
    1. Two distant stations give a usable but very elongated location.
    2. Secondary arrivals are information, but also a source of false association if not modelled.
    3. A same-site calibration shot was the decisive aid.
- **F-35A, 9 Apr 2019, off Misawa** [Metz2023 via Brown2026, Kadri2024, DuncanDallOsto2023lay]. This is the only aircraft case with constrained energy: 900 ± 200 MJ from the accident report's impact speed and mass bounds.
  - It was recorded at H11 at about 3,300 km with a peak of about 0.7 Pa, roughly ten times the background, and confirmed at hydrophones near Japan, in the right time window and from the right back-azimuth.
  - Brown2026 derives a surface-to-SOFAR coupling of order 10⁻⁴ and calls it an upper bound, because the channel axis is only 500–700 m deep at the crash site.
  - DuncanDallOsto2023lay add that the site also had a downward-sloping seabed. Both known routes from a surface source into the deep channel were therefore available, which makes the case **atypically favourable**.
- **AF447, 1 Jun 2009** [Stone2014]. Not a hydroacoustic detection case, but the most instructive ground-truth case on **probability of detection**. A 31-day passive acoustic search for the underwater locator beacons found nothing. The wreck, found in 2011 after a Bayesian reanalysis, lay in an area the passive search had covered thoroughly. Stone2014 conclude both beacons probably failed to actuate. The authors judge that ignoring this possibility delayed the find by up to a year. **A mis-specified detection probability converted a non-detection into false negative evidence.** Kadri2024's hydroacoustic claim for AF447 is graded C below.
- **Kursk, 12 Aug 2000** [Koper2001; Savage2001; Sebe2005]. Recorded seismically, not hydroacoustically, at up to about 5,000 km. The second explosion was about 4–5 t TNT (body-wave magnitude 3.5), 135 s after a first explosion about 250 times smaller. Yield and depth were estimated from bubble-pulse and spectral-notch analysis. This is a methods precedent for source characterisation, not for long-range ocean propagation.
- **USS Scorpion, 22 May 1968** [USNI2025; Rule2018; grey literature]. A SOSUS array near Newfoundland and a Canary Islands hydrophone at about 820 nmi recorded a sequence of 19 signals over about 91 s. Their cross-bearing defined a box of about 12 × 12 miles roughly 400 nmi south-west of the Azores, and the wreck was found five months later at about 3,000 m. No open, peer-reviewed location error exists.
- **Titan, 18 Jun 2023** [NewsTitan2023]. A classified US Navy system detected an anomaly consistent with an implosion; the Navy did not consider it definitive at the time. A NOAA moored recorder about 900 miles away also captured it. Debris was found four days later near the Titanic. No quantitative timing or location error is public.

### 1.3 Claimed aircraft detections with no independent verification (grade C)

Kadri2024 presents ten historical crashes as detections at 2,200–4,700 km. None is accompanied by:

- a predicted arrival time and its residual;
- a false-alarm rate;
- a count of candidate transients in the window.

The previous session reconstructed the timing from the published figures (DIGITISED: transient times read from the panels, impact times from S1, ranges from the paper's maps). I checked the five S1 panels independently, using the stated panel start times and S1 impact times at 1.45–1.52 km/s:

| case, station | predicted water-path arrival | where Kadri's signal lies | verdict |
|---|---|---|---|
| F-35A, H11N/H11S | 11:02:41–11:04:25 / 11:03:41–11:05:29 | panel middle, about −0.5 min | consistent |
| Yemenia 626, H08N | 23:24–23:26 | panel starts 23:29; signal about +9 min | inconsistent |
| Yemenia 626, H08S | 23:25–23:27 | about +5.7 min | inconsistent |
| Sriwijaya 182, H08S | 08:22–08:24 at 3,828 km (later at the 4,694 km S1 states) | panel 08:06–08:16 ends before any water arrival | inconsistent |
| AF447, Transair 810 ×2 | (prior-session reconstruction) | +4 to +6.5 min | inconsistent |
| Lion Air 904, H01W/H08S | (prior-session reconstruction) | −0.8 / +0.1 min | consistent in time; the H01W amplitude is 15 dB above a favourable-coupling prediction, and Kadri himself suggests a different, possibly local event |

**Result (provisional, from digitised and published panel times):**

- **Of eight non-F-35 station-detections assessed, six are inconsistent with water-path timing by 4–12 minutes.** The two consistent ones belong to a low-energy, survivable approach accident, and its amplitude is implausible for that source.
- Three further cases (AB 1103, AirAsia 8501, Asiana 991) were not assessed.
- Several sources sit in shallow shelf seas (Java Sea, East China Sea), where SOFAR coupling is expected to be poor.

The aircraft "detections" therefore do not, at present, constitute a validation set; only the F-35A does.

### 1.4 What the ground-truth cases establish, and what they do not

1. Long-range detection of impulsive ocean sources by IMS triads is real. Timing errors are seconds for clean direct arrivals; location errors are 5–40 km with two or more stations.
2. **Coupling of a near-surface source into the deep channel is site-dependent over at least three decades** (Table A.4 ratios; TGS/Woodside; air7/air9; F-35 site). The only quantified aircraft coupling (F-35, ~10⁻⁴) comes from an exceptionally favourable site.
3. Single-station claims without timing residuals and without a background rate have, on the evidence available, failed when checked against ground truth.
4. Non-detections are informative only with a credible detection probability. AF447 shows the cost of getting that wrong.

---

## 2. IMS network calibration and long-range propagation modelling

- **Network and instruments** [Lawrence2004; Matsumoto2016; Wang2024]. IMS hydrophone triads sit near the channel axis, sample at 250 Hz, and have a nominal pass-band of 1–100 Hz. At H11N the response is roughly flat from 10 to 100 Hz and falls off below 10 Hz (published response figure, secondary). Signals from earthquakes rarely show energy above about 30 Hz; explosions reach 100 Hz [Lawrence2004].
- **Travel-time models.**
  - A spatially uniform celerity of 1.482 km/s with a standard deviation of 10 m/s is used operationally by the French national data centre [Vergoz2021].
  - Path-specific group velocities from normal-mode modelling with climatological profiles gave 1,486.2 and 1,486.35 m/s for the Curtin event paths [CMST2014].
  - Apparent velocity falls through an arrival (1.500 → 1.475 km/s at H10N) because of modal dispersion [Vergoz2021]. Onset and peak picks therefore differ systematically, so **picks must be "feature-based" and consistent between prediction and measurement** [Vergoz2021].
  - At 1,600–2,000 km, ±10 m/s of celerity corresponds to roughly ±7–9 s.
- **Propagation codes.**
  - Range-dependent parabolic equation (RAM/RAMGeo [Collins1993]) has been used for the H01 bearing transects [CMST2014], the Blackman airgun paths (elastic PE at 8 Hz) [Blackman2004UCRL] and the San Juan paths [Vergoz2021].
  - Adiabatic normal modes have been used for group velocity [CMST2014; Heaney1991] and for Diego Garcia blockage prediction [Upton2008].
  - Three-dimensional effects (horizontal refraction and diffraction around islands and ridges) matter at basin scale and near the stations [Heaney2009; Heaney2017; Heaney1991]. Vergoz2021 explicitly did not model them.
  - The standard reference is Jensen2011; profiles are summarised in Munk1974 and in climatologies such as ChuFan2024 (WOA23-based axis depth).
- **Blockage and scattering.** The Ninety East Ridge and Broken Ridge partly shadow H01 from the north-west and west. The Central Indian Ridge and the Chagos–Laccadive Ridge shadow H08 [Blackman2004UCRL]. The Rio Grande Rise costs about 20 dB at 7 Hz [Vergoz2021]. CMST2014 shows a ridge crest rising to about 1,000 m that *reduces* transmission loss by about 20 dB for a near-surface source on top of it, because it converts surface-trapped energy into the channel. Blockage and enhancement are two sides of the same bathymetric coupling.
- **Coupling of near-surface sources.** CMST2014 and DuncanDallOsto2023lay give the mechanism. A near-surface source radiates mostly at steep angles. It reaches the deep channel either by reflection off a seabed sloping down toward the receiver, or where the channel axis approaches the surface (high latitudes, or near the F-35 site). Otherwise the energy is lost in repeated surface and bottom interactions.
- **T-phase literature** [Okal2008; deGrootHedlin1999; Tolstoy2006] supplies the background population that dominates candidate lists: earthquake T-phases, ice events in the Antarctic sector (158–209° at HA01 [CMST2014]), and seismic surveys.

**Calibration status for this geometry.** In the open literature, the only measured transmission loss from near the 7th arc to H01 and H08S is Blackman's air9 (TL about 120–133 dB at H01, 10–60 Hz; about 122–135 dB at H08S, 5–60 Hz; values as transcribed in the brief from Blackman2004UCRL Fig. 23). air8 is the unexplained negative control.

---

## 3. Coupling of acoustic energy from an impacting body into the water column

- **No peer-reviewed measurement of the acoustic efficiency of a large aircraft water impact was found.** The F-35 estimate [Brown2026] is an end-to-end number: SOFAR-equivalent yield ÷ kinetic energy, through the Arons relation. It therefore bundles together:
  - (a) the fraction of mechanical energy radiated as sound at the source, and
  - (b) the site- and frequency-dependent factor coupling that sound into the channel toward a particular receiver.
- **Explosion source physics is mature.**
  - Peak pressure, energy-flux density and bubble period as functions of yield and depth [Arons1954; Chapman1988; Soloway2014].
  - The bubble-period relation was used to recover the calibration charge's depth (33 m) at 6,000 km [Vergoz2021; Nielsen2021].
  - Clarke1996 modelled near-surface and airburst coupling and found a net transfer into the channel of order 10⁻⁵ for a 1 kT burst at 1 km altitude, falling with height [via Brown2026]. Brown2026 sets a conditional upper limit of about 10⁻¹⁰ for bolide airbursts from 53 non-detecting station–fireball pairs.
- **Water-entry hydrodynamics** [Truscott2014] and **splash acoustics** [Franz1959] provide the physics of cavity formation and closure, and of the impulsive pressure at first contact. Kadri2017 reports tank impacts of spheres with pressure signatures structurally similar to some field transients. **No scaling law from these to a 200-tonne airframe with breakup, fuel and attitude has been validated.**
- **Implosion sources** (for the deferred second source in brief §13):
  - Theory and measurement for spherical cavities [Orr1976; Turner2007; Harben2000].
  - The field result that the same sphere was detected at 680 m but not at 320 m [Blackman2004UCRL].
  - The doublet structure inferred for San Juan by cepstral analysis [Vergoz2021].
  - CMST2014 Fig. 14 shows that sources deeper than the channel axis couple efficiently regardless of bathymetry.
- **Energy is not amplitude.** Nielsen2021 cautions against inferring relative source energy from relative received level. Brown2026 shows that Arons over-predicts for shallow sources. Both support the brief's position that energy and τ do not determine pressure, spectrum or directivity.

---

## 4. Acoustic-gravity waves (AGW): theory, observation and claims

- **Theory.** In a compressible ocean of depth H, bottom or surface disturbances radiate surface-gravity waves and a discrete family of acoustic modes. The modes have cut-off frequencies f_n = (2n−1)c/(4H): **0.094 Hz for the first mode at 4,000 m**. Below cut-off a mode does not propagate.
  - The theory was developed for seabed motion [Yamamoto1982; Nosov1999; Stiassnie2010; Oliveira2016; Mei2018], surface disturbances [Renzi2014], elastic seabeds [Eyov2013; Kadri2019; Williams2023], shelf-break interaction [KadriStiassnie2012] and tsunami propagation [Abdolali2017].
  - Gravity changes the mode structure appreciably only near the cut-offs. At 2–40 Hz a 4,000 m water column carries about 27 to 213 propagating modes (my arithmetic from the formula), and these are ordinary acoustic modes for which gravity is negligible.
- **Verified observations exist only near the source.**
  - Ocean-bottom pressure gauges inside the 2003 Tokachi-oki source recorded water-column elastic oscillations at the predicted c/4H resonance [Nosov2007; abstract and secondary].
  - IMS hydrophones near the 2015 Chile source recorded low-frequency T-phase features and the passing tsunami [Matsumoto2016].
  - Tsunami-period signals from 2004 were seen on hydrophones [Hanson2005; metadata only].
  - **I found no independently verified far-field (≥1,000 km) AGW detection from an impulsive surface source.**
- **Claims applied to MH370.**
  - Kadri2017 proposes single-station ranging from "AGW" modal dispersion. Its numerical self-consistency is 0.02%, but against two catalogued M5.1 earthquakes the field error was **+140 km (+5.9%) and −100 km (−1.8%)**.
  - Kadri2017, Kadri2019 and Kadri2024 all high-pass the data at 5 Hz and band-pass 2–40 Hz. **That removes the AGW cut-off band entirely.** What remains is the deep-sound-channel band, where the isovelocity constant-depth layer model behind the inversion is not the governing physics over range-dependent paths.
  - Kadri2019 adds water-to-seabed transmission routes that let the same signal (E1) lie anywhere from 1,900 to 4,294 km. This removes the range constraint rather than sharpening it.
- **Instrument limit.** The AGW band (≲1 Hz at abyssal depth) lies below the nominal 1–100 Hz IMS pass-band. Matsumoto2016 shows that tsunami-period energy is recoverable near the source, so the band is not absent, but any AGW prediction must be convolved with the station's actual low-frequency response before detectability is claimed.

---

## 5. Detection statistics

- **Look-elsewhere / trials factors** [Gross2010]. The global significance of the largest of many correlated tests must be computed over the whole search, either by an effective trials count or by an empirical null of the search maximum. Brief §5's 2·W·B arithmetic reproduces exactly (my check): 216,000 trials and 5.34σ per trial at ±1 h and 30 Hz; 4.39σ and 4.15σ after ±30 s and ±10 s two-station coincidence.
- **Time slides** [Was2010; Abbott2016]. The coincidence background is estimated by repeatedly shifting one detector's data by more than the physical lag. This preserves each detector's non-Gaussian, bursty noise and removes true coincidences. It is the accepted method for multi-site claims.
- **Surrogate nulls** [Theiler1992; Schreiber1996; Schreiber2000]. IAAFT surrogates preserve amplitude distribution and power spectrum but destroy temporal clustering, so they under-estimate the background of burst-like transients. **Burst-preserving resampling** (block bootstrap [Kunsch1989], stationary bootstrap [Politis1994], cycle-permutation for periodic airguns) keeps clustering. Expect null-model dependence: the prior work here shows p ≈ 0.001 under IAAFT against p ≈ 0.6–0.9 under burst- and phase-preserving nulls for the same feature (see critique, item 9).
- **Empirical false-alarm calibration of correlation detectors** on real background [Gibbons2006]. Thresholds are set from the detector's own output on data known to lack the signal, not from Gaussian theory.
- **Detection probability in a Bayesian monitoring model** [Arora2013]. NET-VISA, now used at the IDC, models detection probability per station and phase as a logistic function of magnitude, distance and station terms. It is fitted to historical detections and non-detections, and false detections are a separate Poisson process. That is the structure the brief's §2 rule 2 likelihood `(1 − P_D) + P_D × (match ÷ background)` needs, with the background rate a proper density.
- **Injection-recovery.** Injecting synthetic signals into real background and measuring recovery as a function of amplitude is standard practice in gravitational-wave searches [Abbott2016] and is the only defensible way to obtain P_D under real noise.
- **Single-event Bayes factors.** CMST2014 applied Bayes' theorem to the coincidence of HA01 and RCS arrivals. The form is correct, but the background rate came from two events in five hours, and the conclusion depends strongly on a prior the authors could not set (see critique, item 5).

---

## 6. Synthesis: empirical error distributions to carry into the module

| quantity | demonstrated values | source |
|---|---|---|
| bearing, high SNR | within 1–2°; ±0.75° (HA01, Curtin event); 0.6° mean bias (HA08S, TGS); 0.8° systematic correction applied at HA01 | Blackman2004UCRL; CMST2014; Kadri2017 |
| bearing, low SNR or noisy station | 3.4° (M2.7 Sinabang at H08S, same night); ±4.6° (Ascension, 2024 landslide) | Kadri2024; TrouSansFond2025 (abstract only) |
| bearing, claimed | ±0.4° at 99.5% | Kadri2024 |
| timing, direct arrival | within a few s at 1.49 km/s; ±9 s origin time (San Juan relocation); 3 s pick → 5 km | Blackman2004UCRL; Vergoz2021 |
| two-station time difference | ±4 s (stated); cross-checks 3.2 ± 6 s and 0 ± 7 s | CMST2014 |
| location, two distant triads | 19.8 km (San Juan), 39 km (calibration charge); 3.5 km with reflected arrivals | Nielsen2021; Vergoz2021 |
| single-station range from dispersion | −1.8% to +5.9% | Kadri2017 |
| shallow-source coupling relative to Arons | 4×10⁻⁴ to ~1.7 | Brown2026 Table A.4 |
| aircraft end-to-end coupling | ~10⁻⁴ (upper bound, favourable site) | Brown2026 |

The bearing distribution is **heavy-tailed**: a core of about 0.5–1°, station biases of 0.5–1°, and a low-SNR tail of several degrees.

---

## Implications for this module

1. **Engine validation set (§3, §7 step 1, §11).** Validate against every controlled case in the region, not only air9: air9 at H01 and H08S; air8 as the negative control; the SUS 2003 shots; the 320 m versus 680 m sphere pair; the TGS-detected/Woodside-undetected pair on the MH370 night; and the two Curtin clock cross-check events as timing controls. Treat Brown2026 Table A.4 as an out-of-region check of shallow-source coupling. A model that reproduces air9 but predicts air8 or Woodside as detectable is mis-specified.
2. **Split η (impact source interface; §3).** Model the coupling term as η_src(γ, ż, attitude, breakup, τ) × C_site(f, source depth, local slope, path), with C_site computed by range-dependent PE along each path. The F-35's ~10⁻⁴ is an end-to-end upper bound at a favourable site. Removing its C_site by modelling the H11 path is the only way to transfer it.
3. **Prior width for η (§3, P_D gate §2 rule 2).** The known-yield shallow-source ratios span about 3.5 decades, so the brief's "at least three decades" is a minimum. Carry η_src log-uniform over at least four decades below the F-35-derived anchor. Report received-level sensitivity to η separately. Run injection-recovery across the whole η range, as the 2026-10-08 inbox ruling requires.
4. **Do not use the Arons relation as a source model for shallow aircraft impacts (§11).** It is an in-channel relation that over-predicts for shallow sources. Use it, if at all, only as a relative scaling inside C_site-corrected predictions. The archived near-field shock law at 2,000–3,700 km is already ruled out by brief §11.
5. **Timing model (§1 mission, §6(a)).** Use path-specific group velocity from mode or PE modelling (expect about 1.482–1.487 km/s), with feature-based picks matched between prediction and measurement. The error budget is about ±5–10 s at 1,600–2,000 km, plus a separate alternative for reflected or secondary arrivals arriving minutes later [Vergoz2021]. Do not widen windows to swallow them.
6. **Bearing likelihood (§5).** Use a mixture: a core with σ ≈ 0.5–1°, a station bias term, and a heavy tail (for example Student-t or a 3–5° component) whose weight depends on SNR. The claimed ±0.4° must not be used.
7. **Keep the AGW branch separate and instrument-limited (§2 rule 3; impact source interface).** AGW predictions live below about 1 Hz. They must be convolved with each station's low-frequency response before any detectability claim. Analyses at 2–40 Hz, including all of Kadri's MH370 candidates, belong to the SOFAR branch whatever they are called, and must be scored there.
8. **Significance (§2 rule 4; §5; §6(b)).** Use time slides for cross-station coincidences. Report both an IAAFT null and a burst-preserving null (stationary bootstrap, plus cycle permutation where airguns are present), and treat the more conservative as authoritative. Thresholds come from each detector's empirical false-alarm curve on real background [Gibbons2006].
9. **Likelihood structure (§2 rule 2; §6(g)).** Follow NET-VISA [Arora2013]: P_D per station and branch as a logistic function of predicted received SNR, fitted by injection-recovery; false detections as a separate Poisson density. Include a "source did not couple" component (unfavourable site, ditching). AF447 [Stone2014] shows the cost of omitting failure modes from P_D.
10. **Composer test (§7 step 2).** Use the demonstrated error distributions in item 6 and §6, not the claimed ones. A single H01W detection with bearing only constrains a line. At 1,600–2,000 km, 1° of bearing is about 28–35 km along the arc, so the tail weights in item 6 will dominate how far a marginal detection moves the posterior.
11. **Do not import Duncan & Dall'Osto's 20–30 dB as a module prior (§3).** Their MH370 path is along the 301.6° bearing of the Curtin signal of interest, not the core-estimate geometry near −37°. Treat it as one comparison, and recompute along the core-estimate paths.
12. **Second, delayed source (§13).** Make implosion coupling depth-dependent: efficient below the channel axis [CMST2014 Fig. 14], weak at a few hundred metres [Blackman2004UCRL sphere pair]. Allow doublet or cepstral structure [Vergoz2021] in the source model.
13. **Kadri package (§9).** Ask first for the predicted-arrival residuals and raw triads for the six timing-inconsistent historical cases, and for the impact times and ranges Kadri used. Of his published cases, only the F-35A presently counts as validation.
