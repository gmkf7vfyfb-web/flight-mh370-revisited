# Repeat search: dependent and independent misses

Searched-areas module, 9 October 2026. Step 4 of the architecture sequence of 9 October and brief
§5 ("model repeat-search dependence … carry both, with dependent as the default").

**All numbers below are from the arc-kernel placeholder fixture — plumbing, not evidence.** What is
evidential here is the coverage geometry in §1, which is measured from the Geoscience Australia
mosaics and does not depend on the impact samples at all.

## 1. The union hides 17,391 km² of repeat coverage

`phase2.cov` is the per-cell maximum of the four Phase 2 mosaics. That is the right representation
for a single cumulative campaign — it is what Davey's `P_D(x)` assumes — and it makes repeat search
invisible. Measured from the per-sensor caches on the 0.001° grid, on the authalic sphere:

| sensor | valid-data area |
|---|---|
| deep-tow side-scan | 103,921.5 km² |
| GO Phoenix SAS | 14,627.3 km² |
| Dong Hai Jiu SAS | 3,164.3 km² |
| AUV side-scan | 16,164.1 km² |
| **sum** | **137,877.1 km²** |
| **union (`phase2.cov`)** | **120,486.5 km²** |
| **repeat coverage the union hides** | **17,390.6 km²** |
| ground with data from two or more sensors | 18,129.6 km² |

So **15.0% of the Phase 2 searched ground was swept more than once**, and in the union that ground is
modelled as having been swept once. Repeat-search dependence is therefore not a hypothetical for this
dataset.

`prepare/build_per_sensor_layers.py` writes the same cells as four layers — `phase2-deep-tow`,
`phase2-go-phoenix`, `phase2-dhj`, `phase2-auv` — from the caches `build_coverage.py` already
produced. No new download. Their raster areas are checked in the module's tests to 0.01 km².

## 2. The two arms

A new module parameter, `miss_dependence`, selects them. They are identical wherever campaigns do not
overlap, because a campaign with no coverage contributes exactly 1 under either rule.

```
shared       (default)   P(no find) = ρ + (1 − ρ) · Π_k [1 − c_k q_k]
independent              P(no find) = Π_k [ ρ + (1 − ρ)(1 − c_k q_k) ]
```

`shared` is the dependent treatment the brief asks for as default: undetectability is a property of
the site — burial, terrain masking, a contact dismissed as geology — drawn once, so terrain that hid
the wreck from one pass hides it from the next. `independent` re-rolls it for every campaign, which
is the physically weaker assumption and is reported beside it, never as the estimate.

Hand-computed fixture, in the module's tests: two campaigns over the same fully covered ground,
q = 0.8, ρ = 0.2. Shared gives 0.2 + 0.8 × 0.2² = **0.232**; independent gives (0.2 + 0.8 × 0.2)² =
**0.1296**.

## 3. Three rungs, not two

The layer representation is itself a dependence assumption, so the fixture gives a ladder:

| | what it assumes about a second sweep of the same ground | Z | median | on Phase 2 coverage |
|---|---|---|---|---|
| `run.toml` — Phase 2 as one union campaign | adds nothing at all (maximal dependence) | 0.4040 | −37.24 | 0.173 |
| Phase 2 split, **shared** misses | adds a fresh look at a wreck that was detectable | 0.4001 | −37.23 | 0.165 |
| Phase 2 split, **independent** misses | adds a fresh look even at a wreck that was not | 0.3966 | −37.21 | 0.158 |

ρ = 0.05, Phase 2 q = 0.945, Bluefin-21 q = 0.9 throughout; the ATSB rated detection by region and
not by sensor, so each split campaign carries run.toml's q — a declared assumption, not a measurement.

**The effect is small and the ordering is the expected one.** Treating the repeat coverage as a
second look removes about 1% more mass (Z 0.4040 → 0.4001); re-rolling undetectability as well
removes about another 0.9% (→ 0.3966). The gap that the brief asks to be reported — dependent against
independent — is **0.0035 in Z, 0.9% relative, and 0.007 in the share of mass left on Phase 2
ground.** The three arms are evaluated on the same impact samples with the same weights, so the
comparison between them is exact; it is the absolute level that is placeholder.

**Decision, recorded with its reason.** `run.toml` stays on the union layer as the main estimate. The
brief's campaign table defines Phase 2 as one campaign of 120,486.5 km², the union is what matches the
ATSB's own stated figure, and the split changes the headline by less than the width of the ρ sweep's
smallest step. The split pair is reported as a labelled sensitivity in `search-evidence.pdf`. If a
later ruling prefers the split as the base, nothing but `run.toml` changes.

## 4. A correction the module must carry

The brief states that the marginal likelihood depends only on the mean of ρ, so a broad prior gives
the same answer as a point mass at its mean. **That is exactly true for the shared arm, which is
linear in ρ, and false for the independent arm**, which is a product of terms each linear in ρ and so
depends on its higher moments wherever campaigns overlap.

Hand-computed, in the tests: ρ equal to 0 or 0.4 with equal probability, mean 0.2, two overlapping
campaigns at q = 0.8. Shared gives 0.232 either way. Independent gives 0.1552 when the prior is
averaged and 0.1296 at the mean — a 20% difference. Any future dependent construction built from a
continuous shared detectability inherits this; the mean-only claim travels with the shared two-state
model and with nothing else. The same point is made in `results/seabed-detectable-target.md` §7.

## 5. Tests added

- `repeat_search_dependence_acts_only_where_campaigns_overlap` — the hand-computed pair above, plus
  equality of the two arms at three points where coverage is disjoint, plus the boundary case where
  bilinear interpolation gives both campaigns a half and the arms separate (0.488 against 0.4624).
- `the_marginal_depends_only_on_the_mean_of_rho_under_shared_but_not_independent` — §4.
- `embedded_layers_match_the_prepare_script` extended to the four per-sensor layers.

Nine module tests pass at `RAYON_NUM_THREADS=2`.

---

*Searched areas, 9 October 2026.*
