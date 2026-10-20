# Searched areas on run J at the settled seabed positions, beside the impact point

18 October 2026, Searched Areas module. Task: Pete's ruling of 13 Oct 2026 ("apply the search likelihood to the seabed positions
where settling provides them - that is what the sonar searched"), on settling's run J samples (READY 18 Oct 06:30Z).

**Label for every number here: "Ocean Infinity coverage inferred (grade C), included as best estimate".** The configuration is
the impact-point run J configuration, unchanged (commit 08fb80b; `results/searched-areas-run-j/README.md`): base = ATSB Phase 2 +
Bluefin-21 + Ocean Infinity 2018 + Ocean Infinity 2025–26 (outboard band), inferred geometry, enforced by `base_guard.py`. *Without
Ocean Infinity* is a labelled sensitivity. rho 0 / 0.05 / 0.25 / 0.5. The planned next Ocean Infinity area is a **map layer only**.
Run J convergence: **accepted as a pass by project ruling, 16 Oct 2026**. Settling's labels travel with these numbers: physics
items PROVISIONAL (end of flight's run J note); breakup rows settled from the intact impact point (gap G-bf); P(left) = 0.8
PROVISIONAL.

## Result

1. **The settled seabed position changes the search evidence by very little.** Under D0' (00:19 values held out, transmission
   imposed), Z is **0.3101 at the impact point and 0.3113 at the settled positions** (Δ +0.0012 ± 0.0001, paired on the same
   160,000 outcomes). Over all six 00:19 options Δ is +0.0005 to +0.0012. That agrees with this module's earlier field checks on
   reference-289 (+0.0003) and run D-he (−0.0001 to +0.0007).
2. **Δ is positive in every resolved mixture and stratum cell of the base case** (one cause cell, D1 × C2 silent, is −0.0001 ±
   0.0001). Settling spreads each field about its impact (p50 offset about 0.35 km, p90 2–4 km). Where the impact lies on searched
   ground near its edge, part of the field's mass falls off it and P(no find) rises; where the impact lies just off searched
   ground, part of the field falls on it (0.8–2.3 % of outcomes, Table 1) and P(no find) falls. The first case carries slightly
   more weight, because the posterior mass on searched ground is larger.
3. **Weight on searched ground** before the searches is unchanged to 0.002 (D0' 0.775 → 0.774). After the searches it rises by
   about 0.008 (0.290 → 0.298 on the same outcomes; 0.284 at the impact point over all rows). That is, slightly more of the
   residual weight remains on searched ground when the field is spread.
4. **What counts as a detection is still the larger choice.** If any one settled piece on searched ground counts ('any', the
   optimistic bound), Z falls to 0.2844 under D0' (−0.026 from the impact point). This module reports the 'mean' treatment
   (the field is one object with a covered fraction), as it did on reference-289 and run D-he.
5. **rho is still the largest module-controlled sensitivity** (Table 2): settled Z 0.275 / 0.311 / 0.456 / 0.638 at rho 0 /
   0.05 / 0.25 / 0.5. Without Ocean Infinity, settled Z is 0.3509.
6. **Hypothesis families** (Table 3): the family shares after the searches are the same at the impact point and at the settled
   positions to 0.002 in every option (D0': A1 0.075, A2 0.380, B 0.554).

All numbers are Monte Carlo estimates on the stated samples.

**Table 1. Impact point against settled seabed position, all six 00:19 options, four-family mixture, base, rho 0.05.**

| option | Z impact point (all rows) | Z settled position | Δ settled − point (± MC SE) | Z any settled piece (optimistic bound) | on searched ground before: point → settled | after: point → settled (same outcomes) | after, impact point all rows | impact off searched ground, field on | outcomes |
|---|---|---|---|---|---|---|---|---|---|
| D0' held out | 0.3101 | **0.3113** | +0.0012 ± 0.0001 | 0.2844 | 0.775 → 0.774 | 0.290 → 0.298 | 0.284 | 0.0232 | 160,000 |
| D1 R600 BTO | 0.2745 | **0.2752** | +0.0007 ± 0.0001 | 0.2507 | 0.808 → 0.808 | 0.328 → 0.335 | 0.329 | 0.0211 | 160,000 |
| D2 R600 BTO + BFO | 0.2110 | **0.2122** | +0.0012 ± 0.0001 | 0.1909 | 0.882 → 0.880 | 0.470 → 0.478 | 0.467 | 0.0166 | 160,000 |
| D3 both BFOs (H2 data)† | 0.1507 | **0.1513** | +0.0007 ± 0.0001 | 0.1358 | 0.948 → 0.948 | 0.688 → 0.696 | 0.685 | 0.0134 | 160,000 |
| D4 shared offset (H1 data)† | 0.1366 | **0.1373** | +0.0007 ± 0.0001 | 0.1255 | 0.964 → 0.963 | 0.764 → 0.769 | 0.761 | 0.0084 | 160,000 |
| D5 R1200 BFO with offset | 0.1437 | **0.1442** | +0.0005 ± 0.0001 | 0.1287 | 0.955 → 0.955 | 0.726 → 0.734 | 0.727 | 0.0114 | 160,000 |

**Table 2. D0', mixture: the rho sweep and the sensitivity without Ocean Infinity.**

| case | Z impact point | Z settled | Δ (± SE) | Z any piece | on searched ground after: point → settled (same outcomes) | ATSB ground after, settled | north of 33 S after, settled | in next OI area after, settled (layer) |
|---|---|---|---|---|---|---|---|---|
| base, rho 0.05 (reference) | 0.3101 | **0.3113** | +0.0012 ± 0.0001 | 0.2844 | 0.290 → 0.298 | 0.256 | 0.072 | 0.016 |
| base, rho 0 | 0.2738 | **0.2751** | +0.0012 ± 0.0001 | 0.2467 | 0.195 → 0.205 | 0.164 | 0.079 | 0.018 |
| base, rho 0.25 | 0.4554 | **0.4563** | +0.0009 ± 0.0001 | 0.4350 | 0.516 → 0.519 | 0.474 | 0.054 | 0.011 |
| base, rho 0.5 | 0.6369 | **0.6375** | +0.0006 ± 0.0001 | 0.6233 | 0.652 → 0.652 | 0.607 | 0.043 | 0.008 |
| sensitivity: without Ocean Infinity, rho 0.05 | 0.3502 | **0.3509** | +0.0007 ± 0.0001 | 0.3247 | 0.357 → 0.361 | 0.228 | 0.093 | 0.014 |

**Table 3. By hypothesis family (A1 / A2 / B), mixture, base, rho 0.05: impact point → settled.**

| option | family | Z impact point | Z settled | Δ (± SE) | share before | share after, point | share after, settled | on searched ground after: point → settled | row ESS before: waypoints source / lowest other stratum |
|---|---|---|---|---|---|---|---|---|---|
| D0' held out | A1 | 0.1329 | **0.1335** | +0.0006 ± 0.0001 | 0.172 | 0.075 | 0.075 | 0.768 → 0.768 | 997,405 / 117,172 |
| D0' held out | A2 | 0.3431 | **0.3441** | +0.0010 ± 0.0002 | 0.343 | 0.380 | 0.380 | 0.247 → 0.255 | 742,682 / 120,994 |
| D0' held out | B | 0.3498 | **0.3511** | +0.0013 ± 0.0003 | 0.484 | 0.554 | 0.554 | 0.245 → 0.254 | 716,892 / 149,808 |
| D1 R600 BTO | A1 | 0.1112 | **0.1115** | +0.0003 ± 0.0000 | 0.199 | 0.080 | 0.080 | 0.933 → 0.933 | 1,244,077 / 181,766 |
| D1 R600 BTO | A2 | 0.3236 | **0.3250** | +0.0014 ± 0.0003 | 0.346 | 0.403 | 0.403 | 0.265 → 0.273 | 879,548 / 188,071 |
| D1 R600 BTO | B | 0.3085 | **0.3098** | +0.0013 ± 0.0003 | 0.454 | 0.516 | 0.517 | 0.283 → 0.293 | 688,706 / 169,508 |
| D2 R600 BTO + BFO | A1 | 0.1050 | **0.1054** | +0.0004 ± 0.0000 | 0.238 | 0.119 | 0.119 | 0.986 → 0.985 | 48,477 / 6,159 |
| D2 R600 BTO + BFO | A2 | 0.2466 | **0.2476** | +0.0011 ± 0.0002 | 0.234 | 0.275 | 0.274 | 0.397 → 0.407 | 27,700 / 6,452 |
| D2 R600 BTO + BFO | B | 0.2431 | **0.2447** | +0.0016 ± 0.0003 | 0.527 | 0.604 | 0.605 | 0.401 → 0.412 | 35,949 / 6,363 |
| D3 both BFOs (H2 data)† | A1 | 0.1054 | **0.1058** | +0.0003 ± 0.0000 | 0.080 | 0.056 | 0.056 | 0.988 → 0.987 | 409 / 51 |
| D3 both BFOs (H2 data)† | A2 | 0.1454 | **0.1462** | +0.0008 ± 0.0002 | 0.370 | 0.362 | 0.362 | 0.701 → 0.709 | 5,302 / 843 |
| D3 both BFOs (H2 data)† | B | 0.1608 | **0.1615** | +0.0007 ± 0.0002 | 0.550 | 0.580 | 0.580 | 0.653 → 0.661 | 2,595 / 591 |
| D4 shared offset (H1 data)† | A1 | 0.1098 | **0.1103** | +0.0005 ± 0.0000 | 0.249 | 0.201 | 0.201 | 0.962 → 0.962 | 4,584 / 271 |
| D4 shared offset (H1 data)† | A2 | 0.1396 | **0.1402** | +0.0006 ± 0.0002 | 0.320 | 0.330 | 0.330 | 0.733 → 0.742 | 42,580 / 3,113 |
| D4 shared offset (H1 data)† | B | 0.1499 | **0.1507** | +0.0007 ± 0.0002 | 0.429 | 0.471 | 0.471 | 0.693 → 0.701 | 28,109 / 749 |
| D5 R1200 BFO with offset | A1 | 0.1068 | **0.1070** | +0.0002 ± 0.0000 | 0.060 | 0.045 | 0.045 | 0.979 → 0.978 | 2,178 / 279 |
| D5 R1200 BFO with offset | A2 | 0.1397 | **0.1403** | +0.0006 ± 0.0001 | 0.422 | 0.404 | 0.405 | 0.757 → 0.762 | 20,864 / 3,996 |
| D5 R1200 BFO with offset | B | 0.1512 | **0.1521** | +0.0008 ± 0.0002 | 0.517 | 0.543 | 0.545 | 0.698 → 0.706 | 9,401 / 2,554 |

**Table 4. By log-on cause (C1 / C2 silent), mixture, base, rho 0.05 (settling's resample only; no impact-point all-rows value exists for cause cells).**

| option | cause | Z point (same outcomes) | Z settled (resample) | Δ (± SE) | on searched ground after: point → settled |
|---|---|---|---|---|---|
| D0' held out | C1 | 0.3123 | 0.3133 | +0.0010 ± 0.0002 | 0.282 → 0.290 |
| D0' held out | C2 silent | 0.4561 | 0.4567 | +0.0006 ± 0.0001 | 0.167 → 0.173 |
| D1 R600 BTO | C1 | 0.2765 | 0.2773 | +0.0008 ± 0.0002 | 0.326 → 0.333 |
| D1 R600 BTO | C2 silent | 0.4209 | 0.4207 | -0.0001 ± 0.0001 | 0.186 → 0.192 |
| D2 R600 BTO + BFO | C1 | 0.2114 | 0.2123 | +0.0009 ± 0.0002 | 0.466 → 0.475 |
| D2 R600 BTO + BFO | C2 silent | 0.1459 | 0.1467 | +0.0008 ± 0.0001 | 0.730 → 0.733 |
| D3 both BFOs (H2 data)† | C1 | 0.1508 | 0.1516 | +0.0008 ± 0.0001 | 0.685 → 0.692 |
| D3 both BFOs (H2 data)† | C2 silent | 0.1306 | 0.1311 | +0.0005 ± 0.0001 | 0.809 → 0.812 |
| D4 shared offset (H1 data)† | C1 | 0.1381 | 0.1386 | +0.0006 ± 0.0001 | 0.751 → 0.757 |
| D4 shared offset (H1 data)† | C2 silent | 0.1224 | 0.1236 | +0.0011 ± 0.0001 | 0.868 → 0.870 |
| D5 R1200 BFO with offset | C1 | 0.1432 | 0.1439 | +0.0007 ± 0.0001 | 0.728 → 0.736 |
| D5 R1200 BFO with offset | C2 silent | 0.1284 | 0.1291 | +0.0007 ± 0.0001 | 0.833 → 0.836 |

**Table 5. Per stratum (family folder), all six options, base, rho 0.05: Z impact point → Z settled (Δ ± SE).**

| option | run-j-waypoints | run-j-free | run-j-descent-climb | run-j-repro-radar |
|---|---|---|---|---|
| D0' held out | 0.3101 → 0.3112 (+0.0012 ± 0.0001) | 0.3744 → 0.3763 (+0.0020 ± 0.0002) | 0.3475 → 0.3484 (+0.0010 ± 0.0001) | 0.3749 → 0.3766 (+0.0016 ± 0.0002) |
| D1 R600 BTO | 0.2744 → 0.2751 (+0.0007 ± 0.0001) | 0.3171 → 0.3181 (+0.0011 ± 0.0002) | 0.3006 → 0.3013 (+0.0007 ± 0.0001) | 0.3101 → 0.3107 (+0.0006 ± 0.0001) |
| D2 R600 BTO + BFO | 0.2110 → 0.2122 (+0.0012 ± 0.0001) | 0.2567 → 0.2581 (+0.0014 ± 0.0002) | 0.2387 → 0.2395 (+0.0009 ± 0.0001) | 0.2462 → 0.2473 (+0.0011 ± 0.0002) |
| D3 both BFOs (H2 data)† | 0.1506 → 0.1513 (+0.0007 ± 0.0001) | 0.1872 → 0.1875 (+0.0003 ± 0.0001) | 0.1676 → 0.1684 (+0.0008 ± 0.0001) | 0.1869 → 0.1872 (+0.0003 ± 0.0001) |
| D4 shared offset (H1 data)† | 0.1366 → 0.1372 (+0.0007 ± 0.0001) | 0.1711 → 0.1720 (+0.0009 ± 0.0001) | 0.1566 → 0.1573 (+0.0007 ± 0.0001) | 0.1687 → 0.1693 (+0.0007 ± 0.0001) |
| D5 R1200 BFO with offset | 0.1436 → 0.1441 (+0.0005 ± 0.0001) | 0.1719 → 0.1728 (+0.0008 ± 0.0001) | 0.1587 → 0.1595 (+0.0008 ± 0.0001) | 0.1734 → 0.1735 (+0.0001 ± 0.0001) |

Z = E[P(no find)] under the option's end-of-flight posterior. **Z impact point (all rows)** is the run J impact-point value over
313.6 M rows (`results/searched-areas-run-j/run-j-reduced.json`). **Z settled** = Z impact point (all rows) + Δ, where Δ is the
paired mean of P(no find | settled field) − P(no find | impact) over settling's equal-weight outcomes (a control-variate estimate;
judgement call recorded below). The direct resample mean of P(no find | settled field) is also published (`Z_settled_resample`).
"On searched ground" = 1 − Π_k (1 − f_k c_k) over the four base campaigns. "Same outcomes" = settling's resample, scored at the
impact and at the settled field. Strata are mixed by settling's `stratum-mixture-weights.json` (core share × Z_s per cell);
families within a stratum by the family product's share of the option. † D3/D4: the waypoints stratum is taken from the
both-burst supplement (`settling/run-j/run-j-both-burst-waypoints`), beside, not pooled, with the production waypoints weight.

## What was done

1. **Inputs.** `mh370-exchange/settling/run-j/<stratum>/` (READY; SHA256 of `<tag>_impacts.f64`, `_elements.f64`, `_draws.npz`,
   `_source.npy`, `_info.json` verified against settling's SHA256SUMS before use). 5 sets, **1,865,283 table rows, 2,339,274
   outcomes (row, draw), 155.5 M elements of which 133,115,678 settled (fate 0) and scored**; 22.4 M afloat elements (fate 1)
   excluded (ocean drift's evidence). No element was 'not computed' or refused; **0 outcomes carried** at the impact position.
2. **Coverage at every settled element and at every impact** comes from `mh370 evaluate run.toml` itself (the module's bilinear
   raster code), through a temporary float64 `impacts.npy` with the 21 core columns (position set, weight 1, other columns 0; the
   likelihood reads latitude and longitude only), in 3 M-row chunks, deleted after each chunk. Nothing is reimplemented.
3. **Recipe** = this module's field treatment (`field_coverage_check.py`, `results/seabed-field-coverage-289/`, run D-he
   `results/seabed-search-d-he/field-coverage-table.md`): per outcome, c_k = settled-mass-weighted mean of c_k(x_i) ('mean',
   reported), and 'any' = 1 − Π_i (1 − c_k(x_i)) as the optimistic bound. **Per impact row, the likelihood is the mean of P(no find)
   over the row's settling draws** (brief §2: alternative outcomes are averaged, never multiplied). A product's Z is the plain
   mean over its equal-weight outcomes.
4. **Validated on one seed first** (run-j-free seed-1: 19,773 rows, 26,215 outcomes, 1,487,386 settled elements), then all five
   sets, 4 workers × 2 threads (both-burst after, 4 threads).

**Checks (every set):**
- algebra P = rho + (1 − rho) Π_k (1 − q_k f_k c_k) against evaluate's own `no_find_probability`: max |ΔP| **0.0** at the impacts
  and at all 133.1 M elements;
- point arm against the **published run J impact-point column** (`searched-areas/run-j/<stratum>/seed-k/seabed-lnL.npy` at the
  `source.npy` row): **1,865,283 rows, max |Δ ln L| 0.0**;
- outcomes = Σ settling's draws column; every table row has an outcome; element table in key order;
- averaging test (two identical draws = one): pass; off-ground test (all settled pieces off coverage → ln L exactly 0): pass on
  244,386 outcomes; every published ln L finite;
- settling's resample against the impact-point Z over all rows (96 cells: 4 strata × 6 options × 4 family splits): max |z| 2.46,
  2.1 % of cells above |z| 2, none above 3 (`resample-check.json`). The resample is a fair sample of the posterior.

Wall time: validation 2 s; full scoring 27 s; reduction and tables < 10 s. Disk: exchange output 256 MB; peak temporary scratch
< 3 GB; the Mac stayed at 43 GiB free (the 35 GiB stop was never approached; the repository clone and build in the work area
used about 4.3 GB).

## Exchange

`mh370-exchange/searched-areas/run-j-settled/` (README.md, SHA256SUMS, READY last): per set `outcomes.npz`, `rows.npz`,
`summary.json`, SHA256SUMS, READY; top level `run-j-settled-reduced.json`. `rows.npz` → `lnL_settled_base_rho0.05` (float64) is
this module's settled likelihood column, row-aligned with settling's `<tag>_impacts.f64` (map to `impacts32.npy` via
`<tag>_source.npy`). The rho / without-OI / 'any' variants and the matching `lnL_point_*` are float32 alternatives. **Use one column
per product.** The settled column exists only on settling's resampled table rows; the all-rows impact-point columns stay in
`searched-areas/run-j/`.

## COVERAGE

**(a) Feasible set (what was searched).** As the impact-point run J note: Phase 2 union 120,486.5 km²; Bluefin-21 771.4 km²;
OI 2018 126,009 km² beyond Phase 2 (grade C, reported "over 112,000 km²"); OI 2025–26 7,571 km² placed on the 9,696.9 km²
outboard band (grade C). Not searched ground: the planned next area, the contract area, bathymetric mapping, and the surface
search (ocean drift's).

**(b) Model's reach.** The seabed target is now settling's wreckage field (mass-weighted covered fraction), not the impact
point: the impact-point reach gap of the run J note is **CLOSED** for the rows settling sampled. Remaining reach gaps, declared:
- **G-bf** (settling): in-flight breakup rows are settled from the intact impact point; a fragment field spread along the descent
  is not modelled. Effect on this module: such fields would be wider, so Δ (and the 'any' bracket) would be larger for those rows.
- **Detection definition**: 'mean' reported, 'any' published as the optimistic bound (bracket −0.011 to −0.026 in Z).
- **Size and height-proud response**: a_k ≡ 1 (saturated for aircraft-sized pieces; `results/seabed-size-response.md`); burial
  stays in rho.
- **Passive acoustic (beacon) search, Apr 2014**: not modelled yet (17 Oct scope), small in area.
- rho has no published value → swept 0 to 0.5.
- The north-of-33 S and next-area-layer shares use the impact latitude / position for each outcome (offset p50 about 0.35 km).

**(c) Proposal's coverage.** This module adds no sampling. Settled positions exist for settling's resampled rows (1,865,283 rows
across the five sets; row ESS before the searches as settling's products). Products below the row-ESS gate of 1,000 among those
used: **16 of 144** (4 strata × 36; the 12 waypoints D3/D4 products taken from both-burst instead of production), all family
or cause splits under the two-BFO treatments (D3–D5). In the mixture (waypoints 0.998) only **D3 × A1 (row ESS 409, both-burst)**
is below the gate: a **COVERAGE GAP**, as at the impact point. Fix: more both-burst seeds from end of flight, or a D3-aimed
proposal. The other 15 are in the minor strata (free / descent-climb / repro-radar, combined weight 0.002) and do not change a
mixture value at the precision shown. Every primary (both-cause, all-family) cell is estimable in every stratum. ESS per region is
not computed here; the northern tail (north of 33 S) is thin (core prediction 5; composer ESS 72 with the searches).

**Parameter bounds and sources.** Unchanged from the run J note: q Phase 2 0.945, Bluefin-21 0.9, OI 0.9; f OI 2018 0.889, OI
2025–26 0.7808; rho ∈ {0, 0.05, 0.25, 0.5}, no source (0.05 is Pete's reference, 8 Oct).

## Judgement calls (recorded)

1. **Headline estimator.** Z settled = impact-point Z over all rows + paired Δ on settling's outcomes, because the paired
   difference has about 1/20 of the Monte Carlo noise of the direct resample mean (SE 0.0001 against about 0.002). The direct
   resample mean is published beside it; the two differ only by the resample's noise in the point arm (check above).
2. **Per-row aggregation** over all of a row's settling draws (not only the draws one product selected), because settling's draws
   are independent outcomes for that impact, the same for every 00:19 option.
3. **D3/D4 mixture weight** for the both-burst waypoints set: the production waypoints weight of the cell (settling publishes none
   for the supplement). Waypoints carries 0.998, so the choice does not change a value at the precision shown.

## Deviations

1. Settled likelihood columns cover settling's resampled rows only (1.87 M table rows), not all 313.6 M impact rows; settling
   resampled them. The composer should use them through settling's products, or keep the impact-point columns for all rows.
2. Cause cells (C1 / C2 silent) have no impact-point all-rows value in the run J tables, so Table 4 is resample-only.
3. The rho, without-OI and 'any' row columns are float32 (≤ ~1e-7 in ln L); the base settled column is float64.
4. No figure: the result is a change of ≤ 0.0012 in Z; the run J impact-point maps stand for the seabed maps to that precision.

## Files

`run-j-settled-reduced.json`, `tables.md` / `make_tables.py`, `resample-check.json`. Code: `engine/hypotheses/seabed-search/`
`score_settled_run_j.py`, `reduce_settled_run_j.py`. Commands:
`python hypotheses/seabed-search/score_settled_run_j.py <settling run-j>/<set> --out <exchange>/searched-areas/run-j-settled/<set> --threads 2`
(validation: `--validate-seed 1`), then `reduce_settled_run_j.py <exchange run-j-settled> <settling run-j> results/searched-areas-run-j/run-j-reduced.json <out.json>`.

---
*Footnote (STE100).* These numbers come from the end-of-flight run J samples and the wreck positions on the seabed from settling.
They use the four seabed searches, with the Ocean Infinity areas as a best estimate from community tracings. A wreck field counts
as one object; the part of the field on searched ground sets the chance to find it. The planned next Ocean Infinity area is a map
layer only. It does not change a number.
*Footnote (technical).* P(no find | W) = ρ + (1 − ρ) Π_k [1 − q_k f_k c̄_k(W)], c̄_k = settled-mass-weighted mean of bilinear
c_k(x_i) over fate-0 elements; L(row) = mean over settling draws; ρ = 0.05 unless stated. Row mass: end of flight's seed_terms
cells via settling's products (cell 'total' = both causes, q = 1/3, C2 silent). Strata by settling's stratum-mixture-weights.json
(waypoints 0.9982 core share). D3/D4 waypoints from the both-burst supplement. OI layers grade C (MH370-CAPTION tracings). Run J
convergence accepted as a pass by project ruling, 16 Oct 2026. Breakup rows settled from the intact impact point (G-bf).
