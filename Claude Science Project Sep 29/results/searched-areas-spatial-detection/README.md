# Searched areas: a per-cell detection model (q and ρ as fields) — run J, settled positions

Searched Areas (general session), 18 Oct 2026, to work order
`threads/work-orders/searched-areas-spatial-detection-2026-10-18.md` (Pete, route 2(b)). Code:
`engine/hypotheses/seabed-search/spatial/` (`build_fields.py`, `score_spatial_run_j.py`, `reduce_spatial_run_j.py`).
Columns: `mh370-exchange/searched-areas/run-j-spatial/` (READY). Fields: `mh370-exchange/searched-areas/spatial-fields/`.

**Labels for every number here.** Core run J accepted as a pass by project ruling, 16 Oct 2026. Core × seabed searches only
(not all evidence — the all-evidence views are the composer's). Settled wreckage, 'mean' field treatment. Ocean Infinity
coverage inferred (grade C), included as best estimate. Lower-confidence areas are a proxy digitised from ATSB 2017 Figure 73,
not ATSB polygons. q_hi, q_lpd and ρ0 are judgement values bracketed by V2/V3.

## Result in three lines
1. The per-cell model changes the search factor Z by −0.0015 to −0.0036 across D0–D5 (MC SE 0.0002). The pre-registered
   expectation (total Z moves little, alarm at 0.02) holds. The 500 m grid alone moves Z by −0.0001.
2. What moves is WHERE the "searched and missed" mass sits. Under D3 it shifts onto steep ground (+47 %), onto cells with a high
   lower-confidence fraction (+25 %) and into the orange sub-area north-east of the main area (+17 %), and off smooth ground (−15 %).
3. The LEVEL of ρ and q, not their spatial shape, decides the "inside searched ground and missed" share: under D3 it runs
   0.44 (V3 optimistic) – 0.69 (V1 central) – 0.87 (V2 pessimistic); the spatial shape of ρ alone moves Z by 0.0002.
   Public data cannot fix that level. It is the term that most needs a measurement.

## Headline (search Z and where the probability is, after the searches)

| 00:19 data | V0 base Z | V1 central Z | V2 pessimistic | V3 optimistic | on searched ground after, V0 / V1 / V2 / V3 |
|---|---|---|---|---|---|
| D0 Held Out | 0.3113 | 0.3091 (-0.0022 ± 0.0002) | 0.4911 | 0.2544 | 0.298 / 0.287 / 0.548 / 0.134 |
| D1 R600 BTO Only | 0.2752 | 0.2723 (-0.0029 ± 0.0002) | 0.4588 | 0.2156 | 0.335 / 0.325 / 0.594 / 0.151 |
| D2 R600 BTO + Raw BFO | 0.2122 | 0.2087 (-0.0035 ± 0.0002) | 0.4118 | 0.1469 | 0.478 / 0.465 / 0.724 / 0.242 |
| D3 R600 BTO + both BFOs as recorded | 0.1513 | 0.1477 (-0.0036 ± 0.0002) | 0.3674 | 0.0812 | 0.696 / 0.689 / 0.871 / 0.436 |
| D4 R600 BTO + both BFOs, Holland transient bias added | 0.1373 | 0.1358 (-0.0015 ± 0.0002) | 0.3585 | 0.0679 | 0.769 / 0.760 / 0.905 / 0.523 |
| D5 R600 BTO + R600 BFO + R1200 BFO, Holland transient bias added | 0.1442 | 0.1409 (-0.0033 ± 0.0002) | 0.3612 | 0.0742 | 0.734 / 0.723 / 0.887 / 0.478 |

Full table, every variant and the four-way split (on searched ground / north of 25 S / beyond 25 NM of the arc / near-arc
unsearched south of 25 S), plus family shares after the searches: `tables.md`. Mixture JSON: `run-j-spatial-reduced.json`.
Where the missed mass sits (D0 and D3, waypoints sets): `where_missed.json`.

## Method
P(no find | settled field) = ρ̄ + (1 − ρ̄) Π_k (1 − d̄_k), with mass-weighted means over the settled pieces (settling run J, fate 0):
- **Coverage c.** Phase 2 from the frozen 0.001° valid-pixel caches of the GA 5 m mosaics (they reproduce every committed
  `.cov` exactly), on a 0.005° grid. Mapped gaps are already out of c, so q never carries the gap class again.
- **q for Phase 2:** q = 0.95 (1 − f) + 0.70 f, f = lower-confidence fraction of the covered part of the cell. f comes from the
  green overlay of ATSB 2017 Figure 73 (printed p. 96): render georeferenced in Mercator from its graticule and refined against the
  module's coverage (agreement 1–2 px, about 2–3 km); smoothed (σ ≈ 2.8 km); scaled so each sub-area's coverage-weighted mean
  equals its printed share (red 0.0110, orange 0.0785, yellow 0.0111, purple 0.0151 — reproduced exactly).
  Area-mean q: red 0.9472 (test 3: 0.945 ± 0.003 PASS), orange 0.9304, yellow 0.9472, purple 0.9462, all 0.9442; range 0.905–0.950.
- **ρ:** ρ(x) = min(ρ0 · w(x), 0.95), w = terrain propensity (logistic in slope, maximum slope and roughness from the GA Phase 1
  150 m bathymetry) normalised to mean 1 over Phase 2 covered ground (5th / 50th / 95th percentile 0.46 / 0.75 / 2.42); w = 1 where
  there is no Phase 1 bathymetry (none of Phase 2; 31 % of Ocean Infinity 2018 ground).
- **Ocean Infinity:** slow AIS fixes (< 4 kn, MH370-CAPTION hourly), Gaussian σ 15 km, times the traced layer, scaled to the reported
  searched area (2018: 112,000 km²; 2025–26: 7,571 km²), capped at the layer; q 0.9 (Stone et al.'s cap). 80.5 % of 2018 layer cells
  reach the cap; 35 % for 2025–26.
- **Variants:** V0 base exactly as `run.toml`; V0 at 500 m; V1 central (0.95 / 0.70, ρ0 0.05 terrain-weighted, OI density); ρ0
  sweep 0 / 0.25 / 0.5; ρ flat; lower-confidence from terrain only; OI uniform; without OI; V2 (0.90 / 0.50, ρ0 0.25, OI q 0.63);
  V3 (0.99 / 0.90, ρ0 0.02, OI q 0.95).

## Tests (work order §Tests)
1. V0 reproduces the published run J settled rows: max |Δ ln L| ≤ 6.2 × 10⁻¹⁵ in all five sets; per-outcome coverage to float32 (3 × 10⁻⁸). PASS.
2. Phase 2 area 120,486 km² on the 500 m grid (0.001° count 120,486; deep tow 103,921); 0.01° regrid equals the `.cov` files (max |Δ| 0.0). PASS.
3. Lower-confidence share per sub-area equals the printed value; red-area mean q 0.9472. PASS.
4. Gaps only in c; off-ground outcomes return exactly 0 in every variant (52k–62k per set); two identical draws equal one. PASS.
5. Ocean Infinity fields integrate to 112,000 and 7,571 km² and never exceed the layer. PASS.

## Deviations from the work order (declared)
1. **Step 3 changed.** Terrain explains little of where ATSB drew its lower-confidence areas: blocked cross-validation AUC 0.56
   (slope), 0.57 (slope + roughness), 0.46 with depth. So the PRIMARY lower-confidence field is the figure's own green density, scaled
   per sub-area; the terrain-only field is kept as `V1_lpd_terrain` (Z within 0.0005 of V1). Terrain still sets the shape of ρ.
2. Phase 2 coverage came from the frozen snapshot caches, not a new stream of the 5.7 GB zip; the zip was downloaded to
   `~/Downloads/mh370-large-files/ga-mh370/` and is not needed (it can be removed to recover 5.7 GB).
3. Gap shares in c match the printed values for red (0.28 % against 0.2 %) but read high for the narrow sub-areas (1.7–2.9 % against
   0.6–1.1 %), because partly covered edge cells count as gaps at 500 m and not at ATSB's 100 m metric. This affects the check, not
   the likelihood.
4. ρ is capped at 0.95 per piece (matters only at ρ0 0.5 on the steepest ground).
5. The four-way split uses the impact position's latitude and arc distance; searched share uses the settled field.

## COVERAGE
- **(a) Feasible set:** unchanged from run J (end of flight's note). **(b) Model's reach:** the detection model covers every Phase 2,
  Bluefin-21 and Ocean Infinity layer cell; outside them ln L = 0. **(c) Proposal's coverage:** the run J settled outcomes as published
  (17 of 168 products below row ESS 1,000, all D3–D5 family or cause splits; D3 × A1 409 on both-burst). Unchanged by this work.
- **Gaps in the detection model, with status:**
  - G-LPD: lower-confidence locations are a figure proxy at about 1.5 km pixels, ±2–3 km registration. OPEN — closes if ATSB / GA
    release the gap and lower-confidence polygons (they exist: GA 2022 data review).
  - G-OI25: 46 % of the 2025–26 slow ship fixes lie outside the traced outboard band (including March 2025 work south-west of it);
    that ground is treated as unsearched here. OPEN, conservative (leaves probability on it).
  - G-ρ: the level ρ0 has no measurement; the spatial shape is a judgement from terrain. OPEN; bracketed by V2 / V3 and the ρ0 sweep.
  - G-terrain-OI: 31 % of Ocean Infinity 2018 ground has no Phase 1 bathymetry (w = 1 there). OPEN, small.

## Next (for the composer and for Pete)
- Composer: views v3 with the V1 column as the search factor and V0 / V2 / V3 beside it; the four-way split for all evidence.
- The Davey eq. 11.2 block table for 2026–27 should now rank re-search of low-q / steep cells against new ground; this note's
  `where_missed.json` shows which cells.
- Ask ATSB / GA for the gap and lower-confidence polygons (closes G-LPD).

Footnotes for charts built on these columns. STE100: "The search result uses a map of how well each part of the seabed was
searched. Some map parts come from a published ATSB figure and the shape of the seabed." Technical: "Per-cell detection model V1:
q = 0.95/0.70 by Figure 73 lower-confidence fraction; ρ = 0.05 × terrain weight; Ocean Infinity coverage density from AIS (grade C)."
