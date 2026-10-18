# Drift items 1-8 on run J (architecture stand-in, 17 Oct 2026)

Ordered by Pete 17 Oct 2026 ("work through all 8"). No new forcing downloaded. Items 1-6 use stored runs only; items 7-8 used deskstar.
All results D0' (00:19 data held out, cell `D0 total q=0.333 (C2 silent)`) unless stated; two ocean models with equal weight
(GLORYS12V1 0.494 m + ERA5; GlobCurrent my-p1d 0 m + ERA5, product-relative windage U(-0.75,-0.60) % U10). Drift surfaces: run A rebuilt
(`results/debris-drift-runA-rebuilt`), h = 50 km.

## 1. All four run J flight-path families scored against drift

Scoring: `scripts/drift_columns_inmem.py` = drift's `export_per_impact.py` column definitions with `score_impacts.lookup` and
`surface_arrays` unchanged, computed in memory (not written: the Mac had 16 GiB free; the columns are about 10 GB and regenerate in
about 10 s per seed). Check: run J waypoints seed-1, 6,399,872 rows, 22 fields, 0 differences from the stored `drift-lnL.npy`
(`scripts/validate_inmem.py`). Composition: `scripts/compose_drift_runj_family.py` (= `compose_drift_runj.py` with STRATUM env);
statistics `analyze_runj.py` unchanged; Australian term `apply_australia.py` unchanged except the input npz.

| Family | Seeds | Core lat 5/50/95 % | Shift (no AU) | 95 % transport noise | seed SD | ln BF | Shift, populated AU | ln BF |
|---|---|---|---|---|---|---|---|---|
| waypoints | 24 | -38.40/-37.12/-33.87 | +0.696 | -0.12..+1.45 | 0.027 | -0.755 | +4.439 | -2.296 |
| free | 18 | -38.54/-36.42/-32.01 | +0.675 | -0.31..+1.33 | 0.039 | -0.397 | +4.055 | -1.556 |
| descent-climb | 16 | -38.59/-36.98/-33.63 | +0.621 | -0.42..+1.33 | 0.045 | -0.510 | +4.185 | -1.909 |
| repro-radar | 16 | -38.43/-36.44/-30.49 | +0.741 | -0.42..+1.45 | 0.020 | -0.374 | +4.329 | -1.439 |

All treatments D0-D5: `drift-by-flight-family.csv`; full statistics `by-family/analysis-runj-<family>.json`, `by-family/aus160-<family>.json`.
Not computed share 0.033-0.106 %. Family pooling is the composer's step and is not done here.

## 2. Detection-level curve for the populated-coast Australian term

Delta = -k ln(1 + rho W_pop / (c F)) per model, rho = detection level on populated Australian coasts relative to the find coasts
(rho = 1 reproduces the headline sensitivity +4.439 / -2.296; rho = 0 reproduces no term +0.696 / -0.755). `detection-curve-D0.csv`,
`detection-curve.json` (D0-D5), `detection-curve-ext.json` (rho 4-8). D0 two models: rho 0.1 +1.26, 0.3 +2.21, 0.5 +2.99, 1 +4.44, 2 +6.14, 3 +7.08.

## 3. Uncertainty of the Australian term (rho = 1, D0)

200 replicates each (`aus-noise.json`): node noise only 95 % +4.00..+4.91; plus pilot Delta Monte Carlo noise +3.73..+4.97; plus law
misfit +3.64..+5.22 (ln BF -2.49..-2.09). Seed bootstrap SD 0.049.

## 4. Sinking (biofouling) sensitivity

Survival exp(-t/tau) on the first-beaching day (snapshot harness, core PDF draws, to 30 Jun 2016). Australian arrivals are early (quartiles
day 202/242/321), find-coast arrivals late (504/570/693), so sinking acts as a higher effective detection ratio rho_eff = mean survival
(Australia) / mean survival (find regions). Core PDF: tau 1/2/3 yr -> rho_eff 2.27/1.52/1.32 -> shift +6.39/+5.45/+5.08 at rho = 1
(`sinking-effect.csv`). Approximation: k and c held fixed; region boxes, not segments.

## 5. Find-timing check

For the nine primary finds (`debris-evidence-audit.csv`, decision primary*), the modelled first-arrival dates within 100 km of each site
(`find-timing-check.csv`, figure `find-timing-check.png`). Share of modelled arrivals before the find date, core vs 30 S: Reunion
0.22 vs 0.54, Mossel Bay 0.15 vs 0.37, Paindane 0.23 vs 0.55. Descriptive only (no detection or reporting model).

## 6. Pleiades under the Australian term

`pleiades-australia.json`: ln factor at the six rating-5 targets (two models, mean in L) -1.373 at rho = 1, core -2.125; ln LR Pleiades vs
core from this term alone +0.752 (rho 0.1 +0.227, 0.3 +0.488, 2 +0.696). Approximation: the targets' 23 Mar release is treated as the
8 Mar node surface.

## 7. Targeted refinement of the core nodes (deskstar, 17 Oct 2026)

The 94 run A nodes carrying 95 % of the run J D0' core mass (39.2-32.7 S, 88.1-96.3 E; `scripts/nodes94.json`) were re-run with drift's
production configs (`refine-core94/refine-core94-<model>.toml`: deskstar forcing, independent seeds: seed 2, environment seeds 5-8,
1e5 particles per node, 15-120 E). Node tables: `refine-core94/refine-<model>-nodes.csv`. Comparison `refine-core94.json`
(`scripts/refine_compare.py`):
- independent minus stored ln L: mean +0.25 / +0.19, SD 1.57 / 1.63 (GLORYS12 / GlobCurrent), i.e. about 1.1 per node per run;
- finds only, two models: shift +0.70 (stored), +0.93 (independent), +0.81 (pooled = mean in likelihood); ln BF -0.755 / -0.770 / -0.763;
- headline Australian scheme (tiers 1/0.3/0, level 0.5): +3.83 / +3.81 / +3.82; ln BF -2.12 / -2.06 / -2.09.
The pooled values are the best current estimate. The finds-only shift is still noise-limited (95 % transport-noise half-width
about 0.8 before pooling, about 0.55 after, against the brief's 0.5 trigger); the Australian-term result is not.

## 8. Refloat sensitivity (deskstar snapshot harness v2, 17 Oct 2026)

`scripts/snapshots_onshore.rs` (untracked test on deskstar's drift copy; records where each object is onshore at each output time),
core PDF releases (mode + 200 draws), both models, refloat off / 1/200 / 1/69 per day (`refloat-summary.csv`,
`refloat-onshore-by-time.csv`). First beaching is unchanged by refloat (identical shares). With refloat, beached objects come ashore
3.4 (1/200) or 6.5 (1/69) times on average; afloat at 2 years 44 % (off), 49 % (1/200), 54 % (1/69). The onshore ratio Western Australia :
find regions falls by 3-13 % (1/200) and 7-28 % (1/69). Treated as a proportional change of the Australian detection ratio, the
headline shift +3.83 becomes about +3.5..+3.7 (1/200) and +3.1..+3.7 (1/69). A drift likelihood run with refloat on would settle it.

## Australian scheme (Pete, 17 Oct 2026)

`australia-three-tier.csv`: ABS tiers 1 / 0.3 / 0 (major city + inner regional / outer regional / remote), level 0.3-0.65, central 0.5.
D0' two models: +2.84 / +3.83 / +4.42 deg at 0.3 / 0.5 / 0.65; D1-D5 at 0.5: +3.55..+4.37. Agrees with the arc-latitude thread
within 0.05 deg. `australia-awareness-by-period.csv`: 95 % of Western Australian arrivals fall before the flaperon.
