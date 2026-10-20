# MH370 waypoint hypotheses — 19 September 2026

This archive contains a completed **exploratory calculation**, not a calibrated wreckage-location probability distribution. The main route is MEKAR–NILAM–IGOGU–BULVA–ISBIX. RUNUT is tested separately and never imposed on the main ensemble.

## What is established

- The main route has a three-turn witness passing all declared pre-exhaustion gates at a one-second integration step. Its exhaustion point is approximately 35.1987°S, 92.3964°E. This is a feasibility example, not a probability peak.
- The final integration uses 2,883,584 proposals across ten turn/altitude classes and two independent fixed-proposal replicas for the supported 3/4-turn classes. It retains 15,434 positive importance contributions. ESS is 4.801; the largest contribution has 40.30% weight. Replica normalizing-constant estimates differ by a factor of about 6.3. Refinement history also shows missing-mode risk. **The density has not converged.**
- All 48 largest contributions, accounting for 95.78% of the sampled weight, pass when recomputed at one-second resolution. Endpoint differences are at most 150.3 m. Numerical time-step error is not the main identified limitation in these dominant contributions.
- There is no retained main-route passage within 5, 10 or 20 NM of RUNUT. This finite, low-ESS result cannot exclude true conditional support. A direct-prefix search fails the 19:41 arc/time condition; a four-turn detour comes within 5.010 NM but has a maximum BFO residual of 11.24 Hz versus the 8.6-Hz limit. The latter exhausts at 00:17:30 between the two nominal arcs, so those conditions alone are insufficient.
- Main EoF: 49,152 simulations, 42,897 modeled impacts, 38,528 compatible with the final R600 range gate, and 1,652 additionally compatible with the final-BFO oscillator feasibility envelope. Parent-group ESS remains about 4.7. The 12 EoF families have an explicit equal-weight sensitivity prior, not calibrated behavioral probabilities.
- Baseline EoF: 98,304 simulations, 85,045 modeled impacts, 75,997 range-compatible, and 403 also final-BFO-envelope-compatible. Its pre-existing original importance ESS was about 345; later resampling does not create independent information.
- The strongest main-ensemble distant alignment is Patriot Hills: 48.6% within 1°, catalog-maximum control p=0.355. The earlier IGOGU ensemble's Vostok alignment is 39.3%, adjusted p=0.474. Neither supports an intended destination under this control.
- The full synthetic-data generation/reconstruction null is **not completed**. Spatial randomization is a separate conditional test. A reliable reconstruction estimator is needed to calibrate the entire procedure.

Read `output/pdf/MH370_waypoint_hypotheses.pdf` first. The report distinguishes trial maps, established feasibility, conditional controls and unresolved inference.

## File map

- `inputs/analysis_protocol.json`: route, priors, observational gates and RUNUT scope. It records the recovered trusted early-observation decision; do not silently reintroduce excluded early BTOs.
- `inputs/observations.csv`, `legacy_observations.csv`, `early_exchange.csv`, `satcom_source.csv`, `satellite_ephemeris.csv`: flight-data inputs and trace provenance.
- `inputs/weather.bin`, `weather_manifest.json`: pinned inherited ERA5 cruise weather.
- `inputs/terminal_weather.bin`, `terminal_weather_manifest.json`: independently extended genuine ERA5 coverage, 00:00–02:00 UTC and 500–60,000 ft. Shared original hours/levels agree exactly. Weather below 500 ft is held at the lowest level during descent; no upper-altitude/time extrapolation is used.
- `inputs/previous_EoF_configuration.json`: recovered control-range source. The point-mass implementation preserves the stated envelope, not a validated full-fidelity Boeing dynamics model.
- `inputs/pleiades_equal_thirds_grid.csv`: archived conditional source mixture. It is an overlay only, never an extra flight likelihood.
- `inputs/caption_search_areas.kml`: historical search outlines and 2024 proposal sketches, not authoritative latest remaining-area polygons or sonar detection masks.
- `output/physical_v6_a`, `physical_v6_b`: final independent importance contributions, with seed and proposal count per cell. `physical_proposal_round6_*.npz` contains their fixed proposals.
- `output/prior_cells`: full-prior checks for 0–2 turns. Zero-hit cells are unresolved, not impossible.
- `output/main_exhaustion_states.npz`, `main_summary.json`: assembled exploratory main measure and diagnostics.
- `output/main_exhaustion_states_eof.npz`, `baseline_eof_a.npz`: linked EoF samples, source indices, controls, family labels and terminal weights.
- `output/*_families.csv`, `*_summary.json`: family contributions, model-domain failures and ESS diagnostics.
- `output/control_paths.npz`, `pair_null_*.npz`, `catalog_null_*.npz`, `spatial_controls.csv`: retained baseline path resample and spatial controls.
- `output/destination_alignment.csv`, `main_destination_alignment.csv`, corresponding null/summary files: all 6,587 candidates and catalog-maximum controls.
- `qa/final_audit.json`, `main_final_step_check.npz`, `eof_convergence.json`, `eof_energy.json`: focused numerical/geometric checks.
- `figures`: report figures at standalone resolution.

## Run status and evidence boundaries

`physical_v6_a/b` are the final integration draws. Earlier `physical_v2`–`physical_v5`, `fine_importance_a/b`, MCMC training, DE/Powell optimization, and `run_a`, `flyby_a`, `trusted_efg_a`, `flexible_a` are development or adaptation evidence. **Do not pool their normalized weights as independent posterior draws.** `initial_sampler_pilot` preserves the earlier ESS≈1 importance result. `cruise_weather_eof_pilot` preserves superseded terminal runs whose weather domain was too short. Neither is the released main result.

RUNUT files with `best`, `refined`, `detour` or `prefix` in their names are optimization candidates. They are not posterior samples and not certificates of a global constrained optimum. A slightly better objective can still violate a hard gate.

No Bayes factor between the newly constrained route and the older IGOGU model is claimed: their data conditioning and route assumptions differ. Equal turn/altitude priors are propagated within the new route. EoF normalization conditions on modeled admissible impacts and does not allocate a location distribution to out-of-model failures.

Final-BFO compatibility asks whether there exist offsets 0 ≤ b2 ≤ b1 ≤ 130 Hz leaving both residuals within ±8.6 Hz. This is an envelope, not a calibrated oscillator likelihood. The R600-only and additional-envelope maps are distinct conditional quantities.

## Reproduce the saved analysis

Python packages are pinned in `requirements.txt`. Python 3.12.14 and a C++17 compiler with OpenMP were used. `pdftoppm` is needed only for PDF visual QA. Use a fresh copy before running commands that overwrite outputs.

```bash
python -m pip install -r requirements.txt
python code/build_engine.py
python code/assemble_main.py --source physical_v6
python code/final_audit.py
python code/eof_model.py
python code/run_eof.py --states main_exhaustion_states --draws 4096 --seed 260919
python code/run_eof.py --states baseline_exhaustion_states --draws 8192 --seed 260919 --label baseline_eof_a
python code/destinations.py --states main_exhaustion_states --label main_destination
python code/report.py
```

`model.py` compiles a source-hashed shared engine automatically. `report.py` is the final report generator. `refresh_report.py` is an archived one-off migration and deliberately refuses execution. `report_pages.txt` is an earlier template retained for provenance; use `report.py` as authoritative.

To repeat a final importance cell using its already-frozen round-6 proposal, for example:

```bash
python code/physical_importance.py --turns 3 --alt 0 --round 6 --draws 262144 --seed 266300 --output replay_3_0_a
```

The recorded `cell_*.json` files contain each final seed. Repeating the adaptation rounds is unnecessary for replaying the final fixed proposals, and must not be confused with improving convergence.

`prepare_controls.py` and `prepare_baseline_eof.py` document extraction from the previously saved IGOGU recovery packages. They require those earlier packages to regenerate the pre-existing source estimator. Their ready-to-use outputs (`control_paths.npz` and `baseline_exhaustion_states.npz`) are included, so the new controls, EoF analysis and report can be reproduced without reconstructing that older inference.

Weather-file integrity is recorded in `CHECKPOINT.json`; the terminal engine additionally verifies its weather SHA-256 at load. `terminal_weather.py` documents and can repeat the raw ERA5 extension, requiring network access and approximately 1 GB of compressed source downloads. Ordinary replay uses the bundled derived files and does not need these downloads.

## Interpretation of figures and search status

The main fuel map shows the sampled cloud and weighted contributions; it is not a credible-region estimate. Impact contours use 20-km Gaussian smoothing on an equal-area grid. They visualize the trial sensitivity mixture and inherit its parent sampling limitations. Geometric overlap fractions in `map_statistics.json` are numerical summaries of the current weights, not calibrated wreck-location probabilities.

The official Malaysian Ministry of Transport statement of 29 June 2026 identifies 7,428.54 km² remaining, an agreement through 30 June 2027, and a November 2026–April 2027 asset window. The report links the primary statement. No authoritative remaining-area geometry or detection-quality coverage mask was obtained, so the analysis does not report an exact latest-search overlap percentage.

Waypoint and airport coordinates are treated conditionally; 2014 existence has not been universally authenticated. Antarctic direction does not imply fuel reachability or landing feasibility. Pléiades object association remains unverified. A reliable main density, a calibrated full-reconstruction null, and a definitive RUNUT exclusion remain open.
