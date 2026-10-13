# Residual-PDF views, Davey eq. 11.2, and the Ocean Infinity 2025–26 variant

Searched-areas module, 9 October 2026. Steps 6 and 7 of the architecture sequence of 9 October.
All numbers below are from the smoke-scale end-of-flight run of `results/seabed-search-eof-smoke/` and
are **provisional** (split-half 0.812). **Superseded at full scale by
`results/seabed-search-289-fullscale-alive/`** — see the full-scale section appended at the end, which
is the version to quote. The smoke-scale text is kept because the method and the guards are the same
and because the two scales disagree about how much the 2025–26 variant is worth.

## 1. The residual view is a view, and it says so

The brief's rule is that the residual PDF is the composer applying this module's likelihood column to
a chosen source posterior, compared against the same posterior with the search evidence disabled —
not a second pipeline. `report.py` now produces exactly that pair for whichever run it is given,
names its source posterior in every page header, and carries two guards:

- **The double-application guard.** If the source run's `impact_columns` already contain a
  `seabed-search:` column, the report refuses and says so. Verified by giving it a run whose
  `run.json` was edited to carry `seabed-search:loglik`: it exits with
  *"already carries this module's likelihood … Refusing to apply the search evidence twice."*
  This is the test the brief asks for in §8, and it matters because a doubly-applied posterior looks
  entirely normal.
- **The source is printed, not assumed.** Every page header carries the run name, the terminal module
  and the 00:19 data option.

**Disclosed deviation.** The architecture entry asks for this to be built against `crates/compose`
in a module-local test. A hypothesis may depend only on `geo`, `hypothesis`, `ocean`, `serde` and
`toml` (`hypotheses/Cargo.toml`), so adding `compose` — even as a dev-dependency — is a change to a
shared, core-owned file and fails `make scope`. The view is therefore built on the `mh370 evaluate`
path, which is the same likelihood column the composer would receive. A core request is in
`coordination/architecture.md`.

## 2. Davey eq. 11.2 as a standard output

Davey's eq. (11.2), printed p. 101: for an area `A` searched with constant `P_D`,

```
P(find during search of A) = P_D ∫_A p(x_final | Z_K) dx_final
```

Reported for every candidate area of the residual posterior, on 0.5° blocks, at a planning
`P_D = 0.9` — Stone et al.'s deliberate cap, used here for ground not yet searched, not this module's
`q`. On the end-of-flight smoke posterior:

| rank | candidate area (0.5°) | residual mass | P(find) | km² | mass before the search |
|---|---|---|---|---|---|
| 1 | 39.5°S 89.0°E | 0.0426 | 0.0383 | 2,394 | 0.0337 |
| 2 | 39.0°S 89.0°E | 0.0425 | 0.0383 | 2,411 | 0.0340 |
| 3 | 40.0°S 88.5°E | 0.0387 | 0.0349 | 2,377 | 0.0307 |
| 4 | 39.5°S 88.5°E | 0.0371 | 0.0334 | 2,394 | 0.0293 |
| 5 | 36.5°S 89.0°E | 0.0359 | 0.0323 | 2,493 | 0.0284 |
| 6 | 41.0°S 88.5°E | 0.0349 | 0.0314 | 2,342 | 0.0276 |
| 7 | 40.5°S 88.5°E | 0.0323 | 0.0291 | 2,359 | 0.0255 |
| 8 | 41.5°S 88.5°E | 0.0320 | 0.0288 | 2,324 | 0.0253 |

Cumulatively, best areas first: **P(find) = 25% needs the best 8 blocks, 19,092 km²; 50% needs 31
blocks, 74,074 km²; 75% needs 109 blocks, 262,354 km².** That is the number a search planner wants
and the one Davey names as §11.1's purpose, and the curve is drawn for the residual and for the
same posterior with the search disabled, so the effect of the past searches on the plan is visible
rather than argued.

Every one of the top eight blocks gains mass under the search evidence — they lie off searched
ground, so renormalisation raises them. That is the residual PDF doing its job: it does not find new
places, it re-ranks the ones that were never excluded.

## 3. Ocean Infinity 2025–26, separately reported

No geometry has been published. What exists is a community tracing of the two bands in Ocean
Infinity's March 2024 presentation, graded C by its author, in the September backup's
`search_footprints.geojson`:

| band | traced area | status in the tracing |
|---|---|---|
| outboard / south-east | 9,696.9 km² on the authalic sphere (9,767.8 km² in the file's own property) | "community vessel tracking indicates the outboard band was traversed; exact AUV coverage remains unpublished" |
| inboard / north-west | 6,072.0 km² | "most likely concentration of the official remaining area"; the official residual is 7,428.54 km² |

Together about 15,840 km² — the contract area. The brief forbids two things here and both are
obeyed:

- **The contract area is not searched ground.** Only the outboard band carries coverage; the inboard
  band is the residual and carries none. The two are nearly disjoint — only 615 km² of the inboard
  band falls inside the outboard band's raster grid at all.
- **The reported 7,571 km² is not spread uniformly.** It is put on the outboard band as
  `coverage_fraction = 7,571 / 9,696.9 = 0.7808`, with `q = 0.9`.

`prepare/build_oi_2025_layer.py` writes the raster to `data/external/search-coverage/`; like the 2018
outline, neither the tracing nor its raster is committed.

**Result: it changes nothing measurable.** On the end-of-flight smoke posterior the variant gives
Z = 0.7909 against 0.7913 for `run.toml` — **0.0004 of the mass**, with the median, the 95% interval
and the share on Phase 2 ground unmoved to the printed precision. Reported separately, as the brief
requires, and it is a negative result worth keeping: the renewed search is far too small, and too
far from where this posterior puts its mass, to act as evidence at this scale.

---

*Searched areas, 9 October 2026.*


---

## Full scale, 10 October 2026: what survives and what does not

Run `eof-289-full` (4 seeds x 3.2 x 10^6 impacts, prior track 289.7 deg, 00:19 held out, log-on cause
`other`, end of flight's `+alive` constraint, split-half 0.972). Source:
`results/seabed-search-289-fullscale-alive/`.

| | smoke scale (295.66 prior) | **full scale (289.7 prior, `+alive`)** |
|---|---|---|
| base evidence Z at rho = 0.05 | 0.4040 | **0.7206** |
| + OI 2025–26 inferred, outboard band only | — | **0.7165** |
| the variant is worth | 0.0004 | **0.0041** |
| + OI 2018 inferred, coverage 0.889 | — | 0.6864 |
| + OI 2018 inferred, coverage 0.952 | — | 0.6840 |
| Davey eq. 11.2: P(find) 25 % | 8 blocks, 19,092 km² | **24 blocks, 59,005 km²** |
| 50 % | 31 blocks, 74,074 km² | **70 blocks, 171,921 km²** |
| 75 % | 109 blocks, 262,354 km² | **248 blocks, 623,095 km²** |

**Three corrections to the smoke-scale readings.**

1. **"It changes nothing measurable" was a smoke-scale statement and does not survive.** The 2025–26
   variant is worth 0.0041 in Z at full scale, ten times its smoke-scale figure. It is still the
   smallest layer in the sweep — rho spans 0.15, OI 2018 is worth 0.034–0.037 — but "nothing
   measurable" is no longer the right phrase. It is **small and measurable**, and it is reported
   separately rather than merged, as the brief requires.
2. **The planning problem is three times larger than smoke scale suggested**, in blocks and in area,
   because the full-scale residual is much wider. Any area figure quoted from the smoke-scale section
   above is wrong by about 3x.
3. **The leading candidate blocks moved.** Full scale puts them at 39.0°S 89.0°E and 38.0°S
   90.5–91.0°E, north-east of the smoke-scale set. Block *ordering* remains the least resolved thing
   this module produces — a 0.5 deg block holds about 1.5 % of the residual mass — so the cumulative
   curve is the reportable object and the ranking is orientation only.

**Unchanged.** Both guards still hold: the double-application refusal, and the source posterior printed
in every page header rather than assumed. The 2025–26 layer is still the outboard band alone at
coverage fraction 0.7808, with the inboard band at zero, because the contract area is not searched
ground. It carries the grade-C inferred-coverage footnote of
`engine/hypotheses/seabed-search/coverage/PROVENANCE.md`.
