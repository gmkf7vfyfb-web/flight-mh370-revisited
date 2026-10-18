# Searched areas on run J, at the impact point — Ocean Infinity in the base

18 October 2026, Searched Areas module. Task from coordination (Pete's rulings of 13 Oct and 18 Oct 2026 00:41Z).

**Label for every number here: "Ocean Infinity coverage inferred (grade C), included as best estimate".** Base = ATSB Phase 2 +
Bluefin-21 + Ocean Infinity 2018 + Ocean Infinity 2025–26 (outboard band), inferred geometry. *Without Ocean Infinity* is a labelled
sensitivity. The planned next Ocean Infinity area is a **map layer only** (mass reported, never evidence). **Impact point, not
seabed**: settling has not run on run J. Run J convergence: **accepted as a pass by project ruling, 16 Oct 2026** (split-half,
all four families).

## Result

1. **Under D0' (00:19 values held out, transmission imposed), the searches leave Z = 0.3101 (ln Z −1.171)** on the four-family
   mixture (waypoints 0.998 of core's P(family)). Before the searches, **0.771** of the D0' weight is on searched ground; after them,
   **0.284**. The ATSB ground alone holds 0.724 before and 0.245 after.
2. **Ocean Infinity in the base lowers Z from 0.3502 to 0.3101** (Δln Z −0.122). After the searches it lowers the share on searched
   ground from 0.350 to 0.284 and the share north of 33 S from 0.091 to 0.068.
3. **The planned next Ocean Infinity area (map layer only) holds 0.005 of the D0' weight before the searches and 0.016 after.**
   The layer does not change any weight.
4. **rho is still the largest module-controlled sensitivity:** Z is 0.274 / 0.310 / 0.455 / 0.637 at rho 0 / 0.05 / 0.25 / 0.5.
   No published value for rho exists.
5. **By hypothesis family (D0', mixture):** A1 Z 0.133 (share 0.172 → 0.074), A2 0.343 (0.343 → 0.379), B 0.350 (0.485 → 0.547).
   The searches act most strongly against A1, because 0.967 of the A1 weight is on searched ground.
6. **The composer's stand-in agrees with this module's code on every product it published:** 240 cells (6 options × 8 contexts
   × 5 search cases), with max |Δ ln Z| 1.7e-7, max relative ΔESS 5.0e-7 and max |Δ share| 2.1e-7. On run J free seed-1, its
   transcribed raster lookup reproduces evaluate's ln L with zero difference. The composer's formula (OI 2018 q 0.9 × f 0.889;
   OI 2025–26 outboard q 0.9 × f 0.7808; rho 0.05) is the module's formula. **There is no difference to report.**

**Table 1. D0' (00:19 values held out, transmission imposed) per family folder, base, rho 0.05.**

| family | P(family), core | seeds | rows | Z | Z split-half | Z without OI (sens.) | on searched ground before → after | ATSB ground before → after | in next OI area before → after (layer) | ESS before / after |
|---|---|---|---|---|---|---|---|---|---|---|
| run-j-waypoints | 0.9982 | 24 | 153,599,936 | 0.3101 | 0.3088 / 0.3113 | 0.3501 | 0.771 → 0.284 | 0.724 → 0.245 | 0.005 → 0.016 | 1,941,487 / 860,901 |
| run-j-free | 0.0013 | 18 | 57,600,064 | 0.3744 | 0.3743 / 0.3744 | 0.4497 | 0.701 → 0.237 | 0.613 → 0.176 | 0.010 → 0.025 | 384,629 / 174,307 |
| run-j-descent-climb | 0.0002 | 16 | 51,200,064 | 0.3475 | 0.3603 / 0.3362 | 0.3998 | 0.730 → 0.251 | 0.669 → 0.204 | 0.007 → 0.020 | 397,767 / 165,088 |
| run-j-repro-radar | 0.0003 | 16 | 51,199,904 | 0.3749 | 0.3825 / 0.3682 | 0.4433 | 0.700 → 0.231 | 0.620 → 0.176 | 0.009 → 0.023 | 330,094 / 141,825 |

**Table 2. D0', four-family mixture (core P(family)): the rho sweep and the sensitivity without Ocean Infinity.**

| case | Z | ln Z | on searched ground before → after | ATSB ground before → after | in next OI area before → after (layer) | north of 33 S before → after | ESS after |
|---|---|---|---|---|---|---|---|
| base, rho 0.05 (reference) | 0.3101 | -1.171 | 0.771 → 0.284 | 0.724 → 0.245 | 0.005 → 0.016 | 0.032 → 0.068 | 863,670 |
| base, rho 0 | 0.2738 | -1.295 | 0.771 → 0.191 | 0.724 → 0.153 | 0.005 → 0.018 | 0.032 → 0.075 | 696,181 |
| base, rho 0.25 | 0.4554 | -0.787 | 0.771 → 0.509 | 0.724 → 0.466 | 0.005 → 0.011 | 0.032 → 0.051 | 1,444,729 |
| base, rho 0.5 | 0.6369 | -0.451 | 0.771 → 0.646 | 0.724 → 0.601 | 0.005 → 0.008 | 0.032 → 0.041 | 1,817,992 |
| sensitivity: without Ocean Infinity, rho 0.05 | 0.3502 | -1.049 | 0.771 → 0.350 | 0.724 → 0.217 | 0.005 → 0.014 | 0.032 → 0.091 | 791,498 |

**Table 3. D0', mixture, by hypothesis family (A1 / A2 / B), base, rho 0.05.**

| family | share before | share after | Z | on searched ground before → after | in next OI area after (layer) | ESS before / after |
|---|---|---|---|---|---|---|
| A1 | 0.172 | 0.074 | 0.1329 | 0.967 → 0.774 | 0.018 | 999,271 / 199,740 |
| A2 | 0.343 | 0.379 | 0.3431 | 0.734 → 0.244 | 0.011 | 744,403 / 426,460 |
| B | 0.485 | 0.547 | 0.3498 | 0.727 → 0.246 | 0.018 | 721,538 / 377,262 |

**Table 4. All six 00:19 options, mixture, base, rho 0.05** († D3/D4: waypoints from the both-burst supplementary set).

| option | Z | Z without OI (sens.) | on searched ground before → after | in next OI area after (layer) | ESS before / after | ESS after A1 / A2 / B |
|---|---|---|---|---|---|---|
| D0' held out | 0.3101 | 0.3502 | 0.771 → 0.284 | 0.016 | 1,946,710 / 863,670 | 199,740 / 426,460 / 377,262 |
| D1 R600 BTO | 0.2745 | 0.3048 | 0.810 → 0.329 | 0.005 | 2,145,061 / 1,176,680 | 1,289,914 / 704,141 / 429,711 |
| D2 R600 BTO + BFO | 0.2110 | 0.2469 | 0.881 → 0.467 | 0.007 | 92,216 / 35,135 | 45,450 / 12,846 / 16,560 |
| D3 both BFOs (H2 data)† | 0.1507 | 0.1770 | 0.947 → 0.685 | 0.002 | 6,348 / 1,340 | 402 / 2,587 / 500 |
| D4 shared offset (H1 data)† | 0.1366 | 0.1609 | 0.963 → 0.761 | 0.003 | 44,422 / 24,571 | 2,909 / 19,387 / 10,449 |
| D5 R1200 BFO with offset | 0.1437 | 0.1728 | 0.955 → 0.727 | 0.005 | 25,943 / 9,213 | 1,841 / 7,655 / 3,472 |

**Table 5. D0' per family folder, Z over the rho sweep (base).**

| family | rho 0 | rho 0.05 | rho 0.25 | rho 0.5 | between-seed SD of Z (rho 0.05) |
|---|---|---|---|---|---|
| run-j-waypoints | 0.2737 | 0.3101 | 0.4553 | 0.6369 | 0.0215 |
| run-j-free | 0.3414 | 0.3744 | 0.5061 | 0.6707 | 0.0217 |
| run-j-descent-climb | 0.3131 | 0.3475 | 0.4849 | 0.6566 | 0.0338 |
| run-j-repro-radar | 0.3420 | 0.3749 | 0.5065 | 0.6710 | 0.0149 |

**Table 6. D0' per family folder and hypothesis family, base, rho 0.05: Z (ESS after).**

| family | A1 | A2 | B |
|---|---|---|---|
| run-j-waypoints | 0.1328 (199,190) | 0.3430 (425,340) | 0.3497 (375,878) |
| run-j-free | 0.2015 (25,347) | 0.3945 (57,723) | 0.3982 (100,908) |
| run-j-descent-climb | 0.1697 (30,993) | 0.3679 (71,049) | 0.3777 (84,513) |
| run-j-repro-radar | 0.2006 (25,803) | 0.3907 (62,066) | 0.4053 (70,706) |

Z = E[P(no find | impact)] under the option's end-of-flight posterior. It is the search evidence on an absolute scale. "On searched
ground" = Σ w · [1 − Π_k (1 − f_k c_k)] over the four base campaigns (coverage-fraction weighted, the composer's definition).
"ATSB ground" = Σ w · [1 − (1 − c_P2)(1 − c_BF)]. ESS is the pooled Kish effective sample. Split-half: seeds split by position
within the family folder. All figures are Monte Carlo estimates on the stated samples.

## What was done

1. **`run.toml` is now the four-campaign base** (Phase 2 q 0.945; Bluefin-21 q 0.9; OI 2018 q 0.9, f 0.889; OI 2025–26 outboard
   band q 0.9, f 0.7808; rho 0.05). **`base_guard.py`** stops every scoring driver (`score_run_j.py`, `publish_columns.py`,
   `sweep_release.py`, `report.py`) if run.toml lists any other campaign set, or if a campaign name looks like a planned, contract,
   mapping or surface area. The sensitivity is the override **`without-ocean-infinity.toml`**. The old single-layer overrides
   `ocean-infinity-2018.toml` / `-2025.toml` are marked superseded; they are kept only so that the run D-he variants can be
   reproduced. `sweep_release.py` and `report.py` now use the four-campaign base, with "without Ocean Infinity" as their comparison.
   The brief (`threads/master-prompts/searched-areas.md`) has an amended campaign table and a dated amendment of 18 Oct.
2. **Validated on one seed first** (run-j-free/seed-1, 3,199,968 rows): row count = impacts32 rows; finite on every row; algebra =
   evaluate's own `no_find_probability` and `loglik` (max |Δ| 0.0). The run D-he OI variant columns were reproduced from their
   coverage columns with the same `p_no_find` code: next-run-d-he-oi2018, -oi2025 and next-run-d-he, 51,200,064 rows each, max
   |Δ ln L| **2.6e-7** (< 1e-6; the limit is the float32 storage of the coverage columns). See `validation-crossmodule.json`.
3. **Scored all 74 seeds** (313,599,968 rows), 4 workers × 2 threads, 555 s wall time. Every seed passed the same checks. All
   518 files pass `shasum -c` against the top-level SHA256SUMS. **Then the D3/D4 supplementary set** (`run-j-both-burst/run-j-waypoints`,
   8 seeds, 8,001,249 thinned rows; end of flight's instruction for D3/D4) was scored, 22 s.
4. **Reduction** (`reduce_run_j.py`): the row mass is end of flight's `option_table_0019.seed_terms` cell
   `D<d> total q=0.333 (C2 silent)`, unchanged. Seeds are pooled by evidence. Strata are weighted by core P(family), from
   `core/run-j/<stratum>/summary.json`.

### The conversion edits (approved by Pete, 18 Oct 2026, "as the module recommends") — exactly what they do

Run J is in end of flight's compact format: `impacts32.npy` (float32, times as seconds after T0 = 2014-03-08 00:00 UTC) +
`parents32.npy` + per-seed `run.json`. `mh370 evaluate` refuses it because run.json `impact_columns` does not begin with the 21
core `IMPACT_COLUMNS`. That check is **core-owned (crates/mh370/src/impacts.rs) and was not changed**. The module's recommended
conversion is the stub that was accepted on 11 Oct (architecture.md ~16:40 UTC, with the per-seed temporary-directory amendment).
For each seed:
- `pleiades/prepare/compact_eval.eval_input` writes a **temporary** float64 `impacts.npy` with exactly the 21 core columns, plus a
  run.json whose `impact_columns` lists them;
- the stored columns (latitude_deg, longitude_deg, velocities, mass, takeover position, arc distance, weight, parent, family) are
  copied through end of flight's own reader `compact_impacts.load`. Unix times are restored as t + T0;
- `mode` and `alternative` are joined from parents32 by `parent`; kinetic_energy_j = ½ m |v|², vertical_kinetic_energy_j = ½ m v_up²;
  log_q_correction = 0, because the compact `weight` already carries it;
- `mh370 evaluate run.toml <temp> <out>` runs on that file. The temporary directory is named per seed and deleted when the seed
  ends (the scratch folder was empty at the end of the run).
The seabed-search likelihood reads **latitude and longitude only**, so no rebuilt column enters it. On run C the rebuild with every
non-position column row-reversed gave bit-identical output (11 Oct). The input SHA256 of impacts32.npy, parents32.npy and run.json
was verified against the producer's SHA256SUMS before each seed was used.

## Exchange

- `mh370-exchange/searched-areas/run-j/<family>/seed-N/`, row-aligned with `end-of-flight/run-j/<family>/seed-N/impacts32.npy`:
  `seabed-lnL.npy` (f64, base rho 0.05), `seabed-lnL-rho0 / -rho0.25 / -rho0.5.npy` (f32), `seabed-lnL-without-oi.npy` (f32,
  sensitivity), `seabed-searched-fraction.npy` (f32), `next-oi-area-layer.npy` (u8, map layer only). SHA256SUMS per seed, per family
  and at top level; per-family READY; README.md and READY at top level, written last. **8.5 GB.**
- `mh370-exchange/searched-areas/run-j-both-burst/run-j-waypoints/` — the same columns on the D3/D4 supplementary set (221 MB, READY).

## COVERAGE

**(a) Feasible set (what was searched).** The seabed areas the four campaigns swept, with their sources (coverage/PROVENANCE.md):
Phase 2 union 120,486.5 km² (ATSB valid-data coverage); Bluefin-21 771.4 km² (ATSB states 860); OI 2018 126,009 km² beyond Phase 2
(community tracing, grade C, reported "over 112,000 km²"); OI 2025–26 7,571 km² reported, placed on the 9,696.9 km² outboard band
(grade C). Not searched ground: the inboard band (planned next area), the contract area, bathymetric mapping, and the surface search
(which belongs to ocean drift).

**(b) Model's reach.** Point target at the impact position. The model cannot produce wreckage displaced from the impact point
(settling has not run on run J) → **GAP, declared: every number here is "at the impact point"**. On runs C, D-he and H the
wreckage-field correction was −0.0011 to +0.0025 in Z. The passive acoustic (beacon) search of April 2014 is not modelled yet
(new scope, 17 Oct) → **GAP, declared**; it is small in area. rho has no published value → swept 0 to 0.5.

**(c) Proposal's coverage.** The run J impact samples are end of flight's; this module adds no sampling. ESS after the searches
(pooled Kish, mixture, base): D0' 863,670 (A1 199,740 / A2 426,460 / B 377,262); D1 1,176,680; D2 35,135; D5 9,213; D4 24,571
(A1 2,909); **D3 1,340, with A1 402 and B 500 after the searches (A1 410 before): below the module's estimability floor of 1,000.
D3 for families A1 and B is a COVERAGE GAP** (it comes from the thin both-burst supplement, 8 seeds). Fix: more both-burst seeds
from end of flight, or a D3-aimed proposal. Every other option × family cell is above 1,000. Region: mass north of 33 S is
0.032 → 0.068 under D0'. This module does not compute an ESS for that region; the composer reports 72 for searches including OI
(composer-views-run-j.md), so the northern tail is thin (core prediction 5). That is a limitation of the samples, not of this
likelihood.

**Parameter bounds and sources.** q: Phase 2 0.945 (ATSB detection rating; swept 0.90 / 0.98 in earlier runs), Bluefin-21 0.9,
OI 0.9 (pre-registered). f: OI 2018 0.889 = 112,000 / 126,009 km² (0.952 = 120,000 / 126,009 as sensitivity); OI 2025–26
0.7808 = 7,571 / 9,696.9 km². rho ∈ {0, 0.05, 0.25, 0.5}: no source exists. 0.05 is Pete's reference (8 Oct).

## Deviations

1. **Raw per-campaign coverage columns are not published for run J**, to save disk (the Mac had 34 GiB free at the start and
   22 GiB at the end, and other jobs were writing). The searched-fraction column is published instead.
   `score_run_j.py --with-coverage` regenerates the raw columns per seed.
2. The rho-sweep and without-OI ln L columns are **float32**, and the base column is float64. The float32 storage error is ≤ ~1e-7
   in ln L.
3. The D3/D4 supplementary set had no stratum-level READY. The seeds were used on end of flight's 17 Oct 09:56Z instruction, each
   with its SHA256 verified.
4. The next-area layer is a point-in-polygon on the traced inboard band `oi2024_proposed_inboard_northwest`, read by path from the
   frozen September snapshot (≈ 6,072 km²; the same tracing as the committed OI 2025–26 layer). It is not the 6,388 km² CAPTION
   OI2025B figure, and it is not the official 7,428 km² remainder.

## Files

`run-j-reduced.json` (all options × scenarios × families × strata), `tables.md` / `make_tables.py`,
`composer-standin-comparison.csv`, `validation-crossmodule.json`, `sweep.log`. Code: `engine/hypotheses/seabed-search/`
`score_run_j.py`, `sweep_run_j.py`, `reduce_run_j.py`, `base_guard.py`, `without-ocean-infinity.toml`, `run.toml`.

---
*Footnote (STE100).* These numbers come from the impact samples of the end-of-flight run J. They use the four seabed searches,
with the Ocean Infinity areas as a best estimate from community tracings. They do not use the wreck position on the seabed. The
planned next Ocean Infinity area is shown as a map layer only. It does not change a number.
*Footnote (technical).* P(no find | y) = ρ + (1 − ρ) Π_k [1 − c_k(y) q_k f_k], point target, shared misses; ρ = 0.05 unless stated.
Row mass: end of flight's seed_terms, cell 'D<d> total q=0.333 (C2 silent)'; seeds pooled by evidence; strata by core P(family)
(waypoints 0.9982, free 0.0013, descent-climb 0.0002, repro-radar 0.0003). D3/D4 waypoints from the both-burst supplement. The
OI layers are grade C (MH370-CAPTION tracings), not official geometry. Run J convergence accepted as a pass by project ruling,
16 Oct 2026.
