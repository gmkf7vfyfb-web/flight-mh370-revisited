# The impact PDF and the seabed search across every 00:19 interpretation

Searched-areas module, 9 October 2026, at Pete's request. Greyscale 50/90/99 % highest-posterior-
density maps in the project convention, with each 00:19 data option's impact PDF above and the same
posterior reweighted by the seabed-search likelihood below.

**Provenance.** End of flight's `reference-289` evidential sweep, read in place at the paths posted
16:50 UTC: `runs/eof-289-full-s<k>/bto-bfo/seed-<k>/impacts.npy`, k = 1–4, 3.2 M impacts per seed,
**12,799,968 pooled**. Prior track **289.7°**, terminal module `end-of-flight`, from
`eof-289-full-s1/run.json`. Search side: Phase 2 + Bluefin-21, ρ = 0.05, point-target placeholder.
Provisional on end of flight's dive class (b), which Pete has asked be rebuilt against Boeing.

**Method.** The per-option weighting is end of flight's `option_posteriors` — hand-off weight ×
burst likelihood × the log-on lag density for the fuel-exhaustion cause — imported, not reimplemented.
The search log-likelihood is a function of impact position alone, so it is computed **once per seed**
and every option reweights the same column. Density on a 0.02° grid, Gaussian-smoothed at 0.1° (6 NM),
HPD levels from the smoothed density; areas on the authalic sphere.

## What the 00:19 interpretation is worth

Sorted by the width of the impact PDF before any search evidence. Areas in thousand km².

| option × log-on cause | Z | mass on Phase 2 | 50 % before | 90 % before | 50 % after | 90 % after | median before → after |
|---|---|---|---|---|---|---|---|
| both, inflated, fuel-exhaustion | 0.5772 | 0.471 | 32.2 | **134.7** | 23.1 | 142.0 | −37.34 → −37.79 |
| **R1200, Holland, fuel-exhaustion** | **0.3425** | **0.732** | 15.9 | **139.1** | 50.3 | 237.5 | −36.42 → −35.21 |
| R1200, Holland, other | 0.4585 | 0.603 | 23.6 | 145.6 | 36.7 | 206.7 | −36.08 → −35.19 |
| both, inflated, other | 0.4354 | 0.629 | 25.0 | 148.1 | 42.1 | 193.4 | −36.65 → −37.14 |
| **R600, Holland, fuel-exhaustion** | 0.5842 | 0.463 | 50.0 | **187.0** | 35.0 | 231.4 | −37.54 → −37.99 |
| R1200, raw, other | 0.4726 | 0.588 | 26.5 | 188.2 | 46.9 | 248.8 | −36.11 → −35.25 |
| R1200, raw, fuel-exhaustion | 0.4078 | 0.660 | 20.5 | 191.1 | 66.9 | 264.4 | −36.41 → −35.46 |
| R600, inflated, fuel-exhaustion | 0.5579 | 0.492 | 59.5 | 200.4 | 48.3 | 259.1 | −37.48 → −37.80 |
| R600, Holland, other | 0.5173 | 0.538 | 50.3 | 201.7 | 50.7 | 267.2 | −37.20 → −37.44 |
| **R600, raw, fuel-exhaustion** | 0.4753 | 0.584 | 49.9 | **207.2** | 66.0 | 285.3 | −37.28 → −37.29 |
| R1200, inflated, other | 0.4782 | 0.581 | 27.9 | 211.4 | 53.3 | 281.0 | −36.16 → −35.29 |
| R600, raw, other | 0.5249 | 0.529 | 54.0 | 211.6 | 51.4 | 286.7 | −37.25 → −37.30 |
| R1200, inflated, fuel-exhaustion | 0.4248 | 0.641 | 22.9 | 218.5 | 74.3 | 328.0 | −36.52 → −35.59 |
| R600, inflated, other | 0.6428 | 0.398 | 66.1 | 273.2 | 52.1 | 356.2 | −37.58 → −37.87 |
| held out, fuel-exhaustion | 0.5865 | 0.461 | 74.6 | 306.4 | 81.3 | 417.7 | −36.94 → −36.76 |
| **held out, no log-on cause** | **0.7335** | **0.297** | 106.3 | **519.2** | 103.2 | 616.0 | −36.78 → −36.58 |

Four results follow, and three of them were not expected.

**1. Using any 00:19 burst shrinks the impact PDF by a factor of 2.5 to 4.** The held-out 90 % region
is 519,200 km²; every scored option is between 135,000 and 273,000 km². That is the cost of holding
the bursts out, stated as an area.

**2. Holland's start-up offset does narrow it, as Pete expected — and it narrows it more than the raw
treatment of the same burst.** R600: 207,200 km² raw against **187,000 km²** with the offset. R1200:
191,100 km² raw against **139,100 km²**. The ordering is the same under the `other` log-on cause
(211,600 → 201,700 and 188,200 → 145,600). Holland's treatment is the most informative single-burst
interpretation in the set, and R1200 under it gives the tightest impact PDF of any option except the
two-burst inflated case.

**3. The seabed search makes almost every option WIDER, not narrower.** This is the result worth
sitting with. The search removes a contiguous block of probability — the ground that was looked at —
and what is left is the surrounding ring, so the 90 % region grows even as the evidence falls. The
effect is largest exactly where the impact PDF was tightest: R1200 under Holland goes from 139,100 to
**237,500 km²**, a 71 % increase, while its evidence falls to **Z = 0.3425**, the lowest in the set.
A non-detection is not a localisation.

**4. The 00:19 interpretation decides how much of the impact PDF the ATSB actually searched — and it
is the dominant uncertainty in this module's headline.** The mass on Phase 2 coverage runs from
**0.297** (held out) to **0.732** (R1200, Holland, fuel-exhaustion). The search evidence therefore
removes between **27 %** and **66 %** of the probability depending only on which 00:19 reading is
taken. That spread is far larger than anything inside this module: ρ across its whole 0 → 0.5 sweep
moves the held-out evidence by 14 points, the repeat-search treatment by 0.2, the Ocean Infinity 2018
layer by 4.

**For the paper.** The searched-area result cannot be quoted as a single number. It must be reported
across the 00:19 options, as Pete ruled for the end-of-flight sweep, with the held-out case as the
conservative bound and R1200-under-Holland as the strongest. The honest summary sentence is that the
seabed searches remove between a quarter and two thirds of the probability, and that the range is set
by the 00:19 interpretation rather than by anything in the search record.

## Two notes on scope

- **Two of the ten 00:19 likelihood columns are not covered.** `impacts.npy` carries
  `loglik:both/no-offset` and `loglik:both/startup-offset`, but end of flight's `OPTIONS` list stops
  at `both/inflated`, so `option_posteriors` does not yield them. Under Pete's ruling that the full
  range be sampled, the two-burst raw and two-burst Holland readings are missing from this table.
  Raised with the architecture session.
- **The map is clipped at 26°S.** The held-out 99 % band runs off the top; end of flight report 99 %
  latitude bounds reaching 24–26°S. The areas in the table are computed on the plotted domain
  (82–100°E, 26–44°S) and so are lower bounds for the held-out case.

Figures: `impact-map-0019-options.pdf` and `.png`; numbers in the `.json`.

---

*Searched areas, 9 October 2026.*
