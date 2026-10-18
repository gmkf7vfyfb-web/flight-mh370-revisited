# Work order — searched areas: a per-cell detection model (q and ρ as fields)

**Issued** 18 Oct 2026 by Pete (approved in chat). **Executed by** a general (default-profile) session working strictly to
`threads/master-prompts/searched-areas.md` and this order; it signs as "Searched Areas (general session)".
**Source** `project-assessment-2026-10-18.md`, §4 item 1 and §6 point 1. **Route** 2(b): the lower-confidence areas come from a
terrain proxy calibrated to ATSB 2017 Figure 73, without waiting for ATSB/GA polygons. **Rights** Pete, 18 Oct 2026: the project
has clear rights to use all searched-area information, including the community tracings and the 2014 search polygons.

## Why
The posterior's modal explanation under D3/D4 is "inside searched ground and missed" (0.57–0.66 of the all-evidence mass,
composer views v2). It rests on one q per campaign and one ρ. This order replaces both with fields built from the search record.
The contract does not change: one likelihood column per impact or settled outcome, `ln L = 0` off searched ground.

## Definitions (binding for this order)
P(no detection | x) = ρ(x) + [1 − ρ(x)] · Π_k [1 − c_k(x) · q_k(x)]
- `c_k(x)` coverage: the fraction of the cell with valid data for campaign k. For Phase 2 it is ALREADY measured from the GA 5 m
  mosaics (valid pixels, `prepare/build_coverage.py`), so mapped gaps are already out of `c`. Therefore `q` must NOT carry the gap
  class again (the 0.940 against 0.945 trap in Figure 73).
- `q_k(x)` detection given covered ground and a target in the detectable class (a field of at least 100 m × 100 m, ATSB 2017
  p. 83). For Phase 2: q(x) = [f_hi(x)·q_hi + f_lpd(x)·q_lpd] / [f_hi(x) + f_lpd(x)], where f_lpd is the lower-confidence fraction.
  The Figure 73 confidences are the likelihood that an analyst would detect the field, so they already include analyst review.
- `ρ(x)` the chance a field in covered, good-quality ground still could not be found (terrain masking below grazing angle, burial,
  out-of-class target). Shared by every pass over the cell (dependent misses). ρ(x) = ρ0 · w(x), with w a terrain weight of
  mean 1 over Phase 2 covered ground, so ρ0 keeps its meaning as the area-mean and the reference sweep stays comparable.

## Steps (in order)
1. **Grid.** Move the coverage record to 0.005° (about 500 m), the spacing at which the ATSB footprint was extracted (brief §6,
   the reminder owed to Pete). Reproduce the existing 0.01° `.cov` rasters from the same counts as a check.
2. **Terrain.** From the GA Phase 1 150 m bathymetry (CC BY 4.0) compute slope and roughness per cell.
3. **Lower-confidence proxy.** Digitise the green (LPD) and holiday overlays of ATSB 2017 Figure 73 (printed p. 96) at its native
   scale (about 2 km per pixel). Fit f_lpd(x) = logistic(terrain) to that density, then scale each Figure 73 sub-area (red, orange,
   yellow, purple) so its area-mean f_lpd equals the printed lower-confidence share (1.1 / 7.8 / 1.1 / 1.5 %). State the fit quality.
4. **q(x)** for Phase 2 as defined above. Bluefin-21 keeps 0.9 (no published value). Ocean Infinity keeps q = 0.9 (Stone et al.'s
   cap) but gets a **coverage-density field** in place of the uniform fraction: slow ship fixes (< 4 kn, MH370-CAPTION hourly AIS,
   grade C) smoothed with an AUV working radius, scaled so the total equals Ocean Infinity's searched area (2018: 112,000 km²;
   2025–26: 7,571 km²), capped at 1, and zero outside the traced outline.
5. **ρ(x)**: w(x) from the same terrain propensity as f_lpd, normalised to mean 1 over Phase 2 covered ground.
6. **Score** run J settled outcomes (settling `run-j`, five sets) and the impact points, with the variants below.
7. **Report** `results/searched-areas-spatial-detection/README.md` with a COVERAGE section; columns on the exchange at
   `searched-areas/run-j-spatial/` (READY last); reply in `coordination/architecture.md`; request composer views v3 with the
   three-way split table (on searched ground / glide tail beyond 25 NM / north of 25 S) and the Davey eq. 11.2 block table.

## Variants (pre-registered)
| id | q_hi | q_lpd | ρ0 (terrain-weighted) | Ocean Infinity |
|---|---|---|---|---|
| V0 scalar (reduction) | as run.toml (Phase 2 0.945 flat) | — | 0.05 flat | uniform fraction |
| V1 spatial central | 0.95 | 0.70 | 0.05; sweep 0 / 0.25 / 0.5 | density field, q 0.9 |
| V2 spatial pessimistic | 0.90 (Stone cap) | 0.50 | 0.25 | density field, q 0.9 × 0.7 |
| V3 spatial optimistic | 0.99 | 0.90 | 0.02 | density field, q 0.95 |
Plus V1 without Ocean Infinity (labelled sensitivity) and V1 with ρ flat (to isolate the effect of its spatial shape).

## Tests (all must pass before any number is quoted)
1. V0 reproduces the published run J settled Z (D0′ 0.3113) to Monte Carlo tolerance.
2. Area: Phase 2 union about 120,000 km² and deep tow about 104,104 km² on the 500 m grid; 0.01° regrid equals the `.cov` files.
3. Figure 73: area-mean f_lpd per sub-area equals the printed share; area-mean q over the red area is 0.945 ± 0.003.
4. No double count: gaps appear only in c. Off-ground returns exactly 0. Two identical settling draws give the same likelihood as one.
5. Ocean Infinity density integrates to the stated searched area and is never above 1.

## Pre-registered expectation
Area-mean q barely changes (about 0.94), so total Z moves little. What should change is WHERE the "missed" mass sits: it should
gather in the orange sub-area, in lower-confidence cells and on steep terrain. If total Z moves by more than 0.02, find out why
before reporting.

## Limits to state with every result
LPD and gap locations are a calibrated proxy, not ATSB polygons (route 2(b)); Ocean Infinity coverage is inferred (grade C);
q_hi, q_lpd and ρ0 are judgement values bracketed by V2/V3; the shipwreck positive controls bound q only weakly (2 of 2 detected
gives a one-sided 95 % lower bound of 0.37) and are a sanity check, not a calibration. No core files are changed.

## Resources
Downloads about 6 GB to `~/Downloads/mh370-large-files/ga-mh370/` (read in place, not unpacked). Stop if free disk falls below
20 GiB. Scoring about 1 h at 2–4 threads, outside the heavy lock (no core run).
