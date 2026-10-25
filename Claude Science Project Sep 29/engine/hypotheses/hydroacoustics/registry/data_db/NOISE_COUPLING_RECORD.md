# Noise and acoustic coupling: generated record

Generated from `hydro_data.sqlite` by `build_noise_coupling.py` on 2026-10-25T01:12:49Z. Do not edit by hand; rebuild instead.

**Rules.** Every value carries its definition, unit, source file and SHA-256. Coupling values are used only with the propagation chain of their definition class (views `v_module_chain`, `v_arons_screen`, `v_envelope`, `v_cross_check`, `v_coupling_curve_module`; rules from the coupling thread's `validate_coupling_tables.py`, run in every build). The F-35A values are points on one (coupling, source depth, spectrum) curve from one recording; no ruling is needed (Pete, 24 Oct 2026). Status and defects stay in the registry.

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

**calibration: F-35A 9 Apr 2019; 1 s moving RMS; median over the record; unit dB re 1 uPa; role: background at the F-35A calibration receivers (raw)**

| site_id   |   4-40 Hz |
|:----------|----------:|
| H11N      |      92.8 |
| H11S      |      91.2 |

## 2. Conditions that affect noise

| site_id          | context                  | condition                                                                                      | effect                                                                                        | source                                                 |
|:-----------------|:-------------------------|:-----------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------|:-------------------------------------------------------|
| H08S             | MH370 8 Mar 2014         | periodic airgun shots (about every 10 s) in the Kadri Fig. 9 panels; 110 shots 01:00-01:19 UTC | masking and false alarms; a shot coincidence is a label, not an exclusion (Pete, 23 Oct 2026) | kadri_fig9_noise/summary.json; h08s_template_shots.csv |
| OHASISBIO (all)  | MH370 8 Mar 2014         | powerful seismic shots from an exploration survey obscure most of the data that day            | raised noise and masking at the OHASISBIO sites; no calibrated level extracted yet            | Royer 2016, LDO-201608, p. 3                           |
| IMOS (all)       | MH370 8 Mar 2014         | 8 Hz hardware high-pass corner (header LF); 2-5 Hz band below it                               | 2-5 Hz levels are not ambient-noise estimates                                                 | record headers; imos1d                                 |
| H01W, H08S, H08N | IMS 2003 Blackman cruise | 2003 levels, not 8 Mar 2014                                                                    | use as background estimate with that label; Kadri Fig. 9 gives an 8 Mar 2014 sensitivity      | note.ims_noise_blackman                                |

## 3. Coupling definition classes and the propagation chains they may be used with

| definition_class   | allowed_chains                             |
|:-------------------|:-------------------------------------------|
| D1                 | MODULE_KRAKEN_ONLY, MODULE_KRAKEN_RAM      |
| D2                 | ARONS_1954                                 |
| D3                 | MODULE_KRAKEN_RAM, NEAR_FIELD_SOURCE_MODEL |
| D4                 | MODULE_KRAKEN_ONLY, MODULE_KRAKEN_RAM      |
| S1                 | SEISMIC_LAND                               |

## 4. Coupling values (coupling thread package, 25 Oct 2026)

| value_id   | evidence_id   | quantity                                                                      |      value |   value_low |   value_high | definition_class   | chain                   | role                      | status                    |
|:-----------|:--------------|:------------------------------------------------------------------------------|-----------:|------------:|-------------:|:-------------------|:------------------------|:--------------------------|:--------------------------|
| CV01       | E01           | eta_rad at z_eff 2 m                                                          |   0.054    |   nan       |   nan        | D1                 | MODULE_KRAKEN_RAM       | LIKELIHOOD_RIDGE_POINT    | EVIDENCE                  |
| CV02       | E01           | eta_rad at z_eff 10 m                                                         |   0.00226  |   nan       |   nan        | D1                 | MODULE_KRAKEN_RAM       | LIKELIHOOD_RIDGE_POINT    | EVIDENCE                  |
| CV03       | E01           | eta_rad at z_eff 30 m                                                         |   0.00034  |   nan       |   nan        | D1                 | MODULE_KRAKEN_RAM       | LIKELIHOOD_RIDGE_POINT    | EVIDENCE                  |
| CV04       | E01           | eta_rad at z_eff 2 m (9 Oct calibration)                                      |   0.02     |   nan       |   nan        | D1                 | MODULE_KRAKEN_ONLY      | SUPERSEDED                | EVIDENCE_SUPERSEDED       |
| CV05       | E01           | eta_rad at z_eff 10 m (9 Oct calibration)                                     |   0.0008   |   nan       |   nan        | D1                 | MODULE_KRAKEN_ONLY      | SUPERSEDED                | EVIDENCE_SUPERSEDED       |
| CV06       | E01           | eta_rad at z_eff 30 m (9 Oct calibration)                                     |   0.0001   |   nan       |   nan        | D1                 | MODULE_KRAKEN_ONLY      | SUPERSEDED                | EVIDENCE_SUPERSEDED       |
| CV07       | E02           | eta_rad at z_eff 2 m, near field                                              |   0.106    |   nan       |   nan        | D1                 | MODULE_KRAKEN_ONLY      | MODEL_ERROR_MEASURE       | EVIDENCE                  |
| CV08       | E02           | eta_rad at z_eff 10 m, near field                                             |   0.00443  |   nan       |   nan        | D1                 | MODULE_KRAKEN_ONLY      | MODEL_ERROR_MEASURE       | EVIDENCE                  |
| CV09       | E02           | eta_rad at z_eff 30 m, near field                                             |   0.000679 |   nan       |   nan        | D1                 | MODULE_KRAKEN_ONLY      | MODEL_ERROR_MEASURE       | EVIDENCE                  |
| CV10       | E01           | eta_rad at z_eff 2 m, far field, KRAKEN-only (like-for-like with near field)  |   0.025    |   nan       |   nan        | D1                 | MODULE_KRAKEN_ONLY      | MODEL_ERROR_MEASURE       | EVIDENCE                  |
| CV11       | E01           | eta_rad at z_eff 10 m, far field, KRAKEN-only (like-for-like with near field) |   0.001    |   nan       |   nan        | D1                 | MODULE_KRAKEN_ONLY      | MODEL_ERROR_MEASURE       | EVIDENCE                  |
| CV12       | E01           | eta_rad at z_eff 30 m, far field, KRAKEN-only (like-for-like with near field) |   0.00016  |   nan       |   nan        | D1                 | MODULE_KRAKEN_ONLY      | MODEL_ERROR_MEASURE       | EVIDENCE                  |
| CV13       | E01           | in-band eta at z_eff 10 m                                                     |   0.0012   |     0.00088 |     0.0015   | D4                 | MODULE_KRAKEN_RAM       | CONSISTENCY_CHECK         | EVIDENCE                  |
| CV14       | E05           | Arons-equivalent coupling (Brown)                                             |   0.0001   |   nan       |   nan        | D2                 | ARONS_1954              | CONSISTENCY_CHECK         | EVIDENCE                  |
| CV15       | E05           | Arons-equivalent coupling, reproduced                                         |   0.000208 |     0.00017 |     0.000267 | D2                 | ARONS_1954              | CONSISTENCY_CHECK         | EVIDENCE                  |
| CV16       | E06           | near-field acoustic fraction, bullet entry                                    |   0.01     |     0.001   |     0.01     | D3                 | NEAR_FIELD_SOURCE_MODEL | ENVELOPE_AND_SCALING      | EVIDENCE                  |
| CV17       | E07           | pile-driving energy conversion                                                | nan        |     0.0012  |     0.021    | D3                 | NEAR_FIELD_SOURCE_MODEL | ENVELOPE_AND_SCALING      | EVIDENCE                  |
| CV18       | E08           | raindrop radiated fraction                                                    |   1e-05    |   nan       |   nan        | D3                 | NEAR_FIELD_SOURCE_MODEL | ENVELOPE_AND_SCALING      | EVIDENCE                  |
| CV19       | E09           | iceberg block impact source fraction                                          |   8e-07    |     3.2e-07 |     1.3e-06  | D3                 | NEAR_FIELD_SOURCE_MODEL | ENVELOPE_AND_SCALING      | EVIDENCE                  |
| CV20       | E09           | iceberg block (cylindrical spreading)                                         |   5.16e-10 |   nan       |   nan        | D3                 | NEAR_FIELD_SOURCE_MODEL | SUPERSEDED                | EVIDENCE_SUPERSEDED       |
| CV21       | E12           | Arons-relative coupling, known-yield shallow charges                          | nan        |     0.0004  |     1.7      | D2                 | ARONS_1954              | MODEL_ERROR_MEASURE       | EVIDENCE                  |
| CV22       | E14           | implosion radiated fraction, glass sphere                                     |   0.18     |   nan       |   nan        | D3                 | MODULE_KRAKEN_RAM       | SEPARATE_SOURCE_PRIOR     | EVIDENCE                  |
| CV23       | E14           | implosion radiated fraction, ductile metal shells                             | nan        |     0.002   |     0.006    | D3                 | MODULE_KRAKEN_RAM       | SEPARATE_SOURCE_PRIOR     | EVIDENCE                  |
| CV24       | E15           | seismic coupling S1, Swissair 111                                             | nan        |     5e-07   |     0.00034  | S1                 | SEISMIC_LAND            | CROSS_CHECK               | EVIDENCE                  |
| CV25       | E17           | airburst in-channel equivalent                                                | nan        |     1e-05   |     0.0001   | D2                 | ARONS_1954              | EXCLUDED_FROM_CALIBRATION | EXCLUDED_FROM_CALIBRATION |

### 4a. Impact families (status PROPOSED_STRUCTURE: awaiting Pete's approval of the structure, not of a number)

| family_id   | name                       | status             |
|:------------|:---------------------------|:-------------------|
| R1          | steep high-speed entry     | PROPOSED_STRUCTURE |
| R2          | shallow uncontrolled entry | PROPOSED_STRUCTURE |
| R3          | controlled ditching        | PROPOSED_STRUCTURE |
| I           | implosions while sinking   | PROPOSED_STRUCTURE |
| X           | in-flight break-up         | PROPOSED_STRUCTURE |

### 4b. Historical aircraft impact cases

| case_id   | event                              | family                                      | raw_ims_open                                                 | role                                                         |
|:----------|:-----------------------------------|:--------------------------------------------|:-------------------------------------------------------------|:-------------------------------------------------------------|
| AC01      | JASDF F-35A, off Misawa            | R1                                          | YES - all 6 elements H11N1-3, H11S1-3 (EarthScope, downloade | R1 CALIBRATION (likelihood term). Raw data now replace the d |
| AC02      | Air France 447                     | R2 (flat, high sink rate)                   | NO (pre-Dec-2014; HTTP 204)                                  | COMPARISON SET (Kadri claim); possible R2 test if raw data e |
| AC03      | Yemenia 626                        | R1/R2 boundary (moderate speed, nose first) | NO (pre-Dec-2014)                                            | COMPARISON SET                                               |
| AC04      | Sriwijaya Air 182                  | R1                                          | YES - H08S1 (probe); H01W1 no data at probe time             | COMPARISON SET + REPLICATION TARGET (same raw data Kadri use |
| AC05      | Transair 810 (ditching)            | R3                                          | YES - H11N1, H11S1 (probe)                                   | CANDIDATE R3 CALIBRATION (only ditching with open raw IMS da |
| AC06      | Lion Air 904 (undershoot)          | R3                                          | NO (pre-Dec-2014)                                            | COMPARISON SET                                               |
| AC07      | AB Aviation 1103                   | unknown regime; very low energy             | YES - H08S1 (probe); H08N1 no data                           | COMPARISON SET; likely a negative control                    |
| AC08      | AirAsia 8501                       | R2                                          | YES - H01W1 and H08S1 on 27 Dec 23:50; H08S1 on 28 Dec 08:00 | COMPARISON SET + REPLICATION TARGET; weak R2 test (shallow s |
| AC09      | Asiana 991 (B747F, in-flight fire) | X (in-flight break-up)                      | NO (pre-Dec-2014)                                            | COMPARISON SET (break-up regime is not an MH370 end-of-fligh |
| AC10      | Lion Air 610                       | R1                                          | YES - H08S1 (probe)                                          | NEW TEST CASE (not used by Kadri): weak R1 test, shallow sea |
| AC11      | Swissair 111                       | R1 (moderate speed, steep)                  | NO (no IMS hydrophones in 1998)                              | SEISMIC CROSS-CHECK (class S1 5e-7 to 3.4e-4): energy scale  |
| AC12      | TWA 800                            | X                                           | not applicable / not probed                                  | SEISMIC NULL (limited power); no coupling information        |
| AC13      | EgyptAir 990                       | R1                                          | not applicable / not probed                                  | SEISMIC NULL (limited power); no coupling information        |
| AC14      | Alaska 261                         | R1                                          | not applicable / not probed                                  | SEISMIC NULL (limited power); no coupling information        |
| AC15      | Adam Air 574                       | R1                                          | not applicable / not probed                                  | SEISMIC NULL (limited power); no coupling information        |
| AC16      | Ethiopian 409                      | R1                                          | not applicable / not probed                                  | SEISMIC NULL (limited power); no coupling information        |
| AC17      | Flash Airlines 604                 | R1                                          | not applicable / not probed                                  | SEISMIC NULL (limited power); no coupling information        |
| AC18      | EgyptAir 804                       | R1 (uncertain)                              | not applicable / not probed                                  | SEISMIC NULL (limited power); no coupling information        |

### 4c. Reference events (non-aircraft)

| ref_id   | event                                                                                             | used_for                                                     | raw_ims_open                             |
|:---------|:--------------------------------------------------------------------------------------------------|:-------------------------------------------------------------|:-----------------------------------------|
| RE01     | ARA San Juan loss event                                                                           | implosion branch I; propagation                              | YES - H10N1, H10S1 (probe)               |
| RE02     | San Juan calibration charge                                                                       | propagation (known energy)                                   | YES - H10N1, H10S1 (probe)               |
| RE03     | US Navy full ship shock trial 2016 (5 shots)                                                      | propagation (known energy)                                   | YES - H10N1 on 2016-06-10 (probe)        |
| RE04     | US Navy full ship shock trial 2021 (3 shots)                                                      | propagation (known energy)                                   | YES - H10N1 on 2021-06-18 (probe)        |
| RE05     | 39 kg TNT charges at H11N/H03N (Prior et al.)                                                     | propagation (known energy)                                   | NO (H11N1 2008: HTTP 204)                |
| RE06     | Blackman 2001 airgun sites air7/8/9 and 2003 SUS A1-A11, glass spheres                            | propagation TL validation; implosion (spheres)               | NO (pre-Dec-2014)                        |
| RE07     | Royer 2016 located events (20), 7-8 Mar 2014                                                      | timing and false-alarm calibration on the MH370 night        | NO raw IMS (2014); OHASISBIO request-onl |
| RE08     | Catalogued earthquakes 6-10 Mar 2014 (T-phases)                                                   | timing (1.48 km/s rule), island-station sensitivity          | island seismometers open; IMS 2014 not o |
| RE09     | Open IMS March background 2015-2019                                                               | noise and false-alarm background (proxy for 2014)            | YES (downloaded 00-04 UTC blocks)        |
| RE10     | Bullet water entry (Leslie 1964)                                                                  | eta_rad scaling (upper)                                      |                                          |
| RE11     | Pile driving                                                                                      | eta_rad envelope (upper)                                     |                                          |
| RE12     | Raindrops (Liu 2021)                                                                              | eta_rad scaling (lower)                                      |                                          |
| RE13     | Iceberg block impacts (Glowacki & Deane 2020)                                                     | eta_rad scaling (lower); closest in size to an airliner      |                                          |
| RE14     | Implosions: glass spheres (Orr & Schoenberg 1976), metal shells (Shukla 2018), Harben 2000 flasks | implosion branch I                                           |                                          |
| RE15     | Bolides / fireballs (Brown 2026: 30 events)                                                       | excluded from impact eta (different mechanism); IMS detectio | post-Dec-2014 cases open on EarthScope ( |
| RE16     | Titan (2023), USS Scorpion (1968), Kursk (2000)                                                   | implosion branch I (qualitative)                             | no public quantitative acoustic data     |

### 4d. Received levels measured from raw records

| obs_id   | evidence_id   | station   |   peak_1sRMS_Pa |   median_1sRMS_Pa |   snr_dB |   exposure_Pa2s_30s | band_Hz   | date       |
|:---------|:--------------|:----------|----------------:|------------------:|---------:|--------------------:|:----------|:-----------|
| OB01     | E01           | H11N1     |           0.358 |            0.0435 |     18.3 |               0.237 | 4-40      | 2019-04-09 |
| OB02     | E01           | H11N2     |           0.308 |            0.0454 |     16.6 |               0.262 | 4-40      | 2019-04-09 |
| OB03     | E01           | H11N3     |           0.375 |            0.0437 |     18.7 |               0.28  | 4-40      | 2019-04-09 |
| OB04     | E01           | H11S1     |           0.274 |            0.0362 |     17.6 |               0.119 | 4-40      | 2019-04-09 |
| OB05     | E01           | H11S2     |           0.198 |            0.0337 |     15.4 |               0.069 | 4-40      | 2019-04-09 |
| OB06     | E01           | H11S3     |           0.203 |            0.036  |     15   |               0.068 | 4-40      | 2019-04-09 |

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

| evidence_id   | evidence                                                                                                                                                                             | how_it_is_used                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | independence_group               |
|:--------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------|
| E01           | F-35A far field, Wake Island H11N/H11S (raw IMS records open at EarthScope, all 6 elements; digitised Metz 2023 Fig 3 agrees)                                                        | LIKELIHOOD TERM (the primary calibration)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | G1: F-35A recording              |
| E02           | F-35A near field, cabled seabed stations DSOH/KSP1-3 (Metz 2023 Fig 2, digitised)                                                                                                    | MODEL-ERROR MEASURE (inflates sigma_model; not an independent eta estimate)                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | G1: F-35A recording (same event) |
| E03           | F-35A spectral shape, near and far (Metz 2023)                                                                                                                                       | LIKELIHOOD TERM on S (spectral family weights)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | G1: F-35A recording              |
| E04           | F-35A source duration bound (Metz 2023)                                                                                                                                              | CONSTRAINT on tau family for R1 (source-model calibration on a different aircraft; not fed back to end of flight)                                                                                                                                                                                                                                                                                                                                                                                                                               | G1                               |
| E05           | Brown et al. 2026 Arons-equivalent coupling (Icarus 455:117106)                                                                                                                      | CONSISTENCY CHECK of the forward model (the model must reproduce D2 on the same path); NOT an independent eta - same recording as E01                                                                                                                                                                                                                                                                                                                                                                                                           | G1: F-35A recording              |
| E06           | Leslie 1964, bullet water entry (JASA 36:1138; abstract only)                                                                                                                        | ENVELOPE (upper plausibility bound) and SCALING point                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | G2: mechanism analogs            |
| E07           | Pile driving energy conversion (review)                                                                                                                                              | ENVELOPE (upper)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | G2                               |
| E08           | Raindrop impacts (Liu et al. 2021)                                                                                                                                                   | ENVELOPE (lower) and SCALING point                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | G2                               |
| E09           | Iceberg block impacts (Glowacki & Deane 2020)                                                                                                                                        | ENVELOPE (lower) and SCALING point                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | G2                               |
| E10           | Water-entry physics: slam vs cavity/bubble energy (Li et al. 2021; Leslie; Truscott 2014; Minnaert)                                                                                  | PRIOR STRUCTURE (sets z_eff prior and the low-frequency spectral branch)                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | G3: physics                      |
| E11           | Surface image (Lloyd's mirror) for a near-surface source                                                                                                                             | BUILT INTO FORWARD MODEL (not a datum)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | G3                               |
| E12           | Known-yield explosions at IMS (FSST 2016/2021, 39 kg charges, San Juan calibration charge, SUS) - raw IMS records open for the San Juan charge (H10N/H10S) and FSST 2016/2021 (H10N) | PROPAGATION VALIDATION -> sigma_model; NOT eta                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | G4: propagation                  |
| E13           | Blackman 2001/2003 airgun, SUS and sphere sources at H01/H08                                                                                                                         | PROPAGATION VALIDATION -> sigma_model (frequency-dependent)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | G4                               |
| E14           | Implosions (Orr & Schoenberg 1976 glass ~18 %; Shukla et al. 2018 metal 0.2-0.6 %)                                                                                                   | SEPARATE SOURCE PRIOR                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | G5: implosions                   |
| E15           | Swissair 111 land seismic record (CN.LMN 173 km; MN 0.57)                                                                                                                            | CROSS-CHECK ONLY (different physics; not eta)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | G6: seismic                      |
| E16           | Kadri 2024 claimed aircraft detections (AF447, Yemenia, Sriwijaya, Transair, Lion Air, AirAsia, Asiana)                                                                              | COMPARISON SET: not used to set the coupling priors, because the impact energies are assumed and our checks raised timing and SNR questions. Kept for method replication and reconciliation: for each case, compare Kadri's claim with our prediction and, where raw IMS data are open (Sriwijaya 182, Transair 810, AirAsia 8501, AB Aviation 1103, F-35A), re-analyse the same data. Our timing checks used an exploratory straight-path, one-speed model and our amplitudes come from digitised figures, so a disagreement may be our error. | G7                               |
| E17           | Airbursts and fireballs (Clarke 1996; Kamegai & White 1994; Brown 2026)                                                                                                              | EXCLUDED                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | G8                               |

## 7. Checks

| check | result | description | detail |
|---|---|---|---|
| N01 | PASS | Every noise value uses a declared quantity and its unit | 0 mismatches |
| N02 | PASS | Every noise band has lower edge < upper edge | 0 bad bands |
| N03 | PASS | Noise PSD values inside 40-140 dB re 1 uPa^2/Hz (plausibility) | 0 outside |
| N04 | PASS | IMOS band statistics in the database equal noise_bands.csv (round trip) | 245 values, 0 mismatches |
| N05 | PASS | Blackman medians 5-40 Hz inside the pre-registered 55-105 dB gate | 0 outside |
| N06 | PASS | Every stage-2 input file still matches its SHA-256 | 24 files, 0 changed |
| N07 | PASS | Every IMOS per-record noise row links to a raw record in table segment | 153 records, 0 unmatched |
| N08 | PASS | Every noise row names a site in table site | unknown: [] |
| K01 | PASS | Coupling package validator (validate_coupling_tables.py, coupling thread) passes | PASS coupling_value.definition_class present; PASS coupling_value.propagation_chain_required present; PASS coupling_value.status present; PASS coupling_value.role present; PASS coupling_value.independence_group present; PASS coupling_value.evidence_id present; PASS definition class paired only with  |
| K02 | PASS | Module-chain view holds no Arons-equivalent (D2) or land-seismic (S1) value | 0 wrong rows |
| K03 | PASS | Arons view holds only D2 values | 0 wrong rows |
| K04 | PASS | Every coupling-curve row uses an allowed (definition class, chain) pair | [] |
| K05 | PASS | The 10 m F-35A ridge point recomputed from the curve (geometric mean H11N/H11S, slope 2, mid energy, KRAKEN+RAM, tau 10 s) equals step2_summary and the package value | recomputed 0.00225923; step2_summary 0.00225923; package [0.00226] |
| K06 | PASS | Evidence E02/E01 ridge ratio is about 2.0 at 2, 10 and 30 m (same KRAKEN+RAM chain) | ratios [1.963, 1.96, 1.997] |
| K10 | PASS | Module curve view holds no model-error curve (E02) and no superseded curve | 0 wrong rows |
| K11 | REVIEW | Coupling curve rows above 1 (more acoustic energy than kinetic energy: physically impossible) - listed; such parameter combinations are ruled out by the data | 1420 of 10260 rows: E01_far_field_9oct z=2 m slope 4: 167 rows, tau 0.455-10 s, max 6.61; E01_far_field_H11 z=2 m slope 4: 572 rows, tau 0.455-10 s, max 6.85; E02_near_field_cabled z=2 m slope 2: 142 rows, tau 0.1-10 s, max 1.8e+03; E02_near_field_cabled z=2 m slope 4: 278 rows, tau 0.1-10 s, max 1. |
| K12 | PASS | Module-chain view rows whose role is SUPERSEDED or EXCLUDED while status is EVIDENCE - listed for the coupling thread (package data, not edited here) | none |
| K07 | PASS | Coupling inputs match MANIFEST.tsv SHA-256 | [('db_coupling_evidence.csv', True), ('db_coupling_value.csv', True), ('db_coupling_family.csv', True), ('db_family_element_evidence.csv', True), ('db_impact_case.csv', True), ('db_reference_event.csv', True), ('db_received_observation.csv', True), ('db_data_availability_probe.csv', True), ('validat |
| N09 | PASS | Pa to dB conversion of the raw H11 background round-trips (20 log10(p / 1 uPa)) | 0.0435 Pa -> 92.770 dB re 1 uPa |
| K09 | REVIEW | Text that limits or discounts a source, listed for Pete (label rule 22 Oct 2026); nothing is excluded by it | cp_impact_source_parameters.copy_location [ARA San Juan loss]: 'not held'; cp_impact_source_parameters.copy_location [Arons 1954 relation]: 'not held'; cp_impact_source_parameters.copy_location [Chapman 1985/1988; Gaspin & Shuler 1971; Gaspin et al. 1979]: 'not held'; cp_impact_source_parameters.cop |
