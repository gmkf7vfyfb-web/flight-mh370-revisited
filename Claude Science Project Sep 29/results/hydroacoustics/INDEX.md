# Hydroacoustics: index of data, products, notes and defects (generated from the registry)

*Generated from `engine/hypotheses/hydroacoustics/registry/REGISTRY.json` on `hypothesis/hydroacoustics` (hydro-registry v1 (2026-10-23); built 2026-10-23T02:24:47Z; module c9ac5ccddc4d; work branch 81e552601e9b; sha256 manifests: yes). Do not edit by hand: change `entries.yaml`, rebuild, regenerate.*

**How to use.** Find the item below. Read its status and defects. Read its definition (quoted in REGISTRY.json from the cited lines). Use only CURRENT or CURRENT_WITH_CAVEATS items for results, and state the listed defects beside every number. Pete's rulings: `decisions.md`. Proposals that are not yet rules: `proposals.md`.

**Status counts:** CURRENT 42, CURRENT_WITH_CAVEATS 23, KNOWN_DEFECT 5, PENDING_RULING 2, SUPERSEDED 3, UNCHECKED 3, WITHDRAWN 2

## Status values

| status | meaning |
|---|---|
| CURRENT | No known defect. Not re-verified in this run unless verified_this_run is true. |
| CURRENT_WITH_CAVEATS | Usable with the listed defects/limitations stated beside every number taken from it. |
| KNOWN_DEFECT | Contains at least one listed defect that changes a reported number or claim. Do not use the affected parts. |
| SUPERSEDED | Replaced by the entry named in superseded_by. Kept for history. |
| WITHDRAWN | Withdrawn at Pete's instruction. Do not use. |
| PENDING_RULING | Correct as computed, but its adoption waits for a ruling by Pete. |
| UNCHECKED | No definition located or not inspected in this run. |

## Inputs

| id | status | defects | path | files | GB | definition source |
|---|---|---|---|---|---|---|
| in.imos_raw | CURRENT |  | `INPUTS:imos` | 4598 | 17.349 | INPUTS:imos/MH370/3315_3250_3376__MetaData.txt L[1, 12] |
| in.gebco_2026 | CURRENT |  | `OCEAN:gebco/grid` | 9 | 2.817 | OCEAN:gebco/grid/gebco_2026.json L[1, 12] |
| in.woa23 | CURRENT |  | `OCEAN:woa23` | 489 | 7.908 | NO DEFINITION LOCATED |
| in.run_j_impacts | CURRENT |  | `EOF:run-j` |  |  | NO DEFINITION LOCATED |
| in.module_data | CURRENT |  | `MOD:data` | 52 | 0.008 | NO DEFINITION LOCATED |
| in.royer_2016_digitised | CURRENT |  | `MOD:results-data/digitised/royer-2016` | 135 | 0.054 | NO DEFINITION LOCATED |
| in.h08s_shots | CURRENT |  | `MOD:results-data/h08s_template/h08s_template_shots.csv` | 1 | 0.000 | NO DEFINITION LOCATED |
| in.h08s_shots_v1 | SUPERSEDED -> in.h08s_shots |  | `MOD:results-data/h08s_template/v1_defective` | 4 | 0.000 | NO DEFINITION LOCATED |
| in.geometry_sample | CURRENT_WITH_CAVEATS |  | `EX:run-j-searches/geometry` | 6 | 0.302 | EX:run-j-searches/geometry/run.json L[1, 1] |
| in.sources_pdfs | CURRENT |  | `EX:sources` | 25 | 0.037 | NO DEFINITION LOCATED |

## Products

| id | status | defects | path | files | GB | definition source |
|---|---|---|---|---|---|---|
| ex.ranked | KNOWN_DEFECT -> ex.register_2026_10_23 | D01, D02, D03, D04, D07, D08, D26 | `EX:graphics-2026-10-22/ranked` | 6 | 0.020 | EX:graphics-2026-10-22/ranked/README.txt L[1, 14] |
| ex.arrival_windows | KNOWN_DEFECT | D01, D02, D07 | `EX:graphics-2026-10-22/arrival-windows` | 70 | 0.082 | EX:graphics-2026-10-22/arrival-windows/README.md L[1, 5] |
| ex.kadri_package_v2 | KNOWN_DEFECT -> ex.kadri_predictions_v3 | D01, D22, D07 | `EX:kadri-package-v2` | 59 | 0.040 | EX:kadri-package-v2/README.md L[1, 6] |
| ex.run_j_gated | SUPERSEDED -> ex.run_j_gated_v2 | D22, D01 | `EX:run-j-gated` | 1725 | 9.432 | EX:run-j-gated/README.txt L[1, 7] |
| ex.run_j_gated_v2 | CURRENT_WITH_CAVEATS | D01, D05, D06, D20, D25 | `EX:run-j-gated-v2` | 835 | 7.484 | EX:run-j-gated-v2/README.txt L[1, 14] |
| ex.imos_ram_grid | CURRENT_WITH_CAVEATS |  | `EX:run-j-imos-ram-grid` | 826 | 0.578 | WORK:results/hydroacoustics-imos-ram-grid.md L[3, 9] |
| ex.injection | CURRENT_WITH_CAVEATS | D05, D06, D22 | `EX:run-j-injection` | 28 | 0.209 | EX:run-j-injection/README.txt L[1, 9] |
| ex.levels | CURRENT_WITH_CAVEATS | D01, D05, D25 | `EX:run-j-levels` | 107 | 0.510 | EX:run-j-levels/README.md L[1, 10] |
| ex.metz_f35a | PENDING_RULING |  | `EX:run-j-metz-f35a` | 38 | 0.082 | WORK:results/hydroacoustics-metz-f35a-anchor.md L[3, 7] |
| ex.searches | CURRENT_WITH_CAVEATS | D06, D24, D26 | `EX:run-j-searches` | 32 | 0.306 | WORK:results/hydroacoustics-searches-run-j.md L[3, 5] |
| ex.run_j_smoke | UNCHECKED |  | `EX:run-j-smoke` | 4 | 0.157 | NO DEFINITION LOCATED |
| ex.tl_grid | CURRENT_WITH_CAVEATS |  | `EX:run-j-tl-grid` | 49 | 0.052 | EX:run-j-tl-grid/README.md L[1, 7] |
| ex.tlrecal | UNCHECKED |  | `EX:run-j-tlrecal` | 31 | 0.015 | NO DEFINITION LOCATED |
| ex.weak_signal | CURRENT_WITH_CAVEATS | D05 | `EX:run-j-weak-signal` | 37 | 0.018 | EX:run-j-weak-signal/README.txt L[1, 9] |
| ex.windows | CURRENT |  | `EX:run-j-windows` | 155 | 0.160 | WORK:results/hydroacoustics-run-j-windows.md L[1, 5] |
| ex.digitisation | CURRENT |  | `EX:run-j-digitisation` | 177 | 0.079 | WORK:results/hydroacoustics-digitised-sources.md L[1, 5] |
| ex.run_j_tau_eof | CURRENT_WITH_CAVEATS | D23 | `EX:run-j/primary-tau-eof` | 373 | 15.367 | EX:run-j/primary-tau-eof/README.txt L[1, 6] |
| ex.run_j_tau_scenario | CURRENT_WITH_CAVEATS | D23 | `EX:run-j/sensitivity-tau-scenario` | 373 | 15.367 | EX:run-j/sensitivity-tau-scenario/README.txt L[1, 6] |
| ex.session_staging_1012 | UNCHECKED |  | `EX:session-staging-2026-10-12` | 32 | 0.000 | NO DEFINITION LOCATED |
| art.take2_review | CURRENT_WITH_CAVEATS | D10 | `ART:a35831fe/d28aa25a_hydroacoustics-take2-critical-review-2026-10-22.md` | 1 | 0.000 | ART:a35831fe/d28aa25a_hydroacoustics-take2-critical-review-2026-10-22.md L[1, 24] |
| art.candidates_withdrawal | CURRENT |  | `ART:a35831fe/269947b9_hydroacoustics-candidates-withdrawal-2026-10-23.md` | 1 | 0.000 | ART:a35831fe/269947b9_hydroacoustics-candidates-withdrawal-2026-10-23.md L[1, 3] |
| art.candidates_A_F | WITHDRAWN | D10, D04, D09 | `ART:a35831fe/b5497699_candidates-A-F-summary.csv` | 1 | 0.000 | NO DEFINITION LOCATED |
| art.feasibility_tables | WITHDRAWN | D10 | `ART:a35831fe` | 10 | 0.005 | NO DEFINITION LOCATED |
| art.royer_crossid | CURRENT_WITH_CAVEATS |  | `ART:a35831fe/239646ad_royer-events-crossid-all-sites.csv` | 1 | 0.000 | NO DEFINITION LOCATED |
| ex.register_2026_10_23 | CURRENT_WITH_CAVEATS | D05, D06, D24, D25, D26 | `EX:register-2026-10-23` | 6 | 0.011 | EX:register-2026-10-23/README.txt L[1, 4] |
| ex.kadri_predictions_v3 | CURRENT_WITH_CAVEATS | D05, D25 | `EX:kadri-package-v3-draft-predictions` | 5 | 0.002 | EX:kadri-package-v3-draft-predictions/README.txt L[1, 6] |

## Results notes (claude-science-sep29)

| id | status | defects | path | files | GB | definition source |
|---|---|---|---|---|---|---|
| note.agw_scenarios | CURRENT |  | `WORK:results/hydroacoustics-agw-scenarios.md` | 1 | 0.000 | WORK:results/hydroacoustics-agw-scenarios.md L[1, 5] |
| note.air9_ew0112_source_reference | CURRENT |  | `WORK:results/hydroacoustics-air9-ew0112-source-reference.md` | 1 | 0.000 | WORK:results/hydroacoustics-air9-ew0112-source-reference.md L[2, 13] |
| note.audit_architecture | CURRENT |  | `WORK:results/hydroacoustics-audit-architecture.md` | 1 | 0.000 | WORK:results/hydroacoustics-audit-architecture.md L[1, 6] |
| note.audit_sus_absolute | CURRENT |  | `WORK:results/hydroacoustics-audit-sus-absolute.md` | 1 | 0.000 | WORK:results/hydroacoustics-audit-sus-absolute.md L[1, 6] |
| note.blackman_validation | CURRENT |  | `WORK:results/hydroacoustics-blackman-validation.md` | 1 | 0.000 | WORK:results/hydroacoustics-blackman-validation.md L[1, 6] |
| note.calibration_events_stage1_standin | CURRENT |  | `WORK:results/hydroacoustics-calibration-events-stage1-standin.md` | 1 | 0.000 | WORK:results/hydroacoustics-calibration-events-stage1-standin.md L[1, 7] |
| note.calibration_events_stage1b | CURRENT_WITH_CAVEATS | D13 | `WORK:results/hydroacoustics-calibration-events-stage1b.md` | 1 | 0.000 | WORK:results/hydroacoustics-calibration-events-stage1b.md L[1, 11] |
| note.composition_run_j | CURRENT_WITH_CAVEATS | D01, D05, D06, D20 | `WORK:results/hydroacoustics-composition-run-j.md` | 1 | 0.000 | WORK:results/hydroacoustics-composition-run-j.md L[1, 5] |
| note.core_set_windows | CURRENT |  | `WORK:results/hydroacoustics-core-set-windows.md` | 1 | 0.000 | WORK:results/hydroacoustics-core-set-windows.md L[1, 12] |
| note.coverage | CURRENT |  | `WORK:results/hydroacoustics-coverage.md` | 1 | 0.000 | WORK:results/hydroacoustics-coverage.md L[1, 4] |
| note.digitised_sources | CURRENT |  | `WORK:results/hydroacoustics-digitised-sources.md` | 1 | 0.000 | WORK:results/hydroacoustics-digitised-sources.md L[1, 5] |
| note.f35a_eta_calibration | SUPERSEDED -> ex.metz_f35a | D01 | `WORK:results/hydroacoustics-f35a-eta-calibration.md` | 1 | 0.000 | WORK:results/hydroacoustics-f35a-eta-calibration.md L[1, 6] |
| note.imos_detectors | CURRENT |  | `WORK:results/hydroacoustics-imos-detectors.md` | 1 | 0.000 | WORK:results/hydroacoustics-imos-detectors.md L[1, 5] |
| note.imos_noise | CURRENT |  | `WORK:results/hydroacoustics-imos-noise.md` | 1 | 0.000 | WORK:results/hydroacoustics-imos-noise.md L[1, 4] |
| note.imos_ram_grid | CURRENT_WITH_CAVEATS | D01 | `WORK:results/hydroacoustics-imos-ram-grid.md` | 1 | 0.000 | WORK:results/hydroacoustics-imos-ram-grid.md L[1, 9] |
| note.ims_noise_blackman | CURRENT |  | `WORK:results/hydroacoustics-ims-noise-blackman.md` | 1 | 0.000 | WORK:results/hydroacoustics-ims-noise-blackman.md L[1, 8] |
| note.injection_recovery_run_j | CURRENT_WITH_CAVEATS | D01, D05, D06, D22 | `WORK:results/hydroacoustics-injection-recovery-run-j.md` | 1 | 0.000 | WORK:results/hydroacoustics-injection-recovery-run-j.md L[1, 5] |
| note.item3_injection_recovery | CURRENT_WITH_CAVEATS | D01 | `WORK:results/hydroacoustics-item3-injection-recovery.md` | 1 | 0.000 | WORK:results/hydroacoustics-item3-injection-recovery.md L[1, 7] |
| note.kadri_package_v2 | KNOWN_DEFECT | D01, D22, D07 | `WORK:results/hydroacoustics-kadri-package-v2.md` | 1 | 0.000 | WORK:results/hydroacoustics-kadri-package-v2.md L[1, 10] |
| note.kadri_table1_test | CURRENT |  | `WORK:results/hydroacoustics-kadri-table1-test.md` | 1 | 0.000 | WORK:results/hydroacoustics-kadri-table1-test.md L[1, 4] |
| note.literature_review | CURRENT |  | `WORK:results/hydroacoustics-literature-review.md` | 1 | 0.000 | WORK:results/hydroacoustics-literature-review.md L[1, 3] |
| note.methods_draft | CURRENT |  | `WORK:results/hydroacoustics-methods-draft.md` | 1 | 0.000 | WORK:results/hydroacoustics-methods-draft.md L[1, 11] |
| note.metz_f35a_anchor | PENDING_RULING |  | `WORK:results/hydroacoustics-metz-f35a-anchor.md` | 1 | 0.000 | WORK:results/hydroacoustics-metz-f35a-anchor.md L[1, 7] |
| note.near_limits_planning | CURRENT |  | `WORK:results/hydroacoustics-near-limits-planning.md` | 1 | 0.000 | WORK:results/hydroacoustics-near-limits-planning.md L[1, 5] |
| note.next_run_b_standin | CURRENT |  | `WORK:results/hydroacoustics-next-run-b-standin.md` | 1 | 0.000 | WORK:results/hydroacoustics-next-run-b-standin.md L[1, 6] |
| note.nx2d_corridor | CURRENT |  | `WORK:results/hydroacoustics-nx2d-corridor.md` | 1 | 0.000 | WORK:results/hydroacoustics-nx2d-corridor.md L[2, 13] |
| note.overnight_2026_10_22_summary | KNOWN_DEFECT | D01, D02, D05, D07 | `WORK:results/hydroacoustics-overnight-2026-10-22-summary.md` | 1 | 0.000 | WORK:results/hydroacoustics-overnight-2026-10-22-summary.md L[1, 9] |
| note.pair_tests_oct09 | CURRENT |  | `WORK:results/hydroacoustics-pair-tests-oct09.md` | 1 | 0.000 | WORK:results/hydroacoustics-pair-tests-oct09.md L[1, 4] |
| note.pleiades_test_preregistration | CURRENT |  | `WORK:results/hydroacoustics-pleiades-test-preregistration.md` | 1 | 0.000 | WORK:results/hydroacoustics-pleiades-test-preregistration.md L[1, 6] |
| note.pleiades_test_standin | CURRENT |  | `WORK:results/hydroacoustics-pleiades-test-standin.md` | 1 | 0.000 | WORK:results/hydroacoustics-pleiades-test-standin.md L[1, 7] |
| note.prior_work_critique | CURRENT |  | `WORK:results/hydroacoustics-prior-work-critique.md` | 1 | 0.000 | WORK:results/hydroacoustics-prior-work-critique.md L[1, 3] |
| note.ram_tl_check | CURRENT |  | `WORK:results/hydroacoustics-ram-tl-check.md` | 1 | 0.000 | WORK:results/hydroacoustics-ram-tl-check.md L[1, 4] |
| note.references | CURRENT |  | `WORK:results/hydroacoustics-references.md` | 1 | 0.000 | WORK:results/hydroacoustics-references.md L[1, 4] |
| note.run_c_windows | CURRENT |  | `WORK:results/hydroacoustics-run-c-windows.md` | 1 | 0.000 | WORK:results/hydroacoustics-run-c-windows.md L[1, 3] |
| note.run_j_levels | CURRENT_WITH_CAVEATS | D01, D05, D25 | `WORK:results/hydroacoustics-run-j-levels.md` | 1 | 0.000 | WORK:results/hydroacoustics-run-j-levels.md L[1, 5] |
| note.run_j_windows | CURRENT |  | `WORK:results/hydroacoustics-run-j-windows.md` | 1 | 0.000 | WORK:results/hydroacoustics-run-j-windows.md L[1, 3] |
| note.search_windows_ref289 | CURRENT |  | `WORK:results/hydroacoustics-search-windows-ref289.md` | 1 | 0.000 | WORK:results/hydroacoustics-search-windows-ref289.md L[1, 12] |
| note.searches_run_j | CURRENT_WITH_CAVEATS | D06, D24, D26 | `WORK:results/hydroacoustics-searches-run-j.md` | 1 | 0.000 | WORK:results/hydroacoustics-searches-run-j.md L[1, 5] |
| note.synthetic_composer_test | CURRENT |  | `WORK:results/hydroacoustics-synthetic-composer-test.md` | 1 | 0.000 | WORK:results/hydroacoustics-synthetic-composer-test.md L[1, 5] |
| note.tl_grid_run_j | CURRENT_WITH_CAVEATS | D01 | `WORK:results/hydroacoustics-tl-grid-run-j.md` | 1 | 0.000 | WORK:results/hydroacoustics-tl-grid-run-j.md L[1, 9] |
| note.weak_signal_methods | CURRENT_WITH_CAVEATS | D05 | `WORK:results/hydroacoustics-weak-signal-methods.md` | 1 | 0.000 | WORK:results/hydroacoustics-weak-signal-methods.md L[1, 9] |
| note.source_access_ledger_2026_10_22 | CURRENT |  | `WORK:results/source-access-ledger-2026-10-22.md` | 1 | 0.000 | WORK:results/source-access-ledger-2026-10-22.md L[1, 3] |

## Code

| id | status | defects | path | files | GB | definition source |
|---|---|---|---|---|---|---|
| code.module_prepare | CURRENT |  | `MOD:prepare` | 162 | 0.004 | NO DEFINITION LOCATED |
| code.module_engine | CURRENT |  | `MOD:lib.rs` | 1 | 0.000 | MOD:lib.rs L[1, 12] |

## Defects

| id | defect | what | fixed in this run | affects |
|---|---|---|---|---|
| D01 | Old coupling value 2.1e-4 used as the F-35A "upper anchor" | 2.1e-4 is Brown 2026's Arons-equivalent coupling, a different quantity. Under the module definition the F-35A value from Metz 2023 is 2.26e-3 (pending ruling). Every "x F-35A" multiple on 2.1e-4 is 10.8 times too high. | partly: new register gives both multiples; old products keep the label | ex.arrival_windows, ex.kadri_package_v2, ex.levels, ex.ranked, ex.run_j_gated, ex.run_j_gated_v2, note.composition_run_j, note.f35a_eta_calibration, note.imos_ram_grid, note.injection_recovery_run_j, note.item3_injection_recovery, note.kadri_package_v2, note.overnight_2026_10_22_summary, note.run_j_levels, note.tl_grid_run_j |
| D02 | Diego Garcia (H08S) detections that coincide with airgun shots were ranked as candidates | 44 of 47 H08S single candidates lie within 1.5 s of a shot in h08s_template_shots.csv (chance about 30 %). The searches note itself said only residual rows are candidates (G-S9). Pete (23 Oct): a shot coincidence is not an exclusion; constructive interference and waveform distortion can still carry a detection. | label + envelope interference test in the new register | ex.arrival_windows, ex.ranked, note.overnight_2026_10_22_summary |
| D03 | Scott Reef 3250 used in pairs and triples although its path is blocked | 3250 carries no information (blocked path), but it is in most pairs and triples. | check column in new register | ex.ranked |
| D04 | Detections in bands below the receiver pass band | 2-5 Hz members at IMOS (hardware corner 8 Hz) and on Kadri panels (5 Hz high-pass) lie where the recording chain strongly attenuates; a detection there is unlikely to be impact sound in that band (a corner attenuates, it does not remove all energy). Labelled G-S8 in the searches note but kept in the ranking. | check column in new register | art.candidates_A_F, ex.ranked |
| D05 | Detection power measured only on model-matched templates | On the real F-35A arrival the M1b matched filter keeps only 0-3.4 dB of its model-matched gain; every P_D, eta50 and upper limit built on it is optimistic by about 4-10 dB. | no (next work card: real-arrival validation) | ex.injection, ex.kadri_predictions_v3, ex.levels, ex.register_2026_10_23, ex.run_j_gated_v2, ex.weak_signal, note.composition_run_j, note.injection_recovery_run_j, note.overnight_2026_10_22_summary, note.run_j_levels, note.weak_signal_methods |
| D06 | Stand-in noise backgrounds used without approval | H01W/H08S use IMOS 3376 noise shaped to Blackman medians (proxy); 3315 and 3275 nulls come from the paired logger. Declared, but Pete requires approval for stand-ins. | no (labelled) | ex.injection, ex.register_2026_10_23, ex.run_j_gated_v2, ex.searches, note.composition_run_j, note.injection_recovery_run_j, note.searches_run_j |
| D07 | Known events (Royer 2016) not removed from candidates | By the DIGITISED Royer marks, Kadri text time 00:52:03 lies inside the H01W-2 pick bar of icequake A (00:51:56.77-00:52:04.52) and caption time 00:54:30 is 5.9 s from the arrow for event 5 (00:54:24.06); Royer events 6 and 9 predict IMOS 3315 rows. Sensitivity: every digitised H01W-2 mark sits +7.7 to +16.6 s after Royer's Table 5 time for that event (other stations within about +/-5 s); against Table 5 the text time is +20 s from icequake A (00:51:42.99) and the caption time +17.6 s from event 5 (00:54:12.44). The figure-versus-table offset is an open question for Royer. "Time-consistent" is not identification. | known-event check column in new register | ex.arrival_windows, ex.kadri_package_v2, ex.ranked, note.kadri_package_v2, note.overnight_2026_10_22_summary |
| D08 | Coincidences whose direct path to the receiver crosses land | Example: Kadri 00:40:34 row x Portland 3275; 201 of 2,000 path points above sea level in GEBCO 2026. | land-path check column in new register | ex.ranked |
| D09 | Flight-only Pleiades layer used as if conditional on the Pleiades objects | Early candidate maps used the "post" layer, which is flight-only. | n/a (products withdrawn) | art.candidates_A_F |
| D10 | Candidates A-F withdrawn | Withdrawn at Pete's instruction, 23 Oct 2026, for six stated reasons. | n/a | art.candidates_A_F, art.feasibility_tables, art.take2_review |
| D12 | False "closed access / not held" labels on held sources (Metz 2023, Kadri 2019) | Corrected on 22 Oct; the source-access ledger keeps the old label as an audit trail. | already fixed 22 Oct |  |
| D13 | Kadri crash-panel timing check is exploratory with an incomplete model | Straight geodesic, one speed, no seismic (T-phase) path, inputs not from primary reports, H10S position not from the IMS station file, two events with assumed times. It is NOT evidence that Kadri's panel times are wrong. | relabelled | note.calibration_events_stage1b |
| D18 | Brief says the F-35A coupling is an "upper bound" because of a shallow channel | The Metz work found the shallow-channel effect +2.9 dB, NOT SUPPORTED at the 3 dB rule. | yes: brief paragraph replaced |  |
| D20 | Coupling prior bounds 1e-6..1e-2 were an agent choice, not a ruling | Pete ruled 23 Oct that coupling is a prior range with its sources and the F-35A value is one point in it; the bounds are open. The agent-chosen upper bound 1e-2 lies below some F-35A one-factor values in the Metz note (2 m source 5.4e-2; f^-4 roll-off 1.3e-1), so the current prior truncates part of that range. | no (ruling needed) | ex.run_j_gated_v2, note.composition_run_j |
| D22 | Old IMOS transmission-loss table (constant RAM correction, gap G-TL1) still used | Superseded by imos_tl_ram_arc.csv (RAM along the grid). | no re-run; labelled | ex.injection, ex.kadri_package_v2, ex.run_j_gated, note.injection_recovery_run_j, note.kadri_package_v2 |
| D23 | TL clamped at the table edge for rows outside the TL latitude span | 11-16 % of run J rows by stratum (17 Oct columns). | already fixed in run-j-gated(-v2) by the whole-arc TL grid | ex.run_j_tau_eof, ex.run_j_tau_scenario |
| D24 | Searches covered only the pre-registered windows | Held IMOS records outside the windows (for example the CMST 01:34 event) were not searched; free known-event checks were lost. | no (next work card) | ex.register_2026_10_23, ex.searches, note.searches_run_j |
| D25 | Source depth fixed at 10 m in the MH370 chain | At the F-35A, 2 m or 30 m moves eta by more than two decades. | no (labelled) | ex.kadri_predictions_v3, ex.levels, ex.register_2026_10_23, ex.run_j_gated_v2, note.run_j_levels |
| D26 | Cape Leeuwin and Diego Garcia p-values are not calibrated | Digitised plots at about 14.5 points per second with an emulated IMOS noise reference. | no (labelled) | ex.ranked, ex.register_2026_10_23, ex.searches, note.searches_run_j |

## Constants

| id | value | units | status | note | source |
|---|---|---|---|---|---|
| eta_F35A_metz | 0.00226 | fraction of impact kinetic energy radiated as sound (module definition) | PENDING_RULING | One point inside the coupling prior (Pete ruling 23 Oct). One-factor values in the Metz note table: 2.8e-4 (tau 0.05 s) to 1.3e-1 (f^-4 roll-off); 5.4e-2 at a 2 m source; 3.4e-4 at 30 m; full range over all cases 1.1e-5 to 6.3. | WORK:results/hydroacoustics-metz-f35a-anchor.md L[64, 73] |
| eta_brown_arons | 0.00021 | Arons-equivalent coupling (different quantity) | RETIRED_AS_ANCHOR | Do not use as the F-35A point for the module definition (10.3 dB low). | WORK:results/hydroacoustics-metz-f35a-anchor.md L[171, 171] |
| eta_prior_bounds | [1e-06, 0.01] | log-uniform, 41 points | AGENT_CHOICE_NOT_RULED | Pete: coupling is a prior range with its sources; bounds open. | EX:run-j-gated-v2/README.txt L[13, 13] |
| c_sofar | [1.482, 0.006] | km/s, mean and sd | CURRENT |  | WORK:results/hydroacoustics-searches-run-j.md L[91, 91] |
| pick_sd | 10 | s | CONVENTION_NO_LOCATED_SOURCE | Module convention; no published source located. | MOD:prepare/imos_detectors.py L[23, 23] |
| imos_hw_corner | 8 | Hz (IMOS hardware high-pass corner) | CURRENT |  | WORK:results/hydroacoustics-searches-run-j.md L[90, 90] |
| kadri_highpass | 5 | Hz (Kadri 2017 chain high-pass; 2024 adds 2-40 Hz band-pass) | CURRENT |  | WORK:results/hydroacoustics-digitised-sources.md L[212, 217] |
| imos_duty_cycle | [307, 900] | s recorded per s (about 34 %) | CURRENT |  | WORK:results/hydroacoustics-imos-noise.md L[18, 18] |
| gps_utc_2014 | 16 | s (GPS minus UTC, July 2012 to June 2015) | EXTERNAL_STANDARD | IERS Bulletin C; not in the repo. IMOS hex filenames are 16 s earlier than Portland rec_times.txt (session record). |  LNone |
| shot_window | 1.5 | s (H08S airgun coincidence label) | AGENT_CHOICE_NOT_RULED | Used by the Take 2 review; chance rate taken as 3/10 for a 10 s shot cadence. | ART:a35831fe/d28aa25a_hydroacoustics-take2-critical-review-2026-10-22.md L[159, 159] |

## Lines in the notes that still use a retired value or ruled-out wording

Found by `check_registry.py --stale --wording` after the status banners were added. Notes with a status other than CURRENT carry a one-line banner at the top that states the correction. Notes with status CURRENT carry no banner; each of their hits is marked below with the result of a review in this run. Lines that quote the old value in order to correct it are not listed.

| check | note | status | line | text (first 160 characters) | handling |
|---|---|---|---|---|---|
| STALE | note.audit_architecture | CURRENT | hydroacoustics-audit-architecture.md:125 | **F6 (low). Brown's η ≈ 2.1e-4 uses Arons' free-field shock law at 3,300 km.** Brown (2026) preprint, Eq. 2 on p. 9 and | reviewed: audit finding F6 about Brown's 2.1e-4 (Arons law); correct as written; no change |
| STALE | note.composition_run_j | CURRENT_WITH_CAVEATS | hydroacoustics-composition-run-j.md:7 | **Status: PREDICTIVE, NOT CALIBRATED. No detection is claimed.** The columns written tonight are the module's first likelihood term; **they do not enter the com | banner at top of note |
| STALE | note.composition_run_j | CURRENT_WITH_CAVEATS | hydroacoustics-composition-run-j.md:18 | - **η:** fixed 10⁻³, 2.1 × 10⁻⁴, 10⁻⁴; marginal over the 41-point log-uniform grid [10⁻⁶, 10⁻²]. | banner at top of note |
| STALE | note.composition_run_j | CURRENT_WITH_CAVEATS | hydroacoustics-composition-run-j.md:19 | - **Columns** (float32, row-aligned with `impacts32.npy`, 74 seeds, 313,599,968 rows, NaN = not computed — 0 rows tonight; 0.0 = no information): `hydro-lnL-imo | banner at top of note |
| STALE | note.composition_run_j | CURRENT_WITH_CAVEATS | hydroacoustics-composition-run-j.md:29 | **Table 1. 95 % upper limits on the coupling efficiency η from the non-detection (all latitudes 41–20°S), per 00:19 option and dive probability p; α = 0.05; IMO | banner at top of note |
| STALE | note.composition_run_j | CURRENT_WITH_CAVEATS | hydroacoustics-composition-run-j.md:214 | / η needed for the rows (searches, median impact) / H01W 0.026, H08S 1.5 (F-35A anchor 2.1e-4) / | banner at top of note |
| STALE | note.composition_run_j | CURRENT_WITH_CAVEATS | hydroacoustics-composition-run-j.md:247 | - **Parameter bounds with sources.** α 0.05 primary (13 Oct ruling, report level; 0.3 and 0.01 sensitivities); β = α/55 s (searches window); c 1.482 ± 0.006 km/ | banner at top of note |
| STALE | note.digitised_sources | CURRENT | hydroacoustics-digitised-sources.md:76 | η = 2.1 × 10⁻⁴ for 900 MJ. **The F-35A source spectrum needed by the TL-recalibration track therefore has to | reviewed: restates Brown 2026's Arons value as Brown's, and says the F-35A spectrum must come from Metz; no change |
| STALE | note.f35a_eta_calibration | SUPERSEDED | hydroacoustics-f35a-eta-calibration.md:16 | Stage B anchored η at 2.1×10⁻⁴, an inversion of Brown et al. (2026, p. 17) through Arons' explosive law, | banner at top of note |
| STALE | note.f35a_eta_calibration | SUPERSEDED | hydroacoustics-f35a-eta-calibration.md:48 | - **Comparison with Brown:** Brown's 2.1×10⁻⁴ falls inside this range. The two numbers are of different | banner at top of note |
| STALE | note.imos_ram_grid | CURRENT_WITH_CAVEATS | hydroacoustics-imos-ram-grid.md:8 | 2.1e-4) travel with every number here. Nothing in this note is timed; both Kadri times ("text time 00:52:03", "caption time | banner at top of note |
| STALE | note.imos_ram_grid | CURRENT_WITH_CAVEATS | hydroacoustics-imos-ram-grid.md:21 | 13.6 % (3315) and 0.2 % (3376) at the F-35A anchor η = 2.1e-4 (D0′, p = 0.5). With the new table they are **0.5 % and 1.9 %**; | banner at top of note |
| STALE | note.imos_ram_grid | CURRENT_WITH_CAVEATS | hydroacoustics-imos-ram-grid.md:56 | - **Drop-in rule** (`imos_tl_ram_arc.csv`, same schema as `imos_tl_ramcorr_arc.csv` plus `ram_grid_covered`, `ram_grid_mode`, | banner at top of note |
| STALE | note.imos_ram_grid | CURRENT_WITH_CAVEATS | hydroacoustics-imos-ram-grid.md:142 | 10/20/40 Hz, offset 0; bottom row old against new detectable shares at η = 2.1e-4 and 1e-3, both thresholds. Two footnotes as the | banner at top of note |
| STALE | note.imos_ram_grid | CURRENT_WITH_CAVEATS | hydroacoustics-imos-ram-grid.md:202 | consumed `imos_tl_ramcorr_arc.csv`; the Kadri package's `predictions.csv` IMOS TL columns and flags. The consumers' switch is one | banner at top of note |
| STALE | note.imos_ram_grid | CURRENT_WITH_CAVEATS | hydroacoustics-imos-ram-grid.md:225 | TL-grid tables (fc825c0..894a9e4; `imos_tl_ramcorr_arc.csv` for the raw adiabatic KRAKEN and the row schema), GEBCO 2026 15″, | banner at top of note |
| STALE | note.injection_recovery_run_j | CURRENT_WITH_CAVEATS | hydroacoustics-injection-recovery-run-j.md:13 | 3. **Detectability statement (deliverable 6).** Mapping received level back to coupling efficiency with the run J energies and the TL tables available tonight:  | banner at top of note |
| STALE | note.injection_recovery_run_j | CURRENT_WITH_CAVEATS | hydroacoustics-injection-recovery-run-j.md:179 | - **Parameter bounds with sources.** τ 0.11–10.59 s (run J tau90 5–95 %, method 1); ranges per receiver (run J 5–95 %, inputs.json); level −20..+30 dB (pre-regi | banner at top of note |
| STALE | note.item3_injection_recovery | CURRENT_WITH_CAVEATS | hydroacoustics-item3-injection-recovery.md:63 | / 10⁻⁴ to 2.1×10⁻⁴ (F-35A anchor) / **1.5×10⁻²** / **7.1×10⁻⁴** / | banner at top of note |
| STALE | note.item3_injection_recovery | CURRENT_WITH_CAVEATS | hydroacoustics-item3-injection-recovery.md:81 | 2. **The η anchor mixes definitions.** 2.1×10⁻⁴ is Brown's Arons-based coupling, an equivalent explosive | banner at top of note |
| STALE | note.kadri_package_v2 | KNOWN_DEFECT | hydroacoustics-kadri-package-v2.md:10 | F-35A upper anchor 2.1e-4). Both Kadri times carried everywhere: text time 00:52:03 and caption time 00:54:30.* | banner at top of note |
| STALE | note.kadri_package_v2 | KNOWN_DEFECT | hydroacoustics-kadri-package-v2.md:16 | / `predictions.csv` (1,720 rows × 81 columns), `predictions_meta.json` / `build_predictions_v2.py`: whole-arc grid of block 2 (`run-j-tl-grid/tables`, 41–20°S × | banner at top of note |
| STALE | note.kadri_package_v2 | KNOWN_DEFECT | hydroacoustics-kadri-package-v2.md:32 | - Mass-weighted 5–40 Hz 1 s SPL at H01W (q05 / q50 / q95): η 1e-2 99 / 104 / 113 dB; 1e-3 89 / 94 / 103; anchor 2.1e-4 82 / 88 / 97; 1e-4 79 / 84 / 93; | banner at top of note |
| STALE | note.kadri_package_v2 | KNOWN_DEFECT | hydroacoustics-kadri-package-v2.md:66 | - **Parameter bounds with sources:** c 1.482 ± 0.006 km/s (module standard, 55eb191); AGW 1.40–1.50 km/s (assumed); η grid {1e-2 … 1e-5} with anchor 2.1e-4 | banner at top of note |
| STALE | note.kadri_package_v2 | KNOWN_DEFECT | hydroacoustics-kadri-package-v2.md:73 | - `predictions.csv` gives per-band received level at the anchor η only (scale by 10 log10(η/2.1e-4)); the five-η sweep is given for the 5–40 Hz total. | banner at top of note |
| STALE | note.metz_f35a_anchor | PENDING_RULING | hydroacoustics-metz-f35a-anchor.md:84 | own 9 Oct calibration to about 1 dB** and shows that the 2.1 × 10⁻⁴ carried as the "upper anchor" since then was low by a | banner at top of note |
| STALE | note.metz_f35a_anchor | PENDING_RULING | hydroacoustics-metz-f35a-anchor.md:171 | / F-35A coupling anchor quoted in C2 / 2.1 × 10⁻⁴ (Brown/Arons) / **2.26 × 10⁻³** (single-factor spread 2.8 × 10⁻⁴ at τ 0.05 s to 5.4 × 10⁻² at a 2 m source) /  | banner at top of note |
| STALE | note.overnight_2026_10_22_summary | KNOWN_DEFECT | hydroacoustics-overnight-2026-10-22-summary.md:8 | η = 2.1e-4).** Read this note first, then the block notes it points to. Every block note has its own COVERAGE section and | banner at top of note |
| STALE | note.pleiades_test_preregistration | CURRENT | hydroacoustics-pleiades-test-preregistration.md:81 | - IMOS: KRAKEN adiabatic TL corrected by RAM (`results-data/ram_check/imos_tl_ramcorr.csv`). | reviewed: pre-registration of 10 Oct records the table used then; historical; no change |
| STALE | note.run_j_levels | CURRENT_WITH_CAVEATS | hydroacoustics-run-j-levels.md:7 | **Status: PREDICTIVE, NOT CALIBRATED.** Every number here carries **C1** (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S; after the TL-recalibr | banner at top of note |
| STALE | note.run_j_levels | CURRENT_WITH_CAVEATS | hydroacoustics-run-j-levels.md:11 | At the F-35A upper anchor of the coupling efficiency (η = 2.1e-4), under the primary option (00:19 held out, D0′, dive probability p = 0.5), the **median simula | banner at top of note |
| STALE | note.run_j_levels | CURRENT_WITH_CAVEATS | hydroacoustics-run-j-levels.md:21 | - **Source model** (the per_impact_lnl / lhyd chain, re-implemented as in the TL-grid evidence view): acoustic energy η E with E = `energy_transferred_j` = tota | banner at top of note |
| STALE | note.run_j_levels | CURRENT_WITH_CAVEATS | hydroacoustics-run-j-levels.md:45 | / Receiver / η = 2.1e-4: SNR q10/q50/q90 / share MF / base / η = 1e-3: SNR q10/q50/q90 / share MF / base / blocked mass / η₅₀ MF / η₅₀ base / | banner at top of note |
| STALE | note.run_j_levels | CURRENT_WITH_CAVEATS | hydroacoustics-run-j-levels.md:59 | **Per option and p (matched-filter share at η = 2.1e-4 / 1e-3, p = 0.5):** H01W 8.8 / 23.0 % (D0′), 11.8 / 26.6 % (D2), 10.4 / 46.0 % (D3), 19.8 / 56.2 % (D4);  | banner at top of note |
| STALE | note.run_j_levels | CURRENT_WITH_CAVEATS | hydroacoustics-run-j-levels.md:67 | - `hydroacoustics-run-j-levels-noise-vs-levels-<station>` (8) and `-overview` (2 × 4): background percentiles (median, 10–90 %) per third octave against the pre | banner at top of note |
| STALE | note.run_j_levels | CURRENT_WITH_CAVEATS | hydroacoustics-run-j-levels.md:85 | - **Parameter bounds with sources.** η 1e-6–1e-2 (brief: four decades around the F-35A anchor 2.1e-4, `f35a_eta_calibration`); τ_ac 0.05–10 s (lhyd TAU_GRID, ag | banner at top of note |
| STALE | note.tl_grid_run_j | CURRENT_WITH_CAVEATS | hydroacoustics-tl-grid-run-j.md:8 | octave at H01W/H08S) and **C2** (coupling efficiency not calibrated; η swept over four decades, F-35A upper anchor 2.1e-4). | banner at top of note |
| STALE | note.tl_grid_run_j | CURRENT_WITH_CAVEATS | hydroacoustics-tl-grid-run-j.md:140 | Scott Reef ≤ 48 against 107.8; H08N ≤ 54 against 90.2. **At the F-35A upper anchor (η = 2.1e-4) the median impact at its most | banner at top of note |
| STALE | note.tl_grid_run_j | CURRENT_WITH_CAVEATS | hydroacoustics-tl-grid-run-j.md:186 | - `imos_tl_ramcorr_arc.csv` — schema of `ram_check/imos_tl_ramcorr.csv` (+ lat, lon, offset_nm, `tl_db_raw_kraken`, flags). | banner at top of note |
