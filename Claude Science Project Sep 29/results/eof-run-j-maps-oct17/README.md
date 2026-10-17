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

### 2b. Follow-up, 17 Oct 2026 ~20:45Z (Pete's questions)

**Map extent.** The first version (86.5-99 E, 40.2-30 S) left out about 1.3-1.6 % of the impact probability, nearly all of it
north of 30 S. That is more than the 1 % outside the 99 % region, so the 99 % region was cut at the northern edge. The map is now
86.5-104 E, 40.2-25 S.

| Panel | Outside old window | North of 30 S | Outside new 25-40.2 S window | North of 20 S |
|---|---|---|---|---|
| D0' 00:19 data not used | 1.62 % | 1.57 % | 0.27 % | 0.01 % |
| D2 00:19:29 range + frequency | 1.50 % | 1.48 % | 0.35 % | 0.01 % |
| D4 both, shared start-up offset | 1.45 % | 1.45 % | 0.22 % | < 0.01 % |
| D3/D4/D5 evidence-weighted | 1.30 % | 1.30 % | 0.22 % | 0.01 % |

**Energy distribution** (new Figure `run-j-impact-energy-distribution`: per-treatment histograms of contact kinetic energy on a
log axis, stacked by family; the red outline is the part at or below 212 m/s):

| Treatment | P(E >= 10 GJ) | P(contact speed > 212 m/s) | P(E >= 10 GJ and speed <= 212 m/s) |
|---|---|---|---|
| D0' | 0.189 | 0.329 | 0.000 |
| D1 | 0.211 | 0.362 | 0.000 |
| D2 | 0.233 | 0.358 | 0.000 |
| D3 | 0.343 | 0.569 | 0.000 |
| D4 (Holland's data treatment) | **0.500** | 0.654 | 0.000 |
| D5 | 0.417 | 0.568 | 0.000 |

- **Shape.** The distribution has two modes. There is a broad low-energy body at 0.3-5 GJ, made up of glides, arrested and
  controlled descents and ditchings. There is a narrow spike at 10-12 GJ, made up of steep dives that reach the sea at a median of
  about 350 m/s.
- **Effect of the 00:19:37 frequency.** Using that frequency moves weight from the body into the spike.
- **Speed.** Every impact of 10 GJ or more is faster than 212 m/s (1.25 VMO). That is the G13 credibility threshold; the flag is
  `latent:contact_speed_feasible`.
- **Effect of the 212 m/s cap.** The capped sensitivity ("~v212") would remove the whole spike.
- **Status.** This is a property of the uncalibrated uncontrolled arm (see the caveat), not a prediction.

**Effective sample per 5 deg band** (`smoke/band_ess.py`; `run-j-band-ess.json`). Each cell gives the band mass, the ESS over
impact rows, and the ESS over distinct 00:11 parents:

| Band | D0' | D2 | D3 | D4 |
|---|---|---|---|---|
| 40-35 S | 0.892, 1.88M / 411k | 0.917, 85k / 71k | 0.924, 4.3k / 4.3k | 0.921, 24k / 23k |
| 35-30 S | 0.093, 109k / 30k | 0.068, 6.0k / 5.2k | 0.064, **308 / 306** | 0.065, **370 / 365** |
| 30-25 S | 0.013, 16k / 3.5k | 0.011, 1.1k / 906 | 0.010, **84 / 83** | 0.012, **167 / 155** |
| 25-20 S | 0.0025, 6.5k / 1.5k | 0.0034, 184 / 167 | 0.0020, 22 / 22 | 0.0021, 104 / 88 |

In the treatments that use the 00:19:37 frequency, the northern bands (35-25 S) hold 7-8 % of the mass on a few hundred
independent paths. The limit is the number of distinct core parents there, not descents per parent. This is coverage gap 4, now
measured.

**Attitude sidecar for hydroacoustics.** `seed-k/attitude_v1.npz` (row-aligned, all 74 seeds) has three keys:
- `bank_deg`.
- `bank_source`: 1 = commanded wings level, 0 = free dynamics or a commanded turn.
- `n_pulses`: 1 for every row.

The exact zeros are modelled values. The point-mass integrator sets bank = the commanded bank, and the glide, Track, push-over
and ditching-leg commands hold bank 0. Zero is therefore not a placeholder. The commanded phases carry no bank spread, which is a
declared reach gap. The wings-level share is 0.480-0.508 of rows per seed. No row in the no-intervention arm is exactly 0.

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
| `run-j-impact-maps.{png,pdf}` | Impact HPD maps by 00:19 treatment, with searched sea floor and arcs (25-40.2 S since 20:45Z) |
| `run-j-impact-latitude-0019.{png,pdf}` | Latitude density per treatment |
| `run-j-impact-maps-by-family.{png,pdf}` | 3 families x 6 treatments |
| `run-j-impact-loudness-maps.{png,pdf}` | Peak radiated power classes; loudest-decile shares |
| `run-j-impact-energy-maps.{png,pdf}` | Energy transferred; weighted CDFs |
| `run-j-impact-energy-distribution.{png,pdf}` | Energy histograms per treatment, by family, with the 212 m/s part |
| `run-j-band-ess.json` | Mass and ESS (rows / distinct parents) per 5 deg band |
| `run-j-figures.json` | All printed numbers |
| `run-j-maps-accumulators.json` | Per-treatment and per-family mass and ESS (the check against production) |

The accumulator grids and resample (`run-j-maps-accumulators.npz`, 89 MB) are kept in
`mh370-exchange/end-of-flight/run-j/summary/`, not in git.

To reproduce, run from `engine/hypotheses/end-of-flight/smoke/` with the eof-sim python:

    for k in 0 1 2 3 4 5; do python run_j_maps_pass.py $EOF/run-j $CORE/run-j $EOF/run-j/summary/table-0019-mixture.json OUT $k 6 & done; wait
    python run_j_maps_pass.py --combine OUT 6
    python run_j_figures.py OUT $EOF/run-j/summary $CORE/run-j FIGS

-- End of Flight Module
