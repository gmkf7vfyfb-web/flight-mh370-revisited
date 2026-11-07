# Hydroacoustic data holdings audit, 7 November 2026

Scope: every hydroacoustic dataset the project has used: calibration studies, IMOS loggers, Royer 2016 and the OHASISBIO temporary sites, Kadri and other digitised sources, the registry and the backup-drive list. The audit was read-only. Nothing was deleted, moved or modified. Table: `holdings-audit-2026-11-07.csv` (46 rows, one per dataset or file group). Baseline hash list: `holdings-audit-2026-11-07-host-sha256.tsv` (SHA-256 of all 13,616 files under the two hydro host folders, 79.96 GB).

Statement labels: **[re-run]** = computed in this audit; **[record]** = taken from a project note, memory row or registry; **[not checked]**.

## Summary

- All the calibration raw data that the project kept is present and intact. [re-run]
- All IMOS raw records are present and intact: 540 event-window files for the five loggers and 4,032 background files. Each file has the same SHA-256 as the database and the registry. [re-run]
- All Royer 2016 and OHASISBIO data that the project holds are present and intact. These data are digitised values in hydro_data.sqlite, the Z-call extraction and the Royer PDF. [re-run]
- The project never held OHASISBIO waveforms. Status: not retrieved — ask Pete. [record]
- No hydroacoustic artifact has lost its stored file. In the full project store, 10,657 of 10,728 versions verify. Only 35 stored files are missing, and all 35 are non-hydro reference artifacts of folders that moved to the backup drive. [re-run]
- Some raw data were not kept by design. These are the 2015-2019 Cape Leeuwin and Diego Garcia South miniSEED behind the 26 Oct noise model, and the earthquake waveforms behind the H01W bearing calibration. EarthScope still serves them. A probe on 7 Nov 2026 returned data. [re-run]
- One distribution archive is not on the Mac: `MH370.zip`. It is on the backup-drive list, but no session can read that drive. Its extracted contents are on the Mac and they verify. [re-run / record]
- The Perth Canyon 1 logger (3315) and the Portland 2 logger (3275) are not in the open IMOS archive. For these two loggers, the Mac folder and the distribution zips are the only copies. [re-run]
- The 5-6 Nov downloads have no registry entry yet: earthquake records, random background and the 250 Hz cache. The new hash list in this audit is their first SHA-256 baseline. [re-run]

## 1. Method [re-run]

1. SHA-256 of all 21,523 files under `~/Downloads/mh370-inputs/hydroacoustics`, `~/Downloads/mh370-exchange/hydroacoustics` and every resolvable artifact-store file (148.5 GB). A further pass covered 1,956 artifact versions not reached by the first pass, mostly older versions (15.1 GB) and the GEBCO 2026 and WOA23 grids (498 files).
2. Comparison with every SHA-256 record available:
   - the artifact store's own checksums (10,728 versions);
   - hydro_data.sqlite (segment, file_ref, imported_table, stage2_input, dg_data_imos_recordings);
   - the module registry REGISTRY.json and its 235 per-entry manifests on `hypothesis/hydroacoustics` (14,512 file records);
   - `registry/modules/hydroacoustics/platform_artifacts.tsv` (1,070 versions);
   - the 26 Oct exchange inventory (7,999 files);
   - the IMOS SHA256SUMS files;
   - 384 SHA256SUMS lists inside the exchange folder (2,475 lines; 2,473 verify; the other 2 are a list's line for itself and one README edited after its list was written).
3. Repository-side sources referenced by the database were downloaded and hashed: 464 files, including the four Metz Fig. 2 files.
4. The fetch logs were compared with the files present. The bearing-check event lists were compared with the held earthquake records.
5. Archive tests:
   - CRC tests on 29 hydro zip archives;
   - CRC comparison of all 245 members of `Portland_MH370.zip` against the extracted folder;
   - `PRAGMA integrity_check` on the database, opened read-only.
6. Re-download probes:
   - EarthScope FDSN dataselect (IM network, EDH channel), 7 station-dates;
   - the IMOS open S3 archive listing for loggers 3250, 3274, 3275, 3315 and 3376.

## 2. Findings by area

**Calibration studies.**
- H01W calibration, iteration 1: present and verified [re-run]. This is version 076cefbe, 41 events, also held in the DB tables `array_calibration` and `array_calibration_event`.
- Bearing-check and refit-144 package: present and verified [re-run]. The note c71bc016 and the 22 data and code files it cites verify (23 artifacts). The note cites 24 versions in total: these 22 and 2 figures, which also verify. This includes the calibration parameters 17cc43f3, the error model 77e38556, the scripts 3a409026 and the event data 3f3892b0.
- The refit-144 package has no registry entry and is not in the DB [re-run]. It was made 2.5 h before the 26 Oct registry build and was not imported.
- The raw waveforms behind these fits were not kept [re-run]. The event-data zip holds windows and measurements only. The held earthquake records (`ims_eq_records`, 5 Nov) cover:
  - 2 of the 41 calibration events;
  - 0 of the 146 refit events;
  - 238 of 535 H01W events;
  - 448 of 483 H08S events;
  - 0 of 1,368 H11 events.
- `ims_eq_records` is complete against its log [re-run]: 686 of 686 files.
- `ims_random_background` is complete against its log [re-run]: 326 files. The other 54 of the 380 requests returned "No data available" at download time.
- The 26 Oct noise model products are present [re-run]:
  - 44 `S3_*.npz`;
  - 9 `*_noise.npz` (no H01W 2016-03-08 file; cause not checked);
  - 4 R1/R3 tables;
  - the derived-products zip aa968522.
- Note 129a8b8e records that the raw miniSEED was not kept [record].
- All other calibration groups listed in the task are present and every version verifies [re-run]:
  - bootstrap parameters;
  - Blackman airguns air1-air9 at three stations;
  - Blackman Fig. 23 curves and tables;
  - SUS charges;
  - ARA San Juan;
  - F-35A at H11;
  - QZ8501, JT610, SJ182 and AB1103;
  - held-out tables and retests;
  - injection tests.
- No artifact named "ioretest" exists. The held-out row covers the level-heldout, retest, LOSO and step-2 files. This is our interpretation of the task, and it can be our error.

**IMOS.**
- Event-window records [re-run]:
  - all 540 files verify against the DB and the registry (3250: 100; 3315: 100; 3376: 100; 3274: 144; 3275: 96);
  - all 4,032 background files verify against the DB, the registry and the three SHA256SUMS files (3250, 3274, 3376; 1-7 and 9-15 Mar);
  - the 6 calibration files and 9 documents verify.
- `Portland_MH370.zip` is present and verified [re-run]. Its SHA-256 matches the record, and all 245 members match the extracted files by CRC.
- `MH370.zip` is absent from the Mac [re-run]. It is listed in `archive-to-porsche.v3.sh` (batch 3), and registry entry `xd.imos_mh370_zip_inputs` records it as UNCHECKED [record].
- The open IMOS archive holds 3250, 3274 and 3376 but not 3315 or 3275 [re-run].
- The 250 Hz cache (8 npz, 1.40 GB) and the calibration pickles (`imos_calib.pkl`, `imos_calib_eqclean.pkl`, 21 versions) are present [re-run]. The cache has no registry entry. It is derived data and can be regenerated from the raw records.

**Royer 2016 and OHASISBIO.**
- All 41 `dg_royer_2016_*` tables are present [re-run]. They hold events, arrivals, figure marks, stations, map labels, sensitivity and 34 spectrogram band-reading tables (29,498 rows).
- The row counts equal the import records. Each source file has the SHA-256 recorded in the DB [re-run].
- The Z-call extraction (83b7b376) and the SEANOE sources verify [re-run].
- Every copy of the Royer PDF has the same SHA-256 (2e7190b9…), and that SHA-256 is in the registry [re-run].
- H01W2 appears through Royer's digitised panels only. Open IMS H01W data start in December 2014; the probe for 2014-03-08 returned no data [re-run].

**Kadri and other digitised sources.**
- Kadri 2024 Fig. 9: 44,051 vertices in five tables (8,706 + 8,721 + 8,716 + 8,935 + 8,973) [re-run].
- Kadri 2024 Table 1: 19 rows. Fig. S1: five tables, 96,166 rows [re-run].
- ATSB 2017 Fig. 3 detections: artifact version 1f4241b1, present [re-run].
- CMST 2014: 12 DB tables (8,588 rows) and 14 artifacts [re-run].
- Brown 2026: 5 DB tables, including Fig. C10 with 5,001 rows [re-run].
- Island-seismometer 12 h waveforms: the zip fe96bfde holds 10 stations and passes its CRC test [re-run].
- Every DB source file equals its repository file by SHA-256 [re-run].
- The report to the ATSB (8 Feb 2017) and the Kadri 2024 PDF exist only on the Mac host. They have no artifact-store or registry copy [re-run].

**Registry and backup.**
- Module registry manifests [re-run]:
  - exchange folder: 7,994 of 7,994 local file records match;
  - inputs: 4,597 match, plus one Finder `.DS_Store` that differs;
  - GEBCO and WOA23: 498 of 498 match;
  - repository records: 1,260 are present at the stated path with equal size; 154 are at other paths (150 found by name and size elsewhere; 4 are documents updated since).
- The 26 Oct exchange inventory [re-run]:
  - no file missing and no file new;
  - three differences: a `.DS_Store`, plus two files whose inventory hash came from SHA256SUMS lines that predate the files' last edit. Their modification times are unchanged since 22 Oct, and the module registry hash equals the current file.
- The path `threads/master-prompts/shared-contract.md` does not exist on either branch. The draft `threads/drafts/shared-contract-DRAFT.md` holds no dataset hashes [re-run].
- Backup drive (Porsche 1TB Backup):
  - the only verification list readable on the Mac is `VERIFIED-npy-20261026-1129.txt`, for 96 end-of-flight `.npy` files (96 of 96 OK) [record];
  - hydro items on the drive list: `MH370.zip`, `Portland_MH370.zip`, and the exchange folders `run-i` and `next-run-d-he` [record];
  - their copies on the drive are not confirmed by any session [record].

## 3. Missing items and how to restore each

| Item | Status | Restore |
|---|---|---|
| `MH370.zip` (3250/3315/3376 distribution archive) | Not on Mac; on drive list; drive copy not confirmed | Pete: compare `shasum -a 256` of the drive copy with `imos/SHA256SUMS.txt` (00d02720…). The extracted contents on the Mac are verified. Recommended: keep a second confirmed copy, because 3315 has no open-archive copy. Origin of the zip: not checked. |
| Raw 2015-2019 H01W/H08S miniSEED (26 Oct noise model, 311 blocks) | Not kept by design | Re-download from EarthScope FDSN dataselect, IM EDH, anonymous. Probe returned data, 7 Nov 2026. H01W open data end mid-2019. |
| Raw earthquake waveforms for the H01W calibration (41) and refit (146), and the H11 events (1,368) | Not kept; partly covered by `ims_eq_records` | Re-download from EarthScope as above. The fits can be re-run from the per-event measurements in 3f3892b0 without waveforms. |
| `mh370-exchange/hydroacoustics/run-i`, `next-run-d-he` | On drive list; not on Mac | Restore from the drive only if needed. Pete's ruling: the 7-20 Oct work is not to be reproduced. |
| OHASISBIO waveforms, H01W 8 Mar 2014 raw | Never held | not retrieved — ask Pete |
| 35 non-hydro reference artifacts (run I, next-run, eof-289 end-of-flight folders) | Stored files absent | Outside the hydro scope; on the drive list (archive batches 3 and 4). |

## 4. Held but apparently unused by recent hydroacoustic runs

The test was a keyword search of 270 text files in the 32 hydroacoustic result folders dated 24 Oct to 7 Nov on `claude-science-sep29`. This is a proxy: a missing keyword does not prove non-use. [re-run, proxy]

- `bootstrap_params_*.npy`, the refit-144 parameters (`calibration_parameters.csv`) and the two distribution zips: no recent run text names them. The corrected bearings derived from refit-144 are used.
- Kadri 2024 Fig. S1 traces (5 tables): named only in the 7 Nov Kadri audit, which lists them as unused.
- The 26 Oct noise-model products (S3 spectra, noise.npz): named only in the 26 Oct source-survey supplement. Later runs use the 6 Nov random-background noise model.
- Airliner records QZ8501, JT610, SJ182 and AB1103: named only in the 26 Oct reviews.
- Brown 2026 figures and the island-seismometer waveforms: named in the 26 Oct and 3 Nov runs and in the 6 Nov weak-signal run only.
- The ATSB 2017 Fig. 3 detections (new on 7 Nov) and the Kadri items listed in the 7 Nov Kadri audit (Kadri 2019 Fig. 4, the Fig. 9 spectrograms, the third Scott Reef pick).

## Key assumptions and modelling choices

- Data scope: the two hydro host folders, the whole project artifact store, both repository branches and hydro_data.sqlite version 321ea0f6. Other projects were not checked. *(task scope)*
- Read-only rule: no file was changed; the database was opened with `mode=ro`. *(Pete's ruling)*
- A file counts as intact when its SHA-256 equals a recorded SHA-256. Where only a repository path exists, presence with equal size counts as intact, because git object hashes guard the content. *(agent choice)*
- Finder `.DS_Store` files are excluded from the hash list and are not counted as differences. *(agent choice)*
- "Openly re-downloadable" rests on single-minute probes at sample dates, not on a full re-download. *(agent choice)*
- The task's "ioretest" is taken to be the held-out retest files. *(agent choice; it can be our error)*
- The backup drive cannot be read from sessions. Its contents come from the archive scripts, the one local verification list and the registry `XDRIVE` entries. Pete stated on 26 Oct 2026 that the drive holds the items listed in `~/Downloads/archive-tools/`; this audit could not confirm the individual copies. *(project record; Pete's statement)*
- "Unused" means a keyword absent from recent run texts. *(agent choice, proxy)*
