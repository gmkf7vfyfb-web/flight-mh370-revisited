# Why the 90 % region is larger after the searches than before

10 October 2026, searched-areas module. Pete's question on the core-options chart. Numbers are the
core (b) mixture, `results/seabed-search-b/`; **unconverged**, as labelled there.

## The measurement

| 00:19 option | evidence Z | 50 % region | 90 % region | 99 % region |
|---|---|---|---|---|
| Held Out | 0.688 | **+1 %** | +24 % | +9 % |
| R600 BTO Only | 0.671 | **−18 %** | +20 % | +12 % |
| R600 BTO + Raw BFO | 0.507 | **+4 %** | +34 % | +17 % |
| Holland H1 *(not estimable)* | 0.457 | −23 % | −5 % | +6 % |
| Holland H2 *(not estimable)* | 0.358 | +4 % | +18 % | +10 % |

**The core does not expand.** The 50 % region holds or shrinks in every estimable option — by 18 % for
R600 BTO Only. It is the shoulders that spread. That pattern is the explanation.

## Why

The non-detection likelihood is bounded. With ρ = 0.05 and q = 0.945 it is

* `P(no find) = 1.000` off searched ground,
* `P(no find) = 0.102` where Phase 2 holds full coverage,

a factor of 9.8, not a veto. The posterior after the searches is the posterior before, multiplied by
that factor and **renormalised by the evidence Z**. So each cell is multiplied by:

| 00:19 option | unsearched ground | fully searched ground |
|---|---|---|
| Held Out | **× 1.45** | × 0.15 |
| R600 BTO Only | × 1.49 | × 0.15 |
| R600 BTO + Raw BFO | × 1.97 | × 0.20 |

**Unsearched ground becomes absolutely denser, not just relatively.** Cells on the flanks that sat just
below the 90 % threshold are lifted by 45–97 % and cross it, so they join the region. Meanwhile the
searched ground — which lay in the *middle* of the distribution, along the 7th arc, not around its
rim — is pushed down by a factor of five to seven. The distribution is left flatter, and a flatter
distribution needs more area to hold any given share of probability.

Three consequences follow, and all three are real rather than artefacts of the display.

1. **A 90 % region after the searches is 90 % of a different distribution.** It is the smallest area
   that now holds 90 % of belief, having accounted for the failed searches. Comparing its area with the
   before-region's is comparing two correctly-normalised answers to two different questions, not a
   before-and-after of one quantity.
2. **Operationally: the easy ground has been used up.** The most probable places were searched and
   found empty. To stay 90 % confident you must now cover more area than you would have needed before
   anyone looked. That is the correct consequence of a negative result, not a failure of the method.
3. **The better the search was, the wider the residual region.** Raising q, or lowering ρ, deepens the
   trough in the middle and flattens what is left further. In the limit ρ → 0 and q → 1 the searched
   corridor is removed outright and the residual is a ring, which is the widest case of all. The region
   only begins to shrink once the searches cover enough of the distribution that what remains is small
   in its own right — and 31 % removed is nowhere near that point.

## The exception, and why it is not evidence against this

Holland H1's 90 % region falls 5 %. H1 rests on 255 effective impacts of 51.2 × 10⁶, so its areas are
not results and are reported as not yet estimable. Where a distribution is a narrow ribbon lying mostly
along the searched corridor, removing a segment can shorten it rather than flatten it, so a decrease is
possible in principle — but this particular number should not be used as the example.

## An exception, found by the architecture stand-in's eq. (11.2) curve

For **00:19 R600 BTO Only** the residual planning curve is *steeper* than the search-disabled one up
to about 50 %: 73,000 km² against 78,000 to reach P(find) = 50 %. Beyond 50 % it is shallower again
(75 %: 304,000 against 219,000). That matches the 50 % region of the same option shrinking by 18 % in
the table above, and both have the same cause: this option's mass moves south, off the searched
corridor (median −37.94 → −38.47), so what survives is *more* concentrated in the best unsearched
blocks rather than less.

So the general statement — that a non-detection widens the answer — holds at the 90 % and 99 % levels
and for every option at 75 %, but **it is not universal.** Where the evidence has already moved the
distribution off the searched ground, removing what little remains on it can concentrate the residual.
The honest form of the claim is therefore about the shoulders, not about every quantile.

## What would make the region smaller

Not more search of the same ground. A detection; or information that concentrates the distribution
along the arc rather than removing part of it — the 00:19 interpretations do exactly that, which is why
the before-regions differ by a factor of seven across the options while the search evidence changes
each of them by tens of per cent. **The 00:19 question is worth far more to the width of the answer
than the seabed searches are.**
