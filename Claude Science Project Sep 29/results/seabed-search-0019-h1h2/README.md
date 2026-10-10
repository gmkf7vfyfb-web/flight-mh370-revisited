# The 00:19 interpretation, held out against Holland's two hypotheses — and a convergence wall

9 October 2026, searched-areas module. `impact-map-0019-h1h2.{pdf,png,json}`, from
`engine/hypotheses/seabed-search/impact_map_options.py` on `runs/eof-289-full`
(4 seeds x 3.2 x 10^6 impacts; prior track 289.7 deg at 18:01:49 UTC, base config `config/davey2016.toml`,
resolved `bfo_bias` = 150 +/- 25 Hz; arcs from `runs/fixture-8/run.json`).

Pete asked for four panels: the 00:19 data held out, the R600 burst at face value, Holland's
Hypothesis 1 as implemented, and his Hypothesis 2. The figure draws those four. **Two of them cannot
be read**, and that is the main result of this note.

## The headline: the two "both-burst" arms are not estimable from this sample

| # | arm | ESS before → after | 90 % area before → after (km²) | median lat | mass on Phase 2 | Z | estimable |
|---|---|---|---|---|---|---|---|
| 1 | Held out: no 00:19 observation at all<br>`none__other` | 12,358,800 → 9,477,498 | 519,198 → 615,996 | 36.78°S → 36.58°S | 0.297 → 0.044 | 0.7335 | yes |
| 1a | R600 BTO arc only (derived here, see below)<br>`r600-bto__other` | 6,471,040 → 4,766,050 | 339,324 → 413,892 | 37.71°S → 38.09°S | 0.325 → 0.050 | 0.7078 | yes |
| 2 | R600 BTO + BFO as observed<br>`r600_no-offset__other` | 197,569 → 117,417 | 211,629 → 286,732 | 37.25°S → 37.30°S | 0.529 → 0.108 | 0.5249 | yes |
| 3 | **Holland H1** start-up transient, fuel-exhaustion log-on<br>`both_startup-offset__fuel-exhaustion` | 36 → 26 | 36,787 → 40,035 | 36.38°S → 37.29°S | 0.748 → 0.300 | 0.3287 | **NO** |
| 4 | **Holland H2** both BFOs raw, other log-on cause<br>`both_no-offset__other` | 82 → 40 | 51,462 → 65,033 | 36.24°S → 36.28°S | 0.805 → 0.313 | 0.2772 | **NO** |
| 5 | Inflated sensitivity: independent 34 Hz<br>`both_inflated__fuel-exhaustion` | 2,042 → 1,308 | 134,662 → 142,032 | 37.34°S → 37.79°S | 0.471 → 0.086 | 0.5772 | yes |
|  | R1200 only, Holland offset (narrowest estimable arm)<br>`r1200_startup-offset__fuel-exhaustion` | 10,065 → 4,675 | 139,146 → 237,525 | 36.42°S → 35.21°S | 0.732 → 0.224 | 0.3425 | yes |

Areas are 90 % highest-posterior-density on a 0.02 deg grid smoothed at 0.1 deg, on the authalic
sphere. ESS is the Kish effective sample size of the importance weights, pooled over the four seeds
(12.8 x 10^6 impacts). `Z` is this module's non-detection evidence: the fraction of the option's
probability that survives the seabed searches, so `1 - Z` is the share the searches remove.

**Rows 3 and 4 rest on 36 and 82 effective impacts out of 12.8 million.** Their areas, medians and
evidence are not results and are not quoted anywhere as results. The 50/90/99 bands in those panels
are the handful of surviving particles, which is why they are drawn as speckle: the speckle is the
diagnostic. The panels are labelled NOT ESTIMABLE on the figure.

## Why the collapse happens, and why it is Holland's own argument

Every panel is an importance-weighted reading of the *same* impacts, which end of flight drew
**without** the 00:19 bursts in hand. Reweighting by a sharp likelihood after the fact is only viable
while the likelihood is broad relative to the proposal. The 00:19 pair is not broad. The 00:19:29
BFO is 182 Hz and the 00:19:37 BFO is -2 Hz, eight seconds apart, and the constant BFO bias is shared
between them, so the pair demands one specific and extreme vertical-speed history. Almost no sampled
trajectory supplies it, and the weights concentrate on a few dozen.

That the pair is nearly impossible to fit *without* a start-up transient is exactly why Holland
proposed one. The arithmetic agrees with him: at matched log-on cause the transient arm retains about
four times the effective sample of the raw arm (`both_startup-offset__other` 322 against
`both_no-offset__other` 82). Four times nothing is still nothing, so this is a direction of travel,
not a Bayes factor.

### Where the bottleneck actually is: the hand-off, not the descent proposal

Measured on this run (100,000 parents per seed, 32 children each):

| arm | effective parents / seed | top-100-parent share | effective impacts / seed |
|---|---|---|---|
| `none__other` | 100,000 | 0.001 | 3,089,700 |
| `r600_no-offset__other` | 18,616 | 0.021 | 49,392 |
| `both_inflated__fuel-exhaustion` | 237 | 0.487 | 511 |
| `both_startup-offset__other` | 78 | 0.924 | 80 |
| `both_no-offset__other` | 20 | 1.000 | 21 |
| `both_startup-offset__fuel-exhaustion` | **8** | 1.000 | 9 |

Two readings, and they point away from the terminal stage:

* **Effective impacts ≈ effective parents in the three unconverged arms** (9 against 8, 21 against 20,
  80 against 78 — ratios 1.03 to 1.13, top-100-parent share 0.92 to 1.00). There, essentially one of
  the 32 children carries the weight, so **more children buy nothing** and neither would a better
  within-parent proposal. **`both/inflated` is the exception** and must not be lumped in with them:
  511 effective impacts on 237 effective parents is a ratio of 2.16 with a top-100 share of 0.487, so
  its within-parent weights are not collapsed and a terminal-stage proposal could still gain there —
  the ceiling if they were evened out is 32 × 237 ≈ 7,600. That is the arm Pete asked about, it is
  above the floor already, and its remedy is a different one.
* **These numbers sit on end of flight's own N = 16 split-half limit** of 11-68 effective parents per
  seed (`results/eof-ess-limit-oct09/`, addendum 2), reached here with five times their parents and
  twice their children. The two runs use different prior tracks, so this is corroboration rather than a
  controlled comparison — but it is consistent with their verdict that `both` is concentration-limited
  and that no terminal-stage proposal can lift it.

The binding constraint is therefore the **00:11 hand-off**: of 100,000 posterior states from the cruise
filter, about ten can produce the 00:19 pair at all. The cruise filter excludes both 00:19 epochs
(`exclude_epochs`), so nothing in it is aimed at that region of state space.

Two consequences follow, and neither is this module's to fix:

* **Scoring both 00:19 bursts needs the hand-off to be aimed at them** — a look-ahead (auxiliary)
  resampling of the 00:11 parents against a cheap approximation of the 00:19 likelihood, with the
  exact `p/q` correction, so no bias is introduced and the cruise filter's physics is untouched. Its
  ceiling is the number of feasible states in the cruise filter's full particle set, not in the 100,000
  that are handed off. Raised with end of flight and architecture.
* **Until then the comparison Pete asked for cannot be completed.** Rows 1, 1a, 2 and 5 are sound;
  rows 3 and 4 are blocked.

## What the estimable arms do say

* **The 00:19:29 BTO arc on its own is weak evidence about position.** Row 1a narrows the 90 % region
  from 519,200 to 339,300 km2 — a factor of 1.5, against 2.5 for the BTO *and* BFO together — and
  moves the median 0.93 deg south. It is an arc constraint, and the trajectories reaching 00:19 were
  already close to satisfying it.
* **The searches still remove the most probability from the arms that use the 00:19 BFOs.** Among the
  estimable arms `1 - Z` runs 0.27 (held out), 0.29 (BTO arc only), 0.42 (both, inflated), 0.48 (R600
  as observed) and 0.66 (R1200 with Holland's offset); the share of impact mass sitting on Phase 2
  coverage runs 0.297 to 0.732 in the same order.
* **The search evidence widens almost every arm**, as before: it removes a contiguous block from the
  middle of the corridor and leaves the ring. Row 2 goes 211,600 -> 286,700 km2.

## Two derivations and one disclosure

* **`r600-bto` is derived in this module, not run.** `config/integrated.toml` declares the option but
  the sweep produced no column for it. The engine's `loglik:r600/no-offset` is exactly
  `-0.5 (bto_residual/63 us)^2 - 0.5 (bfo_innovation/7.3755 Hz)^2 + const` (least squares on 4 x 10^5
  impacts of seed 1: max residual 2.5 x 10^-10, R^2 = 1), so the BTO term separates cleanly and
  `p(r600-bto) = p(none) x exp(-0.5 (bto_residual/63)^2)`, renormalised. If the option is ever run,
  this row should be replaced by the engine's own column.
* **End of flight's `OPTIONS` list names eight of the ten `loglik:` columns the run carries.** This
  script sets the list from the run's own columns before calling their `option_posteriors`, so the
  weighting stays their single definition and only the column list widens. Their file is unchanged.
* **A caveat on the figure delivered earlier today.** `results/seabed-search-0019-options/` quotes
  `both/inflated` at ESS 2,042 before the search and 1,308 after - above the floor of 1,000 used here,
  but thin. Its numbers stand; they are the weakest in that table and should be read as such. Every
  other arm in that figure is above 4,000.

## What is assumed

The seabed-search layer is the ATSB Phase 2 union (120,486.5 km2) plus Bluefin-21/Artemis
(771.4 km2), rasterised at 0.01 deg, with detection probability 0.945 (Phase 2) and 0.900
(Bluefin-21) conditional on a detectable target, undetectable fraction rho = 0.05, a **point target**
(the size response g(W) is not implemented), and shared miss dependence where campaigns overlap.
Ocean Infinity 2018 and 2025-26 are excluded here. Full footnotes are on the figure itself.
