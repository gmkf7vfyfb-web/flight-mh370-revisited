# Metz et al. 2023 F-35A near-field records (180–255 km): digitisation, source spectrum and duration

EXPLORATORY. This is a calibration of the source model on a different aircraft (F-35A, 9 April 2019). Nothing in this note returns a likelihood to the composer. No received duration goes back to end of flight. No p-values are calculated in this note.

Source: Metz, Obana & Fukao (2023), *Pure Appl. Geophys.* 180:1343–1351, doi 10.1007/s00024-022-03117-6 (held artifact 7e4d336f; PDF sha256 652d200a…). Far-field records: the project's digitisation of Fig. 3 (module branch hypothesis/hydroacoustics, results-data/digitised/metz2023). Date of work: 24 Oct 2026.

## 1. Main findings

1. **The raw near-field waveforms are not openly downloadable.** The stations belong to the JAMSTEC Off Kushiro-Tokachi Cabled Observatory. Its Submarine Cable Data Center (www.jamstec.go.jp/scdc/) now redirects to a notice of "partial suspension of access to the data and services". Before that, data download was for registered users only (web search snippet of a 2009 JAMSTEC paper on the Off-Hatsushima observatory, https://www.mdpi.com/1424-8220/9/11/9241 and PMC3260640: registered users download data from the SCDC server, and the same site also serves the off-Kushiro–Tokachi and off-Muroto observatory data; full text not fetched; status in 2019 not confirmed). The IRIS FDSN station service and the IRIS federator catalogue return no DSOH or KSP stations for 9 April 2019. Free-registration source to list: JAMSTEC SCDC (now suspended). I did not register.
2. **The project had already digitised Fig. 2.** The module branch holds Fig. 2E–H envelope vertices and Fig. 2A–D spectrograms (prepare/digitise_metz_2023.py). The statement "not digitised" in the 23 Oct survey is stale. I digitised the figure again, independently, as a check. Envelope peaks agree to 0.002 dB. Spectrogram pixels agree to a median of 0.10 dB.
3. **The digitisation reproduces the numbers that Metz state.** Metz give a reading error of ±5.7 s at KSP2 and ±1.4 s at H11S1, defined as half the envelope width at the level midway between peak and ambient. These are the largest and smallest values of all traces. My values are 5.62 s at KSP2 (5.84 s with pre-onset noise) and 1.38 s at H11S1, and they are also the largest and smallest. Peak level above pre-onset noise is 21.9 dB (DSOH) and 21.6 dB (KSP1). Metz say "up to 20 dB above ambient".
4. **The near-field arrivals are about twice as long as the far-field arrivals.** The 5–95 % energy span is 7.1–10.5 s near (180–255 km) and 3.3–5.0 s far (3,249–3,341 km; six elements). Propagation cannot make a signal shorter. Thus the source energy span (at the angles that the deep sound channel holds) is at most about 3.3 s (H11S1). Most of the near-field length therefore comes from the path, that is, the seabed and slope reverberation at the near stations.
5. **The near-field onset is sharp.** The 10–90 % rise of the 1-s RMS envelope is 0.76 s at DSOH and 0.84 s at KSP3. A step onset through a 1-s window gives 0.80 s. So the 1-s window does not resolve the onset. The emergent onset at H11N ("overture", 10–90 % rise 3.1–3.7 s) is therefore a path effect of the deep sound channel, not a source property.
6. **High frequencies come first and stop early in the near field.** The 25–40 Hz energy has a 5–95 % span of 1.9 s (DSOH) and 2.5 s (KSP1), with its median 1.3–1.6 s after onset. The 4–10 Hz energy (74–90 % of the 4–40 Hz energy) continues to 7.9–12.9 s. At Wake Island all bands arrive together. One interpretation is a short broadband entry phase (≤ about 2–3 s) followed by low-frequency energy. Path dispersion in the near field can also produce this pattern. The far field cannot separate the two.
7. **The ~20 Hz gap is present at all four near stations and both far stations.** The 18–24 Hz band is at the colour floor (≤ 90 dB re 1 µPa²/Hz) at all near stations. It is 0.8–4.6 dB (floor filled at 90 dB) or 5.3–11.2 dB (floor filled at 80 dB) below the mean of the 12–17 Hz and 26–34 Hz bands. Because the gap does not move with range or receiver geometry, it is not a surface-image notch at the assumed depths. A first notch at 20 Hz needs d·sinθ ≈ 37 m (f = c / 2d sinθ). That is impossible for d ≤ 30 m, and such a notch would move with the ray angle. The gap is therefore a source feature or a common processing feature. Two pulses about 25 ms apart would give notches at 20 and 60 Hz, but this explanation is not tested.
8. **Received spectra are almost the same near and far; the implied source spectrum is steeper than f⁻².** Over 5–40 Hz the received excess spectrum falls by −4.0 to −8.5 dB/octave near and −4.4 to −4.8 dB/octave far (floor at the colour floor). After the module TL is removed (KRAKEN, surface image included), the implied source ESD slope is −12.3 ± 0.5 dB/octave near and −10.1 ± 0.5 dB/octave far at z_s 10 m. The values at 2 m and 30 m are within 0.7 dB/octave of these. Over the like-for-like 5–16 Hz band the near stations give −12.6 to −14.8, H11N1 −12.6 and H11S1 −6.8 dB/octave. The project's one-pole f⁻² model (−6.0 dB/octave above the corner) plus a surface image does not fit. An f⁻⁴-like source (−12 dB/octave) plus a surface image fits at all three depths. Caveat: the module TL fails the 2001 airgun frequency-slope check (measured minus predicted +12.7 dB/octave at H01W, +7.4 dB/octave at H08S). If that tilt is a path error, the implied source slopes are biased steep by a similar amount. The received near-versus-far comparison does not use TL and is not affected.
9. **The near field does not narrow the coupling and source-depth trade-off.** The D1 coupling from the near field is 0.106 (2 m), 0.00443 (10 m) and 0.000679 (30 m). That is 4.2 × the like-for-like far-field KRAKEN value at every depth (2.4 × without KSP2). The ratio does not change with depth, because both near and far records are in the low-kd surface-image regime. The near-field TL slopes differ between depths by at most 1.3 dB/octave, which is less than the 3.7 dB/octave scatter between stations. A soft bottom changes the near-field value by about ×200. The near-field level calibration is therefore dominated by the bottom model.
10. **The Metz location is 21.4 km from the module working point.** The point 180 km from DSOH, 255 km from KSP3 and 134.7 km from Misawa is 40.4496 N 142.9237 E. The module working point (40.64 N 142.96 E) is also 134.8 km from Misawa, but it is only 162.4 km from DSOH and 236.6 km from KSP3. Kadri S1 (40°30′10″N 142°04′37″E) is 64.0 km from Misawa, which confirms the noted discrepancy. I used the Metz-consistent point for the near-field paths.

## 2. Crash geometry as Metz give it

Metz give no epicentre coordinates. They state these facts. The last radar contact was at 10:26:30 UTC, about 135 km east of Misawa Air Base. The descent was steep, at about 300 m/s. The acoustic origin time is 10:26:32 ± 9 s. The 90 % ellipse is 844 km² (semi-axes 36.8 and 7.3 km) and lies within 8 km of the 135-km circle (cross in Fig. 1E). The cabled stations are 180 km (DSOH) to 255 km (KSP3) from the event, at depths of 2,124 m (KSP3) to 3,428 m (KSP2). The local travel-time model is a constant 1,475 m/s.

I read the station positions from the Fig. 1A markers. That map is an unscaled latitude-longitude grid at 317.5 px per degree. The aircraft icon reads 40.706 N 141.383 E (Misawa Air Base is about 40.70 N 141.37 E). The east edge of the 135-km circle reads 136 km from the icon. GEBCO 2026 depths at the read positions agree with Metz: KSP2 is 3,442 m (Metz 3,428 m) and KSP3 is 2,136 m (Metz 2,124 m).

| Item | Lat (°N) | Lon (°E) | Source of position | GEBCO depth (m) | Metz depth (m) | Range from P (km) | Range from W (km) |
|---|---|---|---|---|---|---|---|
| Off Kushiro-Tokachi DSOH | 41.6630 | 144.3433 | Metz Fig. 1A marker (bbox centre, graticule 317.5 px/deg), +/-~2 km | 2626 |  | 180.0 | 162.4 |
| KSP1 | 41.6835 | 144.3953 | Metz Fig. 1A marker | 2364 |  | 184.6 | 167.2 |
| KSP2 | 41.9370 | 145.0598 | Metz Fig. 1A marker | 3442 | 3428 | 243.7 | 227.3 |
| KSP3 | 42.2504 | 144.8142 | Metz Fig. 1A marker | 2136 | 2124 | 255.0 | 236.6 |
| P: source point consistent with Metz ranges | 40.4496 | 142.9237 | intersection of 180 km (DSOH) and 255 km (KSP3) circles, branch 134.7 km from Misawa | 1532 |  | 0.0 | 21.4 |
| W: module working point | 40.6400 | 142.9600 | prereg.py SRC; 134.8 km from Misawa | 1509 |  | 21.4 | 0.0 |
| Kadri S1 site | 40.5028 | 142.0769 | Kadri S1 40d30'10"N 142d04'37"E; 64.0 km from Misawa (Metz: ~135 km) |  |  | 72.0 | 76.3 |
| Misawa Air Base (icon) | 40.7055 | 141.3827 | Metz Fig. 1A aircraft icon; reference 40.703 N 141.368 E used for ranges |  |  | 133.5 | 133.6 |

Table file: [metz-geometry.csv]({{artifact:3018d01d-c250-4727-a1dc-cf7c7e5f7d60}}).

## 3. Digitisation (Fig. 2) and checks

![Digitisation check: digitised envelopes over the published Fig. 2 and re-rendered digitised spectrograms]({{artifact:4299d543-c3b1-4b12-b556-fb69d76265a7}})

- **Envelopes (E–H).** These are PDF vector polylines (PyMuPDF get_drawings, page 4), with 1,656–1,738 vertices per trace including Bezier sampling. They are resampled to Metz's 0.02-s step (1-s RMS with 98 % overlap). The axes come from the vector frame and tick strokes. The 10-s ticks are 25.901 pt apart (KSP2 25.607 pt). Every frame spans 30.000 s. The y-tick residual is ≤ 0.0004 dB. The time axes start at 10:28:20 (DSOH), 10:28:25 (KSP1), 10:29:10 (KSP2) and 10:29:15 (KSP3).
- **Spectrograms (A–D).** These come from the embedded raster (xref 42, 1652 × 251 px), inverted to the nearest colour-bar colour (90–110 dB re 1 µPa²/Hz, 0–40 Hz). The colour bar is trimmed by two rows at each end, because the frame stroke bleeds into it. Frame and tick pixels (colour distance > 30 RGB units, 1.7–2.0 % of pixels) are masked and filled along time. The unmasked colour distance is 7–10 RGB units at p95. White means at or below the 90 dB floor.
- **Calibration check.** The 4–40 Hz exposure integrated from the spectrogram agrees with the envelope exposure to −0.27 to +1.04 dB at the four stations.
- **Finding for the project files.** The module-branch Fig. 2A–D files keep the frame and tick pixels at about 110 dB (median 109.9 dB at the pixels I masked). The far-field Fig. 3A/B files show 13–17 % saturated pixels on their edge rows and columns, which suggests the same artefact. These pixels lie mostly at the panel edges, outside the arrival windows and the 4–64 Hz rows. The effect on the project's far-field numbers is probably small, but I did not quantify it.

Files: [metz-fig2-digitised-DSOH.csv]({{artifact:af9726e0-874f-41ed-b927-48535b374e25}}), [metz-fig2-digitised-KSP1.csv]({{artifact:f2b38ae0-e0bc-4a50-a80c-8b40cc0448bb}}), [metz-fig2-digitised-KSP2.csv]({{artifact:67e0ed65-2772-4e56-9fb2-f5aee85912b9}}), [metz-fig2-digitised-KSP3.csv]({{artifact:a4430b68-265a-480d-b405-13c2a7a6ebc7}}), the raw vertices [metz-fig2-vertices.csv]({{artifact:f4565054-4560-40bf-84ef-ec443f7f0e23}}), the spectrograms (.npz, one per station, for example [metz-fig2-spectrogram-DSOH.npz]({{artifact:b7e5f973-1463-4da2-b48c-791f19722905}})) and the checks [digitise_fig2_checks.json]({{artifact:823f4e50-bef7-4a6b-bfd8-52121c44814d}}).

## 4. Received duration and arrival structure

![Near-field and far-field envelopes aligned at onset]({{artifact:c2341cdf-3942-4357-8165-82ee3faf5620}})

Conventions are those of prepare/metz_f35a/obs.py. Module noise is the median outside ±8 s of the peak. The arrival is the interval where L exceeds noise + 1 dB. The 5–95 % span is that of the noise-subtracted energy. I add a second noise level (pre-onset noise: median of the 4 s that end 1 s before onset), because the DSOH coda reaches beyond +8 s. Onset is the last sample before the peak at or below noise + 3 dB.

| Station | Range (km) | Peak 1-s RMS (dB re 1 µPa) | Pre-onset noise (dB) | Peak SNR, pre-onset noise (dB) | Peak SNR, module noise (dB) | −6 dB width (s) | −10 dB width (s) | 5–95 % energy span (s) | Length above noise+1 dB (s) | 10–90 % rise (s) | Peak after onset (s) | Decay (dB/s) | SEL (dB re 1 µPa²s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DSOH | 180 | 117.5 | 95.6 | 21.9 | 16.6 | 4.2 | 7.4 | 8.1 | 12.3 | 0.76 | 1.7 | -1.2 | 121.9 |
| KSP1 | 185 | 118.9 | 97.2 | 21.6 | 20.9 | 5.3 | 6.7 | 9.4 | 16.0 | 2.52 | 5.1 | -1.3 | 124.3 |
| KSP2 | 244 | 112.1 | 99.4 | 12.7 | 11.9 | 11.3 | 15.4 | 10.5 | 16.2 | 2.28 | 6.3 | -0.8 | 120.3 |
| KSP3 | 255 | 112.4 | 100.8 | 11.7 | 11.9 | 8.0 | 9.8 | 7.1 | 10.3 | 0.84 | 5.9 | -2.7 | 118.9 |
| H11N1 | 3249 | 110.6 | 96.5 | 14.1 | 15.2 | 3.2 | 5.5 | 4.9 | 10.2 | 3.55 | 5.2 | -6.4 | 113.9 |
| H11N2 | 3249 | 109.9 | 96.8 | 13.1 | 13.7 | 3.9 | 5.9 | 4.6 | 10.0 | 3.10 | 5.5 | -6.7 | 114.3 |
| H11N3 | 3249 | 111.3 | 96.4 | 14.8 | 15.9 | 3.5 | 5.8 | 5.0 | 11.2 | 3.70 | 5.4 | -5.3 | 114.7 |
| H11S1 | 3341 | 108.7 | 94.4 | 14.3 | 14.6 | 2.3 | 4.3 | 3.3 | 6.7 | 1.45 | 2.4 | -4.6 | 110.8 |
| H11S2 | 3341 | 106.1 | 93.5 | 12.5 | 12.6 | 2.9 | 5.0 | 3.3 | 6.3 | 1.40 | 2.5 | -4.6 | 108.7 |
| H11S3 | 3341 | 106.5 | 94.9 | 11.6 | 12.2 | 2.5 | 5.3 | 3.6 | 7.3 | 1.55 | 2.4 | -4.4 | 108.6 |

Table file: [metz-nearfield-derived.csv]({{artifact:817bdb0f-4188-44a5-add8-92402b7a054b}}) (includes sub-peak lists and all spectral metrics).

**Arrival structure.** Sub-peaks with prominence ≥ 2 dB are listed below.

- DSOH has one main peak, 1.7 s after onset.
- KSP1 has a first plateau at about 1.4 s, the main peak at 5.1 s and a second peak at 9.8 s (3.7 dB prominence).
- KSP2 has one broad peak at 6.3 s.
- KSP3 has a precursor at 1.2 s (2.5 dB prominence) and the main peak at 5.9 s.

The interval between the first and the main arrival is 0 to 4.7 s, and it changes from station to station. A sub-event sequence at the source would keep the same intervals at every station. The structure is therefore consistent with multipath (bottom-bounce groups), not with source sub-events. In the near field there is no emergent "overture". It is a feature of the far-field channel.

**Per-band timing** (relative to onset; 5–95 % span, median, share of 4–40 Hz energy):

| Station | 4–10 Hz | 10–17 Hz | 25–40 Hz |
|---|---|---|---|
| DSOH | 1.0–10.4 s (median 3.5, 73.8 %) | 0.9–6.4 s (median 2.6, 19.1 %) | 0.6–2.5 s (median 1.6, 6.9 %) |
| KSP1 | 1.2–11.5 s (median 4.9, 81.4 %) | 1.1–5.9 s (median 3.0, 15.5 %) | 0.6–3.1 s (median 1.3, 3.1 %) |
| KSP2 | 2.3–12.9 s (median 6.7, 90.0 %) | 1.6–9.8 s (median 6.2, 9.6 %) | 0.9–9.1 s (median 2.1, 0.3 %) |
| KSP3 | 0.8–7.9 s (median 5.7, 89.2 %) | 0.2–6.8 s (median 3.5, 7.0 %) | 0.4–4.9 s (median 2.2, 3.7 %) |
| H11N1 | 1.4–6.2 s (median 4.7, 72.4 %) | 1.0–5.5 s (median 4.9, 19.1 %) | -0.6–5.9 s (median 4.6, 7.8 %) |
| H11S1 | 0.7–4.2 s (median 2.4, 64.7 %) | 1.2–3.3 s (median 2.3, 27.8 %) | 0.8–4.6 s (median 2.2, 5.8 %) |

![Per-band arrival timing near and far]({{artifact:d0d0d9d4-d386-425a-8f8f-4af14f78b664}})

**Path model for duration (declared simple model, not the module).** I computed Bellhop eigenray arrivals (from the same Acoustics Toolbox build as the module's KRAKEN). The model uses the GEBCO 2026 track of each path, one range-independent WOA23 April profile (median along the path), the module hard bottom and seabed receivers. Bins of 0.1 s are summed coherently and averaged over 5–40 Hz. The model has 28–90 eigenrays per path. With a short source (τ = 0) it predicts −6 dB widths of 1.0–1.9 s, against 4.2–11.3 s observed. The best-fit boxcar source lengths at 10 m are 6–10 s. These conflict with the far-field bound of about 3.3 s. The ray model thus does not represent the near-field reverberation, and **τ is not identifiable from the near field with this path model.**

| Station | Path-only (τ = 0) RMS misfit (dB) | Path-only −6 dB width (s) | Observed −6 dB width (s) | Path-only 5–95 % span (s) | Observed span (s) | Best boxcar τ (s) | Misfit at best τ (dB) |
|---|---|---|---|---|---|---|---|
| DSOH | 8.8 | 1.0 | 4.2 | 2.8 | 8.1 | 10 | 4.1 |
| KSP1 | 8.1 | 1.0 | 5.3 | 5.7 | 9.4 | 8 | 2.8 |
| KSP2 | 7.0 | 1.0 | 11.3 | 1.5 | 10.5 | 10 | 1.9 |
| KSP3 | 3.3 | 1.9 | 8.0 | 4.4 | 7.1 | 6 | 1.0 |

Files: [metz-nearfield-duration-fit.csv]({{artifact:d9e65af0-9c28-48ee-a141-072c53c29b53}}), [metz-nearfield-arrivals.csv]({{artifact:d77636fa-327a-4888-89c2-522d33ebe7ef}}), [metz-nearfield-impulse-response.csv]({{artifact:693435f8-2f82-4a83-9f12-0110eb3fb6cd}}), [metz-nearfield-pred-envelopes.csv]({{artifact:21e4ab2f-8a12-49c0-9558-074b0fef05fc}}).

## 5. Spectral shape

![Received and implied source spectra, near and far]({{artifact:dd4f3c72-92f1-4946-82ff-1afed3ed3bdd}})

The table uses the colour floor as fill (near 90 dB, far 80 dB). The alternative fills (80 / 70 dB) are in the CSV. Slopes are least-squares fits over the third-octave bands with signal − noise ≥ 3 dB (the route-2 rule of step2_invert.py). KSP1–3 keep only the 5–12.5 Hz bands, so the 5–16 Hz column is the like-for-like value. ESD slope = band-energy slope − 3.01 dB/octave. The project's route-2 numbers (step4_route2.json) are band-energy slopes: −5.95 to −7.31 dB/octave far, which is −9.0 to −10.3 dB/octave as ESD, in agreement with the values here.

| Station | Received excess slope 5–40 Hz (dB/octave) | Received excess slope 5–16 Hz | Implied source ESD slope 5–40 Hz, z_s 2/10/30 m | Same, 5–16 Hz | Mean PSD 12–17 Hz (dB re 1 µPa²/Hz) | 18–24 Hz | 26–34 Hz | Gap depth (dB) | Spectrogram minus envelope exposure (dB) |
|---|---|---|---|---|---|---|---|---|---|
| DSOH | -4.0 ± 0.8 (n 8) | -6.5 | -11.2 / -11.1 / -9.9 | -13.5 / -13.5 / -13.2 | 95.7 | 90.2 | 93.8 | ≥ 4.6 | +0.46 |
| KSP1 | -6.1 ± 0.7 (n 5) | -6.1 | -12.6 / -12.6 / -12.4 | -12.6 / -12.6 / -12.4 | 95.3 | 90.1 | 92.2 | ≥ 3.7 | -0.27 |
| KSP2 | -8.5 ± 1.8 (n 5) | -8.5 | -14.9 / -14.8 / -14.5 | -14.9 / -14.8 / -14.5 | 91.4 | 90.0 | 90.1 | ≥ 0.8 | +0.62 |
| KSP3 | -7.2 ± 2.7 (n 4) | -7.2 | -12.9 / -12.8 / -12.7 | -12.9 / -12.8 / -12.7 | 91.9 | 90.0 | 91.5 | ≥ 1.7 | +0.17 |
| H11N1 | -4.8 ± 0.8 (n 9) | -6.9 | -10.4 / -10.3 / -9.6 | -12.7 / -12.6 / -12.4 | 86.6 | 80.7 | 85.7 | ≥ 5.5 | -0.93 |
| H11S1 | -4.4 ± 0.7 (n 8) | -1.2 | -10.0 / -10.0 / -9.4 | -6.8 / -6.8 / -6.7 | 86.3 | 81.4 | 83.3 | ≥ 3.4 | -0.87 |

The TL gain slope (KRAKEN, which includes the surface image) is +6.5 / +6.4 / +5.2 dB/octave near and +5.6 / +5.6 / +4.9 dB/octave far at 2 / 10 / 30 m. Thus a surface image at any of the three depths, combined with an f⁻² source, predicts a received slope of about 0 dB/octave, whereas −4 to −8.5 dB/octave is observed. Combined with an f⁻⁴-like source, the prediction is about −6 dB/octave, which agrees. Files: [metz-band-spectra.csv]({{artifact:0e36b9a2-cdc9-492a-afdd-d9374c6f943b}}), [metz-source-slope.csv]({{artifact:36fce763-909c-4e20-97db-40fff3772877}}), [metz-source-slope-5-16Hz.csv]({{artifact:aaca7cad-fd23-4e8b-ac04-ff757a39a126}}), [metz-band-timing.json]({{artifact:7d624a71-c8c0-4d94-ba51-6ce49c0700fa}}).

## 6. Source implications and near-field coupling (D1)

![Coupling efficiency by source depth, near and far]({{artifact:404abd1e-b492-4df1-a3a5-316aad7933e4}})

**Definition class D1.** η = SE_rx / [E ρc/(2π) Σ_b W_b s_b(τ, slope) 10^(−TL_b/10)]. This is the step2_invert.py relation, unchanged. It uses a one-pole ESD normalised over 1–500 Hz, E = 900 MJ (Brown et al. 2026) and ρc = 1025 × 1500. Near-field inputs: SE_rx is the 4–40 Hz exposure of the digitised envelope, over the third-octave bands 5–40 Hz (W_40 = 0.47, the share of the 40 Hz band below 40 Hz, by analogy with W63). TL is the module KRAKEN chain (adiabatic incoherent modes, GEBCO 2026, WOA23 B5C2 April, hard bottom cp 1650, ρ 1.9, 0.5 dB/λ, Francois-Garrison absorption, surface image at z_s), on paths from the Metz-consistent point P to receivers 2 m above the seabed. The far-field reference is step2_eta.csv (primary path, τ 1.1 s, slope 2, E mid). D4 (in-band 5–40 Hz radiated energy / KE) is given for completeness.

| z_s | Near D1, geometric mean (hard bottom, f⁻², τ ≥ 1.1 s, 900 MJ) | Near D1 by station | Station spread (max/min) | Near, soft bottom | Near, module working point | Near, pre-onset noise | Near, slope 4 | Near, τ 0.3 s | Far D1, KRAKEN only | Far D1, KRAKEN + RAM (project) | Near / far (KRAKEN) | Near D4 in-band 5–40 Hz | Far D4 in-band 5–40 Hz (KRAKEN) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 m | 0.106 | DSOH 0.043, KSP1 0.068, KSP2 0.57, KSP3 0.075 | 13.1 | 24.6 | 0.163 | 0.11 | 6.97 | 0.054 | 0.025 | 0.054 | 4.25 | 0.0923 (0.0547 without KSP2) | 0.0181 |
| 10 m | 0.00443 | DSOH 0.0018, KSP1 0.0029, KSP2 0.024, KSP3 0.0031 | 13.3 | 0.995 | 0.00671 | 0.0046 | 0.283 | 0.00225 | 0.00105 | 0.00226 | 4.22 | 0.0037 (0.00219 without KSP2) | 0.000727 |
| 30 m | 0.000679 | DSOH 0.00028, KSP1 0.00044, KSP2 0.0039, KSP3 0.00044 | 13.9 | 0.123 | 0.000952 | 0.000705 | 0.0346 | 0.000346 | 0.000162 | 0.000344 | 4.19 | 0.000422 (0.00025 without KSP2) | 8.26e-05 |

Files: [metz-nearfield-eta.csv]({{artifact:c17c4332-c48a-46b6-bb04-71a5e445a90c}}) (all stations, bottoms, source points, depths, slopes, τ grid, energies and noise definitions), [metz-source-implications.json]({{artifact:91b658bc-8aab-4d29-8530-a83087c0b81e}}), [metz-nearfield-tl.csv]({{artifact:da968925-ff5e-4666-86dc-fdd94168da75}}).

**What this means for the source model (exploratory).**

1. **Duration τ.** The far-field records bound the in-channel source energy span to about ≤ 3.3 s. That bound includes the 1-s window and the channel dispersion. The near-field onset is not resolved by the 1-s window. The high-frequency phase lasts about 2–2.5 s at the two closest stations. In the project's one-pole model, η does not depend on τ for τ ≥ 1.1 s, and τ = 0.3 s gives ×0.51. The step-5 pulse check used τ = 10 s, which is longer than the far-field bound. These results do not feed back into end of flight.
2. **Spectrum.** Over 5–40 Hz the near and far records imply source ESD slopes of -9.4 to -14.9 dB/octave (all stations, z_s 2–30 m), not −6 dB/octave. Over 5–16 Hz H11S1 alone is shallower (−6.7 to −6.8 dB/octave). Under the D1 relation, slope 4 instead of slope 2 increases η by ×64 (near) and ×76 (far, KRAKEN). The source-slope choice is a larger lever on η than the near/far discrepancy. The airgun slope caveat applies (finding 8).
3. **Surface-image dipole.** In the low-kd regime the dipole is consistent with the near-field slopes at 2, 10 and 30 m if the source spectrum is f⁻⁴-like, and inconsistent at all three depths if it is f⁻². The near field gives no depth discrimination (finding 9). The 20 Hz gap is not a surface-image notch at these depths (finding 7).
4. **Coupling and depth.** The near-field D1 values are 0.106 / 0.00443 / 0.000679 at 2 / 10 / 30 m. They are 4.2 × the far-field KRAKEN values (2.50 × 10⁻² / 1.05 × 10⁻³ / 1.62 × 10⁻⁴) and 1.9–2.0 × the project RAM-corrected values (5.4 × 10⁻² / 2.26 × 10⁻³ / 3.4 × 10⁻⁴). The near/far ratio is a measure of the self-consistency of the module chain between 200 km and 3,300 km. It is not a new anchor. With the soft bottom the near values move by ×200, so the near-field level does not constrain η better than the far field. η and z_s must still be sampled together (survey rule).

## 7. Standing caveats

1. The propagation model fails the frequency-slope check against the 2001 airguns (+10 dB/octave at H01W, +7 dB/octave at H08S), although levels pass. This bears directly on the implied source slopes in section 5.
2. Detection probability is a proxy unless measured on real data. No detection statistic is computed here.
3. All values come from digitised published figures, not waveforms. The spectrograms are censored at the 90 dB colour floor (near) and the 80 dB floor (far), and their dynamic range is 20 dB.

## 8. Method summary and scripts

1. [digitise_metz_fig2.py]({{artifact:7e5c43f1-8ccb-499b-9bf0-b620e6efab8e}}): digitises Fig. 2 from the PDF (vectors + raster) and runs the axis checks.
2. [derive_nearfield.py]({{artifact:07ac961b-5565-4554-aadf-7b0040109414}}): computes the envelope and spectral metrics, near and far, with the same functions.
3. [nearfield_tl.py]({{artifact:1f5b749d-eed9-4157-a39b-74723ecc26ff}}): runs the module KRAKEN chain on the near-field paths (two source points, hard and soft bottom), with the FIELD fallback.
4. [source_implications.py]({{artifact:ee680eef-0687-410a-835c-6eb8fd5e08bc}}): computes the implied source slopes and the D1/D4 coupling.
5. [nearfield_arrivals.py]({{artifact:465cde08-6516-4ad5-bd97-79ae78803b26}}) and [nearfield_duration_fit.py]({{artifact:0ec651c9-1583-4e58-bb0b-ddae535e03c1}}): run the Bellhop arrivals and the source-duration fit.
6. [make_figures.py]({{artifact:20b33ee8-63ad-49f6-a90e-8cad07f95040}}): makes Figs. 1–5. This script regenerated the saved figures.

Environment: conda mh370-hydro; Acoustics Toolbox at_2026_8_29 binaries from ~/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a/at; ocean data from ~/Downloads/mh370-ocean-data (GEBCO 2026 NW Pacific layer, WOA23 B5C2 April soundspeed_nwpac); module code from hypothesis/hydroacoustics (read only).

## 9. Deviations

1. **Substituted source of data:** digitised figures replace the raw waveforms. The waveforms are not openly available (SCDC suspended; registration was required before). NIED was not checked. geofon.gfz-potsdam.de was blocked by the sandbox and not requested, because the IRIS federator, which also queries other FDSN centres, returned no stations.
2. **Repeated work:** Fig. 2 was already digitised in the project. My digitisation is an independent repeat. The far field uses the project's Fig. 3 digitisation unchanged; I did not digitise it again.
3. **Station positions** are read from Fig. 1A (±~2 km). They are not from an official station list, which was not available.
4. **Source point P** comes from Metz's rounded ranges (180, 255 km). The rounding uncertainty (a few km) is not propagated. I did not recompute the far-field η at P (P is 21.4 km from W; the project's ±8 km test changed η by ≤ 8 %).
5. **KRAKEN FIELD defect:** field.exe (at_2026_8_29) aborts deterministically for some profile counts (ReadModes.f90 line 184). For 240 of 576 near-field TL rows I removed the mid-path profile. On 138 rows where both ways run, the effect is ≤ 0.01 dB. KRAKEN ran serially. Three TL rows are infinite (zero field) and are excluded.
6. **Near-field TL is KRAKEN only** (no RAM, no N×2D). The like-for-like far-field comparison therefore uses KRAKEN only. RAM values are quoted for reference.
7. **Duration path model** is a declared simple model (Bellhop eigenrays, range-independent sound speed, bottom loss at 10 Hz, 6,001 beams), not a module tool. Its τ fit is inconclusive and is not used.
8. **Spectral censoring:** colour-floor fill 90 dB, with 80 dB as sensitivity. Masked tick pixels (1.7–2.0 %) are filled by interpolation. KSP1–3 retain only 4–5 bands for the slopes.
9. **Choices of mine:** W_40 = 0.47; pre-onset noise as a second noise definition; onset at noise + 3 dB; E fixed at 900 MJ in the headline (700/1100 MJ values are in the CSV).
10. **Not done:** near-field RAM or N×2D; quantification of the effect of the tick artefacts in the project's far-field spectrogram files; a test of the two-pulse explanation of the 20 Hz gap.
