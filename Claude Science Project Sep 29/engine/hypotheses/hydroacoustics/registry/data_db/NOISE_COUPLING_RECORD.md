# Noise and acoustic coupling: generated record

Generated from `hydro_data.sqlite` by `build_noise_coupling.py` on 2026-10-25T01:05:11Z. Do not edit by hand; rebuild instead.

**Rules.** Every value carries its definition, unit, source file and SHA-256. Coupling values are used only with the propagation relation of their definition (views `v_coupling_for_module_chain`, `v_coupling_path_blind`, `v_coupling_implosion`). The F-35A values are points on one (coupling, source depth, spectrum) curve from one recording; no ruling is needed (Pete, 24 Oct 2026). Status and defects stay in the registry.

## 1. Background noise, median band level by site (dB re 1 uPa^2/Hz unless stated)

**IMS 2003 Blackman cruise; 6 s window; statistic over panels; unit dB re 1 uPa^2/Hz; role: background (2003; primary for IMS)**

| site_id   |   1/3 octave 5 Hz |   1/3 octave 6.3 Hz |   1/3 octave 8 Hz |   1/3 octave 10 Hz |   1/3 octave 12.5 Hz |   1/3 octave 16 Hz |   1/3 octave 20 Hz |   1/3 octave 25 Hz |   1/3 octave 31.5 Hz |   1/3 octave 40 Hz |
|:----------|------------------:|--------------------:|------------------:|-------------------:|---------------------:|-------------------:|-------------------:|-------------------:|---------------------:|-------------------:|
| H01W      |              87   |                85.6 |              84.8 |               84.6 |                 83.5 |               88.4 |               89.8 |               86.8 |                 81.5 |               79.4 |
| H08N      |              77.3 |                76   |              75.2 |               73.8 |                 73.9 |               73.7 |               74.5 |               74.4 |                 74   |               76.1 |
| H08S      |              79.8 |                80.1 |              80.6 |               79   |                 77.5 |               80.4 |               81.2 |               80.2 |                 79.1 |               79.6 |

**MH370 8 Mar 2014; spectrogram colour over the panel; unit dB re 1 uPa^2/Hz; role: sensitivity (Delta added as a labelled sensitivity (Blackman retained as primary))**

| site_id   |   1/3 octave 5 Hz |   1/3 octave 6.3 Hz |   1/3 octave 8 Hz |   1/3 octave 10 Hz |   1/3 octave 12.5 Hz |   1/3 octave 16 Hz |   1/3 octave 20 Hz |   1/3 octave 25 Hz |   1/3 octave 31.5 Hz |   1/3 octave 40 Hz |
|:----------|------------------:|--------------------:|------------------:|-------------------:|---------------------:|-------------------:|-------------------:|-------------------:|---------------------:|-------------------:|
| H01W      |              70.1 |                70.1 |              70.1 |               69.7 |                 70.5 |               70.5 |               70.1 |               70.5 |                 70.1 |               70.1 |
| H08S      |              64.3 |                67   |              68.1 |               67   |                 67.5 |               67   |               68.1 |               68.1 |                 67.5 |               66.5 |

**MH370 8 Mar 2014; 1 s Hann periodograms; unit dB re 1 uPa^2/Hz; role: background (event day)**

| site_id   |   2-5 Hz |   5-10 Hz |   10-20 Hz |   20-40 Hz |   40-80 Hz |   80-160 Hz |   160-240 Hz |
|:----------|---------:|----------:|-----------:|-----------:|-----------:|------------:|-------------:|
| IMOS3250  |    111.2 |      96.2 |       81.7 |       83.2 |       69.2 |        56.4 |         52.5 |
| IMOS3274  |    101.2 |      93.2 |       86.7 |       82.3 |       77.2 |        70.9 |         68.5 |
| IMOS3275  |     85.7 |      79.4 |       78.9 |       78.6 |       76.2 |        71.4 |         69.6 |
| IMOS3315  |     88.5 |      78.8 |       82.4 |       81.7 |       76.9 |        66.3 |         62.2 |
| IMOS3376  |     99.3 |      81.9 |       81.8 |       79.3 |       75.3 |        65.9 |         62.2 |

**MH370 8 Mar 2014; Welch per record, across records; unit dB re 1 uPa^2/Hz; role: background (event day)**

| site_id   |   2-5 Hz |   5-10 Hz |   10-20 Hz |   20-40 Hz |   40-80 Hz |   80-160 Hz |   160-240 Hz |
|:----------|---------:|----------:|-----------:|-----------:|-----------:|------------:|-------------:|
| IMOS3250  |    116.8 |     101.5 |       91.5 |       93.1 |       78.1 |        64.6 |         58.2 |
| IMOS3274  |    100.5 |      93.4 |       87.2 |       82.6 |       77.2 |        71.2 |         68.6 |
| IMOS3275  |     85.7 |      80.2 |       79.3 |       78.9 |       76.4 |        71.6 |         69.5 |
| IMOS3315  |     87.3 |      79.7 |       83.1 |       82.6 |       77   |        66.5 |         62.3 |
| IMOS3376  |     98   |      82.4 |       82.1 |       79.6 |       75.8 |        65.7 |         62.8 |

**calibration: F-35A 9 Apr 2019; 1 s RMS envelope; median outside the arrival per element, mean over elements; unit dB re 1 uPa; role: background at the F-35A calibration receivers**

| site_id   |   4-64 Hz |
|:----------|----------:|
| H11N      |      95.7 |
| H11S      |      93.9 |

## 2. Conditions that affect noise

| site_id          | context                  | condition                                                                                      | effect                                                                                        | source                                                 |
|:-----------------|:-------------------------|:-----------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------|:-------------------------------------------------------|
| H08S             | MH370 8 Mar 2014         | periodic airgun shots (about every 10 s) in the Kadri Fig. 9 panels; 110 shots 01:00-01:19 UTC | masking and false alarms; a shot coincidence is a label, not an exclusion (Pete, 23 Oct 2026) | kadri_fig9_noise/summary.json; h08s_template_shots.csv |
| OHASISBIO (all)  | MH370 8 Mar 2014         | powerful seismic shots from an exploration survey obscure most of the data that day            | raised noise and masking at the OHASISBIO sites; no calibrated level extracted yet            | Royer 2016, LDO-201608, p. 3                           |
| IMOS (all)       | MH370 8 Mar 2014         | 8 Hz hardware high-pass corner (header LF); 2-5 Hz band below it                               | 2-5 Hz levels are not ambient-noise estimates                                                 | record headers; imos1d                                 |
| H01W, H08S, H08N | IMS 2003 Blackman cruise | 2003 levels, not 8 Mar 2014                                                                    | use as background estimate with that label; Kadri Fig. 9 gives an 8 Mar 2014 sensitivity      | note.ims_noise_blackman                                |

## 3. Coupling definitions

| def_id   | name                                                                        | allowed_chain           | rule                                                                                                                              |
|:---------|:----------------------------------------------------------------------------|:------------------------|:----------------------------------------------------------------------------------------------------------------------------------|
| D1       | source radiated acoustic energy / impact kinetic energy (model-inverted)    | module_tl               | Use only with the module propagation chain and the source depth and spectrum it was inverted with. Never with the Arons relation. |
| D2       | Arons-equivalent in-channel TNT energy / impact kinetic energy (path-blind) | path_blind              | Use only as an end-to-end screen with the Arons relation. Never combine with a transmission-loss model (path counted twice).      |
| D3       | near-field measured acoustic energy / kinetic or hammer energy              | near_field_source_model | Envelope and scaling evidence only. Not coupling into the deep sound channel.                                                     |
| D4       | in-band source radiated energy / impact kinetic energy (lower bound of D1)  | module_tl               | Consistency check on D1; same chain rules as D1.                                                                                  |
| D3I      | implosion radiated energy / P V                                             | implosion_branch        | Separate implosion branch. Different denominator: never mix with impact coupling.                                                 |

## 4. Coupling values (as published or derived; status)

| value_id                      | def_id   | value_as_written                  |   range_low |   range_high | role_in_prior                                                    | role_status          |
|:------------------------------|:---------|:----------------------------------|------------:|-------------:|:-----------------------------------------------------------------|:---------------------|
| PRIOR-A (recommended, module) | D1       | log-uniform                       |     1e-06   |     0.01     | PRIOR                                                            | PROPOSAL (not ruled) |
| PRIOR-B (screening only)      | D2       | log-uniform                       |     1e-08   |     0.0002   | PRIOR (screening)                                                | PROPOSAL (not ruled) |
| F35-BROWN                     | D2       | 1e-4 (order)                      |   nan       |   nan        | upper bound of PRIOR-B                                           | EVIDENCE             |
| F35-BROWN-REPRO               | D2       | 2.08e-4                           |     0.00017 |     0.000267 | upper bound of PRIOR-B                                           | EVIDENCE             |
| F35-PROJ-22OCT                | D1       | 2.26e-3                           |     0.00034 |     0.054    | anchor of PRIOR-A                                                | EVIDENCE             |
| F35-PROJ-09OCT                | D1       | 8e-4                              |     0.0001  |     0.02     | superseded by F35-PROJ-22OCT                                     | SUPERSEDED           |
| F35-PROJ-INBAND               | D4       | 1.2e-3                            |     0.00088 |     0.0015   | consistency check                                                | EVIDENCE             |
| LESLIE1964                    | D3       | ~1e-2                             |     0.001   |     0.01     | upper bound of PRIOR-A (total, all bands)                        | EVIDENCE             |
| PILE                          | D3       | 0.12-2.13%                        |     0.0012  |     0.021    | supporting upper range                                           | EVIDENCE             |
| RAINDROP                      | D3       | 1e-5                              |   nan       |   nan        | supporting lower range                                           | EVIDENCE             |
| ICE-2020                      | D3       | 8e-7                              |     3.2e-07 |     1.3e-06  | lower bound of PRIOR-A                                           | EVIDENCE             |
| ICE-2015                      | D3       | 5.16e-10                          |   nan       |   nan        | exclude (superseded)                                             | EXCLUDED             |
| CHARGES-ARONS                 | D2       | 4e-4 to 1.7                       |     0.0004  |     1.7      | exclude for impacts; shows site/path scatter of D2 (3.5 decades) | EXCLUDED             |
| IMPLOSION-GLASS               | D3I      | 0.18                              |   nan       |   nan        | separate implosion prior (upper)                                 | EVIDENCE             |
| IMPLOSION-METAL               | D3I      | 0.2-0.6%                          |     0.002   |     0.006    | separate implosion prior (lower)                                 | EVIDENCE             |
| AIRBURST                      | D2       | 1e-5 to 1e-4; <=1e-10 (fireballs) |   nan       |   nan        | exclude (not an impact mechanism)                                | EXCLUDED             |

## 5. F-35A coupling curve against source depth (module chain, register E01; E02 near field for model error)

| curve_id              |   src_depth_m |    n |   eta_min |    eta_max |
|:----------------------|--------------:|-----:|----------:|-----------:|
| E01_far_field_9oct    |             2 |  600 |  0.00315  |   6.61     |
| E01_far_field_9oct    |            10 |  600 |  0.000131 |   0.266    |
| E01_far_field_9oct    |            30 |  600 |  1.96e-05 |   0.0308   |
| E01_far_field_H11     |             2 | 2100 |  0.00163  |   6.85     |
| E01_far_field_H11     |            10 | 2100 |  6.81e-05 |   0.276    |
| E01_far_field_H11     |            30 | 2100 |  1.07e-05 |   0.0351   |
| E02_near_field_cabled |             2 |  720 |  0.00683  |   1.98e+04 |
| E02_near_field_cabled |            10 |  720 |  0.000286 | 791        |
| E02_near_field_cabled |            30 |  720 |  4.52e-05 |  88.9      |

## 6. Evidence register (roles and independence groups)

| evidence_id   | evidence                                                                                                | how_it_is_used                                                                                                                        | independence_group               |
|:--------------|:--------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------|
| E01           | F-35A far field, Wake Island H11N/H11S (Metz 2023 Fig 3, digitised)                                     | LIKELIHOOD TERM (the primary calibration)                                                                                             | G1: F-35A recording              |
| E02           | F-35A near field, cabled seabed stations DSOH/KSP1-3 (Metz 2023 Fig 2, digitised)                       | MODEL-ERROR MEASURE (inflates sigma_model; not an independent eta estimate)                                                           | G1: F-35A recording (same event) |
| E03           | F-35A spectral shape, near and far (Metz 2023)                                                          | LIKELIHOOD TERM on S (spectral family weights)                                                                                        | G1: F-35A recording              |
| E04           | F-35A source duration bound (Metz 2023)                                                                 | CONSTRAINT on tau family for R1 (source-model calibration on a different aircraft; not fed back to end of flight)                     | G1                               |
| E05           | Brown et al. 2026 Arons-equivalent coupling (Icarus 455:117106)                                         | CONSISTENCY CHECK of the forward model (the model must reproduce D2 on the same path); NOT an independent eta - same recording as E01 | G1: F-35A recording              |
| E06           | Leslie 1964, bullet water entry (JASA 36:1138; abstract only)                                           | ENVELOPE (upper plausibility bound) and SCALING point                                                                                 | G2: mechanism analogs            |
| E07           | Pile driving energy conversion (review)                                                                 | ENVELOPE (upper)                                                                                                                      | G2                               |
| E08           | Raindrop impacts (Liu et al. 2021)                                                                      | ENVELOPE (lower) and SCALING point                                                                                                    | G2                               |
| E09           | Iceberg block impacts (Glowacki & Deane 2020)                                                           | ENVELOPE (lower) and SCALING point                                                                                                    | G2                               |
| E10           | Water-entry physics: slam vs cavity/bubble energy (Li et al. 2021; Leslie; Truscott 2014; Minnaert)     | PRIOR STRUCTURE (sets z_eff prior and the low-frequency spectral branch)                                                              | G3: physics                      |
| E11           | Surface image (Lloyd's mirror) for a near-surface source                                                | BUILT INTO FORWARD MODEL (not a datum)                                                                                                | G3                               |
| E12           | Known-yield explosions at IMS (FSST 2016/2021, 39 kg charges, San Juan calibration charge, SUS)         | PROPAGATION VALIDATION -> sigma_model; NOT eta                                                                                        | G4: propagation                  |
| E13           | Blackman 2001/2003 airgun, SUS and sphere sources at H01/H08                                            | PROPAGATION VALIDATION -> sigma_model (frequency-dependent)                                                                           | G4                               |
| E14           | Implosions (Orr & Schoenberg 1976 glass ~18 %; Shukla et al. 2018 metal 0.2-0.6 %)                      | SEPARATE SOURCE PRIOR                                                                                                                 | G5: implosions                   |
| E15           | Swissair 111 land seismic record (CN.LMN 173 km; MN 0.57)                                               | CROSS-CHECK ONLY (different physics; not eta)                                                                                         | G6: seismic                      |
| E16           | Kadri 2024 claimed aircraft detections (AF447, Yemenia, Sriwijaya, Transair, Lion Air, AirAsia, Asiana) | EXCLUDED from calibration (SNR < 2 on own figures; timing checks inconsistent in an exploratory model; no independent reproduction)   | G7                               |
| E17           | Airbursts and fireballs (Clarke 1996; Kamegai & White 1994; Brown 2026)                                 | EXCLUDED                                                                                                                              | G8                               |

## 7. Checks

| check | result | description | detail |
|---|---|---|---|
| N01 | PASS | Every noise value uses a declared quantity and its unit | 0 mismatches |
| N02 | PASS | Every noise band has lower edge < upper edge | 0 bad bands |
| N03 | PASS | Noise PSD values inside 40-140 dB re 1 uPa^2/Hz (plausibility) | 0 outside |
| N04 | PASS | IMOS band statistics in the database equal noise_bands.csv (round trip) | 245 values, 0 mismatches |
| N05 | PASS | Blackman medians 5-40 Hz inside the pre-registered 55-105 dB gate | 0 outside |
| N06 | PASS | Every stage-2 input file still matches its SHA-256 | 14 files, 0 changed |
| N07 | PASS | Every IMOS per-record noise row links to a raw record in table segment | 153 records, 0 unmatched |
| N08 | PASS | Every noise row names a site in table site | unknown: [] |
| K01 | PASS | Every coupling value has a declared definition | PRIOR-A (recommended, module)->D1; PRIOR-B (screening only)->D2; F35-BROWN->D2; F35-BROWN-REPRO->D2; F35-PROJ-22OCT->D1; F35-PROJ-09OCT->D1; F35-PROJ-INBAND->D4; LESLIE1964->D3; PILE->D3; RAINDROP->D3; ICE-2020->D3; ICE-2015->D3; CHARGES-ARONS->D2; IMPLOSION-GLASS->D3I; IMPLOSION-METAL->D3I; AIRBURS |
| K02 | PASS | Module-chain view holds no path-blind, near-field or implosion value | 0 wrong rows |
| K03 | PASS | Path-blind view holds only Arons-equivalent values | 0 wrong rows |
| K04 | PASS | Implosion values use the P V denominator and stay out of the impact views | [('IMPLOSION-GLASS', 'P V'), ('IMPLOSION-METAL', 'P V')] |
| K05 | PASS | Recomputed from the far-field curve, the 10 m point (geometric mean H11N/H11S, slope 2, mid energy, KRAKEN+RAM, tau 10 s) equals step2_summary anchor_eta | recomputed 0.00225923; anchor 0.00225923; rows 2 |
| K06 | PASS | Register E02/E01 ridge ratio is about 2.0 at 2, 10 and 30 m (same KRAKEN+RAM chain) | ratios [1.963, 1.96, 1.997] |
| K10 | PASS | Module-chain view holds no model-error curve (E02) and no superseded curve | 0 wrong rows |
| K11 | REVIEW | Coupling curve rows above 1 (more acoustic energy than kinetic energy: physically impossible) - listed; such parameter combinations are ruled out by the data | 1420 of 10260 rows: E01_far_field_9oct z=2 m slope 4: 167 rows, tau 0.455-10 s, max 6.61; E01_far_field_H11 z=2 m slope 4: 572 rows, tau 0.455-10 s, max 6.85; E02_near_field_cabled z=2 m slope 2: 142 rows, tau 0.1-10 s, max 1.8e+03; E02_near_field_cabled z=2 m slope 4: 278 rows, tau 0.1-10 s, max 1. |
| K07 | PASS | Coupling inputs match MANIFEST.tsv SHA-256 | [('coupling-prior-range.csv', True), ('coupling-evidence-register.csv', True), ('impact-source-parameters.csv', True), ('metz-nearfield-eta.csv', True), ('coupling-structure-proposal-2026-10-24.md', True)] |
| K08 | PASS | F-35A evidence items share one independence group and only E01 is the likelihood term | E01: LIKELIHOOD TERM (the primary calibration; E02: MODEL-ERROR MEASURE (inflates sigma_mode; E03: LIKELIHOOD TERM on S (spectral family we; E04: CONSTRAINT on tau family for R1 (source-; E05: CONSISTENCY CHECK of the forward model ( |
| K09 | REVIEW | Text that limits or discounts a source, listed for Pete (label rule 22 Oct 2026); nothing is excluded by it | coupling_value.read_in_primary_as_written [LESLIE1964]: 'no legitimate copy'; cp_impact_source_parameters.copy_location [ARA San Juan loss]: 'not held'; cp_impact_source_parameters.copy_location [Arons 1954 relation]: 'not held'; cp_impact_source_parameters.copy_location [Chapman 1985/1988; Gaspin & |
