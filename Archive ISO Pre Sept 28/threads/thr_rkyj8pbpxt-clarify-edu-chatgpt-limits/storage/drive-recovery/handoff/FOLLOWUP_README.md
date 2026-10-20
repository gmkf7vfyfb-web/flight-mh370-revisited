# IGOGU conditional: continuation handoff

This directory is the 19 September 2026 follow-up to the conditional IGOGU run. It preserves all original positive-weight trajectories by replaying the original seeds, tests the newly requested R600 seventh-arc observation, overlays the existing equal-thirds Pléiades source mixture, inspects initial tracks, and diagnoses 100 exact-due-south cases.

The original inference remains unchanged and provisional. The new R600 results are explicit terminal-motion sensitivities, not a validated post-fuel-exhaustion or wreckage posterior. No 00:19 BFO is used.

## Read first

- `output/mh370_igogu_followup.pdf`: six-page report with all four requested analyses.
- `output/seventh_arc_summary.json`: exact importance-weight results, terminal assumptions and reference observation.
- `output/pleiades_mixture_summary.json`: equal thirds, normalization and mode.
- `output/initial_path_summary.json`: initial-course posterior and representative-path FIR comparison.
- `output/due_south_summary.json`, `output/due_south_geometric_bound.json`: sampling result and model-conditional geometric exclusion.
- The original nine-page PDF and original complete archive remain in the Drive folder as separate artifacts.

## Observational and modeling boundaries

The original conditional starting state is IGOGU, 7°31'01"N, 94°25'E, arrival normal 18:38 UTC with 60 s standard deviation truncated 18:36-18:40. There are equally weighted 0-4 additional turns after the required initial turn. Altitude classes are 50% constant and 50% two cruise step climbs. Fuel exhaustion is constrained by the specified triangular likelihood, 00:15-00:19, mode 00:17:30. The original priors, observations and public fuel/performance approximations are in the original archive.

Original BTO/BFO position likelihood ends at 00:10:59.928. The original model used BTO sigma 29 us, BFO sigma 4.3 Hz, hard two-sigma checks, and both phone-call BFO series. Original 00:19 use was fuel-event timing only. The present user explicitly requested a separate test using the 00:19:29.416 R600 BTO. Its raw 23000 us minus the 4600 us channel correction gives 18400 us. Table 10.1 in Davey et al. assigns sigma 63 us to that observation (the general R600 discussion gives 62 us). The present two-sigma test is therefore +/-126 us. Neither 00:19 BFO nor the 00:19:37 R1200 BTO is added.

Fuel-exhaustion positions are earlier than the R600 epoch. The terminal sensitivity continues the last horizontal ground speed and geodesic course without additional turns. Four descent assumptions are reported: 0, 1000, 3000 and 6000 ft/min, with height floored at zero. This is kinematic extrapolation, not a physical glide/impact model. An additional any-height/all-heights envelope is compatibility only and has no probabilistic altitude interpretation.

The nominal arc-centre crossing within +/-60 s is also supplied as a separate diagnostic. It is not the primary R600 Gaussian range test. Imposing that rule on all earlier contacts remains the poorly supported legacy subset of the original run.

## Main numerical results

- Recovered exactly 1,710,701 original positive-weight trajectories from the 8,388,608 final proposals. Each cell's recovered endpoint array is bitwise equal to its archived endpoint array in the original order.
- The original largest draw has weight 0.0462624596, exhaustion at 31.5519329°S, 95.4003175°E, about 99.392 km inside the nominal seventh arc at its altitude. Its terminal course is westward. Constant-height continuation gives residual -665.125 us, -10.558 sigma, and fails. It also fails all tested descent variants.
- Constant-height R600 selection retains 1,525,595 raw draws and 95.2071% of the original weight. After Gaussian reweighting and the gate, exhaustion-position coordinate medians are 34.0741893°S, 93.7477160°E. Importance ESS is 1000.48; largest weight remains 1.7054%, so the original 1% convergence criterion still fails.
- Initial true-ground-course median is 184.3635°, central sampled 95% 183.9258-184.8078°. The original prior allowed 150-210°, not exactly 180°. Finite initial turns shift tracks west of the FIR line. The representative path sample crosses 6°N near 94.100°E, about 35 km west of the FIR boundary; this is a display-sample statistic.
- All 100 physically/fuel-feasible exact-180° cases pass the 18:40 call gate but first fail at the 19:41 BTO, with residuals +199.925 to +254.236 us versus +/-58. No case passes all pre-00:19 checks or the continued R600 gate.
- These diagnostic exhaustion endpoints range 33.9861-39.1926°S, median 36.8295°S, longitude 94.1503-94.2218°E. Distance to the nominal R600 arc at each endpoint's own altitude is 5.158-422.835 km, median 230.119 km, on the longer-range side. This direct endpoint comparison is geometric, not the observation-time likelihood.
- A conservative bound rules out that exact-due-south continuation within the frozen initial-turn model. Even assigning the entire maximum 46.882 km initial-turn path westward cannot put it west of 93.990837°E. At any latitude, even at 41000 ft, the 19:41 +2-sigma boundary reaches only 93.932099°E. Best residual at the conservative longitude bound is +82.641 us, still over +58. This does not rule out other initial-turn rules, other initial courses or later maneuvers.

## Pléiades inputs and mixture

`inputs/pleiades/grid.csv`, `surfaces.csv` and `manifest.json` were retrieved from the existing Drive source-surface handoff. Their grid/surface byte hashes match that manifest. Source folder: https://drive.google.com/drive/folders/1WBdiH5VuL11sCHULVkD6HsH7t94DimtO

The overlay is the arithmetic mean of the three independently area-normalized densities: BRAN2016, OSCAR v2 Final and GLORYS12/WAVERYS, each weight 1/3. It matches the already saved equal-family mixture. It is not a product of the three models, and the flight and drift layers are not fused. The source assumes exactly one associated object among twelve rating-5 image locations; identity is unknown. The finite grid edge is uncomputed support, not evidence of zero probability outside. No calibrated model evidence exists for changing the family weights.

The mixture mode is 35.217849°S, 92.246983°E. Its separation from the original flight coordinate-median point is about 189 km. The source surface refers to 00:19 source/impact time, whereas the original flight density is at fuel exhaustion.

## Restore and run

Use the top-level `restore_igogu.py` supplied in the Drive folder to reassemble and SHA-256-check all split archives. Extract the original IGOGU archive so `mh370_igogu_conditional/` (or the original workspace name `igogu_conditional/`) is a sibling of this `igogu_followup/` directory. The original archive includes the actual ERA5 weather bytes, so no original scratch symlink is required after extraction.

Requirements: Python 3.12 with the original pinned numpy, scipy, pandas, pyproj, matplotlib dependencies; g++ supporting C++17 and OpenMP. PyMuPDF is used only for rendering/QA. `OPENBLAS_NUM_THREADS=1` prevents excessive thread contention.

```bash
OPENBLAS_NUM_THREADS=1 python igogu_followup/code/recover_survivors.py
OPENBLAS_NUM_THREADS=1 python igogu_followup/code/check_seventh_arc.py
OPENBLAS_NUM_THREADS=1 python igogu_followup/code/due_south.py
OPENBLAS_NUM_THREADS=1 python igogu_followup/code/geometric_bound.py
OPENBLAS_NUM_THREADS=1 python igogu_followup/code/make_followup_report.py
```

The replay skips already saved recovered cells. It is not a new Monte Carlo run and introduces no new evidence or adaptation. The diagnostic engine is a separate instrumented copy. Its first 24 output columns reproduce the original model when the diagnostic control flag is off; a 128-case bitwise check and every surviving endpoint are checked.

## Machine-readable schemas

`output/recovered/{refined_a,refined_b}_{turns}_{altitude}.npz` contains all surviving `u` (unit-prior coordinates), `values` (40-column diagnostic output), exact `log_weights`, original `proposal_indices`, and scalar `proposal_count`. `u` dimensions and decoding remain the original `model.py` contract. Altitude class 0 is constant, 1 is step climbs. Turn counts exclude the first IGOGU turn.

`values[:,0:24]` are the original output contract documented in the original code. Added fields: 24 endpoint ground speed m/s, 25 true ground course radians, 26 vertical speed m/s, 27 exhaustion seconds after 18:22:12 UTC, 31 diagnostic rejection stage (1 turn timing, 2 fuel anchor, 3 physical checks, 0 physically feasible), 32-34 raw endpoint latitude/longitude/height before fuel gating. Other added columns are reserved zero.

`output/seventh_arc_measure.npz` keeps original weights, reweighted measures for each descent assumption, exhaustion positions (latitude degrees, longitude degrees, height metres), component columns (replicate index, additional turns, altitude class), constant-height R600 positions, residuals in microseconds, height-envelope compatibility booleans and nominal-centre-crossing booleans. All arrays retain the exact original endpoint ordering. Weighted PDF summaries use the raw independent importance weights, never resampled display counts.

`output/due_south_100.npz` contains physical parameters, values and observation states. Observation states follow original `OBS` row order with columns latitude, longitude, altitude m, ground speed m/s, true ground course rad, vertical speed m/s, predicted BTO us, predicted BFO Hz. `due_south_100.csv` provides the human-readable per-trajectory rejection and endpoint diagnostics. Paths are time, latitude, longitude, altitude, ground speed, true course, vertical speed.

`output/pleiades_equal_thirds_grid.csv` contains the original geometry and quadrature areas plus each component density, mean density per km² and quadrature mass. Density is for comparison; mass must not be multiplied into another probability grid as a likelihood.

## Suggested continuation

Keep this result separate from a claim of global MH370 localization. The largest-weight/convergence issue improved after the R600 check but has not disappeared. A properly probabilistic terminal/glide model would be needed before interpreting R600 reweighting as a final posterior; independent posterior exploration and aircraft/fuel calibration remain necessary. If exact FIR following is intended, implement and sample a new initial turn/intercept rule explicitly rather than relabeling these trajectories.

Primary references: released SATCOM logs https://www.atsb.gov.au/sites/default/files/media/5772619/public_mh370-data-communication-logs.pdf ; Davey et al., Bayesian Methods in the Search for MH370 https://link.springer.com/content/pdf/10.1007/978-981-10-0379-0.pdf . Historical FIR/airway sources are preserved in the separate `bto_arc_charts` package.
