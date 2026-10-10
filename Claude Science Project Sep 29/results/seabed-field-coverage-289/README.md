# Does the point target matter? Coverage read over settling's real wreckage fields

10 October 2026, searched-areas module. `engine/hypotheses/seabed-search/field_coverage_check.py`;
`engine/runs/seabed-search-analysis/field-coverage-check.json`.

Settling delivered seabed wreckage samples on reference-289 (`mh370-exchange/settling/
reference-289-wreckage-field/`, set A = `none__other`, 200,000 systematically resampled equally
weighted outcomes) with the resting latitude and longitude of **every settled element**. Until now this
module read the coverage raster at one point, the impact position, because there was nothing else to
read it at. Settling's extent summary (`results/settling-field-extent-289/`) says the structural R90 of
a field is 0.86-3.6 km at the median, against a 0.01 deg (about 1.1 km) raster cell — so this is
exactly the second regime of `results/seabed-detectable-target.md` §6, the one the size-response
saturation result does **not** cover.

Measured on 40,000 outcomes (every fifth, stride-wise so the stratification survives) and their
2,177,085 settled elements. Afloat elements are excluded: they are ocean drift's evidence, not the
seabed search's. Coverage is read by the module's own raster code, via `mh370 evaluate` on the element
positions, and the point-target arm is asserted against the module's own `no_find_probability` column.

| campaign term | Z | mass removed | mean Phase 2 coverage |
|---|---|---|---|
| **point** — `c_k(impact)`, what every run to date uses | 0.7337 | 0.2663 | 0.2966 |
| **mean** — mass-weighted mean of `c_k(x_i)` over settled elements | **0.7340** | 0.2660 | 0.2963 |
| **any** — `1 − Π_i [1 − c_k(x_i)]`, some element on valid data | 0.7106 | 0.2894 | 0.3224 |

ρ = 0.05, q = 0.945 (Phase 2) and 0.900 (Bluefin-21).

## What this settles

1. **The point target is adequate — for the conservative treatment.** Reading coverage at the impact
   position instead of over the whole settled field changes the evidence by **0.0003 in Z**, three
   decimal places below anything else in this module's uncertainty budget. Limitation 1 of the methods
   draft can be downgraded from "conservative for a large field and optimistic for a small one" to
   "measured, and worth 0.0003".
2. **The coarse-against-fine choice is worth 2.3 points, and it is now the larger of the two.**
   `any` removes 28.9% of the probability against `mean`'s 26.6%. §5 adopted the coarse treatment by
   argument; that argument is now carrying a real difference and should be stated as a reported
   bracket rather than a settled choice. **This module reports `mean`**: recognition is a
   campaign-level event on a recognisable signature, not on one imaged pixel of one element, so `any`
   is the optimistic bound and `mean` the conservative one.
3. **Where the difference lives.** Per outcome, the Phase 2 coverage seen by the field minus that seen
   by the impact point has mean −0.0004 and standard deviation 0.024; it exceeds 0.05 in 2.46% of
   outcomes and 0.25 in 0.19%. In **2.29% of outcomes the impact position lies on unsearched ground
   while part of the settled field reaches onto searched ground**, and the reverse never happens. That
   asymmetry is the whole effect: fields straddling the edge of the searched corridor, which a point
   target places wholly outside it.

So the honest summary is that the field model changes the *answer* by almost nothing and changes the
*bracket* by 2.3 points, and that the bracket is an assumption about what counts as a detection rather
than anything the coverage data can resolve.

## Caveats

- Set A is the held-out arm only. The four-option re-run belongs with the next impacts.
- Settling emits no plan length or height proud, so `a_k ≡ 1` here: this is the coverage question in
  isolation, with the size response at its saturated value, which §6 and
  `results/seabed-size-response.md` justify.
- PROVISIONAL on settling's side: breakup table, dive class (b), Boeing glide, uncorrected fuel.
- `+alive` is a filter on impact time and is not applied here. On the held-out arm it moves Z by
  0.013 (`results/seabed-search-0019-h1h2-alive/`): about forty times the field-model effect measured
  above (0.0003) and a little over half the detection-definition bracket (0.023). So the ordering of
  these three, smallest first, is field model, then `+alive`, then what counts as a detection.
