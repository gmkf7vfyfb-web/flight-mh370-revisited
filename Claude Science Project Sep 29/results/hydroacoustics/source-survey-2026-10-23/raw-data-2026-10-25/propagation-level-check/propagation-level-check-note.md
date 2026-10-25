# Absolute level check of the propagation chain on known-energy explosions, and the ARA San Juan event, from raw IMS data

Hydroacoustics module, track 3, 25 October 2026. Exploratory, with a protocol written before any statistic was computed
(section 1; timestamp 2026-10-25T01:45:53Z). Nothing here is a likelihood and nothing moves the posterior. Standing caveats:
(1) frequency-slope failure of the propagation model on the 2001 airguns (+10 dB/oct H01W, +7 dB/oct H08S) — section 5 says how
this result changes it; (2) detection probability is a proxy unless measured on real data — section 6 gives the first real-data
measurement for M1b. Units: Pa, Pa^2 s, dB re 1 uPa (peak), dB re 1 uPa^2 s/Hz (band-average energy spectral density, ESD).

## Results in one paragraph
Raw IMS records at Ascension (H10N, H10S; EarthScope, anonymous) were downloaded for the San Juan calibration charge, the San Juan
loss event and all eight US Navy shock-trial shots (2016 x 5, 2021 x 3). The raw data reproduce the published levels: San Juan
peaks at H10N 138.2 dB re 1 uPa (Vergoz: 139), charge 128.5 dB (Vergoz: 130); the digitised Nielsen Fig. 5c PSD is matched by a
raw 60 s Welch PSD within 1.7 dB. **The stage-1b level FAIL (-14.4 dB) was mostly a unit conversion.** The digitised PSD was
converted to energy with a 10 s signal duration; the raw data show that the averaging window was about 50 s (39-71 s by band),
so that step understated the measured energy by about 7 dB. On raw data the charge at H10N is -2.8 to -8.2 dB (model too loud,
spread set by the source model), and at H10S it is -0.9 to +5.7 dB. Across 17 explosion-station pairs, 2 chains and 3 declared
source models, **the residual frequency slope is -3.7 to +2.9 dB/octave; none shows the airgun-type +7 to +13 dB/octave.**
Absolute level scatters by about 4-5 dB (SD over pairs, KRAKEN-only) about a bias that depends on the source model and, for the
shock trials, on a charge depth that no primary source gives. The model does not reproduce the H10S-H10N station difference for
the South American sources (measured +5.4 dB, predicted -1 to -2 dB), consistent with unmodelled Rio Grande Rise blockage on
the H10N path. The module's M1b matched filter detects the real San Juan arrival at p = 0.0026 (the floor, n = 379) at all five
usable elements, and the charge at p = 0.0027-0.0082; but background windows reach 0.93-0.98 on the same statistic. Through the
same chain the San Juan event is a 9-918 kg TNT-equivalent source for depths 200-900 m (G&S construction and 800 ft reference; up to 2,059 kg with the 300 ft reference; Heyburn et al. 2020: 428 kg lies inside
the range only for depths of about 800-900 m).

## 1. Pre-registration (written before computing; full text `prereg.md`)
Disclosure: the charge result at H10N was not blind (stage 1b digitised result known). Raw measurements, H10S, the FSST shots,
the second source model and the San Juan event were blind. Measurement (M1-M8): full StationXML response removed (input unit
PA, checked); arrival = 1-s RMS envelope peak (2-40 Hz) in [d/1.500 - 60 s, d/1.460 + 60 s]; signal window 60 s centred on the peak
(20 s and 120 s sensitivity); noise = median of 10 equal windows ending 60 s before; FFT ESD in base-2 third octaves, noise
subtracted; elements departing > 6 dB from the triad median in >= 3 bands flagged; peaks 1-60 Hz and 4-40 Hz; back-azimuth by
plane-wave fit to cross-correlation delays. Prediction (P1-P4): module KRAKEN and RAM, unchanged; two declared source models;
charge 108 kg / 33 m; FSST depth 61 m with 30 and 100 m sensitivity. Statistics: criteria.md C1 (LEVEL 4/7 dB, SLOPE 1.5/3 dB/oct,
SHAPE 3/5 dB). M1b test: module statistic unchanged, null from the same element on the same day, p = (k+1)/(n+1).

## 2. Inputs, definitions and cross-checks
| item | value used | source / definition | cross-check |
|---|---|---|---|
| Raw data | IM.H10N1-3, H10S1-3, EDH, 250 Hz | EarthScope FDSN dataselect, anonymous; StationXML response (PA -> COUNTS, ~1,800 counts/Pa at 10 Hz; one epoch since 2004-09-14) | pipeline reproduces stored F-35A OB01 exactly (1-s RMS 0.358 Pa, instantaneous 0.880 Pa, exposure 0.237 Pa^2 s) |
| Charge time, position | 20:04:30 +/- 14 s; 45.666 S 59.240 W | Vergoz et al. 2021 pp. 2528, 2543 | Nielsen et al. 2021 p. 2561 gives 45 40.00'S 59 24.900'W = 59.415 W, 13.6 km west: run as sensitivity (level change -1.5 to +0.5 dB) |
| Charge yield, depth | 108 kg TNT, 33 m | Vergoz (cepstral 0.454 s with Willis T = 2.1 W^1/3/(z+10)^5/6) | Nielsen 102 kg, ~30 m; 30 and 38 m run |
| San Juan event | 13:51:05 +/- 9 s; wreck 45.950 S 59.773 W, ~920 m | Vergoz 2021 pp. 2528, 2543 | arrival times within 1 s of the three published picks |
| FSST times, positions | 2016-06-10 17:10:48.64 (30.0335, -79.6406); 06-23 17:20:29.45 (29.9948, -79.449); 07-16 20:00:10.22 (29.7651, -79.4341); 09-04 18:29:29.80 (30.0952, -79.5416); 09-21 16:30:52.90 (30.0745, -79.5044); 2021-06-18 19:48:39.595 (29.7433, -79.3493); 07-16 17:48:33.533 (30.0852, -79.3251); 08-08 19:55:18.252 (30.1465, -79.6066) | USGS ComCat, event type "experimental explosion", horizontal error 3.0-7.1 km, depth fixed 0 | dates match Navy releases (2021: 18 Jun, 16 Jul, 8 Aug); observed back-azimuths at H10N within 0.8 deg of the geodesic. Heyburn et al. 2018 (BSSA, paywalled) not read |
| FSST yield | 6,759 kg TNT (2016), 18,000 kg (2021) | Brown 2026 Table A.4 as digitised in the ground-truth table | 2016 = 10,000 lb charge (Heyburn 2018 abstract) x HBX-type TNT equivalence; 2021 = 40,000 lb (Navy) |
| FSST charge depth | 61 m (200 ft) | **not found for 2016 or 2021**; 73 FR 43129 (2008 FSST, same 10,000 lb class) | 30 and 100 m run: the level moves by about 11 dB over that range |
| Paths | 21 sections (6 South American, 15 Florida) | GEBCO_2026 15" (3x3 median), WOA23 B5C2 event month (seasonal below 1,500 m), TEOS-10, 25 km nodes; audit paths.py convention, global netCDF loaders | rebuilt charge->H10N agrees with the ocean-transport export: depth median 2 m, c within 0.015 m/s (95 %); KRAKEN TL within 0.05-0.23 dB of stage 1b |
| Source SA | G&S 1971 construction re-implemented (audit gs_reconstruct.py, kappa 4, sin^2) + 191.1 dB | G&S NOLTR 71-160 Table 2 relations | reproduces G&S Table 3 at 800 ft to median +0.2 dB; over-predicts shallow tails by +5.7 to +11.2 dB (audit) |
| Source SB | G&S Table 3 column by explosion similitude: ESD(f) = ESD_ref(f s) + 20 log10(a s), a = (W/W_ref)^1/3, s = a ((z_ref+33 ft)/(z+33 ft))^5/6 | G&S Table 3 (p. 12), Table 2 time similitude | reference columns 1.8 lb at 60/300/800 ft, 3 lb at 60/500 ft; spread reported |

Validity: G&S state "small charges (weighing up to a few lb)" to about 1,000 ft. 108 kg, 6,759 kg and 18,000 kg are 50-10,000
times outside that range; reduced depths (z/W^1/3, ft/lb^1/3) are 17.5 (charge), 8.1 (FSST 2016), 5.9 (FSST 2021) against 42-658
for the G&S columns. Source uncertainty is therefore not +/-3 dB; the spread between SA and SB (3.7-5.3 dB at the charge) is the
honest lower bound.

## 3. Measurements (raw data)
Tables: `arrivals_levels_by_element.csv`, `backazimuth_by_triad.csv`, `triad_bands.csv`, `meas_bands.csv`, `peaks_by_band.csv`.
- **H10S1 is excluded in every event**: it reads about 30 dB below H10S2/S3 (e.g. San Juan 0.44 Pa against 15.6-19.0 Pa), consistent
  with Nielsen 2021 (H10S1 electronic noise, excluded from IDC processing). H10S2/S3 background is 0.13-0.30 Pa (1-s RMS, 4-40 Hz)
  in 2016-2017 against 0.05-0.09 Pa at H10N.
- Arrival times and group speeds: charge H10N 21:12:04.6-06.0 UTC (published picks 21:12:03-06), c = 1.4768 km/s; San Juan H10N
  14:59:16-17, H10S 14:58:03-04, c = 1.476 km/s; FSST c = 1.486-1.490 km/s. Module SOFAR prior 1.482 +/- 0.006 km/s: South American
  paths at -0.9 sd, Florida paths at +0.7 to +1.3 sd.
- Back-azimuth residuals (observed minus geodesic): H10N -0.8 to +0.4 deg (all 10 events); H10S -1.3 to +2.2 deg except FSST 2016-5
  (-25 deg, min pair correlation 0.16; H10S1 timing in the fit). Brown Table A.4 FSST observed 303.8-305.1 deg: ours 303.9-305.0 at H10N.
- Peaks (1-60 Hz, triad median): San Juan 8.11 Pa H10N, 17.3 Pa H10S; charge 2.66 Pa H10N, 5.70 Pa H10S; FSST 2016 16.4-28.8 Pa H10N;
  FSST 2021 21.1-65.3 Pa H10N. Brown's FSST peaks (9.3-15.1 Pa 2016, 15.2-39.6 Pa 2021) lie between our 4-9 Hz and 5-20 Hz values;
  his band is not identifiable from the table.
- Like-for-like with Nielsen Fig. 5c (digitised): raw Welch PSD on a 60 s window vs digitised signal PSD, 5-40 Hz:
  -1.7 to +0.1 dB (e.g. 10 Hz 90.8 vs 91.7, noise 82.0 vs 82.3 dB re 1 uPa^2/Hz). Implied PSD-to-energy window 38.6-70.7 s (median 49.6 s).

## 4. Measured minus predicted (sigma_model)
Tables: `sigma_model_table.csv` (event, station, band, residual, chain, source), `sigma_model_pooled_by_band.csv`,
`scores_primary.csv`, `sigma_model_summary.csv`, `residuals.csv` (all sensitivity rows), `station_difference.csv`.

San Juan charge (33 m, Vergoz position), median r_b (dB) / slope (dB/oct) / shape (dB):
| station | chain | G&S construction | G&S table 3 lb/60 ft | G&S table 1.8 lb/300 ft |
|---|---|---|---|---|
| H10N | KRAKEN | -7.1 / +2.56 / 1.16 FAIL | -2.8 / +0.29 / 1.52 PASS | -7.4 / +0.56 / 1.16 FAIL |
| H10N | KRAKEN+RAM | -7.7 / +1.80 / 1.05 FAIL | -4.0 / -0.47 / 1.75 PASS | -8.2 / -0.20 / 1.30 FAIL |
| H10S | KRAKEN | -0.6 / +1.42 / 1.01 PASS | +3.8 / -1.99 / 0.75 PARTIAL | -0.9 / -1.31 / 0.97 PASS |
| H10S | KRAKEN+RAM | +0.4 / +0.85 / 0.87 PASS | +5.7 / -2.56 / 1.02 PARTIAL | -0.0 / -1.88 / 1.36 PARTIAL |
Sensitivity: Nielsen position changes the level by -1.5 to +0.5 dB; depth 30 / 38 m moves it by +0.5 to +0.9 / -1.4 to -1.5 dB (construction, KRAKEN).

Shock trials (61 m, KRAKEN, G&S construction): median r_b 2016 +2.6 to +8.7 dB, 2021 -1.9 to +10.7 dB; slopes -2.5 to +1.1 dB/oct;
shape 3.2-6.1 dB (the Florida residuals bend down at 5 and 40 Hz). Depth 30 / 100 m: +6.6 to +7.0 / -3.8 to -4.5 dB relative to 61 m (median over shots).
With RAM (shots 2016-1 and 2021-1): +7.7 to +13.6 dB; RAM is up to 8 dB more lossy than KRAKEN above 12.5 Hz on these paths
(sources on the Blake Plateau, water 770-860 m, above the 850 m channel axis). At 61 m the radiated 5-40 Hz energy inverted
through the chain exceeds the declared explosive energy at 4 of 15 shot-station pairs (KRAKEN; 0.16-2.0 overall) and 3 of 4 (KRAKEN+RAM) — physically impossible, so the
chain is too lossy on the Florida paths, or the charges were deeper, or both (`explosion_radiated_fraction.csv`).

Pooled over 17 event-station pairs (KRAKEN-only): level mean +4.0 dB, SD 4.6 dB (construction); +2.5 / 4.2 (table 300 ft);
+6.7 / 4.2 (table 60 ft). Slope mean -0.2 to -1.7, SD 1.1-1.4 dB/oct, range -3.74 to +2.56. KRAKEN+RAM (6 pairs): level SD
7.3-8.2 dB, slope -2.56 to +2.87. By band (KRAKEN, construction) the residual SD is 4.2-6.4 dB in every band.

**Proposed sigma_model for the coupling structure (provisional):** level sigma about 5 dB (1 SD over events and stations,
KRAKEN-only) plus a source-model term of about 4 dB and, for any path that crosses a ridge into the channel, a path term of at
least 6 dB (station difference below); slope sigma about 1.5 dB/oct with no significant mean slope. These are measured on
explosions at 6,000-8,200 km in the Atlantic; transfer to the Indian Ocean paths and to impact sources is an assumption.

Station difference (same source cancels): charge H10S-H10N measured +5.4 dB, predicted -1.1 (KRAKEN) / -2.0 (RAM): misfit
+6.5 / +7.1 dB. FSST 2016: misfit -2.1 to +1.6 dB (KRAKEN). FSST 2021: -3.0 to -7.9 dB. The 2021 deficit at H10S, together with a
~7 dB drop in the H10S2 background between 2016-2017 and 2021, may be a change of H10S hardware or gain not in the single-epoch
StationXML; it is unresolved (would be resolved by a common distant source recorded at both triads in each year, or the
operator's calibration history).

## 5. Does this change standing caveat (1)?
Yes, in part. On sources whose energy is independently known, the chain's residual frequency slope over 5-40 Hz is within
+/-3 dB/oct for every event, station, chain and source model (PASS or PARTIAL), and its mean is about zero. The +10/+7 dB/oct
airgun misfit is therefore not a property of the propagation chain on these paths at 5-40 Hz; this supports the audit's reading
that it lies in the airgun source description (array directivity removes about two thirds of it). Proposed wording: "the
propagation model's frequency slope is within +/-3 dB/octave on known-energy explosions at Ascension (17 event-station pairs);
it failed by +7 to +10 dB/octave on the 2001 airguns, attributed to the airgun source term; absolute level has sigma about 5 dB
plus source and path terms". Limits: different ocean (Atlantic), explosive not impact sources, source spectra outside G&S
validity, and two G&S variants that differ in slope by up to 2.6 dB/oct. The Indian Ocean airgun paths are not re-tested here.

## 6. San Juan loss event: real-arrival test of M1b and source energy
Matched filter (module prepare/weak_signal M1b unchanged; template bank 1,800-3,000 km, Indian Ocean profile; 5-40 Hz at 100 Hz):
| event | element | M1b score | n null | k >= | p (floor) | null p95 / max | SNR (1-s RMS) |
|---|---|---|---|---|---|---|---|
| San Juan | H10N1/2/3 | 0.963/0.981/0.978 | 379 | 0 | 0.0026 (0.0026) | 0.66-0.70 / 0.93-0.96 | 36.0-36.7 dB |
| San Juan | H10S2/3 | 0.987/0.985 | 379 | 0 | 0.0026 | 0.58-0.66 / 0.97-0.98 | 27.4/34.2 dB |
| Charge | H10N1/2/3 | 0.881/0.901/0.920 | 363 | 2/1/1 | 0.0082/0.0055/0.0055 | 0.59-0.64 / 0.98 | 23.0-24.0 dB |
| Charge | H10S2/3 | 0.928/0.897 | 363 | 0/1 | 0.0027/0.0055 | 0.46-0.56 / 0.75-0.93 | 16.2/21.1 dB |
All are at the report level (p <= 0.05). The statistic is amplitude-blind: background windows on the same day reach 0.93-0.98,
so at the 16-24 dB SNR of the charge the real arrival ranks only 2nd-3rd at four of five elements. M1b on its own is a weak discriminator
at low SNR on real data (gap G11-1 confirmed); its detection probability below about 15 dB SNR is not measured here and remains a
proxy.

Source energy (inverted through the chain, 5-40 Hz; `sanjuan_event_energy_vs_depth.csv`, `sanjuan_event_tnt_equivalent.csv`):
radiated 3.5e6-3.2e7 J (H10N) and 1.8e7-1.5e8 J (H10S) for 200-900 m. Explosion-equivalent yield (G&S charge at the same depth
radiating the same band energy): construction 9-94 kg (H10N), 41-389 kg (H10S); table 1.8 lb/800 ft 12-243 / 51-918 kg; RAM at
500/900 m 25-80 / 81-384 kg (construction). Charge-relative route (event/charge band energy x 108 kg, path error cancels):
15-166 kg with the two stations within 1.4x. Heyburn et al. 2020 (via Vergoz) 428 kg: inside our range only at about 800-900 m
with the deep-reference model and H10S; below it otherwise. For the implosion branch: radiated / (rho g z V) = 8.6-35 % (V 10 m^3),
0.86-3.5 % (100 m^3) at H10N; 43-171 % and 4.3-17 % at H10S (values above 100 % rule out V = 10 m^3 at that station). V and the implosion depth are not known.
No duration or timing from this event is used for MH370.

## 7. Disagreements with published authors (both sides)
- Stage 1b / Nielsen Fig. 5c level: resolved on our side (PSD-to-energy window). Nielsen's figure is consistent with the raw data.
- Vergoz: 20 dB Rio Grande Rise loss at 7 Hz for a 500 m source, TL 138 dB "rel. amplitude at 1 m". Our 2-D KRAKEN gives 105.5 dB
  at 6.3 Hz for 500 m. Possible causes, our side: no N x 2D/3-D around the rise, the hard sediment bottom (a basalt or rough
  rise would scatter more), the WOA23 climatological channel. Their side: a different definition of the quoted number, a 2-D section
  through a shallower part of the rise, or scattering in their RAM. Resolving data: H10S vs H10N measured difference (+5.4 dB,
  model -1 to -2 dB) says the H10N path does lose more than our model has; an N x 2D fan run would test the magnitude.
- Brown 2026 D2 ratios: charge H10N 0.005 (ours 0.085 at 1-60 Hz, 0.018 at 5-20 Hz, 0.001 at 4-9 Hz); FSST 2016 0.10-0.34 (ours
  0.43-1.9 at 1-60 Hz, 0.14-0.56 at 5-20 Hz). The difference is the peak definition (band, beam). Brown's band is not stated in the
  digitised table; it would be resolved by his processing description.
- Heyburn 2020 428 kg: our chain gives 9-918 kg depending on depth and model; agreement needs a source near the wreck depth.
  Our side: G&S out of validity, unknown mechanism (implosion spectra differ), and the 6 dB station term; their side: seismic
  magnitude scaling and peak ratios, which depend on similar assumptions.

## 8. DB rows
- `db_coupling_value_new_rows.csv`: CV26-CV31, D2 Arons-relative ratios from raw 1-60 Hz peaks (ARONS_1954, MODEL_ERROR_MEASURE,
  EVIDENCE, G4): FSST 2016 H10N 0.82 (0.42-1.88, 5 shots), H10S 1.15 (0.14-2.59, 4 shots); FSST 2021 H10N 0.62 (0.31-6.18), H10S 0.13 (0.09-0.45);
  charge H10N 0.086 (0.083-0.112), H10S 0.61 (0.58-0.65). Validator on the package with these rows: RESULT PASS (0 failures).
- The module-chain radiated fractions of the charges (`explosion_radiated_fraction.csv`) are NOT written as coupling rows: the
  validator's v_module_chain view selects on chain and status only, so explosion values would enter the impact view. Decision for
  the importer.
- `db_received_observation.csv`: OB01-OB06 unchanged + OB07-OB63 (57 rows, same definitions; H10S1 rows marked EXCLUDED).

## 9. Deviations
- RAM run on 10 of 21 paths: all four charge paths (33 m), both San Juan event paths (500, 900 m), and FSST shots 2016-1 and 2021-1
  (61 m, H10N and H10S). The other 6 FSST shots, depth sensitivity and the event depth sweep (200-900 m) are KRAKEN-only.
- FSST charge depth not found in any 2016/2021 primary or official source; 61 m from the 2008 FSST notice is an analog.
- H10S1 excluded (all events); FSST 2016-4 has no H10S data (HTTP 204). Charge W120 noise estimate at H10S used 8 of 10 windows.
- The M1b template bank is the module's (1,800-3,000 km, Indian Ocean); not rebuilt for 6,000 km Atlantic paths (deliberately, to
  test the module as is).
- Source models: Chapman 1985/1988 and Arons energy-flux formulas not held; only G&S variants used. H04S, H03S: no open data or path.
- Heyburn et al. 2018 (BSSA) and 2020 (GJI) not read (paywalled); their numbers via Vergoz and USGS only.
- RAM background run stalled once (no job finished for ~2 h); relaunched from cached per-job results, no values changed.
- Exploratory: written in advance, but the charge-H10N half was not blind.
