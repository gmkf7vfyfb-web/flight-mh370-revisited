# hydro_data.sqlite — hydroacoustic data held by the project (raw and digitised data, background noise, acoustic coupling)

One SQLite file that lists every hydroacoustic **data** item the project holds: raw IMOS seabed-logger records and the values digitised from publications (Kadri, Royer, CMST, Blackman, Metz, Brown, Nielsen, Vergoz, Duncan & Dall'Osto) (stage 1), and every background-noise level and acoustic-coupling value with its definition, unit, source file and SHA-256 (stage 2, from 25 Oct 2026). Analysis **results** (detections, likelihoods, detectability) are not in this file. They stay in the module registry `registry/REGISTRY.json`, and every row here carries the registry entry id that covers its files.

Stage 1 first built 2026-10-23T21:00:42Z (module 131e520). Full rebuild of all stages on 2026-10-26 with `rebuild_all.sh` (module 53db637 plus the new stage scripts; claude-science-sep29 114bebc for the imports). Schema `hydro-data-db v1`; stage 3 `imports v1`; stage 4 `noise-fixes v1`.

## Contents

| table | rows | what it holds |
|---|---|---|
| site | 23 | one row per station or logger: name, network, position, depths, position source |
| sensor | 21 | IMS hydrophone elements (FDSN EarthScope, 2014 epoch) |
| dataset | 52 | one row per data product: form, context, UTC span, continuity, duty fraction, band, band basis, sample rate, path, registry id, caveat |
| segment | 4654 | one row per file or panel: UTC start/end, logger time, clock error, sample rate, samples, band, role, file path, bytes, SHA-256 and check result, `same_file_in` |
| pick | 1397 | point times: Royer Table 5 and figure marks, Kadri 2024 Table 1, Kadri 2019 Table 3, CMST Figs 5 and 7 detections, airgun shots |
| event | 20 | Royer 2016 located events (origin, position, errors) |
| attribute / attribute_key | 250 / 33 | open-ended properties (sensitivity, clock sets and drift, gain file, filters, author processing, timing and amplitude caveats); add new keys here |
| imported_table + `dg_*` tables | 142 | every digitised and module data CSV imported verbatim, with source path, SHA-256 and header comments |
| file_ref | 276 | every non-CSV digitised file (npz grids, rasters, json, xml) with SHA-256 and dataset link |
| check_log | 182 | build checks with result and detail (stage 1 C, arc L, stage 2 N/K, stage 3 I, stage 4 F) |

Views: `v_dataset_summary`, `v_site_holdings`, `v_picks_by_site`, `v_arc_los_by_location`. Table `arc_path`: see the line-of-sight section.

Datasets by form: digitised_trace 13, raw_waveform 9, digitised_table 9, digitised_spectrogram 7, raster_copy 5, digitised_picks 5, digitised_band_series 2, instrument_metadata 1, derived_from_digitised 1.
Datasets by context: MH370 7-8 Mar 2014 30, calibration cases 15, background for MH370 7-8 Mar 2014 3, all 2, instrument calibration 1, MH370 7-8 Mar 2014 and calibration cases 1.

## Conventions

- All `*_utc` columns are ISO 8601 UTC strings (`YYYY-MM-DDTHH:MM:SS.sssZ`).
- IMOS times: true UTC = logger time − e(t). e(t) is linear between 'system clock set 1' and 'set 2' in the Curtin metadata (convention A; the module clock test reproduces the CMST 01:33:44 event to −0.24 s). The record start is the header 'First Data' time. The file-name hex time is 16 s earlier (check C08); it is not used.
- `continuity`: continuous / duty-cycled / separate windows / point picks / no time axis. `duty_fraction` = covered time ÷ span; overlapping panels are counted once.
- `band_basis` gives the origin of the band: logger hardware filter, author's stated processing, or the frequency axis of the published plot.
- Path roots: `INPUTS:` = `~/Downloads/mh370-inputs/hydroacoustics`; `MOD:` = `Claude Science Project Sep 29/engine/hypotheses/hydroacoustics` on the module branch.

## 7th-arc line of sight (added 23 Oct 2026)

- Table `arc_path` (3856 rows): one row per site and 7th-arc point (0.1° latitude steps from 20° S to the arc's southern end at 43.9° S) for 16 instruments. Columns: path length, receiver depth, km over land, km blocking, km shallower than 1,000 m, km shallower than the hydrophone, shallowest obstacle (depth, position, distance from arc, name) and `class` (clear / ridge (partial) / large attenuation / blocked).
- Site attributes `arc_line_of_sight` (summary text), `arc_blocked_lat`, `arc_large_attenuation_lat`, `arc_ridge_partial_lat`, `arc_receiver_depth_m`.
- 8 March 2014 inventory attributes: `recording_8mar2014` (with source), `station_location` (co-located instruments counted once), `data_held` (raw / digitised / none). Not recording on 8 Mar 2014: HA04 Crozet (installed Dec 2016, certified Jun 2017); IMOS Kangaroo Island, Tuncurry and Pilbara (no 8 Mar 2014 files in the public archive).
- View `v_arc_los_by_location` joins `arc_path` with the inventory.
- Method: 7th arc = small circle, centre 0.570° N 64.252° E, radius 44.501°. WGS84 geodesics sampled every ~1 km on GEBCO 2026 (15 arc-s). Blocked: land, or water shallower than min(receiver depth, 200 m), more than 20 km from the receiver. Large attenuation: >= 10 km shallower than 1,000 m, more than 100 km from the receiver. Ridge above hydrophone depth: deep receivers only, >= 10 km shallower than the hydrophone. This is a geometric screen, not a transmission-loss result.

## Noise and coupling (stage 2, added 25 Oct 2026)

Pete, 24-25 Oct 2026: bring all hydroacoustic noise and acoustic-coupling information into this one database, to stop errors from scattered files ("Bring it into one database. The F35 ruling was a red herring"). Built by `build_noise_coupling.py` (stage 2; it re-creates only its own tables). Readable summary: `NOISE_COUPLING_RECORD.md`, generated by the same run (never edit it by hand).

**Noise (this database's design)**

| table / view | what it holds |
|---|---|
| quantity_def | allowed noise quantities and their fixed units: band-mean PSD (dB re 1 uPa^2/Hz), RMS level (dB re 1 uPa), level spread (dB) |
| noise_estimate | one row per noise value: site, context (MH370 8 Mar 2014 / IMS 2003 Blackman cruise / F-35A calibration 9 Apr 2019), period, band, quantity, statistic, value, original value, unit and field, averaging, n, method (measured from raw / traced / digitised), source, input file and SHA-256, registry entry and status, role, caveat |
| noise_condition | conditions that change noise or masking: H08S airgun shots, OHASISBIO seismic survey on 8 Mar 2014, IMOS 8 Hz high-pass, 2003 levels against 2014 |
| v_noise_summary, v_noise_8mar2014 | noise statistics with site names and units |

Sources: IMOS raw records on the event day (`results-data/imos1d`, per record and per logger and band), IMS levels traced from Blackman 2004 App. B (2003; primary for IMS), Kadri 2024 Fig. 9 spectrogram backgrounds (8 Mar 2014; sensitivity), Metz 2023 Fig. 3 envelope backgrounds and the raw H11 records (F-35A calibration receivers).

**Coupling (the coupling thread's package, imported unchanged)**

The coupling thread (session c764a583) owns the coupling content. Its package of 25 Oct 2026 (`results/hydroacoustics/source-survey-2026-10-23/coupling-db-package-2026-10-25/` on `claude-science-sep29`, commit 7e5859d) is copied to `inputs/coupling/` with `MANIFEST.tsv` (file, origin, SHA-256). Its validator `validate_coupling_tables.py` runs in every build (check K01); its class-to-chain rules fill `coupling_definition`. A new package version means a new manifest and a rebuild; this database is the one writer.

| table / view | what it holds |
|---|---|
| coupling_definition | definition class (D1 model-inverted, D2 Arons-equivalent, D3 near-field, D4 in-band, S1 land seismic) and each propagation chain it may be used with |
| coupling_value | 25 coupling values with evidence link, definition class, required chain, independence group, role and status |
| coupling_evidence | 17 evidence items: what each measures, its observation operator, how it is used, independence group, status |
| coupling_family, coupling_family_element_evidence | impact families R1, R2, R3, I, X (PROPOSED_STRUCTURE) and the evidence that informs each element |
| impact_case, reference_event | 18 historical aircraft impacts and 16 non-aircraft reference events, with data held and raw IMS availability |
| received_observation, data_availability_probe | levels measured from raw records (F-35A at H11) and the EarthScope availability probes |
| coupling_curve | this database's part: the F-35A coupling curves over source depth, spectrum, duration and energy (E01 far field, likelihood; E02 near field, model error; 9 Oct calibration, superseded) |
| cp_impact_source_parameters, cp_coupling_prior_range_2026_10_23 | survey tables imported verbatim (the prior-range table is superseded by the package) |
| v_module_chain, v_arons_screen, v_envelope, v_cross_check | the package's per-chain views |
| v_coupling_curve_module | F-35A likelihood curves valid with the module chain only |

Rules (each is a build check; N01-N09, K01-K12):
- A noise value has one declared quantity and its unit; the original value, unit and field are kept; IMOS statistics round-trip exactly to the module file; Pa-to-dB conversions round-trip.
- A coupling value is used only with the propagation chain of its definition class. The views make the wrong pairing impossible: the module-chain view never returns an Arons-equivalent or land-seismic value.
- The F-35A values are points on one (coupling, source depth, spectrum) curve from one recording; no ruling is needed and no value is an "anchor". Brown's ~1e-4 is the same recording read through the Arons relation (consistency check, not independent evidence).
- Text that limits or discounts a source ("not held", "paywalled", ...) is listed for Pete in check K09 (label rule, 22 Oct 2026); nothing is excluded by it.
- Coupling-curve rows above 1 are physically impossible; check K11 lists them so those parameter combinations are seen as ruled out by the data.
- Check K12 guards the module-chain view: it fails to REVIEW if a row there has role SUPERSEDED or EXCLUDED (status EVIDENCE_SUPERSEDED rows are already outside the view).

```sql
-- 8 March 2014 median background between 8 and 22 Hz at every site
SELECT site_id, band_label, statistic, value, unit, method FROM v_noise_8mar2014 WHERE band_lo_hz >= 8 AND band_hi_hz <= 22 AND statistic = 'median';
-- coupling values that may be used with the module propagation chain, current role only
SELECT value_id, quantity, value, definition_class, propagation_chain_required, role FROM v_module_chain WHERE role != 'SUPERSEDED';
```

Run order (since 26 Oct 2026; `rebuild_all.sh` runs it): `build_hydro_data_db.py` → `build_noise_coupling.py --db hydro_data.sqlite --mod <module root> --coupling inputs/coupling --record NOISE_COUPLING_RECORD.md` → `build_imports.py --db hydro_data.sqlite --mod <module root> --work <'Claude Science Project Sep 29' on claude-science-sep29>` → `build_noise_fixes.py --db hydro_data.sqlite --mod <module root>` → `arc_line_of_sight.py --db hydro_data.sqlite --gebco <gebco grid dir>` → `arc_station_count.py --db hydro_data.sqlite --out arc_los_station_count` → VACUUM; then `make_sites_map.py` / `arc_recording_opportunity.py` (charts; they read the database only).

```sql
-- stations with clear line of sight to the arc point at 37.0 S
SELECT location, data_held FROM v_arc_los_by_location WHERE arc_lat = -37.0 AND class = 'clear' GROUP BY location;
```

## Example queries

```sql
-- what is held at one site
SELECT dataset_id, data_form, t_start_utc, t_end_utc, continuity, band_lo_hz, band_hi_hz, caveat
FROM v_dataset_summary WHERE site_id = 'H01W';
-- IMOS records that cover a given UTC instant
SELECT dataset_id, label, t_start_utc, t_end_utc, file_path FROM segment
WHERE '2014-03-08T00:52:03Z' BETWEEN t_start_utc AND t_end_utc;
-- all published picks within 60 s of a time, any site
SELECT site_id, dataset_id, kind, label, t_utc, bearing_deg FROM pick
WHERE abs(julianday(t_utc) - julianday('2014-03-08T00:52:03Z')) * 86400 <= 60;
-- properties of a logger
SELECT key, value_text, value_num, unit, evidence FROM attribute WHERE entity_id = 'IMOS3376';
```

## Adding data (from 26 Oct 2026): one block in imports.yaml, then rebuild

Pete, 26 Oct 2026: "please pull everything in and instruct all modules and threads to update the respository going forward". Every thread adds data this way. Nobody edits `hydro_data.sqlite` by hand.

1. Commit the source file (CSV or JSON) to the repository first (a result folder with `manifest.json` on `claude-science-sep29`, or the module branch).
2. Add ONE block to `imports.yaml`: `id` (imp_<name>), `path` (root `WORK:` = 'Claude Science Project Sep 29' on claude-science-sep29, or `MOD:` = module root), `branch`, `commit`, `sha256` of the file, `kind`, `table` (new table name), `units` (column → unit for every numeric column, or `auto` for name-suffix rules), `key` (columns that must be unique), `registry_id` (module registry entry that covers the file), `role`, `caveat` (copy the producer's caveat; do not add a new limiting label).
   Kinds: `table` (verbatim copy), `table_concat` (several files, same columns), `noise_percentiles` (verbatim table plus `noise_estimate` rows), `array_calibration` (JSON calibration to tables and site attributes), `coupling_package_append` (rows appended to the coupling package tables after the package validator passes on base + new rows; an update keeps the old row in `package_row_history`).
3. Rebuild: `sh rebuild_all.sh <module root> <'Claude Science Project Sep 29' folder> hydro_data.sqlite build_log.txt` (about 1 min; reads `~/Downloads/mh370-inputs/hydroacoustics/imos` and the GEBCO grid read-only). Every block gets checks I01-I09 (SHA-256 equals the manifest, rows equal the source, units declared, key unique; for coupling rows the validator passes). A FAIL stops the build.
4. Commit the database, `imports.yaml` and `build_log.txt` together; record the new SHA-256 in the registry (`in.hydro_data_db`).
5. Files that duplicate an imported table go to `not_imported` with the reason (check I09).

Stage-1 properties (`attribute` / `attribute_key`) and new stage-1 sources (`SOURCES`, dataset, segment, pick rows in `build_hydro_data_db.py`) work as before.

## Stage 3: imports of 26 Oct 2026 (build_imports.py, imports.yaml)

| block | kind | target table(s) | rows | registry entry |
|---|---|---|---|---|
| imp_ims_march_noise_percentiles | noise_percentiles | ims_march_noise_percentile | 9520 | res.next_steps_2026_10_24 |
| imp_ims_march_false_alarm_rates | table | ims_false_alarm_rate | 900 | res.next_steps_2026_10_24 |
| imp_ims_march_noise_vs_references | table | ims_noise_vs_reference | 280 | res.next_steps_2026_10_24 |
| imp_ims_open_availability | table | ims_open_availability | 4311 | res.next_steps_2026_10_24 |
| imp_h01w_array_calibration | array_calibration | array_calibration, array_calibration_event | 41 | res.next_steps_2026_10_24 |
| imp_island_seismic_detection | table | island_seismic_detection | 20484 | res.next_steps_2026_10_24 |
| imp_island_seismic_association | table | island_seismic_association | 6648 | res.next_steps_2026_10_24 |
| imp_island_impact_window_unexplained | table | island_impact_window_unexplained | 312 | res.next_steps_2026_10_24 |
| imp_royer_event_labelled | table | royer_event_labelled | 840 | res.next_steps_2026_10_24 |
| imp_airliner_seismic_case | table | airliner_seismic_case | 10 | res.next_steps_2026_10_24 |
| imp_airliner_seismic_station_test | table | airliner_seismic_station_test | 72 | res.next_steps_2026_10_24 |
| imp_swissair111_seismic | table | swissair111_seismic | 57 | res.next_steps_2026_10_24 |
| imp_swissair111_energy_sensitivity | table | swissair111_energy_sensitivity | 12 | res.next_steps_2026_10_24 |
| imp_metz_geometry | table | metz_geometry | 8 | res.next_steps_2026_10_24 |
| imp_metz_source_slope | table | metz_source_slope | 84 | res.next_steps_2026_10_24 |
| imp_aadc_2014_access | table | aadc_2014_access | 4 | res.next_steps_2026_10_24 |
| imp_metz_nearfield_derived | table | metz_nearfield_derived | 16 | res.next_steps_2026_10_24 |
| imp_metz_fig2_digitised | table_concat | metz_fig2_digitised | 5999 | res.next_steps_2026_10_24 |
| imp_known_event | table | known_event | 298 | res.source_survey_2026_10_23 |
| imp_source_type | table | source_type | 41 | res.source_survey_2026_10_23 |
| imp_source_catalogue | table | source_catalogue | 45 | res.source_survey_2026_10_23 |
| imp_explosion_radiated_fraction | table | explosion_radiated_fraction | 23 | res.raw_ims_2026_10_25.propagation_level_check |
| imp_coupling_wave3 | coupling_package_append | coupling_value, received_observation, coupling_evidence, data_availability_probe (+ updates of impact_case AC05, coupling_family_element_evidence R3) | 182 | res.raw_ims_2026_10_25.db_rows_merged |
| imp_coupling_wave3_id_map | table | coupling_wave3_id_map | 173 | res.raw_ims_2026_10_25.db_rows_merged |

Bookkeeping tables: `import_block` (one row per block: path, branch, commit, SHA-256, role, caveat, rows), `import_table`, `import_not_imported`, `package_row_history` (rows replaced by an update), `import_erratum` (the 7 verifier errata of raw-data-2026-10-25/README.md and how each reaches the database; values are not changed). Shared tables carry the column `import_block`.
- Noise: the March 2015-2019 open raw IMS percentiles add 9520 `noise_estimate` rows (1/3-octave PSD, 1/3-octave SPL and 5-40 Hz SPL; context 'IMS March 2015-2019 open raw (proxy for 8 Mar 2014)'). The 1-Hz PSD percentiles stay in the verbatim table `ims_march_noise_percentile` only.
- Coupling: wave-3 rows CV26-CV123 and OB07-OB81, evidence E18 and 6 probes; AC05 and R3 updated (old rows in `package_row_history`). The explosion radiated fractions are in their own table `explosion_radiated_fraction`, not in `coupling_value`, so `v_module_chain` cannot mix them with impact values (importer decision, 26 Oct 2026).

## Stage 4: noise caveat fixes of 26 Oct 2026 (build_noise_fixes.py)

Pete, 26 Oct 2026: "(3) please check on and fix the items noted in caveats". Rows are added; no row is deleted. Status UNCHECKED (no independent verifier yet). Note: `results/hydroacoustics/noise-caveat-fixes-2026-10-26/README.md` on claude-science-sep29.
- C1: `noise_estimate` rows with method 'digitised from published pressure trace' (Kadri 2024 Fig. 9, 5-40 Hz, median 1-s RMS from the 1-s peak-to-peak of the vertices / k; k from raw IMS records of 8 March 2015-2019, `results-data/noise-caveat-fixes-2026-10-26/`). Column `uncertainty_db` (1 sigma) and `uncertainty_note`.
- Views `v_noise_summary` and `v_noise_8mar2014` now carry `noise_id`, `uncertainty_db`, `preferred_8mar2014` and `preference_reason` (table `noise_preference`): which 8 Mar 2014 row is preferred at H01W and H08S, and why.
- C2: table `imos_gain_check`; checks F05-F07 (the IMOS band levels already include the per-bin logger gain; no correction).
- C3: table `absolute_level_check` (IMOS 3315 against CMST Fig. 1), view `v_ims_noise_5_40_compare` (table `noise_compare_5_40`: H01W and H08S 5-40 Hz levels from every held source), and SSEIR/SWAMS3 rows with method 'transfer calibration via H01W2 (Royer 2016 spectrograms)'. Summary table `noise_fix_result`; inputs and quoted definitions in `noise_fix_input`.

```sql
-- the preferred 8 March 2014 level at each IMS station, with its uncertainty and the reason
SELECT site_id, band_label, statistic, value, uncertainty_db, method, preference_reason FROM v_noise_8mar2014 WHERE preferred_8mar2014 = 1;
-- all 5-40 Hz levels at H01W and H08S side by side
SELECT * FROM v_ims_noise_5_40_compare;
```

## Build checks (182 on 26 Oct 2026: 179 PASS, 3 REVIEW; the 36 stage-1 checks below and the 20 stage-2 checks are unchanged in result and detail; stage 3 and 4 checks are in build_log.txt and check_log)

- C01 PASS: IMS element positions: module stations.csv against FDSN station list
- C02 PASS: IMS element positions: Royer 2016 Table 1 against FDSN (recorded; FDSN used)
- C03_3250 PASS: IMOS 3250 background: files on disk equal SHA256SUMS lines
- C03_3274 PASS: IMOS 3274 background: files on disk equal SHA256SUMS lines
- C03_3376 PASS: IMOS 3376 background: files on disk equal SHA256SUMS lines
- C04 PASS: IMOS raw files: SHA-256 recomputed against recordings.csv / SHA256SUMS
- C05_imos3250_background PASS: imos3250_background: one sample rate and one filter setting in all records
- C05_imos3250_mh370_day PASS: imos3250_mh370_day: one sample rate and one filter setting in all records
- C05_imos3274_background PASS: imos3274_background: one sample rate and one filter setting in all records
- C05_imos3274_mh370_day PASS: imos3274_mh370_day: one sample rate and one filter setting in all records
- C05_imos3275_mh370_day PASS: imos3275_mh370_day: one sample rate and one filter setting in all records
- C05_imos3315_mh370_day PASS: imos3315_mh370_day: one sample rate and one filter setting in all records
- C05_imos3376_background PASS: imos3376_background: one sample rate and one filter setting in all records
- C05_imos3376_mh370_day PASS: imos3376_mh370_day: one sample rate and one filter setting in all records
- C06_3250 PASS: IMOS 3250 event-day records: start spacing (expected about 900 s)
- C06_3274 PASS: IMOS 3274 event-day records: start spacing (expected about 900 s)
- C06_3275 PASS: IMOS 3275 event-day records: start spacing (expected about 900 s)
- C06_3315 PASS: IMOS 3315 event-day records: start spacing (expected about 900 s)
- C06_3376 PASS: IMOS 3376 event-day records: start spacing (expected about 900 s)
- C07 PASS: IMOS event-day: recordings.csv rows equal .DAT files on disk
- C08 PASS: IMOS file-name hex time against header 'First Data' (logger clock), recorded only
- C09 PASS: Digitised and module data files: CSV imported verbatim as tables, other files referenced with SHA-256
- C10 PASS: Every dataset site_id exists in site
- C11 PASS: Every pick site_id exists in site
- C12 PASS: Segment end not before start
- C13 PASS: Every dataset registry_entry_id exists in REGISTRY.json
- C14 PASS: Every imported table and file reference is linked to a dataset
- C15 PASS: kadri2024_table1 times lie inside the kadri2024_fig9_h01w panels
- C16 PASS: h08s_airgun_shots times lie inside the kadri2024_fig9_h08s panels
- C17 PASS: IMOS logger positions: metadata parse against module preregistration.json
- C18 PASS: Every dataset has at least one segment, pick, imported table or file reference
- C19 PASS: Digitised traces: every UTC value parses (ISO 8601)
- C20 PASS: Records held in two IMOS sets (byte-identical files; marked in segment.same_file_in, counted once for coverage)
- L01 PASS: Control: Diego Garcia North has no clear path at any arc latitude (Chagos Bank; dropped by ruling 23 Oct 2026)
- L02 PASS: Control: Scott Reef blocked south of about 29.6 S (23 Oct 2026 sweep, artifact arc_path_obstacles_20S_40S.csv)
- L03 PASS: Arc sampling: 20.0 S to southern end

## Known limits recorded in the data

- IMOS loggers record 307 s every 15 min (34 % of the time). Below 8 Hz the hardware high-pass removes signal.
- 56 IMOS records are byte-identical files held in both an event-day set and a background set (3274 on 7 Mar, 3250 and 3376 on 9 Mar). They are marked in `segment.same_file_in`.
- Digitised traces are envelope-resolution vertices of the plotted trace (Kadri Fig. 9 about 15 points/s), not instrument samples. Kadri Fig. 9 panel e has a +8.8 dB amplitude step at the panel join.
- Royer Cape Leeuwin figure times are 7.7–16.6 s later than his Table 5 (cause not resolved).
- CMST Fig. 10 survey detections have no printed time origin: they are in the imported table only, without UTC.
- Positions of H03N/H03S (Juan Fernandez) and H04S (Crozet) are not in the held files or the FDSN EarthScope list; these sites are used only by calibration datasets.
