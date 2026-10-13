# Review of the two architecture stand-in notes on core (b)

10 October 2026, searched-areas module. Reviewing
`results/searched-areas-next-run-b-rho-eq11-2-coverage-standin.md` (ρ sweep, Davey eq. 11.2,
field coverage) and §3 of `results/pleiades-conditional-r600-raw-bfo-standin.md` (the searches under
the Pléiades hypothesis). **Both accepted**, with four findings and one correction to a sensitivity
that was reported as run but cannot have tested what it says.

## 1. ρ sweep, eq. (11.2), field coverage — ACCEPTED

The reproduction check is the right one and it passes: `+alive` with fixed weights reproduces this
module's own (b) README to every printed digit, per stratum as well as mixed. The nine declared
deviations are all ones I would have had to declare myself. Three readings I adopt:

* **ρ remains the largest term this module controls**, 0.6718 → 0.8359 in Z on Held Out across
  ρ = 0 → 0.5, and what it really sets is the share left on searched ground, 3.1 % → 22.0 %.
* **On (b) the source posterior is worth as much as ρ over its defensible range.** The spread across
  strata is 0.033–0.062 at ρ = 0.05, against 0.016–0.026 for the whole ρ 0 → 0.05 step. This sharpens
  what I had written and I have adopted the stand-in's phrasing.
* **The re-weighting of ruling C moves Z by ≤ 0.0007 here**, consistent with the ≤ 0.0093 I measured
  on the `+alive` arms. Both mixtures are reported side by side.

**Finding 1 — an exception to "a non-detection is not a localisation", which I had stated too
broadly.** For 00:19 R600 BTO Only the residual eq. (11.2) curve is *steeper* than the search-disabled
curve up to about 50 % (73,000 km² against 78,000). Its mass moves south, off the searched corridor,
so what is left is more concentrated in the best unsearched blocks. That matches my own finding that
this option's 50 % highest-posterior-density region *shrinks* by 18 %. The general statement holds at
75 % and for the other options; it does not hold for this one below 50 %, and
`results/seabed-search-why-wider.md` has been corrected to say so.

**Finding 2 — the memory cap.** Peak RSS was 7.98 GB in the driver plus 3.24 GB in the `mh370
evaluate` child, overlapping, so plausibly ~11 GB against an 8–10 GB cap. The driver was the
stand-in's, not a module script, but the fix belongs here and is noted in §4 below.

**Finding 3 — reproducibility.** The field check read settling's private workspace. Settling has since
posted `next-run-b-core-set/` to the exchange, and **I have now re-run all three estimable options from
the published copy and reproduced the stand-in exactly** (Held Out fixed 0.6857 / re-weighted 0.6867;
R600 BTO Only 0.6740 / 0.6732; R600 BTO + Raw BFO 0.5079 / 0.5085). That closes the gap.

## 2. Pléiades §3, the searches under H — ACCEPTED, with one correction

The construction is right: the H-conditional impact samples are reweighted by this module's own
likelihood, ρ swept, Ocean Infinity kept separate and labelled grade C. Two results are worth carrying
forward — under H the searches remove **64 % against 49 %**, because the H-conditional mass sits on and
beside Phase 2 ground; and the 90 % region under H still *grows*, 38,309 → 47,003 km², leaving two
lobes, which is the same mechanism as in the unconditional case.

**Correction.** The sensitivity table reports "independent misses" as equal to shared misses, with the
reason "Phase 2 and Bluefin-21 do not overlap at these impacts". That reason is correct and it means
**the row does not test the dependence question at all**. The miss-dependence alternative acts on the
*internal* overlap of Phase 2 — the four sensors, 17,390.6 km² of repeat coverage over 18,129.6 km² of
ground, 15.0 % of the searched area — which is reached only with the per-sensor split layer, and the
note says that split was not computed. The row should either be run with the split or dropped, because
as it stands it reads as evidence that the dependence choice does not matter, and this module's own
measurement is that it is worth 0.002 in Z on (b). I have asked Pléiades to amend it.

## 3. Holland H1 and H2: the field check now runs

The stand-in could not run the field-coverage check on H1 or H2: this module's script keyed an outcome
as `row × 1000 + draw`, and in settling's resample of a low-ESS option one impact is drawn 1,638 times,
so the key collided silently. The stride is now taken from the data with an overflow assertion.

A second defect surfaced while testing it, and would have been worse: outcomes were matched to element
blocks **by rank** rather than by key, which is correct only when the draws file lists exactly the
element table's outcomes. The moment a mixture mask selects a subset — which the posted layout uses —
elements were attached to the wrong impacts. With the rank matching, H1 returned a field-minus-point
standard deviation of 0.68 and a 24.8 % "reverse" share, both impossible; with key matching it returns
0.014 and 0.0 %. Both fixes are tested, and the reference-289 result reproduces to six decimals.

| 00:19 option | Z point | Z field (mean) | Z any piece | field − point | any − mean | edge outcomes |
|---|---|---|---|---|---|---|
| Held Out | 0.6857 | 0.6858 | 0.6638 | +0.0001 | −0.0220 | 2.31 % |
| R600 BTO Only | 0.6740 | 0.6739 | 0.6520 | −0.0001 | −0.0219 | 2.29 % |
| R600 BTO + Raw BFO | 0.5079 | 0.5076 | 0.4760 | −0.0003 | −0.0316 | 3.31 % |
| **Holland H1** *(not estimable)* | 0.4574 | 0.4585 | 0.4523 | +0.0011 | **−0.0062** | 0.72 % |
| **Holland H2** *(not estimable)* | 0.3586 | 0.3586 | 0.3489 | +0.0001 | **−0.0097** | 0.68 % |

Fixed-weight mixtures; H1 and H2 are identical under both because ruling C excludes them from
re-weighting. "Edge outcomes" is the share whose impact point lies off searched ground while part of
the settled field lies on it; the reverse never occurs in any option.

**The detection-definition bracket is three times narrower for H1 and H2** (0.006–0.010) than for the
estimable options (0.022–0.032), because those posteriors are narrow ribbons that lie either well
inside or well outside the corridor, with few outcomes straddling its edge. That is a property worth
knowing when they become estimable — **their areas and medians remain not results.**

## 4. Composer pass-0 rulings applied to this module's inputs

* **Ruling 1, carry not-computed rows at the neutral value.** This module's not-computed weight on
  core (b) is **0.000** in all five core options: every impact carries a finite position. The
  interface point that matters is a different one — **off-raster impacts are not "not computed"**.
  They return `ln L = 0` by the brief's binding ruling, which is the informative statement "nobody
  searched there", and the composer must not fold the two together. Separately, the field-coverage
  script now **carries** an outcome that settling refused (fate −1, outside its ocean window) at the
  impact position rather than dropping it, and reports the carried count: 1 of 40,001 on Held Out,
  7 of 40,000 on reference-289. Previously those outcomes were silently treated as fully unsearched.
* **Ruling 3, convergence flag.** This module's own factor is converged — split-half 0.890–0.915 after
  the searches on (b). The source is not. Under the ruling the composed flag is the AND, so every
  product carrying this factor is **not converged**, and the labels say so.
* Rulings 2, 4, 5, 6, 7 and 8 are other modules' or core's.

## 5. Readiness for run C

`adapt_exchange_run.sh` (per stratum, verifying SHA256SUMS), then `rerun_next.sh`, then the
field-coverage check against settling's run C samples. The memory point of finding 2 applies to the
accumulation, not to `mh370 evaluate`: this module's map script already keeps a 13,000-bin latitude
histogram instead of per-seed weight arrays, which is what took the earlier pooled attempt to ~18 GB.
