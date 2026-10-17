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

## Status at commit (17 Oct 2026)

Items 1-6 done. Items 7 (94-node refinement) and 8 (refloat snapshots) running on deskstar, ~/mh370/drift/job3 (chain3.sh);
results to follow. Detection-level discussion with Pete and the arc-latitude thread is open (see drafts/ocean-drift-v2-DRAFT.md, section 5,
which still carries the withdrawn "10x" wording until Pete rules).
