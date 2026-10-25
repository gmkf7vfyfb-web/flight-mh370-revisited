# Transair 810 (B737-200 ditching off Oahu, 2 July 2021) at Wake Island: first ditching-family (R3) case

Hydroacoustics module, track 2. 25 Oct 2026. Raw IMS records, EarthScope FDSN (net IM, cha EDH, 250 Hz).
Pre-registration written and saved before any statistic was computed on the hydrophone data:
[transair810-preregistration.md]({{artifact:986504a4-4ccc-4c75-82d1-144325a8a08c}}) (SHA-256 360cf299…).
Everything marked EXPLORATORY was added after the first run.

## Summary

1. **NTSB facts (DCA21FA174).** Water impact was at 11:45:17 UTC, at 21.27616 N, 158.02565 W. Groundspeed was 114.6 kt (58.96 m/s), descent rate about 4–6 m/s, pitch +12.3°, bank −14.9°, mass 42.0 t. Kinetic energy is **73.6 MJ (90 % 69.4–77.9)** and vertical kinetic energy 0.56 MJ (0.33–0.85). The project's ~86 MJ was an assumption and is 17 % high. The fuselage broke in two at BS 540. The wreck lies at 104–111 m depth.
2. **Path.** The paths to H11N (3,655 km) and H11S (3,700 km) are clear in deep water: the minimum depth beyond 30 km is 1,329 m, and there is no land on the ±2 km corridor. The only obstacle is the Oahu shelf at the source. Water stays under 200 m for the first 9 km, and the module KRAKEN chain finds no propagating modes at ≤ 40 Hz on the great circle from the NTSB point.
3. **Predicted window (ditching site).** Arrivals are predicted at 12:26:24 UTC (H11N) and 12:26:53 UTC (H11S), with 1σ ≈ 10 s. Neither triad gives a matched-filter p below 0.05: H11N p = 0.079 (mark), H11S p = 0.095 (mark), with n = 1,244 / 1,246 and p floor 0.0008. The bearings at the coherence maxima are 35° and 94° off the expected direction. **No significant detection with limited power.**
4. **Kadri's box.** A signal is present at his time and roughly his level. It does not come from the ditching site.
   - Matched filter: p = 0.0088 at H11N (report) and 0.057 at H11S. At H11S, D1 and coherence are also at mark level.
   - Bearing at H11S: two coherent pulses 42 s apart (12:31:42 and 12:32:24) from **152.6°**, apparent speed 1.44 km/s. The expected bearing is 79.2°.
   - Inter-triad timing: H11N receives both pulses 72–73 s after H11S. A plane wave from 152.6° predicts +74.5 s; a source at the ditching site predicts −29.7 s.
   - Time of flight from 11:45:17 would be 1.30–1.32 km/s, not a deep-channel speed.
   - The source is unidentified and EXPLORATORY: the bearing points toward the Tonga–Kermadec arc, and no USGS (M ≥ 3) or ISC event fits.
5. **Coupling, measured detection probability.** Injecting the real F-35A arrival into 14 days of H11 background gives a 50 % detection level (M1b p < 0.05) of 0.065 Pa (H11N) and 0.048 Pa (H11S), as 1-s RMS in 5–40 Hz.
6. **Coupling upper limit (R3).** Through the module chain (KRAKEN + RAM, source 3 km seaward, f⁻², total KE), η_rad,UL50 at H11S is 3.2e-4 / 1.2e-3 / 7.4e-3 / 3.0e-2 / 0.12 for z_eff = 10 / 5 / 2 / 1 / 0.5 m. H11N is 2.3× looser.
   - This is **0.14× (H11S) and 0.31–0.32× (H11N) the F-35A ridge at the same depth**, measured at 2–10 m and on the extended ridge below 2 m.
   - It is 30–30,000× above the slow-blunt analogs (raindrops ~1e-5, ice blocks ~8e-7). The data therefore exclude an F-35A-like coupling for the ditching but cannot test a slow-blunt one.

Standing caveats on every limit and ratio here:
- (C1) The propagation model failed the frequency-slope check against the 2001 airguns (+10 dB/octave at H01W, +7 at H08S) although levels passed. This work does not test or change that. The upper limit weights 5–63 Hz through the same model, so an unresolved slope error passes into it, unquantified.
- (C2) The detection probability is measured on real background but with a borrowed arrival shape (the F-35A). A longer ditching arrival would make the matched filter less efficient, which would make the limits optimistic.

## 1. Primary facts (NTSB) and kinetic energy

Sources: the NTSB docket at data.ntsb.gov, read in this session. They are the final report (CAROL, 45 pp.), the Aircraft Performance Group (APG) study with Table 4, the FDR specialist's report and its data attachment (CSV), the EGPWS specialist's report, the Search and Recovery factual, the Structures factual and the Survival factual. Second sources are Wikipedia, Aviation Safety Network, Kadri S1 and GEBCO 2026. Table: [ntsb_primary_facts.csv]({{artifact:96e05656-1298-4a2a-932b-4ebeb0a17608}}).

| item | value | source; cross-check |
|---|---|---|
| time of water impact | 11:45:17 UTC (01:45:17 HST) | Final report: CVR "sounds consistent with impact at 0145:17". ADS-B ends 11:45:17.902 UTC. The FDR CSV ends 01:45:16.94 HST with no impact spike. Kadri S1: "around 11:46". |
| position | 21.27616 N, 158.02565 W | APG Table 4, "Estimated water impact" (ADS-B). The forward fuselage (S&R Table 1) lies 167 m away. Wikipedia gives 21.275 N 158.026 W. Kadri S1 gives 21°18′41″N 157°54′16″W, near HNL airport and 13 km from this point. |
| groundspeed | 114.6 kt = 58.96 m/s | APG Table 4. Kadri's 215 km/h = 59.7 m/s agrees. |
| vertical speed | ADS-B −764 fpm (3.9 m/s). EGPWS radio altitude 64.5 → 55.0 → 42.5 → 26.5 ft at 1-s steps (2.9, 3.8, 4.9 m/s). | Modelled as U(3.8, 6.5) m/s, to allow ~1–1.5 s of further acceleration to contact (declared). |
| attitude | pitch +12.3°, bank −14.9° (left wing down); flaps 1, gear up | APG Table 4 and s. 5 |
| weight | take-off 93,557 lb (42.44 t) | Final report and APG Table 1. Impact mass 42.0 t, after an assumed 300–1,500 lb of fuel burned (not given in the documents read; declared). |
| water depth | wreck 104–111 m (340–364 ft) | S&R Table 1. GEBCO gives 117 m at the wreck and 108–178 m at the ADS-B point. |
| break-up | fuselage fractured near BS 540 into two pieces; both engines separated; wings attached; tail floated, then sank | S&R and Structures factuals; Survival factual (the first officer saw two pieces) |

Monte Carlo over mass, groundspeed (sd 2 kt) and vertical speed gives:
- KE = **73.6 MJ (5–95 %: 69.4–77.9)**;
- KE_vertical = **0.56 MJ (0.33–0.85)**.

Kadri S1 ref. 5 is the Atlas Air 3591 report (AAR2201), not Transair, as already noted in the project.

## 2. Predicted windows and path check

The geodesics (WGS84; element positions identical in StationXML and stations.csv) are in [arrival_geometry.csv]({{artifact:84b0a981-e7fc-43b2-9fc4-6d9a0c3719fe}}):

| triad | distance | back-azimuth | travel time at 1.482 ± 0.006 km/s | predicted arrival |
|---|---|---|---|---|
| H11N | 3,655.44 km | 81.07° | 2,466.6 s (sd 10.0 s) | 12:26:23.6 UTC |
| H11S | 3,699.58 km | 79.22° | 2,496.3 s (sd 10.1 s) | 12:26:53.3 UTC |

The path check used GEBCO_2026 15″ along the geodesics at 250 m steps, with a ±2 km corridor; see Fig. 4.
- **Clear**: no land and no water shallower than the hydrophone depth beyond 14 km. The shallowest deep-water point is 1,329 m (H11N, 2,555 km) and 1,569 m (H11S).
- At the source end, depth is < 200 m for 9.3 / 9.0 km and > 1,000 m from 16 km.
- The seaward slope from the ditching point reaches 500 m within 7.5–10 km on bearings 180–250°.

![Path depth profiles]({{artifact:d2224130-ad47-49d2-95f4-e1025b51ca8c}})

## 3. Detection (pre-registered)

**Method.** Exactly as in the pre-registration.
- Pre-processing: full StationXML response removed to Pa, then 5–40 Hz, then 100 Hz.
- Statistics: module D1 (STA 2 s / LTA 30 s, triad mean) and module M1b (envelope matched filter). The M1b template is the F-35A raw-record envelope of the same triad, checked against OB01–OB06: same peak times, levels −0.7 dB because of the 5–40 versus 4–40 Hz band. C3 is triad coherence in 8-s frames, with a plane-wave bearing at the frame of maximum coherence.
- Null: non-overlapping 90-s windows from the 14 adjacent days (11:30–13:30 UTC) and from the event day (10:00–12:20 and 12:40–14:00 UTC). Of 2,500 windows tiled, 10 were excluded for > 1 % gaps, leaving n = 1,244 (H11N) and 1,246 (H11S); p floor = 1/(n+1) = 0.0008.

**Results.** Table: [observed_windows_prereg.csv]({{artifact:bb57a995-033d-4bf7-a001-786929df5b09}}).

| triad, window | D1 (rank, p) | M1b (rank, p) | coherence C3 (rank, p) | bearing at C3 max (Δ from expected), apparent speed | SNR | 1-s RMS peak; instantaneous peak |
|---|---|---|---|---|---|---|
| H11N, predicted | 2.28 (366, 0.294 screen) | 0.658 (98, **0.079 mark**) | 0.349 (423, 0.340) | 46.1° (−35.0°), 1.47 km/s | 3.8 dB | 0.076 Pa at 12:27:03.5; 0.244 Pa |
| H11S, predicted | 1.86 (441, 0.354) | 0.676 (118, **0.095 mark**) | 0.271 (497, 0.399) | 173.5° (+94.3°), 4.42 km/s | 2.4 dB | 0.059 Pa at 12:26:38.5; 0.179 Pa |
| H11N, Kadri box | 3.42 (161, 0.129 screen) | 0.831 (11, **0.0088 report**) | 0.326 (484, 0.389) | 143.4° (+62.3°), 1.65 km/s | 6.9 dB | 0.105 Pa at 12:32:55.5; 0.337 Pa |
| H11S, Kadri box | 5.38 (101, 0.081 mark) | 0.694 (71, 0.057 mark) | 0.624 (82, 0.066 mark) | 152.6° (+73.4°), 1.44 km/s | 9.1 dB | 0.124 Pa at 12:31:42.5; 0.337 Pa |

SNR here is 10 log10 of the peak 1-s mean square over the median of the 600 s before the window, 5–40 Hz.

**Decision (pre-registered rule).**
- Predicted window: the M1b p is not below 0.05 at either triad, so this is **no significant detection with limited power**.
- Kadri window: the rule ("signal present") needs M1b p < 0.05 at both triads, or at one triad together with C3 p < 0.05 and a consistent bearing. It is **not met**: H11N M1b p = 0.0088, but its C3 p = 0.39.
- Multiplicity: 12 tests give 8 rows at screen level (3.6 expected by chance), 6 at mark (1.2 expected) and 1 at report (0.6 expected). Inside the predicted windows alone (6 tests): 3 at screen (1.8 expected), 2 at mark (0.6 expected), 0 at report (0.3 expected).
- The two predicted-window marks have bearings that are not consistent with the ditching site; the H11S one has a non-acoustic apparent speed. EXPLORATORY: a 20-s periodic pulse train runs through the H11N record (envelope autocorrelation peak at 20.0 s, r = 0.45) and is the likely cause of the H11N mark. Its source was not examined.

**Likelihood ratio** (pre-registered, M1b, Gaussian KDE) for a signal at Kadri's level in the predicted window against noise only: LR = 0.57 (H11N) and 0.87 (H11S). This is weak because M1b is amplitude-blind.
EXPLORATORY, amplitude-aware (1-s RMS peak): none of the 150 injections at Kadri's level gave a predicted-window peak as low as the one observed, at either triad (fraction < 1/151). The KDE values (log10 LR −10.2 and −1.7) are tail-dominated and are not quoted as findings. Tables: [likelihood_ratio_pw.csv]({{artifact:2da13eda-cffc-4df5-b7d4-df09f27b53e9}}) and [likelihood_ratio_pw_amplitude_EXPLORATORY.csv]({{artifact:6ef7dc60-d26b-4118-b021-c2df8eb49fdc}}).

![Event-day record and bearings]({{artifact:e9d2b845-5abb-44bc-81d6-a249dbfeaab5}})

## 4. Comparison with Kadri (2024, Fig. 5b; ground-truth rows TA810-H11S / TA810-H11N)

**His panels and boxes.** The panels start at 12:28 UTC (H11N) and 12:27 UTC (H11S). Read from the PMC JPEG at 2.4 s per pixel, the boxes are H11N 12:32:13–12:33:40 and H11S 12:31:11–12:32:39. Column digitisation: [kadri_fig5b_digitised_columns.csv]({{artifact:b9e1e98c-3e71-4928-8378-eb09352207e2}}).
- The predicted H11N arrival (12:26:24) is earlier than the start of his H11N panel, so the predicted time is not on his plot.
- In his own H11N trace, the box maximum (~0.36 Pa by our colour mask) is not above excursions outside the box (~0.44 Pa).

**Does a signal appear at his time and level?** Yes.
- Raw-data instantaneous peaks inside his boxes are 0.26–0.38 Pa (H11N1-3) and 0.31–0.35 Pa (H11S1-3), in 5–40 Hz. Kadri's reading was 0.40–0.45 Pa, with his filter band not stated.
- 1-s RMS peaks are 0.10–0.15 Pa, SNR 6.3–10.5 dB (element rows OB10–OB12 and OB16–OB18).
- H11S shows two pulses 42 s apart; this agrees with his "double signal".

**Is it consistent with a source at the ditching site?** No, on three independent counts:
1. **Bearing.** The H11S arrival comes from 152.6° (all frames above the event-day 99th-percentile coherence: 152.5–152.8°) at 1.44 km/s; the expected bearing is 79.2°. The same estimator applied to the F-35A record gives 323.7° / 325.8° against 320.8° / 322.3° expected, an offset of +2.9 / +3.5° ([bearing_check_f35a.txt]({{artifact:e2ea3fcc-1e3a-4c37-ba9f-1faab5530f0e}})). The 73° discrepancy is about 20 times that offset.
2. **Two-station timing.** This is independent of the within-triad bearing and uses the 136 km baseline. H11N receives both pulses 72 s and 73 s after H11S. A plane wave from 152.6° predicts +74.5 s; the ditching site predicts −29.7 s, with H11N first.
3. **Time.** From 11:45:17 the box times imply 1.30–1.32 km/s. That is below the deep-channel range (1.482 ± 0.006 km/s) and below the registry's acoustic-gravity branch (1.40–1.50 km/s).

**What is it?** EXPLORATORY: unidentified.
- The 152.6° great circle from H11S crosses the Tonga trench at 4,500–5,000 km. A deep-channel arrival from there would need an origin time of about 11:35–11:41 UTC.
- The USGS catalogue (M ≥ 3, 09:00–12:35 UTC) has no event on this bearing at a fitting time. Its nearest candidate is an M 4.7 north of Tonga at 09:04:57 (bearing 148.6°), which would arrive at 09:53.
- The ISC lists an IDC mb 3.6 event south of Fiji at 12:25:52, too late to arrive at 12:31. EMSC returned no events for the region.
- A small uncatalogued T-phase from the Tonga–Kermadec arc is plausible but unproven. Other sources (seismic survey shots, volcanic activity, a biological source) were not tested.

**Possible causes of the disagreement, on both sides.**

Kadri:
- His source position was ~13 km off (near the airport) and his time approximate (~11:46).
- His panels begin after the predicted H11N arrival.
- The box appears to be chosen by eye within a 10-min panel, with no bearing or two-triad timing test shown.
- The double structure was read as ditching-related.

Ours:
- (a) Our propagation speed could be wrong. However, 1.30 km/s is not a water-borne speed.
- (b) The NTSB time could be wrong. However, CVR, ADS-B and FDR agree to about 1 s.
- (c) Element positions or element timing could bias the bearing. The F-35A check limits this to about 3°, and the two-triad timing does not use these quantities.
- (d) The ditching could have made a later sound, such as wreck break-up or the tail sinking. Its bearing would still be 79–81°, so it cannot explain a 152° arrival.
- (e) We read his boxes from a low-resolution JPEG. A ±2.4 s reading error does not change any conclusion.

What would resolve it, using only data that can be downloaded: Tonga–Fiji regional seismic stations on public FDSN services (T-phase onset and origin), H11 records on adjacent hours (repeating events from the same bearing), and Kadri's processing band. No request to anyone is needed for these.

## 5. Coupling for the ditching family (R3): measured detection probability and upper limit

**Injection** (pre-registered). The F-35A raw waveform (H11N1 / H11S1, 5–40 Hz, [peak − 35, peak + 15] s) was injected into all three elements with plane-wave delays for 81.07° / 79.22° at 1.482 km/s. Settings:
- arrival peak uniform within the 90-s window;
- 16 levels from 0.003 to 0.3 Pa, 150 injections per level per triad (2,400 per triad), plus 150 with no injection and 150 at Kadri's level;
- background from the 14 adjacent days only.

Detection probability, pre-registered, with M1b p < 0.05 counting as detected ([detection_probability_L50.csv]({{artifact:5044751c-d0d7-42bc-9820-d29a8552f234}}), [curve]({{artifact:ff7bf440-77b0-4bca-ba4e-125641585b7d}})):

| triad | L50, report (Pa, 1-s RMS) | L50, mark | L50, screen | P_D ceiling | P_D with no injection | SE_50 (4–40 Hz, Pa² s) | P_D at Kadri's level |
|---|---|---|---|---|---|---|---|
| H11N | 0.0647 | 0.0605 | 0.0472 | 0.84 | 0.040 | 0.0089 | 0.85 |
| H11S | 0.0483 | 0.0474 | 0.0344 | 0.84 | 0.033 | 0.0043 | 0.77 |

- Kadri's level means a signal instantaneous peak of 0.425 Pa, which corresponds to 1-s RMS 0.165 Pa (H11N) and 0.107 Pa (H11S).
- The ceiling below 1 comes from loud background windows (median 1-s RMS up to ~0.14 Pa, against ~0.045 Pa typical).
- With noise within 1.5 dB of the event day (sensitivity, not pre-registered), L50 is 0.058 / 0.048 Pa and the ceiling 0.97 / 0.92.

![Detection probability]({{artifact:466fbfc9-a9b3-44ed-bff9-435c6bc20483}})

**Upper limit.** The relation is η_rad,UL50 = SE_50 / [E ρc/(2π) Σ_b W_b s_b(τ, slope) 10^(−TL_b/10)]. This is the step2_invert.py relation, unchanged; my implementation reproduces CV02 = 2.259e-3 from the module's F-35A files.
- Transmission loss: the module KRAKEN chain (tl_grid_run_j.build_path, air9 profiles, kraken_tl), with two loaders substituted. Bathymetry is the GEBCO_2026 global netCDF, because the extracted grids stop at 180° E. Sound speed is WOA23 B5C2 July with TEOS-10. The bottom is hard. Table: [ta810_tl.csv]({{artifact:a09431ed-00a4-4533-8cd3-01f2da54a135}}).
- **Source end.** On the great circle from the NTSB point, KRAKEN has no modes at ≤ 40 Hz (first 5-km profile 37 m, along the Barbers Point shelf). RAM on that geometry gives 165.6 / 169.5 / 179.3 dB (H11S, 5 / 10 / 20 Hz, 10 m source). A 2-D path along the coast is not where the sound goes. The source was therefore moved seaward along 180° by 3 km (239 m water, primary), 6 km (361 m) and 10 km (531 m), as declared alternatives.
- **RAM correction** (pyram, module ram_job unchanged, 10 m source). RAM − KRAKEN on the 3 km path is +3.5 / +3.7 / +4.2 / −1.5 dB at H11S (5 / 10 / 20 / 40 Hz) and +2.4 / −2.2 dB at H11N (10 / 40 Hz). A 2 m source at 20 Hz gives +2.8 dB. Table: [ram_vs_kraken_transair.csv]({{artifact:7a92b9af-8fa3-4dac-99b7-73d28334ea15}}).
- E = total KE, 73.6 MJ; τ = 1 s (the limits are the same for τ ≥ 1 s and lower by ×0.51 at τ = 0.3 s).

Primary upper limits and their sensitivities ([eta_rad_upper_limit_primary.csv]({{artifact:6644ed72-1040-430f-837c-d85be9c21dcf}}); full grid over source end × z × chain × slope × τ × energy × noise condition: [eta_rad_upper_limit_grid.csv]({{artifact:5761dd9b-e35f-4916-a6b9-5a32c712bfd0}})):

| z_eff | H11S η_UL50 | H11N η_UL50 | F-35A ridge at same z (CV01–03) | H11S / ridge | H11S, f⁻⁴ | H11S, KRAKEN only | H11S, vertical KE |
|---|---|---|---|---|---|---|---|
| 0.5 m | 0.118 | 0.267 | 0.83 (extended) | 0.14 | 9.7 | 0.102 | 15.7 |
| 1 m | 0.0296 | 0.0669 | 0.21 (extended) | 0.14 | 2.4 | 0.025 | 3.9 |
| 2 m | 0.00742 | 0.0168 | 0.054 | 0.14 | 0.61 | 0.0064 | 0.98 |
| 5 m | 0.00120 | 0.00272 | 0.0089 (interpolated) | 0.14 | 0.097 | 0.0010 | 0.16 |
| 10 m | 0.000316 | 0.000715 | 0.00226 | 0.14 | 0.025 | 0.00027 | 0.042 |

Sensitivities: the source end (3 / 6 / 10 km) moves the limits by up to ×1.2 (H11S) and ×1.26 (H11N); the KE interval by ±6 %.

How to read this:
- At any shared depth and spectral family, a ditching that coupled like the F-35A ridge would have been detected more than half of the time. The ditching's η_rad is therefore below about 0.14× (H11S) to 0.31× (H11N) the R1 ridge value at that depth. Under the widest source-end choice, H11N is only 0.40×.
- The limit decreases as z_eff increases, as z⁻², the surface-image regime. A ditching source is very shallow; if its z_eff is 0.5–1 m, the limit is 0.03–0.27. That is 3,000–27,000× the raindrop value and 37,000–330,000× the ice-block value, so it says nothing about where R3 lies inside the analog envelope.
- With an f⁻⁴ family or vertical KE as the denominator, the limit rises ×80 or ×130 and the case is uninformative.
- R3 conclusion (robustness rule): "below R1" holds for both triads, all source-end options, and both chains, for the f⁻² family with the KE denominator. It does not hold for f⁻⁴ / shallow z combined, so it is reported as **conditional on the spectral family and on E = total KE**.

![Coupling upper limit]({{artifact:341f8319-e98c-4931-aeb2-01963482b47f}})

## 6. DB rows (coupling-db-package schema) and validator

New rows only:
- [db_coupling_value_new_rows.csv]({{artifact:1a7d53a2-731c-403f-9da6-18a5660526bd}}): CV26–CV35. Quantity "eta_rad UPPER LIMIT (50 % detection) at z_eff X m, H11S/H11N"; D1; MODULE_KRAKEN_RAM; independence group G9; status EVIDENCE; role LIKELIHOOD_RIDGE_POINT. The notes state "UPPER LIMIT, censored, not a ridge point" (see open question 1). value = the 3 km source end; value_high = the maximum over source ends and the KE 5 % quantile.
- [db_coupling_evidence_new_rows.csv]({{artifact:6bf49798-a074-43b3-b417-0c0ac88d81d3}}): E18 (Transair 810 non-detection, raw H11, G9).
- [db_impact_case_AC05_update.csv]({{artifact:55427c27-ce5a-4d60-9880-74e5167ae99c}}): NTSB facts, energy, depth, role "R3 UPPER LIMIT", Kadri comparison.
- [db_received_observation_new_rows.csv]({{artifact:fb57c12d-0ca5-4912-a537-74b0fc18e58a}}): OB07–OB18, element level, both windows. Predicted windows are under E18; Kadri boxes under E16.
- [db_family_element_evidence_R3_update.csv]({{artifact:940258bf-e248-4a40-a83c-daf65c0a7e9a}}) and [db_data_availability_probe_new_rows.csv]({{artifact:bd3915dc-1f89-42b1-8ae3-aa00c1ac2d92}}).

Full package with the rows applied: [coupling-db-package-ta810.zip]({{artifact:183e6ede-05f4-45ef-9e44-835ba34df54d}}). The validator **PASSES** with 0 failures; v_module_chain has 22 rows ([validator_output.txt]({{artifact:a72ef87e-6543-4b2c-b7d1-97106b3c0e35}})). Nothing was committed to the repository.

**Open questions for Pete** (structure, not values):
1. The role vocabulary has no "upper limit" or "censored" role. LIKELIHOOD_RIDGE_POINT is used because the non-detection enters the R3 likelihood; CROSS_CHECK is the alternative. Should a CENSORED_LIKELIHOOD role be added?
2. Should the R3 prior use E = total KE (D1 convention, as for the F-35A) or a transferred-energy definition closer to vertical KE? The limit moves by ×132 between the two.

## 7. Deviations (everything cut, capped, substituted or unreachable)

1. **Transmission loss source end substituted.** The great circle from the NTSB point has no KRAKEN modes at ≤ 40 Hz. The source was moved 3 / 6 / 10 km seaward (3 km primary). This is a declared alternative, not a measured path.
2. **RAM reduced.** RAM ran only at 10 m depth, on the 3 km paths: 5, 10, 20 and 40 Hz at H11S; 10 and 40 Hz at H11N, with H11N's 5 and 20 Hz values taken from H11S. One 2 m check was run (20 Hz, H11S).
   - The 40 Hz value is applied to 50 and 63 Hz, and the 10 m correction to all depths 0.5–10 m. The 6 and 10 km paths use the 3 km correction.
   - A daemon restart cancelled several RAM jobs and they were not rerun: the 10 km path, 40 Hz on the great circle, H11N 5 and 20 Hz, and 2 m at 40 Hz.
3. **Loaders substituted.** GEBCO_2026 global netCDF and WOA23 B5C2 July netCDF (monthly to 1,500 m, Jul–Sep seasonal below; TEOS-10) replace the module's extracted grids, which do not reach east of 180° E. The GEBCO TID array is not used.
4. **Added after the first run (not pre-registered):**
   - the noise-matched P_D sensitivity;
   - the amplitude-aware likelihood ratio;
   - the bearing time series and source identification, including the catalogue searches (USGS, EMSC, ISC);
   - the F-35A bearing check;
   - the 20-s pulse-train note.
5. **Injection pool.** The first and last window of each background day were excluded to leave room for the 65 s lead-in and 20 s tail; the pool is 11:31:10–13:28 UTC.
6. **L50 fit.** The logistic was fitted with its floor fixed at the no-injection rate and its ceiling free. The pre-registration did not fix this detail.
7. **Assumed inputs.**
   - Fuel burn 300–1,500 lb: not in the documents read.
   - Vertical speed at contact U(3.8, 6.5) m/s: extrapolated from the EGPWS and ADS-B values.
   - Groundspeed sd 2 kt.
   - Kadri's Fig. 5 filter band is unknown.
   - His boxes were read from a 669 × 717 px JPEG.
8. **F-35A ridge below 2 m.** It is extended at the 2–10 m log-slope (CV01–CV02); this is not a measured ridge point.
9. **Data and artifacts.**
   - The raw H11 MiniSEED (90 files, 247 MB) is not saved as an artifact; it can be re-downloaded with [ta810_download.py]({{artifact:9978a356-8ef7-4d7d-a042-ab29bceef761}}) and [download_log.csv]({{artifact:190a6d17-fed2-474a-96d8-2951cc9da3a5}}).
   - The filenames f35a_templates.npz/.json and transair_H11_resp.xml already existed in the project; my files were saved as new versions (v3) of those artifacts.
10. **Session interruption.** A daemon restart cleared the kernel state. All tables were regenerated from saved intermediates by [ta810_results.py]({{artifact:b91323ba-c08b-467c-9742-615e2300c92a}}). The plotting code for Figs. 1, 2 and 4 ran in the kernel and is in the session lineage, not in a script file.
11. **Compute.** Local only; at most 4 threads or processes; the remote machine was not used.

## 8. Files

- Scripts: [ta810-scripts.zip]({{artifact:171977b6-5968-43d5-aa89-65180a245d5b}}) (common, download, template, detect, inject, tl, ram, results, db_rows, facts_tables) and [ta810_bearing_check_f35a.py]({{artifact:c676c11d-3eee-4c9b-b71f-c8fe8a080386}}).
- Inputs produced: [f35a_templates.npz]({{artifact:9596dc30-8e1b-44d5-bcda-41ac30156532}}), [f35a_templates.json]({{artifact:94c7afed-9320-4bca-9094-cfc65c134f79}}) and [transair_H11_resp.xml]({{artifact:966db7cc-d5bd-4711-91f1-a886b24eec51}}) (StationXML, 2021 epoch).
- Null and injection scores: [null_window_scores.csv]({{artifact:273a4a9a-b8f0-4d53-b523-7380ca934aec}}) and [injection_results.csv]({{artifact:419e1f29-9ac4-4ee4-85cd-449fbbe34f4b}}).
