# HYDROACOUSTICS inbox

Read at the start of each working session and before every commit. Append new entries at the end, dated in UTC.
**This inbox was started again on 26 Oct 2026.** The history from 7 to 26 Oct 2026 is in `coordination/archive/HYDROACOUSTICS-2026-10-07-to-2026-10-26.md`. It is background only. Where it differs from `threads/status/hydroacoustics.md`, the status file is correct.

## 2026-10-26 — REPOSITORY RULE for all modules and all threads (Pete: "please pull everything in and instruct all modules and threads to update the respository going forward"; decisions P62, P66)
From the hydroacoustics overview session (8b907e71), for every module and every thread, on any profile.
1. The repository is the record. A result that exists only as an artifact, in a session workspace or in a kernel is not a result. Commit data, code and results before you report work as done.
2. Commit at the end of every work step, not only at the end of the thread. A thread can stop at any time.
3. Data go into the module's data store only through its build scripts. Hydroacoustics: add a block to `engine/hypotheses/hydroacoustics/registry/data_db/imports.yaml`, rebuild, record the SHA-256. One rebuild at a time; say in the module inbox when you rebuild. Never edit a database by hand.
4. Results go to `results/<module>/<run id>/` with `manifest.json` (schema `registry/manifest.schema.json`). On a module branch: `results-data/<run id>/` with `manifest.json`. No loose files. No `-v2` or `-FINAL` names: give a new run id and set `supersedes`.
5. Registry: add the entry with status UNCHECKED. Only an independent verifier sets CURRENT. Then run the module registry build and the project registry import (`registry/README.md`).
6. Push: install the pre-push hook once per clone (`make -C "Claude Science Project Sep 29/registry" install-hooks`). Never use `--no-verify`. Run `git pull --rebase` before every push. Read branch heads with `git ls-remote`, never from memory.
7. Artifacts are viewing copies for Pete. Put the artifact version id in the manifest (`artifact_version_id`). The file in the repository is the source.
8. A sub-agent may save artifacts and not commit. The parent thread then commits the sub-agent's deliverables before it reports.
9. Read status from the registry and from `threads/status/<module>.md` where that file exists. Memory rows are context, not authority.
10. If you cannot push (no credential, the hook fails), say so at the top of your report and list the files not committed, with their artifact version ids.
-- hydroacoustics overview session 8b907e71, 26 Oct 2026. The same rule is now in every module profile prompt and in the default profile (MH370 project only).

## 2026-10-26 — Two new hydroacoustic threads and their work orders (from the hydroacoustics overview session 8b907e71, at Pete's request)
- **Forward model** (Hydroacoustic Module profile): `threads/work-orders/hydroacoustics-forward-model-order-2026-10-26.md`. It continues the plan of session c764a583 after c764a583 commits its Phase 1 outputs (noise model, airgun level unit audit, bearing check, 777 source physics).
- **Detection model, clean sheet** (Hydroacoustic Module profile): `threads/work-orders/hydroacoustics-detection-order-2026-10-26.md`, with the draft specification `threads/specs/hydro-detection-model-spec-2026-10-26.md`. Step D0 is the specification review with Pete.
- **Ownership:** forward model owns `prepare/forward/`, the transmission-loss grids, source and coupling code and the simulated-arrivals files. Detection owns `detect/`, the interface schema and validator, the injection bench, the known-event association and the Kadri package. The interface schema `interfaces/simulated_arrivals.schema.json` is written by detection (step D1) and agreed by the forward model here in this inbox.
- **Data store:** the repository import of 26 Oct (sub-agent of 8b907e71) adds a declarative import stage (`registry/data_db/imports.yaml`). Rebuild one at a time and announce it here before and after.
- **Overview:** session 8b907e71 keeps the overview for Pete (P72). Post progress, results and questions for the overview here. The overview session reads this inbox and the thread transcripts, and updates `threads/status/hydroacoustics.md`.
-- hydroacoustics overview session 8b907e71

## 2026-10-26 — For session c764a583 (Aircraft Impact Acoustic Source Survey)
- Please commit your Phase 1 outputs under the repository rule above (run folders with manifest.json, UNCHECKED until your verifier passes), and post an entry here that lists them.
- The overview session recommends to Pete that the forward-model thread then takes over your phases 2-5, and that the detection test of your phase 4 moves to the detection thread (clean sheet, P57). Pete decides this; wait for his message.
-- hydroacoustics overview session 8b907e71

## 2026-10-27 — Repository import done and verified (from the hydroacoustics overview session 8b907e71)
- The data store now holds the 23-26 Oct work through `registry/data_db/imports.yaml` (24 blocks) and the noise caveat fixes C1-C3. Rebuild all stages with `rebuild_all.sh`. SHA-256 e0442acebc6c112e4b062a97349dda80af70f4b2253f7b56f19bba40645caf91. Commits: module 8a65657, 4452f265; project 573a4588.
- Independent verification: `results/hydroacoustics/import-verification-2026-10-26/` (V1-V6 agree; use about 1 dB, not 0.34/0.40 dB, for the C1 trace levels).
- Note: the inbox restart of 26 Oct broke 11 phase-2 status-evidence paths in the project build. The import repointed them to the archived inbox (module commit 4452f265). If you cite an old inbox line, cite `coordination/archive/HYDROACOUSTICS-2026-10-07-to-2026-10-26.md`.
- Status file `threads/status/hydroacoustics.md` updated (sections 2, 3, 6).
-- hydroacoustics overview session 8b907e71

## 2026-10-27 — ON HOLD: add the OHASISBIO sites to the transmission-loss grid (for the forward-model thread; Pete asked for the requirement and the run-time estimate, and wants to close out other work first)
From session 2ed32de0 (seafloor-path sheets for Pete). **Do not start until Pete approves in this inbox or in your thread.**

**Finding (27 Oct 2026).** The run J transmission-loss grid (`prepare/tl_grid_run_j.py`, `results-data/tl_grid_run_j/`, module commit 4452f265) has receivers H01W, H08S, H08N and IMOS 3315, 3376, 3250, 3274, 3275 only. No OHASISBIO site has a transmission loss in the model. For the model receivers, paths rebuilt with `tl_grid_run_j.build_path` at 20, 25, 30, 35 and 40 S (offset 0) agree exactly with the stored grid: range, minimum track depth, minimum corridor depth, km shallower than 1,000 m, shallowest point outside the last 100 km, end depth and minimum profile depth (245 values, 0 differ). Artifacts: sheets `seafloor_paths_arc_{20,25,30,35,40}S.png` (versions c783e3a0, 593226c2, 8d4b6b5a, 8daac1cc, cf1419ab), check table `seafloor_paths_model_check.csv` (6a97566b), path summary `seafloor_paths_summary.csv` (3d2db978), profiles `seafloor_paths_bathy_500m.csv.gz` (142e8b29), script `seafloor_paths_rebuild.py` (a991aad2). These artifacts are not yet committed; the forward-model thread commits the ones it uses.

**Requirement.**
1. Receivers: SWAMS1, SWAMS2, SWAMS3, SSEIR, MAD, NCRO, WKER. Leave out NEAMS (data lost on recovery). Read positions and hydrophone depths from the `site` table of the current `hydro_data.sqlite` (Royer 2016 Table 1). Record the DB SHA-256 in the manifest. `run_j_windows.py` has its own OHASISBIO position list: compare it with the DB and report any difference.
2. Method: no change. Use the run J grid code as it is: same source points (`arc_sources`, 41.0 S to 20.0 S every 0.5 deg, offsets -60, -30, 0, +30, +60 NM), WGS84 paths every 250 m, GEBCO_2026 3 x 3 median, WOA23 March 2005-2014, KRAKEN adiabatic incoherent modes, profiles every 5 km, hard bottom, Francois-Garrison, spherical correction, source depths 2, 10, 30 m, ten third-octave bands 5-40 Hz, same blockage rule. The receiver depth is the hydrophone depth (moored in deep water, as the IMS triads). Add an `ohasisbio` receiver kind to `receivers()`; change nothing else.
3. Outputs: a new run folder `results-data/<run id>/` with `manifest.json`, rows in the `tl_grid.csv` schema, and a drop-in table in the `ims_tl_kraken_arc.csv` schema with the `ridge_source` and `adiabatic_suspect` flags computed as for the IMS rows. Deep-channel travel time per path as the grid records it (c = 1.482 +/- 0.006 km/s). Registry status UNCHECKED until an independent verifier passes.
4. RAM: no RAM delta exists for these sites. Pete chooses one of: (a) compute a RAM delta at one arc point per site (the run J median point, as `ims_ram_delta.csv`), 10 bands, 10 m source; or (b) carry raw KRAKEN with the label 'no RAM delta: upper bound on loss', as H08N. Recommended: (a), because it puts these sites on the same footing as H01W and H08S.
5. Acceptance: (i) rebuild the offset-0 paths at 20, 25, 30, 35 and 40 S and match `seafloor_paths_summary.csv` exactly; (ii) time 3 paths first and compare with the estimate below; stop and report if the real time is more than 2 x the estimate; (iii) no land or 'no_modes_shallow' rows are expected at offset 0 (the shallowest point on the 25 sampled paths is 728 m, NCRO from 30 S). Any such row is a finding to report, not an error to fix.
6. Out of scope (separate items, not estimated here): a noise level for the OHASISBIO sites (no calibrated level exists; the Royer 2016 spectrograms in the DB are digitised, not calibrated), and any use of these sites in detection. The data held for these sites are digitised figures only.

**Run-time estimate.** Measured from the 22 Oct grid run (1,760 paths, all 10 bands and 3 source depths per path, 4 processes, parallel efficiency 3.97 of 4): wall time per path = 0.0050 s/km x range - 0.7 s (residual SD 3.6 s). The multiprocessing pool of `tl_grid_run_j.py` works in the mh370-hydro environment (tested 27 Oct 2026). OHASISBIO path ranges come from the 25 rebuilt paths, interpolated over latitude.

| Item | Paths or jobs | CPU time | Elapsed, 4 processes | Elapsed, 2 processes (outside the heavy lock) | Elapsed, 12 processes (heavy lock) |
|---|---|---|---|---|---|
| A. KRAKEN grid, 7 sites, offset 0 only | 301 paths | 1.2 h | 18 min | 36 min | about 6 min (not measured above 6 processes) |
| B. KRAKEN grid, 7 sites, all 5 offsets (full requirement) | 1,505 paths | 6.0 h | 1.5 h | 3.0 h | about 30 min (not measured above 6 processes) |
| B'. As B with SWAMS2 only for the SWAMS group (SWAMS1-3 lie within about 10 km) | 1,075 paths | 4.7 h | 1.2 h | 2.3 h | about 25 min |
| C. RAM delta, 5 site groups, 1 point, 10 bands (option 4a) | 50 jobs | about 1.8 h (+/- 50 %: RAM cost measured only at 31.5 and 40 Hz, 0.058 and 0.094 s/km, scaled linearly in frequency) | about 30 min | about 55 min | about 10 min |
| D. Drop-in table, flags, checks | 1 | < 5 min | < 5 min | < 5 min | < 5 min |

Development: about 2 h (receiver kind, table output, manifest, DB import block, registry entry), plus about 1 h for the independent verifier. Recommended order: A first (18 min), check acceptance (i) and (iii), then B and C.
-- session 2ed32de0, 27 Oct 2026
