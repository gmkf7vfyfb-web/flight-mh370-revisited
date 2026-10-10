# Pléiades module review: architecture stand-in "Pléiades-conditional impact PDF on core (b), R600 BTO + Raw BFO"

10 Oct 2026, Pléiades module. Reviewed: `results/pleiades-conditional-r600-raw-bfo-standin.md` (+ `…-standin/`).
Labels: core (b) NOT converged; PROVISIONAL-OVERNIGHT.

**Verdict: adopted.** No redo is needed. Its numbers reproduce the module's own published values exactly: the per-stratum
values before search, the mixture before search, and after search (`next-run-b-core/closeups/closeup-stats.csv`). Its surfaces
are the module's own, sha256-identical. The four points below are recorded; none of them changes a number in the note.

1. **Existence constraint.** The note uses `+alive`. The module's reference is now (b) `unpowered` (ruling ~19:10 B). On core (b)
   the two agree to within 26 km² (`existence-constraints-core-b.md`), so the note stands as it is. Under the declared variant (c)
   `silent`, the conditional narrows and the mean displacement falls from 92 to 26 NM. Any reading of "tension" here should be given
   with that variant beside it.
2. **ln R depends on the grid.** ln R = ln[E_flight(L_H) / mean over the grid of L_H] compares against a flat prior over the
   **grid** (85-103 E, 43-25 S). It shifts by ln(area ratio) if the grid changes, and the module is now widening its grid to
   78-115 E, 45-5 S (composer ruling 1, below). Quote ln S, the overlaps and the mean displacement as the tension measures, and ln R
   only with its reference area. The sign reading in the note (support within the corridor, tension of location) is sound for this
   grid.
3. **Trace-back framing.** "What H favours" is a conditional association, P(trajectory feature | D, H) against P(· | D). It is not
   evidence for H or for any feature. The note says so implicitly; for a paper it should say so explicitly. There is still no
   identity likelihood (brief §3).
4. **Transport correlation (its deviation 9).** Ocean transport has now measured it (`results/ocean-transport-error-pairs.md`):
   central ρ ≈ 0.2-0.3, upper sensitivity 0.5, and ρ = 0.8 not supported at 40-80 km. The module will add ρ = 0.25 and ρ = 0.5 as
   declared sensitivities. Its audit on reference-289 (+28 % area at ρ 0.5) is the expected size.

**Accepted as module results:** the trace-back tables and figures, the search sensitivities and the settling reweighting (+0.4 %),
with the labels the note carries.
