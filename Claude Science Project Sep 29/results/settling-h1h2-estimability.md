# Why Holland H1 and H2 are not estimable, and what fixes it

Ocean settling, 10 Oct 2026, in reply to Pete ("why is Holland not estimable ... what are you going to do to fix it?").

## Short answer

Settling cannot make H1 or H2 estimable. It is a transform: every effective impact becomes one seabed field. If only
36-124 impacts carry H1 or H2 weight, settling can only show 36-124 fields, however many times it resamples them.
The shortage lies upstream, in end of flight's **descent proposal**. Its 00:19 descents almost never perform the
push-over that both 00:19 bursts require together. This is a sampling-efficiency problem, not evidence against H1 or H2.
It is fixable with a proposal targeted on the burst states and corrected exactly. Neither likelihood changes.

## Diagnosis (end of flight next-run on core (b), seed 1 of each stratum; read in place, 106 columns)

| stratum | parents | prior share with Δv(00:19:29→00:19:37) < −8,000 ft/min | parents with any such child | best ln L: R600 / R1200 / H2 / H1 | top-200 Δv under H2 (ft/min) | top-200 Δv under H1 (ft/min) |
|---|---|---|---|---|---|---|
| next-free | 99,999 | 0.78 % | 11,635 | -8.0 / -2.9 / -11.1 / -13.0 | -11,834 / -9,438 / -7,844 | -11,626 / -9,755 / -8,496 |
| next-repro-radar | 100,000 | 0.78 % | 11,616 | -8.0 / -2.9 / -11.6 / -13.0 | -12,263 / -9,662 / -7,732 | -11,664 / -9,810 / -8,350 |
| next-descent-climb | 100,000 | 0.76 % | 12,668 | -8.0 / -2.9 / -11.0 / -13.0 | -11,419 / -9,280 / -8,457 | -11,088 / -9,849 / -9,211 |
| next-routes | 100,001 | 0.80 % | 12,999 | -8.0 / -2.9 / -11.2 / -13.0 | -12,276 / -9,220 / -7,727 | -11,701 / -9,605 / -8,505 |

Top-200 Δv columns are p5 / p50 / p95.

On `next-free` seed 1 (and on reference-289 seed 1) about 300 of 100,000 hand-off parents carry any H1 or H2 mass.
Parent ESS is 8-18 per seed against 5,700-7,700 for R600 as observed.

What this shows:
1. **Each burst alone is easy to fit.** The best R1200 impact scores ln L −2.9, and the best R600 −8.0. Many parents fit
   either one.
2. **Both together need a push-over.** The best-fitting H2 descents change vertical speed by about −9,400 ft/min in the 8.0 s
   between 00:19:29.416 and 00:19:37.443 (about −5,000 to −14,300 ft/min). That is a sustained 0.6 g downward acceleration;
   under H1 the figure is about −9,800 ft/min.
3. **The proposal rarely produces it.** Only about 0.8 % of the descent proposal's weight has Δv below −8,000 ft/min. Within that,
   only a few hundred children also have the right absolute vertical speed at 00:19:29. Each parent gets 32 descents (8 children x
   4 descents), so about 300 parents hold all of the H1 and H2 mass.
4. **Good two-burst fits do exist; they are just rare.** The best H2 impact scores ln L −11.1. That is close to the sum of the
   two single-burst bests (−8.0 + −2.9 = −10.9), so the proposal does reach the region the bursts demand. It reaches it in a few
   hundred children out of 3.2 million, which is too few to estimate a posterior from.

This agrees with end of flight's own count: H2 has 52-89 effective parents over 4 seeds; H1 has 227-265 parents but 34-125
effective impacts, with split-half 0.34-0.48.

## The fix (end of flight's descent sampler and core's hand-off hook; not settling code)

1. **A burst-state-targeted descent proposal, per two-burst option.**
   - For each parent, draw the 00:19:29 and 00:19:37 vertical states from a proposal centred on what the option's own BFO
     model implies at those times. For H1 that includes Holland's start-up offset as a random term.
   - Build the descent through those states.
   - Weight each child by prior / proposal, exactly, in a defensive mixture with the current proposal (for example ε = 0.2),
     so that every other option stays unbiased.
   - This is a proposal change only. It narrows nothing in the model, so Holland's descent bounds are not imposed as a
     constraint (Pete's rule).
   - Expected effect: the share of proposals in the push-over region rises from under 1 % to most of the targeted component.
     That should take pooled ESS from 36-124 to thousands.
2. **Cheap interim step:** more descents per parent for the about 12,000 parents that already reach Δv < −8,000 ft/min, for
   example 256 rather than 32. This helps by a factor of a few, not enough on its own.
3. **For H1 also:** the per-hypothesis hand-off look-ahead (core request 10, hook (5)): g = the fuel-exhaustion lag density at
   each parent's predicted flame-out. Only 9-14 % of hand-off weight flames out in H1's window (end of flight, 9 Oct 20:55).
4. **Acceptance:** pooled impact ESS ≥ 1,000 for H1 and H2, split-half above the floor, and evidence unchanged within MC error
   against the current run on the options it already resolves.

## What settling does

- I have posted this request to END_OF_FLIGHT, with CORE_STAGES for hook (5) and architecture. I have also asked ocean transport
  for a wider GLORYS profile (below).
- When per-hypothesis impacts land, settling re-runs unchanged. `wreckage_field_rerun.sh` produces the four-option map, plain and
  `+alive`, in under 10 min at 2 threads. It drops the NOT ESTIMABLE stamp only when pooled impact ESS is at least 1,000.
- I should have posted this diagnosis and request when the stamp first appeared (9 Oct), not only noted the shortfall as blocked.

## Review of the architecture stand-in's settling re-run (`results/settling-next-run-b-standin.md`)

- Accepted. It used settling's own recipe unchanged; the bit-identity check on 500 impacts passes. The mixture ESS formula
  1 / Σ_f P_f² Σ_s (1/16)/ESS_fs is the right Kish combination for fixed P(family).
- Results stand: settling adds 0.13 % (held out) and 0.34 % (R600 as observed) to the mixture's 90 % area. The impact PDF's
  shrinkage comes from core (b) and is labelled unconverged.
- **Correction to my own notes:** "under 0.02 % not computed" held for reference-289. On next-run single strata it reaches
  0.035-0.048 % in estimable panels (0.30 % in routes-H1, not estimable).
  - Cause: the GLORYS12V1 profile column ends at 18° S (it covers 80-112° E, 45-18° S). The surface current and ERA5 extend to 0° S.
  - I cannot widen settling's window without a wider column. I have asked ocean transport for one, at 75-115° E, 45-10° S. Until then the
    excluded share is reported per panel.
