# Fuel feasibility of Davey's posterior — direct check (core order 2026-10-15b step 3)

15 October 2026, deskstar job d7ed2f2b (runs), re-analysed in job e49cf3be. Binary `bin-9681a10`
(sha256 17052ae0…df71). Script `engine/scripts/fuel_feasibility.py` (sha256 eadfd1eb…796e). The three
JSON files in this folder are its full output.

## Question
Item 5 (`threads/work-orders/item5-fuel-evidence-2026-10-15.md`) read the 2.16 nat fuel cost as
"only about one in eight (e^−2.16 = 0.115) of the trajectories Davey's infinite-fuel model accepts could
have flown them on the fuel aboard". That contradicts Davey's Assumption 4 (p. 60). The reading is
exact only if the fuel model acts as a hard indicator: Z_constrained / Z_unconstrained = P(feasible | data).
This check measures P(feasible | data) directly.

## Runs
- **Model.** `davey2016-inmarsat.toml`: Davey's dynamics, priors and observations, with Inmarsat's satellite
  states and the 289.7° track. Fuel is TRACKED, NOT CONSTRAINING: no require_power_until, no
  exhaustion-timing term, no hard reject, no ceiling, no single-engine dynamics, and the profile is drawn
  from Davey's prior.
- **Variants.**
  - **ff-tables**: the fuel model behind the 0.12 reading. Boeing-derived tables, κ ~ N(1.0085, 0.0178),
    36,609 kg.
  - **ff-internal**: the production burn model. internal-v1 with temperature, κ ~ N(1.0004, 0.0196),
    initial fuel 43,800 − 7,228 κ, two tanks, INOP flow 0.5.
  - Overlays: `engine/config/sensitivity/fuel-feasibility/`.
- **Scale.** 4 seeds × 1.75M particles (1/4 of Davey's per-seed count), at 88 threads. Each run took about
  4 min.
- **Check.** Both variants give the SAME ln Z (−97.07609488020748), the same mode probabilities and the same
  mode medians. The fuel bookkeeping changes nothing in the filter, as intended.
- **Pooling.** Row weight × mode_probability / (row-weight sum of the mode), with the seeds equally weighted.
  Times are `fuel_exhausted_s_after_0000` (F12). Arc 6 = 00:10:59, arc 7 = 00:19:29.
  - For ff-internal the times are for the SECOND engine. The first engine is reported separately.

## Results (pooled, 4 seeds; ± = seed sd / √4)

| quantity | ff-tables | ff-internal | run I repro-radar (constrained, 8 seeds) |
|---|---|---|---|
| **share dry before 00:10:59** | **0.858 ± 0.007** | **0.906 ± 0.007** | 0 (by construction) |
| **share feasible (power at 00:10:59)** | **0.142** | **0.094** | 1 |
| implied ln P(feasible) | −1.95 nat | −2.37 nat | — |
| share dry between arcs 6 and 7 | 0.066 | 0.049 | 0.554 (seed sd 0.057) |
| share dry 00:19:29–00:19:37 | 0.0005 | 0.0004 | 0.0072 |
| share with fuel left at 00:19:37 | 0.076 | 0.044 | 0.438 |
| FE 5% / 50% / 95% (UTC) | 23:07:12 / 23:44:21 / after 00:19:37 | 22:53:18 / 23:33:41 / 00:18:09 | 00:11:38 / 00:18:33 / after 00:19:37 |
| first engine dry before 00:10:59 | — | 0.952 | 0.482 |
| any time above the weight-dependent ceiling | 0.221 | 0.165 | 0 (ceiling imposed) |
| any time with table extrapolation | 0.849 | 0.853 | 0.952 |

## Reading
1. **The one-in-eight reading is confirmed in direction and roughly in size.**
   - On the fuel model it came from, 14.2% of Davey's posterior is feasible: ln P = −1.95, against the
     −2.16 inferred from the evidence difference.
   - The 0.2 nat gap is within what the different configurations allow: item 5's runs had the
     vertical-rate BFO term, the older prior track and tempering.
   - On the production burn model the feasible share is 9.4% (about 1 in 11).
2. **Davey's Assumption 4 ("the majority are feasible") does not hold under a profile-dependent burn.**
   - Even the most favourable model leaves 86% of the posterior dry before the 00:11 transmission. The
     median dry time is 23:34–23:44, about 30 min short.
   - The ceiling explanation proposed in item 5 is at most a minor part: only 17–22% of the mass ever flies
     above the weight-dependent ceiling.
   - The bulk must come from the Mach and altitude profiles that Davey's prior admits, which burn faster
     than an endurance profile. Not decomposed here.
3. **Run I's 51% between arcs 6 and 7 is a product of the constraint, not of Davey's posterior.**
   - Unconstrained, only 5–7% of the mass runs dry between the arcs.
   - Recomputed on run I's repro stratum with this script, the figure is 55.4%. The order's 51.01% and the
     FE median of 00:19:12 are all-strata figures whose source was not found in the committed record; the
     repro stratum alone gives a median of 00:18:33.

## Predictions recorded before the run (CORE_STAGES, 15 Oct about 19:35Z)
- **Order's prediction "share dry before 00:11 is 0.10–0.20": NOT MET (0.86–0.91).** The order inverted the
  quantity, as flagged before the run.
- **Core, ff-tables, dry 0.80–0.92: MET (0.858).**
- **Core, ff-internal, dry 0.70–0.90: MISSED, just above (0.906).** My reasoning that κ about 0.8% lower would
  give about 3 min more endurance was wrong in sign overall: with the temperature term and internal-v1 the
  median FE is 11 min EARLIER.
- **Core, above-ceiling share 0.4–0.5: MISSED (0.17–0.22).** The audit's 44–47% was on reference-289
  weight, a different posterior.
- **Core, FE 5% before 00:00 and 50% before 00:10:59: MET.** Arcs 6–7 share far below run I's: MET.

## Caveats
- Reduced scale (4 × 1.75M). Seed sd of the dry share is 0.014. This is enough for the headline share, not
  for tails.
- 85% of the mass spends some time where the tables are extrapolated (`fuel_extrapolated_s > 0`; run I
  repro: 95%). The durations were not summarised, so how much of the burn rests on extrapolation is NOT
  ASSESSED here.
- The paper may state the direct measurement. It should name the fuel model and say that the posterior is
  Davey's own, with fuel as bookkeeping only.
