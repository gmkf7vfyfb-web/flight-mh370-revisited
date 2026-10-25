# F-35A coupling ridge re-derived from the raw Wake Island records (H11N1-3, H11S1-3)

Hydroacoustics module, track 1, 25 Oct 2026. **EXPLORATORY** calibration of the source model on another event (F-35A, 9 Apr 2019). Nothing here returns to end of flight; no received duration is used for MH370. The measurements, the 20 Hz gap test and the ridge were **pre-registered** before computation ([f35a-raw-prereg.md]({{artifact:493a290e-9620-430a-85fe-b6f0ae751a8d}})); the corner-frequency family (Ffit_c), the per-triad RAM delta used as a sensitivity row and the pre-event-only noise σ are **post hoc** and labelled. No detection statistic or p-value is computed here.

## 1. Main findings

1. **The raw records reproduce the digitised Metz numbers.** Exposure 4-64 Hz is +0.22 to +0.29 dB higher than digitised at every element (triads H11N 0.284 vs 0.270 Pa² s, H11S 0.0955 vs 0.0896 Pa² s); 1-s RMS peaks +0.44 to +0.76 dB; noise +0.13 to +0.17 dB; −6 dB widths 0.05-0.30 s shorter; 5-95 % spans 0.08-0.27 s shorter; peak times within ±0.24 s. The N/S exposure split stays at 4.7 dB.
2. **The ~20 Hz gap is real in the raw data at all six elements** (pre-registered G1: "present" at 6/6). Excess-energy notch 18-24 Hz is −7.2 to −12.0 dB (95 % upper bounds −4.99 to −9.43 dB). It is not the instrument (response feature +0.10 dB, smooth through 12-34 Hz), not a noise peak (the noise has a slight dip, −0.2 to −1.7 dB, not a 20 Hz fin-whale-type peak), not noise subtraction (the arrival PSD itself drops 5.0-7.3 dB before subtraction), not Metz filtering (our own processing), and not the modelled TL (KRAKEN TL is smooth through 16-25 Hz). No 60 Hz notch is resolved (2 elements "absent", 4 "unresolved"); the 25-ms two-pulse explanation is therefore not supported where the data have power, but the 60 Hz SNR is low (window/noise 1-2 dB). The received shape matches the digitised shape: received ESD slope 5-40 Hz −4.48 to −5.10 dB/octave (digitised −4.4/−4.8).
3. **Implied source slope agrees with the digitised result; the raw 2-4 Hz bands add a corner.** Source ESD slope 5-40 Hz −10.2 ± 0.7 dB/octave at 10 m (KRAKEN only; digitised far field −10.1 ± 0.5), −9.45 ± 0.8 with RAM, i.e. exponent n ≈ 3.1-3.4. The pre-registered cavity branch is **not supported**: at 2-4 Hz the implied source lies 0 to −10 dB *below* the power-law extrapolation, not ≥3 dB above it. A post hoc fit puts a corner at 4.5-5.75 Hz (1σ 3.5-6.25 Hz) with n 2.65-3.5 above it.
4. **The ridge (D1).** f⁻², KRAKEN+RAM (module convention), 900 MJ: 0.229 / 0.0572 / 0.00925 / 0.00240 / 6.84e-4 / 3.64e-4 / 1.86e-4 at 1/2/5/10/20/30/50 m, 1.06-1.07 × the digitised CV01-CV03. With the data-supported corner (Ffit_c) η is 0.6-1.0 × the f⁻² value at every depth on KRAKEN+RAM. The f⁻⁴ and fitted-no-corner families give 37-61 × and 3-13 × the f⁻² value because they put most energy below 4 Hz, where the raw data show none; they exceed η = 1 (energy limit) at z_eff ≤ 2 m (f⁻⁴) and 1 m (fitted, no corner). Across families η falls by about 1,200-6,400 × from 1 m to 50 m.
5. **The 68 % error budget is dominated by station spread and location**, σ_ln ≈ 0.61 in total (factor 1.84): energy ±200 MJ σ_ln 0.23, element 0.13, station 0.38-0.45, location (module point W vs Metz-consistent point P, 21.4 km apart) 0.30-0.41. The location term is larger than the project's earlier ±8 km test (≤8 %) because P is farther away and on a different TL path.
6. **A new pyram run (per triad) removes most of the H11N/H11S split (gap G-F2).** The module applied the H11S RAM delta to both triads. The H11N delta is smaller at 10-40 Hz (0.36-1.91 dB vs 2.83-3.90 dB at H11S). With each triad's own delta, η_N/η_S at 10 m falls from 2.16 to 1.26 (σ_ln station 0.39 → 0.11) and pooled η at 10 m becomes 1.81e-3 (0.75-0.78 × the module-convention value). The new H11S delta reproduces the module delta to within 0.7 dB.
7. **Near field.** The digitised near-field values are 3.95-4.0 × the raw KRAKEN-only far field and 1.85-1.86 × the raw KRAKEN+RAM far field (previously 4.2 × and ~2.0 ×).
8. **Brown's D2 recomputed.** Raw instantaneous peaks are 0.69-1.29 Pa (4-40 / 4-64 Hz) and 0.93-1.28 Pa (2-100 Hz). Arons D2 (900 MJ) = 5.4e-4 geometric mean in 4-64 Hz (element range 2.9e-4 to 1.0e-3), 4.6e-4 in 4-40 Hz, 7.6e-4 in 2-100 Hz, 2.1e-5 from the 1-s RMS peak. Brown's 0.7 Pa (band not stated) equals our lowest element peak (H11S3, 4-40 Hz, 0.689 Pa) and gives 2.08e-4, 2.2-2.6 × below our geometric means.
9. **Back-azimuth disagrees with Metz by 3-4°.** Plane-wave fits with the FDSN element coordinates give 323.7° (H11N) and 325.7° (H11S), SD ≤ 0.03°, apparent velocity 1452-1456 m/s; the geodesic from W is 320.8° / 322.3° and Metz give 320.6° / 321.7°, 1473 / 1463 m/s. The back-azimuth is not used in the coupling ridge.

## 2. Method (as pre-registered unless stated)

Raw IM.H11N1-3/H11S1-3 EDH, 250 Hz, EarthScope FDSN dataselect (anonymous): event window 10:30-11:40 UTC plus seven 30-min backgrounds (01, 04, 07, 14, 17, 20, 23 h UTC) the same day; StationXML response for 9 Apr 2019 (one channel epoch, 2007-open; coordinates identical to module data/stations.csv). Full response removed to Pa (pre-filt 0.5/1/110/120 Hz). Envelope: 4-pole zero-phase 4-64 Hz, 1-s boxcar mean square, 0.02-s step; module observation operator obs.py unchanged (Metz frames H11N 11:02:55-11:03:25, H11S 11:03:55-11:04:25; noise = median outside peak ±8 s; arrival window L > L_n + 1 dB). Third-octave bands 2-100 Hz over the arrival window ±2 s, noise 10:45-11:01 UTC; a band is "measured" if excess ≥ 2σ (σ from all background windows) and window/noise ≥ 3 dB. TL: module KRAKEN chain unchanged (tl_grid_run_j.run_path + step2_tl loaders; GEBCO_2026, WOA23 B5C2 April, hard bottom, Francois-Garrison), extended to depths 1-50 m and bands 2-100 Hz; it reproduces module step2_tl.csv to < 1e-6 dB on the shared grid. D1 = SE_obs / [E ρc/2π Σ W_b S_b 10^(−TL_b/10)], bands 5-63 Hz, W63 0.54, τ 3.30 s, geometric mean of triads (step2_invert.py relation). D4 = route-B in-band energy / E. D2 = Arons (P = 52.4e6 (R/W^1/3)^−1.13 Pa, R 3248.8 / 3341.5 km, 4.184 MJ/kg).

## 3. Raw versus digitised (per element)

| element | 1-s peak UTC (raw − dig., s) | onset UTC | peak 1-s RMS dB re 1 µPa (Δ dB) | noise dB re 1 µPa (Δ) | SNR dB | exposure 4-64 Hz, Pa² s raw / dig. (Δ dB) | −6 dB width s raw / dig. | 5-95 % span s raw / dig. | inst. peak Pa 4-64 / 2-100 Hz |
|---|---|---|---|---|---|---|---|---|---|
| H11N1 | 11:03:05.38 (+0.23) | 11:03:00.22 | 111.35 (+0.76) | 95.58 (+0.17) | 15.8 | 0.2577 / 0.2427 (+0.26) | 2.96 / 3.15 | 4.80 / 4.92 | 0.950 / 1.235 |
| H11N2 | 11:03:04.10 (-0.20) | 11:02:59.00 | 110.46 (+0.56) | 96.39 (+0.15) | 14.1 | 0.2859 / 0.2720 (+0.22) | 3.60 / 3.90 | 4.29 / 4.56 | 1.141 / 1.268 |
| H11N3 | 11:03:05.48 (-0.17) | 11:03:00.34 | 111.91 (+0.65) | 95.49 (+0.15) | 16.4 | 0.3095 / 0.2944 (+0.22) | 3.20 / 3.50 | 4.77 / 5.03 | 1.287 / 1.283 |
| H11S1 | 11:04:06.88 (+0.18) | 11:04:04.34 | 109.28 (+0.55) | 94.28 (+0.14) | 15.0 | 0.1299 / 0.1214 (+0.29) | 2.10 / 2.30 | 3.14 / 3.26 | 1.070 / 1.253 |
| H11S2 | 11:04:07.76 (-0.24) | 11:04:05.54 | 106.51 (+0.44) | 93.57 (+0.13) | 12.9 | 0.0788 / 0.0742 (+0.26) | 2.80 / 2.85 | 3.24 / 3.33 | 0.893 / 0.930 |
| H11S3 | 11:04:06.72 (-0.18) | 11:04:04.64 | 107.05 (+0.54) | 94.41 (+0.14) | 12.6 | 0.0779 / 0.0733 (+0.26) | 2.14 / 2.45 | 3.52 / 3.60 | 0.780 / 0.941 |

Back-azimuth (6-s windows, 1-s step; Metz gates closure ≤ 16 ms and 1430-1530 m/s):

| triad | band (Hz) | windows (pass gates) | back-azimuth (°) | SD (°) | apparent velocity (m/s) | closure median (ms) | geodesic from W / P (°) | Metz digitised (°, m/s) |
|---|---|---|---|---|---|---|---|---|
| H11N | 4-64 | 11 (6) | 323.73 | 0.03 | 1452.4 ± 3.7 | 1.42 | 320.78 / 320.43 | 320.61, 1473 |
| H11N | 5-40 | 11 (6) | 323.70 | 0.03 | 1452.4 ± 3.3 | 0.73 | 320.78 / 320.43 | 320.61, 1473 |
| H11S | 4-64 | 8 (5) | 325.72 | 0.01 | 1455.1 ± 0.6 | 0.65 | 322.30 / 321.98 | 321.73, 1463 |
| H11S | 5-40 | 8 (7) | 325.75 | 0.02 | 1456.3 ± 1.1 | 1.62 | 322.30 / 321.98 | 321.73, 1463 |

Possible causes of the 3-4° bearing difference. On our side: the FDSN element coordinates may not be the deployed (or mooring-displaced) positions; a ~100 m lateral position error over the 2.03-km aperture, or inter-element timing offsets of tens of ms, would produce both the bearing bias and the low apparent velocity (1452-1456 m/s is below the expected horizontal phase speed ~1480 m/s, which points to a geometry or timing error, not to refraction); 3-m to 24-m depth offsets were ignored (estimated ≤ 0.1°). On Metz's side: different (possibly CTBTO-calibrated) element positions or corrections, and the digitisation of their bearing markers. Resolution: fit a known-direction source in the open H11 data (e.g. a located earthquake T-phase or a known shot) with the same coordinates.

## 4. 20 Hz gap test (pre-registered G1-G4)

| element | 18-24 Hz gap depth, excess (dB) | 95 % interval | verdict | same, arrival PSD before noise removal | noise before arrival | background median | 60 Hz statistic (95 %) | 60 Hz verdict |
|---|---|---|---|---|---|---|---|---|
| H11N1 | -12.0 | -16.2 to -9.4 | present | -7.3 | -1.7 | -0.4 | 1.1 (-1.9 to 4.0) | absent |
| H11N2 | -9.1 | -10.9 to -6.2 | present | -6.6 | -1.5 | -0.4 | -0.7 (-6.0 to 2.2) | unresolved |
| H11N3 | -9.5 | -12.5 to -7.7 | present | -6.8 | -1.1 | -0.5 | -1.6 (-5.0 to 1.6) | unresolved |
| H11S1 | -7.9 | -13.6 to -5.4 | present | -5.7 | -0.5 | -0.6 | -2.2 (-10.7 to -0.4) | unresolved |
| H11S2 | -11.9 | -14.0 to -6.5 | present | -6.5 | -0.2 | -0.6 | -0.8 (-2.9 to 2.0) | absent |
| H11S3 | -7.2 | -13.2 to -5.0 | present | -5.0 | -0.6 | -0.6 | -3.6 (-8.9 to 3.9) | unresolved |

Window/noise ratio (dB) per third-octave band; "·" = not measured by the P7 rule:

| band (Hz) | H11N1 | H11N2 | H11N3 | H11S1 | H11S2 | H11S3 |
|---|---|---|---|---|---|---|
| 2 | 2.3 · | 1.0 · | 3.5 | 2.7 · | -2.8 · | 0.3 · |
| 2.5 | 0.8 · | 3.8 | 0.2 · | 2.9 · | 2.4 · | -1.1 · |
| 3.15 | 6.2 | 10.5 | 6.4 | 4.8 | 1.7 · | 0.5 · |
| 4 | 17.7 | 18.8 | 17.2 | 16.0 | 11.3 · | 11.0 |
| 5 | 19.0 | 20.6 | 18.8 | 17.1 | 14.7 · | 13.0 · |
| 6.3 | 20.8 | 19.9 | 21.5 | 15.5 | 17.1 | 12.6 · |
| 8 | 15.3 | 13.1 | 15.3 | 11.7 | 11.1 | 10.3 |
| 10 | 13.4 | 14.7 | 14.3 | 14.9 | 12.8 | 11.9 |
| 12.5 | 6.6 | 7.9 | 9.9 | 13.2 | 12.1 | 12.1 |
| 16 | 8.0 | 8.1 | 8.6 | 5.9 | 5.1 | 5.2 |
| 20 | 0.2 · | 1.2 · | 0.9 · | 0.5 · | 0.5 · | 0.7 · |
| 25 | 3.7 | 4.5 | 4.8 | 4.5 | 2.2 · | 4.3 |
| 31.5 | 5.7 | 5.8 | 5.6 | 4.7 | 5.2 | 2.9 · |
| 40 | 3.7 | 5.0 | 5.5 | 3.9 | 2.8 · | 3.0 |
| 50 | 2.2 · | 2.2 · | 1.7 · | 3.0 | 2.8 · | 2.4 · |
| 63 | 1.0 · | 1.1 · | 1.0 · | 1.2 · | 1.2 · | 0.5 · |
| 80 | 0.5 · | 0.8 · | 1.6 · | 2.5 · | 2.5 · | 2.8 · |
| 100 | 3.0 | 2.5 · | 3.1 | 4.0 | 3.7 | 2.5 · |

![Received spectra, noise and instrument response]({{artifact:177d1970-606d-49d9-a45e-576f161274bb}})

Humility note (gap): we agree with Metz that the gap exists. Possible causes we cannot yet separate: a source feature (structure, cavity or entry dynamics), or a propagation feature common to both near (180-255 km, cabled seabed) and far (3,300 km, SOFAR) paths — the latter is unlikely because the module TL has no 20 Hz feature and the gap does not move with range, but the module TL fails the airgun slope check, so a TL error is not excluded. A cepstral and per-time-window analysis of the raw arrival would test a delayed-pulse mechanism more directly.

## 5. Implied source spectrum and families

| chain | z_eff (m) | source ESD slope 5-40 Hz (dB/oct) | 5-16 Hz | received ESD slope 5-40 Hz | exponent n |
|---|---|---|---|---|---|
| KRAKEN_ONLY | 2 | -10.31 ± 0.73 | -11.62 ± 1.56 | -4.69 ± 0.74 | 3.42 |
| KRAKEN_ONLY | 10 | -10.23 ± 0.74 | -11.60 ± 1.55 | -4.69 ± 0.74 | 3.40 |
| KRAKEN_ONLY | 30 | -9.56 ± 0.81 | -11.43 ± 1.53 | -4.69 ± 0.74 | 3.18 |
| KRAKEN_ONLY | 50 | -8.40 ± 0.95 | -11.09 ± 1.49 | -4.69 ± 0.74 | 2.79 |
| KRAKEN_RAM | 2 | -9.53 ± 0.79 | -10.08 ± 1.87 | -4.69 ± 0.74 | 3.17 |
| KRAKEN_RAM | 10 | -9.45 ± 0.79 | -10.06 ± 1.87 | -4.69 ± 0.74 | 3.14 |
| KRAKEN_RAM | 30 | -8.99 ± 0.83 | -10.28 ± 1.77 | -4.69 ± 0.74 | 2.99 |
| KRAKEN_RAM | 50 | -7.83 ± 0.94 | -9.94 ± 1.72 | -4.69 ± 0.74 | 2.60 |

Corner fit (post hoc; flat to the corner, f^−n above, module band_fraction shape; bands 3.15-40 Hz with ≥ 2 measured elements):

| chain | z_eff (m) | corner (Hz) | 1σ range (Hz) | exponent above corner | rms misfit (dB) |
|---|---|---|---|---|---|
| KRAKEN_ONLY | 2 | 5 | 4.5-5.75 | 3.50 | 1.73 |
| KRAKEN_ONLY | 10 | 5 | 4.25-5.5 | 3.45 | 1.75 |
| KRAKEN_ONLY | 30 | 4.75 | 4-5.5 | 3.20 | 1.94 |
| KRAKEN_ONLY | 50 | 4.5 | 3.5-5.25 | 2.80 | 2.26 |
| KRAKEN_RAM | 2 | 5.75 | 5-6.25 | 3.35 | 1.77 |
| KRAKEN_RAM | 10 | 5.75 | 5-6.25 | 3.30 | 1.79 |
| KRAKEN_RAM | 30 | 5.25 | 4.25-6 | 3.05 | 1.96 |
| KRAKEN_RAM | 50 | 4.75 | 3.75-5.75 | 2.65 | 2.24 |

![Implied source spectrum at 10 m with the four families]({{artifact:45efbd4c-87d5-4b8f-af80-6b900abb030f}})

## 6. The ridge η_rad(z_eff, S) — D1, 900 MJ, scored 5-63 Hz (68 % range)

| z_eff (m) | f⁻² K+RAM | f⁻² K+RAM, per-triad RAM | f⁻² KRAKEN only | fitted, ~5 Hz corner, K+RAM | same, KRAKEN only | fitted, no corner, K+RAM | f⁻⁴ K+RAM | f⁻⁴ KRAKEN only |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.229 (0.124-0.422) | 0.173 (0.082-0.363) | 0.106 (0.0572-0.196) | 0.22 (0.123-0.396) | 0.171 (0.0948-0.307) | 2.89 (1.6-5.21) **>1** | 13.9 (7.76-24.8) **>1** | 8.35 (4.67-14.9) **>1** |
| 2 | 0.0572 (0.031-0.106) | 0.0432 (0.0205-0.0908) | 0.0265 (0.0143-0.049) | 0.0551 (0.0306-0.099) | 0.0426 (0.0237-0.0767) | 0.722 (0.401-1.3) | 3.47 (1.94-6.19) **>1** | 2.09 (1.17-3.73) **>1** |
| 5 | 0.00925 (0.00502-0.0171) | 0.00698 (0.00332-0.0147) | 0.00428 (0.00232-0.00793) | 0.00884 (0.00492-0.0159) | 0.00685 (0.00381-0.0123) | 0.115 (0.0636-0.207) | 0.555 (0.311-0.992) | 0.335 (0.187-0.599) |
| 10 | 0.0024 (0.0013-0.00442) | 0.00181 (0.000867-0.00378) | 0.00111 (0.000601-0.00206) | 0.00217 (0.00121-0.00391) | 0.00167 (0.000928-0.00301) | 0.0279 (0.0154-0.0503) | 0.14 (0.0781-0.249) | 0.0843 (0.0471-0.151) |
| 20 | 0.000684 (0.000371-0.00126) | 0.000529 (0.000263-0.00107) | 0.00032 (0.000173-0.000591) | 0.000588 (0.000326-0.00106) | 0.000422 (0.000234-0.000759) | 0.00678 (0.00376-0.0122) | 0.037 (0.0207-0.0661) | 0.0216 (0.0121-0.0386) |
| 30 | 0.000364 (0.000198-0.000671) | 0.000285 (0.000144-0.000563) | 0.000172 (9.31e-05-0.000317) | 0.000282 (0.000156-0.000508) | 0.000192 (0.000106-0.000346) | 0.00271 (0.0015-0.00489) | 0.0176 (0.00987-0.0315) | 0.00996 (0.00557-0.0178) |
| 50 | 0.000186 (0.000102-0.000339) | 0.000143 (7.12e-05-0.000287) | 8.98e-05 (4.91e-05-0.000164) | 0.00011 (6.06e-05-0.000198) | 6.77e-05 (3.75e-05-0.000123) | 0.000564 (0.000312-0.00102) | 0.00683 (0.00382-0.0122) | 0.00391 (0.00219-0.00699) |

**>1** = exceeds the energy limit; those points are excluded from the DB rows. "K+RAM" = module convention (H11S RAM delta on both triads); "per-triad RAM" = new pyram deltas (sensitivity).

Error budget at z_eff 10 m (σ in natural-log units; propagation option and family are epistemic switches, given as ratios, not added):

| family | chain | RAM delta | η | H11N | H11S | σ_ln energy | σ_ln element | σ_ln station | σ_ln location | σ_ln total | RAM/KRAKEN | family/f⁻² |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F2 | KRAKEN_ONLY | none | 0.00111 | 0.00163 | 0.000757 | 0.23 | 0.12 | 0.39 | 0.40 | 0.62 | 2.15 | 1.00 |
| F2 | KRAKEN_RAM | module | 0.0024 | 0.00352 | 0.00163 | 0.23 | 0.12 | 0.39 | 0.40 | 0.61 | 2.15 | 1.00 |
| F2 | KRAKEN_RAM | own_new | 0.00181 | 0.00203 | 0.00161 | 0.23 | 0.12 | 0.11 | 0.68 | 0.74 | 2.15 | 0.76 |
| F4 | KRAKEN_ONLY | none | 0.0843 | 0.125 | 0.0569 | 0.23 | 0.12 | 0.39 | 0.34 | 0.58 | 1.66 | 75.77 |
| F4 | KRAKEN_RAM | module | 0.14 | 0.208 | 0.0936 | 0.23 | 0.12 | 0.40 | 0.33 | 0.58 | 1.66 | 58.27 |
| F4 | KRAKEN_RAM | own_new | 0.128 | 0.175 | 0.0938 | 0.23 | 0.12 | 0.31 | 0.42 | 0.58 | 1.66 | 53.45 |
| Ffit | KRAKEN_ONLY | none | 0.0257 | 0.0378 | 0.0174 | 0.23 | 0.12 | 0.39 | 0.36 | 0.59 | 1.09 | 23.07 |
| Ffit | KRAKEN_RAM | module | 0.0279 | 0.0412 | 0.0189 | 0.23 | 0.12 | 0.39 | 0.36 | 0.59 | 1.09 | 11.63 |
| Ffit | KRAKEN_RAM | own_new | 0.0232 | 0.029 | 0.0186 | 0.23 | 0.12 | 0.22 | 0.54 | 0.64 | 1.09 | 9.70 |
| Ffit_c | KRAKEN_ONLY | none | 0.00167 | 0.00246 | 0.00113 | 0.23 | 0.12 | 0.39 | 0.36 | 0.59 | 1.30 | 1.50 |
| Ffit_c | KRAKEN_RAM | module | 0.00217 | 0.0032 | 0.00147 | 0.23 | 0.12 | 0.39 | 0.36 | 0.59 | 1.30 | 0.91 |
| Ffit_c | KRAKEN_RAM | own_new | 0.0018 | 0.00225 | 0.00144 | 0.23 | 0.12 | 0.22 | 0.54 | 0.64 | 1.30 | 0.75 |

RAM − KRAKEN delta (dB; no water absorption in either model):

| band (Hz) | z (m) | module H11S delta (dB) | new H11S | new H11N |
|---|---|---|---|---|
| 5 | 10 | 0.80 | 1.22 | 1.67 |
| 5 | 30 | 1.46 | 1.87 | 2.38 |
| 10 | 10 | 3.52 | 2.83 | 1.91 |
| 10 | 30 | 3.50 | 2.85 | 1.88 |
| 20 | 10 | 3.09 | 3.04 | 0.36 |
| 20 | 30 | 3.17 | 2.98 | 0.41 |
| 40 | 10 | 3.80 | 3.90 | 0.92 |
| 40 | 30 | 3.69 | 3.77 | 1.42 |

![Coupling ridge against source depth]({{artifact:a9e26a68-cfde-48b5-9f15-4d9b7d87d253}})

Extension scored 2-100 Hz (sum of band excesses): f⁻² at 10 m 1.95e-3 (K+RAM) and 9.16e-4 (KRAKEN only), 0.81-0.82 × the 5-63 Hz values.

## 7. Comparisons

Near field (digitised) against the raw far field, f⁻²:

| z_eff (m) | near field (dig., KRAKEN only) | raw far, KRAKEN only | near / raw (KRAKEN only) | raw far, K+RAM | near / raw (K+RAM) | raw / digitised far, K+RAM | raw / digitised far, KRAKEN only |
|---|---|---|---|---|---|---|---|
| 2 | 0.106 | 0.0265 | 4.00 | 0.0572 | 1.85 | 1.060 | 1.059 |
| 10 | 0.00443 | 0.00111 | 3.98 | 0.0024 | 1.85 | 1.060 | 1.059 |
| 30 | 0.000679 | 0.000172 | 3.95 | 0.000364 | 1.86 | 1.072 | 1.060 |

D4 in-band (route B; lower bound of D1 at the same depth):

| z_eff (m) | D4 4-64 Hz, K+RAM (triad range) | D4 4-64 Hz, KRAKEN only | D4 measured bands 2-100 Hz, K+RAM |
|---|---|---|---|
| 1 | 0.113 (0.0696-0.184) | 0.069 | 0.153 |
| 2 | 0.0283 (0.0174-0.0459) | 0.0172 | 0.0382 |
| 5 | 0.00453 (0.00279-0.00735) | 0.00276 | 0.00611 |
| 10 | 0.00113 (0.000699-0.00184) | 0.000692 | 0.00153 |
| 20 | 0.000297 (0.000182-0.000485) | 0.000175 | 0.000404 |
| 30 | 0.000139 (8.47e-05-0.000229) | 7.89e-05 | 0.000191 |
| 50 | 5.39e-05 (3.26e-05-8.9e-05) | 3.02e-05 | 7.25e-05 |

D2 (Arons, path-blind; never combined with a TL model):

| peak definition | P over 6 elements (Pa) | D2 geometric mean | element range (900 MJ) | incl. E 700-1100 MJ |
|---|---|---|---|---|
| 1-110 Hz instantaneous (response removal only) | 1.01-1.57 | 0.00111 | 0.000577-0.00168 | 0.000472-0.00217 |
| 2-100 Hz instantaneous | 0.93-1.28 | 0.000756 | 0.000459-0.00101 | 0.000375-0.0013 |
| 4-40 Hz instantaneous | 0.689-1.26 | 0.000459 | 0.000207-0.000938 | 0.000169-0.00121 |
| 4-64 Hz 1-s RMS peak | 0.212-0.394 | 2.11e-05 | 9e-06-4.31e-05 | 7.37e-06-5.55e-05 |
| 4-64 Hz instantaneous | 0.78-1.29 | 0.000543 | 0.000288-0.001 | 0.000236-0.00129 |

Humility note (Brown): the factor 2.2-2.6 between Brown's D2 and ours can come from Brown's band, element, filter or peak definition (none stated), from Brown using 3,300 km and one element, or from our peak picking over ±15 s including noise peaks (noise RMS 0.05-0.07 Pa, so noise extremes are ≤ ~0.3 Pa, well below the 0.7-1.3 Pa signal peaks). A statement of Brown's processing would resolve it. Brown's value is not wrong for his definition; it is the low end of the raw-peak range.

## 8. DB rows and validator

[f35a-raw-coupling-rows.csv]({{artifact:308c987e-62b4-4474-a766-6082bc6094ea}}): 82 rows CV26-CV107 (64 D1 on MODULE_KRAKEN_RAM / MODULE_KRAKEN_ONLY, 14 D4, 4 D2 on ARONS_1954), all status EVIDENCE, independence group G1; the per-triad RAM rows have role MODEL_ERROR_MEASURE. Six D1 points with η ≥ 1 are omitted. [f35a-raw-received-observation-rows.csv]({{artifact:cb856065-87fd-4c12-a557-cbefa327cb09}}): OB07-OB12 (4-64 Hz; OB01-OB06 used 4-40 Hz). Validator on the package tables plus these rows: **RESULT: PASS (0 failures)**, v_module_chain 90 rows, v_arons_screen 7 ([validator_output.txt]({{artifact:3d1f8969-1612-4b4d-bbcf-7a6ac14305bd}})). The value_ids CV26 onward assume no other track has used them; the importer should renumber if needed.

## 9. Deviations

1. **63 Hz RAM band dropped** (cost ~70 min); the new RAM deltas cover 5/10/20/40 Hz at 10/20/30/50 m, held at end values outside (module convention). Depths < 10 m use the 10 m delta (RAM grid dz λ/20 cannot place 1-5 m sources).
2. **Primary KRAKEN+RAM uses the module H11S delta on both triads**, as pre-registered; the per-triad delta is a sensitivity and is recommended to the registry owner because it removes most of the station spread.
3. **Post hoc additions:** corner-frequency family Ffit_c; σ from pre-event noise only (makes 4-6.3 Hz "measured" at all six elements; changes the source slope by +0.45 dB/octave); 2-100 Hz scoring extension.
4. **σ_b (pre-registered) includes diurnal non-stationarity** of the backgrounds, which made 4-6.3 Hz "not measured" at H11S2/S3 despite 11-17 dB window/noise; it is conservative.
5. **The 100 Hz band** (89-112 Hz) lies partly in the anti-alias roll-off (−3.7 dB at 105, −13 dB at 110 Hz) and the pre-filt taper; its excess (window/noise 2.5-4 dB) is not used in the ridge.
6. **Back-azimuth** ignores element depth differences; the 3-4° discrepancy is unresolved.
7. **Location sensitivity** uses P (Metz-consistent point) only; Metz's ellipse (36.8 × 7.3 km) was not sampled.
8. **One H11N3 background window** (23 h) has a gap (19.3 of 30 min used). No other data were cut. The RAM run was interrupted once by a daemon restart and resumed from the saved partial rows (no recomputation of finished rows).
9. **Not done:** cepstral test of the gap; T-phase bearing calibration; RAM at 1-5 m.

## 10. Standing caveats

(1) The module propagation model fails the frequency-slope check against the 2001 airguns (+10 dB/octave at H01W, +7 at H08S) although levels pass. This result does **not** change that: the raw spectra confirm the received slope that Metz show, and the implied source slopes (and hence the family weights) are biased steep by a similar amount if the tilt is a path error. (2) Detection probability is a proxy unless measured on real data; no detection statistic is computed here. (3) One event (G1), counted once; all ridge points are evidence, not parameters.

## 11. Files

Tables: [f35a-raw-measurements.csv]({{artifact:a29fe11a-da64-40ee-add9-3efb5584225c}}), [f35a-raw-ridge.csv]({{artifact:b4c0d30b-bb85-4f93-acc3-4c4a6c3a00b4}}), [f35a-raw-band-exposure.csv]({{artifact:fb6cb1d7-f03d-47a2-b30b-bfa5627549a6}}), [f35a-raw-gap-test.csv]({{artifact:d9da5279-c10c-4dad-a22b-bfedcb26b389}}), [f35a-raw-bazimuth.csv]({{artifact:48736460-a76a-456e-a2a8-a24a7ada9f1b}}), [f35a-raw-spectra.csv]({{artifact:4e657c67-8035-4be6-a01b-16866bfb5ad7}}), [f35a-raw-source-slope.csv]({{artifact:1d800f59-dcd3-472d-a025-7d70cace70ae}}), [f35a-raw-corner-fit.csv]({{artifact:41918a5c-1a5c-401b-86ec-85e0e79e3be9}}), [f35a-raw-d4.csv]({{artifact:d52d370d-64e6-4ec1-84dd-5383c648e63d}}), [f35a-raw-d2.csv]({{artifact:74a3aaf4-d3d2-4cc0-a6ef-4739a1c14f04}}), [f35a-raw-ram-delta.csv]({{artifact:477815d8-64d9-42df-9357-448f56f0e30c}}), [f35a-raw-tl-kraken.csv]({{artifact:201ef4d5-0260-4e02-8bdf-c84e8001b73d}}). Figure: ![Raw and digitised envelopes]({{artifact:14a34def-36de-40b6-9c7e-d71d6c3dc494}})
Scripts: [fetch_raw.py]({{artifact:e18ccd15-0cb6-42a6-8077-c38e303c4670}}), [raw_lib.py]({{artifact:ad38d476-bba8-4950-9593-dbed67da193c}}), [tl_ridge.py]({{artifact:1d808027-18c6-4e5a-9a99-23a0d3e00262}}), [ram_ridge.py]({{artifact:8181fd47-35c0-4a3a-8031-849c8cc35571}}), [f35a_raw_analysis.py]({{artifact:46ebd02b-70df-46e7-8e80-9efb9937a0d7}}), [make_figures.py]({{artifact:90de5e02-f36a-4bc5-b158-45a9783d8d4d}}), [make_db_rows.py]({{artifact:0821f8b9-a075-4576-be2f-553b83d30526}}). Environment mh370-hydro; module branch hypothesis/hydroacoustics read only; Acoustics Toolbox binaries from ~/Downloads/mh370-exchange/hydroacoustics/run-j-metz-f35a/at; nothing committed.
