# Held-out level tests and path-class level correction: pre-registration

3 Nov 2026. Hydroacoustics, source-grid method (proposal X18, Pete decisions P73-P74). Written and saved BEFORE any correction fit or held-out statistic was computed.
Status: EXPLORATORY and UNCHECKED until an independent verifier passes it. Nothing is committed to GitHub here.

## 0. What was already seen (disclosure)

- Per-family residual means for the frozen chain tl-chain-2026-10-27 (L1 seabed) were seen in the 27-28 Oct notes: SUS 2003 route A about +7 to +12 dB, route B about -1 to +5 dB; FSST shots about +11 to +17 dB; San Juan charge about 0 dB; San Juan charge station difference (south minus north) +11.6 dB; air7 to Cape Leeuwin over-blocked by about 20 dB.
- The path classes (section rule, index 97e0f6e3) were seen: all Atlantic paths are "ridge above the channel axis"; SUS paths to Cape Leeuwin are "ridge near the channel axis"; SUS A6-A9 to Diego Garcia South are "clear deep path".
- Royer path classes and Royer transmission losses were NOT seen (the RAM run is not finished). Royer arrival energies were not yet extracted.
- No fit of the correction model and no held-out statistic had been computed.

## 1. Model and data scope

- Propagation model under test: frozen chain tl-chain-2026-10-27, L1 seabed (GlobSed v3 sediment over 3500 m/s basement), RAM, reciprocal runs. This is the chain of the 7th-arc dense grid (v3bbc0a2c). Rows from other seabeds (H0, bare rock, T3) are not used.
- Frequency domain: the ten third-octave bands 5-40 Hz (5, 6.3, 8, 10, 12.5, 16, 20, 25, 31.5, 40 Hz). Bands at 50-63 Hz are listed in the residual table but are not fitted and not scored.
- Residual: r = observed received band level minus predicted band level (dB). Predicted = source model + array or receiver factor - TL (frozen chain).
- Path class: the section rule of index 97e0f6e3 ("clear deep path", "ridge near the channel axis", "ridge above the channel axis", "blocked"). The old classifier ("ridge", "plateau") is not used. Royer paths take the class that comes with the Royer TL table; if none comes, the same section rule is applied to the Royer sections and this is declared.
- No outlier rejection. air7 to Cape Leeuwin and the San Juan south-north difference stay in.

## 2. Data rows (row types)

| Family (hold-out unit) | Events | Row type | Source term | Use |
|---|---|---|---|---|
| Blackman 2003 SUS charges (A6-A10) | 8 shot-sites | known-source level | route B primary; route A sensitivity | fit + held out |
| Blackman 2003 SUS charge A11 (size unknown) | 1 | free-level (charge unknown) | cancels | fit (slope only); Diego Garcia South path (N x 2D corridor, not the 2D chain) excluded |
| San Juan calibration charge 2017-12-01 | 1 | known-source level | G&S construction, 30 m (primary rows of the 27 Oct run) | fit + held out |
| US Navy ship shock trials 2016 and 2021 | 8 shots | known-source level | G&S construction, 61 m (primary rows) | fit + held out |
| San Juan loss event 2017-11-15 | 1 | station difference (south minus north) | cancels | fit + held out |
| F-35A crash 2019 (Wake) | 1 | station difference (south minus north) | cancels | fit + held out |
| Blackman 2001 airguns, Fig. 23 TL | 5 sites (air1-4, 7, 9 with traced bands) | free-level per airgun site (source and Blackman spectral convention unknown; shared by the stations of one site) | cancels; source-shape slope sd 1.5 dB/oct shared by the family | fit + held out |
| Blackman 2001 airguns, detection floor | 7 sites | one-sided (detected or not), Tolstoy far-field source at 7.5 m | not in fit | held-out one-sided check only |
| Royer 2016 events | each event its own hold-out unit | station energy differences, 5-40 Hz, against the first station that has a measurable arrival | cancels | fit + held out |
| Wake and Juan Fernandez 2008 charges | - | - | - | EXCLUDED: no frozen-chain paths exist for these, and new sound-model runs are out of scope |
| Glass spheres 2003 | - | - | - | EXCLUDED: deep implosion branch, not this correction |

Reasons:
- Airgun absolute level from Fig. 23 is not two-sided: the 27 Oct addendum rejects a single Blackman spectral convention. So airgun Fig. 23 rows carry a free level per site. They inform slope and the difference between the classes of the stations of one site.
- Rows with known level are not also entered as station differences (no double use). Station-difference rows are used only where no level row exists.

### 2.1 SUS source choice (primary = route B)

Route B (pulse re-built at the shot depth) is primary. Route A is reported as a sensitivity. Reasons, all physical, fixed before the fit:
1. The 2003 charges are at 610 and 915 m. Gaspin & Shuler (1971) state validity to about 1,000 ft. Route A scales their table outside that depth AND extrapolates below their lowest band at 16-25 Hz with a fitted slope.
2. In 16-63 Hz the charges radiate far below the bubble frequency (108-151 Hz). There a pulse with zero net impulse has an f^2 tail (+6 dB/oct). Route A rises +11 to +13 dB/oct, steeper than that tail. Route B rises +3.5 to +10.5 dB/oct, which is physically possible.
3. Route B uses secondary-literature shock coefficients. This is a known weakness. It is carried as source uncertainty (below).
SUS source sd per band = sqrt(source_sd_db^2 + ((r_A - r_B)/2)^2). This is shared by all SUS shots and stations (one family term). It treats the two routes as about +/-1 sd brackets.

### 2.2 Source and observation terms

- Family source error u_F ~ N(0, s_F^2), shared by all rows of a family with known source: SUS per band as above; FSST 4.98 dB and San Juan charge 2.60 dB (source-model spread of the 28 Oct sigma table).
- Per-event charge term 1.0 dB (shot-to-shot), shared by the rows of one event.
- Observation sd and TL band sd: as recorded in the source tables (meas_sd_db, tl_band_sd_db; for rows where only a combined sd is recorded, that combined sd is used).
- Airgun site source shape: slope random term, sd 1.5 dB/oct, shared by all airgun Fig. 23 rows.

### 2.3 Royer station energies (data reduction rule)

- Events: the five events with four-station 3-minute panels (Royer Figs 4-8: A, B, C1, C2, D2). Secondary: the 30-minute appendix panels (Cape Leeuwin H01W2, SSEIR, SWAMS3, 00:00-02:00) for any other Royer event with an arrival inside a panel at two or more of these stations.
- Arrival time at each station: Royer observed time if in the labelled set, else the labelled-set predicted time.
- Column psd_db_5_40 (colour-read PSD, 5-40 Hz) is taken as 10 log10 of the band-mean power. Power P = 10^(psd/10).
- Noise N = median P in the panel outside [t_arr - 30 s, t_arr + 75 s].
- Arrival energy E = sum over [t_arr - 15 s, t_arr + 45 s] of (P - N) dt (no clamping).
- Measurable if 10 log10(mean P in window / N) >= 3 dB and E > 0. Else the station is not used for that event.
- Observation sd: the same window sum applied to noise-only stretches of the same panel (all non-overlapping 60 s stretches outside the arrival exclusion zone); sd(E_noise) gives sd_dB = 4.34 sd/E, floor 0.5 dB.
- Station calibration: H01W2 colour reading +2.9 dB, OHASISBIO +0.86 dB (royer noise calibration, 3c3a4576). Calibration sd: 1.15 dB at H01W2 (failed texture test); 2.0 dB between H01W2 and any OHASISBIO site (Royer Table 3 factor cannot be checked); 0.5 dB among OHASISBIO sites.
- Predicted level difference: band-summed energy with a flat source energy spectrum per Hz over 5-40 Hz, source depth 10 m (primary), using the ten band TLs of each path. Row frequency for the slope term: the energy-weighted mean of log2(f/10) over the bands of the two paths.
- Sensitivities (reported, not primary): window 40 s and 90 s; source spectrum f^-2; source depth at the shallowest and deepest TL depth.

## 3. Correction model

Mean residual of a row in class c at band f: b_c + s_c * log2(f / 10 Hz).
- Known-source level rows: mean b_c + s_c x.
- Free-level rows: mean a_g + b_c + s_c x, a_g a free nuisance per group (airgun site; A11 shot).
- Difference rows (path i minus path j): mean (b_ci - b_cj) + (s_ci x_i - s_cj x_j).

Random terms (Gaussian, independent):
- tau: path offset, one per station path, the same for all bands of that path.
- sigma_band: band shape term, one per path and band (in addition to the recorded TL band sd).
- family source term, event charge term, airgun slope term (fixed sd, section 2.2).
- observation and TL band sd (recorded).

Estimation:
- tau and sigma_band: restricted maximum likelihood (REML), global (shared by all classes), on a grid of 0.25 dB (0 to 20 dB).
- b_c, s_c, a_g: generalised least squares given the REML variance terms. Parameter covariance from GLS.
- Class eligibility: a class gets its own (b_c, s_c) if it has >= 3 distinct source EVENTS that inform its level (known-source level rows, or difference / free-level groups that join it to another class). Else the class uses the pooled global (b, s), fitted with one (b, s) for all rows.
- Predictive sd of a new path's band level in class c at 10 Hz: sd_db = sqrt(tau^2 + sigma_band^2 + var(b_c + s_c*0)). It excludes the source term, the observation sd and the TL band sd of the new path (the search adds the TL table band sd).

## 4. Leave-one-source-out scheme

- Hold-out units: (1) SUS 2003 (A6-A11 together); (2) San Juan charge; (3) ship shock trials 2016 and 2021 together (one source model; sensitivity: 2016 and 2021 as separate units); (4) San Juan loss event; (5) F-35A; (6) airgun Fig. 23 rows; (7) each Royer event in turn.
- In each fold: re-fit tau, sigma_band, the global and class parameters, and class eligibility, on all other units. Predict the held-out rows.
- Held-out prediction for a row: mean m = predicted bias (class model if eligible in that fold, else global), and total sd S = sqrt(obs^2 + TL band sd^2 + family source^2 + charge^2 + tau^2 + sigma_band^2 + parameter variance) for level rows; for difference rows the source terms cancel and the path terms count for both paths. For free-level groups the free level is removed by centring on the group (rows minus group mean, with matching sd).
- z = (r - m) / S.

## 5. Statistics and pass rules (fixed now)

Primary set: all held-out rows, 5-40 Hz, pooled over folds (each band counts once).
- P1: |mean z| <= 0.5.
- P2: sd z in [0.7, 1.4].
- P3: 90 % central prediction interval (m +/- 1.645 S) covers 80-97 % of held-out bands.
- CRPS (Gaussian, closed form) of the corrected forecast N(m, S^2) against the uncorrected forecast N(0, S^2) (same sd, bias effect only; primary) and against N(0, S_u^2) with S_u^2 = obs^2 + TL band sd^2 + source^2 + 5.0^2 + 3.07^2 (the earlier provisional sigma_model; secondary). Improvement is claimed only if the pooled mean CRPS is lower AND it is lower in at least half of the hold-out units.
- The same P1-P3 are reported per hold-out unit and per path class. A unit or class with fewer than 10 held-out bands, or a class with fewer than 3 source events, is reported as INFORMATION, not graded.
- Secondary: a unit-balanced version (each hold-out unit weight 1) of P1-P3.
- Airgun detection floors (one-sided): per case-station, the predictive probability of the observed outcome, P(det) = Phi(M_c / S_f), where M_c = median floor margin (S >= N rule) + predicted bias, S_f^2 = predictive variance + window term 4.0^2 + back-projection 5.0^2. Report the log score against the uncorrected margin. Information only.
- A class is TESTABLE only if, after its own sources are held out, it still has >= 3 source events from other units. Classes that are not testable are named as such; their correction is then the global value or an untested class value.

## 6. Final fit and output

- Final fit on all units, with the same rules. Output level_correction.json in the shared schema; classes that fail eligibility carry the global values and say so in notes.
- If P1-P3 fail in the primary set, level_correction.json is still written, but its notes say FAIL, and the version string carries "-provisional".

## 7. AMENDMENT A1 (3 Nov 2026, after Royer energies were extracted, BEFORE the Royer TL table was received or any Royer residual was formed)

Reason: the section 2.3 rule failed on technical grounds. (a) The 3-minute panels leave fewer than two 60 s noise-only stretches, so the observation sd was undefined. (b) SSEIR and SWAMS3 carry seismic survey shots; a median noise level gives a positive bias. (c) Royer's observed arrival times put one arrival under several events at one station (for example SWAMS3: events 5, 6, 11, 12, 13 within 16 s; Cape Leeuwin: events 2 and A within 2.4 s).
Changed rule (replaces the noise, sd and measurability lines of section 2.3):
1. Noise: the panel outside [t_arr - 30 s, t_arr + 75 s] is cut into 10 s blocks. E = (sum of P dt over the 60 s window) - 6 x (mean block sum). sd_E = sqrt(6) x (sd of block sums). At least 4 blocks.
2. Measurable if E >= 2 sd_E.
3. Overlap: if the windows of two events at one station are closer than 60 s, that station is not used for either event. Event C3 (1.1 s and 0.07 deg from C2) is merged into C2.
4. Panel priority for one event and station: 3-minute figure panel, then 30-minute appendix panel, then the 45-minute Fig. 2 panel.
5. Extra reading sd 2.0 dB per station measurement. Basis: the same event and station read on two panels differ by -3.4 to +0.3 dB (4 pairs, before the overlap rule). This uses no model value.
Result of the data reduction (no model used): four events keep two or more measurable stations: A (SWAMS3, MAD, WKER, SSEIR), B (Cape Leeuwin H01W2, SSEIR), event 5 (SSEIR, H01W2), event 10 (SWAMS3, H01W2). That gives 6 independent station differences. These four events are the Royer hold-out units.
