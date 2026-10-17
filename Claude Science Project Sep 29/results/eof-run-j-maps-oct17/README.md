# End of flight on core run J: impact maps, latitude densities, family maps, loudness and energy maps (17 Oct 2026)

End of Flight Module, 17 Oct 2026, 14:15Z. This note covers the standard figure set Pete requested on 17 Oct, re-made for the run J
production pass. It follows the run I conventions: maps by 00:19 treatment, the latitude density, maps by family, and the
loudness scatter maps. The previous run I versions are `run-i-dive-impact-maps`, `run-i-dive-impact-latitude-0019`,
`settling-seabed-wreckage-run-i-waypoints-family` (seabed) and `fig-impact-loudness-maps` (one seed only). The figures here use
all four strata and all 74 seeds.

Core run J has been accepted as a pass by project ruling, 16 Oct 2026. The thin northern detail (few independent paths north of
33 S) is a limitation of the tail shape, not non-convergence.

**Caveat (verbatim).** The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all three rounds.
Impact energy, attitude, flight-path angle and energy-transfer duration from this arm are a labelled sensitivity on uncalibrated
dynamics, not a physical prediction.

## 1. What was run

- `engine/hypotheses/end-of-flight/smoke/run_j_maps_pass.py` makes one streaming pass over `mh370-exchange/end-of-flight/run-j/`.
  It covers 4 strata and 24/18/16/16 seeds, 6.4M rows per waypoints seed, and took about 2 minutes on 6 workers.
- For each 00:19 treatment D0'..D5 it builds the same per-row log mass as the production table. That is the competing-causes total
  (q = 1/3, C2 silent), with the survival factor applied and transmission imposed.
- It accumulates a 0.02 deg impact histogram per treatment and per family (A1, A2, B = codes 3+6). It also keeps a mass-preserving
  systematic resample of 10,000 rows per seed per treatment. The resample carries the tau90_v1 sidecar's peak radiated power and
  energy transferred.
- **Check against production:** the mass of every treatment is 1.0000 relative to `table-0019-mixture.json`. ln Z, ESS and the
  A1/A2 shares are identical. B here includes the uncontrolled planned descents (code 6), which adds 0.0008-0.0019.
- `smoke/run_j_figures.py` draws the figures from the accumulators in about 10 s. Every number printed on a figure is in
  `run-j-figures.json`.

## 2. Results

**Impact location by treatment** (Figure `run-j-impact-maps`; 0.02 deg grid, Gaussian sigma 0.08 deg):

| Panel | Median | Peak | 5-95 % latitude | HPD area 50 / 90 / 99 % (thousand km2) | ESS |
|---|---|---|---|---|---|
| a. 00:19 data not used (D0') | 37.13 S | 37.09 S | 38.41-33.87 S | 19 / 162 / 614 | 1.95M |
| b. 00:19:29 range and frequency (D2) | 37.13 S | 37.09 S | 38.17-34.35 S | 11 / 103 / 399 | 92.2k |
| c. both frequencies, shared start-up offset (D4) | 37.21 S | 37.29 S | 37.99-34.39 S | 6 / 58 / 215 | 21.2k |
| d. evidence-weighted D3/D4/D5 (0.381 / 0.408 / 0.212) | 37.25 S | 37.31 S | 38.01-34.43 S | 6 / 60 / 224 | (by component) |

- **Peaks.** All six treatments peak between 37.08 and 37.34 S (Figure `run-j-impact-latitude-0019`). The treatments that use the
  00:19:37 frequency (D3, D4, D5) peak at 37.29-37.34 S. The treatments that do not (D0', D1, D2) peak at 37.08-37.09 S.
- **Spread.** Adding the 00:19:37 frequency narrows the 90 % area from 162 to 58 thousand km2.
- **Searched ground.** In every panel the 50 % region (about 89-91 E, 36.5-38.5 S) lies within or along the Phase 2 search outline.
  It is south-west of the Ocean Infinity 2025 box. The search evidence is not applied in these figures.

**By family** (Figure `run-j-impact-maps-by-family`; each panel normalised to itself):

| Family | Share D0' / D2 / D3 / D4 / D5 | Median latitude, D0' / D4 | 90 % area (thousand km2), D0' / D4 | ESS D3 / D4 |
|---|---|---|---|---|
| Fuel exhaustion, then no control (A1) | 0.17 / 0.24 / 0.09 / 0.25 / 0.06 | 37.03 / 37.01 S | 31 / 21 | **369 (not estimable)** / 1,915 |
| Fuel exhaustion, then controlled to the surface (A2) | 0.34 / 0.23 / 0.41 / 0.35 / 0.42 | 37.27 / 37.29 S | 156 / 55 | 4,017 / 32,246 |
| Deliberate descent before fuel exhaustion (B, codes 3+6) | 0.49 / 0.53 / 0.50 / 0.40 / 0.52 | 37.15 / 37.35 S | 186 / 63 | 1,698 / 14,884 |

- **A1 location.** A1 impacts are tightly confined near the 7th arc at about 37.0 S, with a 90 % area of 14-31 thousand km2. Its
  location barely moves with the 00:19 treatment.
- **A2 and B.** These carry the northern tail along the arc and the wider south-western lobe.
- **Thin cells.** A1 under D3 is the declared coverage gap (ESS 369 < 1,000), and its panel is marked "Not estimable". A1 under D4
  (1,915) and D5 (2,181) are estimable but thin.

**Loudness and energy** (Figures `run-j-impact-loudness-maps`, `run-j-impact-energy-maps`; a labelled sensitivity on uncalibrated
dynamics, see the caveat):

| Treatment | Share in held-out loudest decile, peak power / energy | Energy transferred, GJ (5 / 50 / 95 %) |
|---|---|---|
| D0' 00:19 data not used | 0.100 / 0.100 | 0.35 / 1.17 / 11.4 |
| D1 00:19:29 range | 0.114 / 0.112 | 0.35 / 1.52 / 11.5 |
| D2 00:19:29 range + frequency | 0.132 / 0.131 | 0.35 / 1.14 / 11.5 |
| D3 both frequencies, recorded | 0.107 / 0.116 | 0.46 / 6.47 / 11.4 |
| D4 both, shared start-up offset | 0.223 / 0.238 | 0.49 / 10.0 / 11.8 |
| D5 offset on 00:19:37 only | 0.104 / 0.122 | 0.45 / 6.72 / 11.4 |

- **Class boundaries.** These are the held-out (D0') weighted quantiles of peak radiated power: median 4.2e8 W, top decile 7.2e10 W.
  The total-energy top decile is 11.0 GJ.
- **Effect of the 00:19:37 frequency.** Every treatment that uses it moves the median energy from about 1.2 GJ to 6.5-10 GJ. That
  frequency selects descents that are fast at impact. Only D4 (shared start-up offset) also doubles the share in the loudest decile,
  to 0.22-0.24. D3 and D5 stay at 0.10-0.12.
- **Measure dependence.** In the run I single-seed figure the two loudness measures disagreed by up to 0.2 in share. Here they agree
  to within 0.02 in every treatment.
- **Status.** These are sampling coordinates on uncalibrated dynamics. They are not predictions of the acoustic source.

## 3. COVERAGE

- **(a) Feasible set.** All 777-200ER end-of-flight behaviour after the 00:11 hand-off: fuel exhaustion with no input (A1),
  fuel exhaustion with controlled or arrested descent (A2), and planned descent before exhaustion (B, controlled and uncontrolled).
  The spiral bank limit runs up to 90 deg; Boeing no-input traces reach 53-60 deg. Steep dives to the surface are included, and so
  are Holland-type rapid descents.
- **(b) Model's reach.**
  - Round-3 uncontrolled laws; the bank limit is drawn U[52, 90] deg (Pete, 16 Oct).
  - A push-over can dive to the surface (p = 0.5, Decision 4) or level off.
  - Piloted-turn model and INTERIM pitch-down, both PROVISIONAL.
  - There is no descent-rate cap beyond the physics.
  - **Pre-00:11 planned descents are not in this pass.** They come from joined V2 (`results/eof-run-j-joined-v2-oct17/`, B 0.196
    fuel-tied, 16 seeds). The maps here are conditional on the aircraft still flying at the 00:11 hand-off.
- **(c) Proposal's coverage.** ESS per treatment (all families): D0' 1.95M, D1 2.14M, D2 92.2k, D3 4.7k, D4 21.2k, D5 25.9k. ESS per
  family is in the table in section 2.
- **Gaps and their status.**
  1. A1 under D3: ESS 369, not estimable. This is declared; the fix is an A1-aimed descent proposal, which is in the backlog. The
     supplementary both-burst pass raises it to about 400 only.
  2. B under D3: ESS 1,698, estimable but thin.
  3. The B-uncontrolled family (about 0.001) is folded into B and is not separately estimable.
  4. The northern tail north of 33 S has few independent core paths (core run J prediction 5).
  5. Pre-00:11 B is parent-limited (joined V2, about 121 effective 22:41 parents per seed).
- **Bounds and sources.**
  - Bank limit U[52, 90] deg (Pete, 16 Oct 2026; Boeing traces 53-60 deg).
  - p = 0.5 (Decision 4).
  - q = 1/3, C2 silent (12 Oct rulings).
  - W = 00:10:58-01:15:56 UTC.
  - D5 offset U[17, 130] Hz.
  - Strata weights from core run J P(family): 0.9982/0.0013/0.0003/0.0002.

## 4. Files

| File | Content |
|---|---|
| `run-j-impact-maps.{png,pdf}` | Impact HPD maps by 00:19 treatment, with searched sea floor and arcs |
| `run-j-impact-latitude-0019.{png,pdf}` | Latitude density per treatment |
| `run-j-impact-maps-by-family.{png,pdf}` | 3 families x 6 treatments |
| `run-j-impact-loudness-maps.{png,pdf}` | Peak radiated power classes; loudest-decile shares |
| `run-j-impact-energy-maps.{png,pdf}` | Energy transferred; weighted CDFs |
| `run-j-figures.json` | All printed numbers |
| `run-j-maps-accumulators.json` | Per-treatment and per-family mass and ESS (the check against production) |

The accumulator grids and resample (`run-j-maps-accumulators.npz`, 89 MB) are kept in
`mh370-exchange/end-of-flight/run-j/summary/`, not in git.

To reproduce, run from `engine/hypotheses/end-of-flight/smoke/` with the eof-sim python:

    for k in 0 1 2 3 4 5; do python run_j_maps_pass.py $EOF/run-j $CORE/run-j $EOF/run-j/summary/table-0019-mixture.json OUT $k 6 & done; wait
    python run_j_maps_pass.py --combine OUT 6
    python run_j_figures.py OUT $EOF/run-j/summary $CORE/run-j FIGS

-- End of Flight Module
