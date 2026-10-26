# Hydroacoustics repository import, 26 October 2026

Status: UNCHECKED (RULE 4). Made by session d8445a3f (sub-agent of the coordinating session 8b907e71).
Instruction (Pete, 26 Oct 2026): "please pull everything in and instruct all modules and threads to update the respository going forward".
Scope: every hydroacoustic data item and result made since 23 Oct 2026. Data go to hydro_data.sqlite through its build scripts. Results go to registered run folders.
Inventory: [inventory.csv](inventory.csv) (1399 rows: item, source, sha256, in_repo, action, reason). Data-readiness rule: each item is listed with its location and SHA-256 before import; no stand-ins.

## How the repository is updated from now on
- Data: add ONE block to `engine/hypotheses/hydroacoustics/registry/data_db/imports.yaml` on `hypothesis/hydroacoustics`, then run `rebuild_all.sh`. See that folder's README.md ("Adding data").
- Results: a run folder `results/hydroacoustics/<run id>/` with `manifest.json` (registry/manifest.schema.json), status UNCHECKED until an independent verifier passes, then a module registry entry.

## Data imported (hydro_data.sqlite stage 3, build_imports.py; 24 blocks)

| block | kind | rows in the database | registry entry |
|---|---|---|---|
| imp_ims_march_noise_percentiles | noise_percentiles | 9520 | res.next_steps_2026_10_24 |
| imp_ims_march_false_alarm_rates | table | 900 | res.next_steps_2026_10_24 |
| imp_ims_march_noise_vs_references | table | 280 | res.next_steps_2026_10_24 |
| imp_ims_open_availability | table | 4311 | res.next_steps_2026_10_24 |
| imp_h01w_array_calibration | array_calibration | 41 | res.next_steps_2026_10_24 |
| imp_island_seismic_detection | table | 20484 | res.next_steps_2026_10_24 |
| imp_island_seismic_association | table | 6648 | res.next_steps_2026_10_24 |
| imp_island_impact_window_unexplained | table | 312 | res.next_steps_2026_10_24 |
| imp_royer_event_labelled | table | 840 | res.next_steps_2026_10_24 |
| imp_airliner_seismic_case | table | 10 | res.next_steps_2026_10_24 |
| imp_airliner_seismic_station_test | table | 72 | res.next_steps_2026_10_24 |
| imp_swissair111_seismic | table | 57 | res.next_steps_2026_10_24 |
| imp_swissair111_energy_sensitivity | table | 12 | res.next_steps_2026_10_24 |
| imp_metz_geometry | table | 8 | res.next_steps_2026_10_24 |
| imp_metz_source_slope | table | 84 | res.next_steps_2026_10_24 |
| imp_aadc_2014_access | table | 4 | res.next_steps_2026_10_24 |
| imp_metz_nearfield_derived | table | 16 | res.next_steps_2026_10_24 |
| imp_metz_fig2_digitised | table_concat | 5999 | res.next_steps_2026_10_24 |
| imp_known_event | table | 298 | res.source_survey_2026_10_23 |
| imp_source_type | table | 41 | res.source_survey_2026_10_23 |
| imp_source_catalogue | table | 45 | res.source_survey_2026_10_23 |
| imp_explosion_radiated_fraction | table | 23 | res.raw_ims_2026_10_25.propagation_level_check |
| imp_coupling_wave3 | coupling_package_append | 182 | res.raw_ims_2026_10_25.db_rows_merged |
| imp_coupling_wave3_id_map | table | 173 | res.raw_ims_2026_10_25.db_rows_merged |

Not imported, by design (duplicates of existing tables, or track-local copies of merged rows): 7 files; see `import_not_imported` and inventory.csv.
The 7 verifier errata of raw-data-2026-10-25/README.md are in table `import_erratum`. Values are not changed. Erratum 5 (H10S1 at the San Juan charge, OB16) and erratum 7 (AC05 lags) are written to the row column `erratum`.
The explosion radiated fractions are in their own table `explosion_radiated_fraction`, not in `coupling_value`, so `v_module_chain` cannot mix them with impact values.

## Checks
Full rebuild with rebuild_all.sh: 182 checks, 179 PASS, 3 REVIEW. The 56 checks of 25 Oct (54 PASS, 2 REVIEW) are unchanged in result and detail.
New REVIEW I08c (for the coupling thread, session c764a583): base-package row CV01 (stage 2) still says "one-pole f^-2". Verifier erratum 1 corrected this wording only in the wave-3 rows. The base package is not edited here.

## Platform artifacts (sessions since 23 Oct 2026)
- Sessions: 880dfd82 (Kadri review), c764a583 (source survey; still running), c0b15646 (site noise review), 9e0bf4fe (data inventory), 8b907e71 (status review).
- Session c764a583 dispatched its Phase 1 tracks (noise model, airgun level, bearing check, 777 source physics) at 2026-10-26T19:03:40Z (creation time of the four track frames). Its 248 artifacts made after that time are excluded; that session commits its own outputs.
- Committed now (byte-identical copies, SHA-256 checked, artifact version in each manifest):
  - kadri-independent-review-2026-10-26/ (5 files), status-review-2026-10-26/ (4), source-survey-supplement-2026-10-26/ (156), site-noise-review-supplement-2026-10-26/ (14).
- Not committed (467), by reason:
  - raw waveform, binary intermediate or archive: 348
  - copy or text of a published document or a large PDF: 58
  - another version of a committed file with the same name: 18
  - scratch, preview, memory dump or hand-off text: 9
  - text dump of a report, paper or code listing: 6
  - saved web page: 5
  - image of a published figure page: 3
  - job list with host file paths: 3
  - raw AADC object listing: 3
  - copy of a file in a host data home: 3
  - earlier draft of a figure: 2
  - larger than 10 MB: 2
  - copy of a published report: 2
  - large binary: 1
  - crop of a published figure: 1
  - scratch file: 1
  - contains session-workspace paths: 1
  - session plan file: 1

## Known limits
- No independent verifier pass: this session is a leaf sub-agent and cannot start one. Everything here stays UNCHECKED.
- Artifacts are classified by rules (git blob match, file type, name). The rules are in this README and in the reason column. A rule can put a useful file in 'not committed'; the artifact stays in the store and can be committed later.
