# Ocean drift: status (updated 9 November 2026, evening)

Read after `threads/master-prompts/ocean-drift.md`. Replace entries when they change; history is in git and in `coordination/OCEAN_DRIFT.md`.
Details: `results/drift/drift-level-prior-correction-2026-11-09/README.md` (sections 1 to 8b).

## Current base
- **Core (satellite and flight data): the ruled input** is the final 7 November end-of-flight Davey model with fuel, log-on event only (treatment D0, no 00:19 measurement):
  `end-of-flight/final-2026-11-07/results/eof-final-handoff-df.npz`. Median 36.4° S, mean 35.95° S, 8.1 % north of 33° S.
  The evidence-combined Run J accumulator (99.87 % waypoint family) was used by mistake in all earlier drift work; it is now a sensitivity only (README section 6).
- Drift code: `hypothesis/debris-drift` at 6f75971. Run: 84 arc-latitude release points, two ocean models, 16 ocean samples (32 south of 33.25° S), finds to 30 Jan 2017, 6250 particles per class.
  Transport and coefficients: `results/drift/drift-extended-window-2026-11-08/`. Scoring, smoothing, tables and figures: `results/drift/drift-level-prior-correction-2026-11-09/`.
- Detection prior in time (provisional, not pre-registered): period medians 0.1 / 0.5 / 1 / 1, log-normal sigma 1. The 8 November offline scoring used constant levels (defect, withdrawn).
  The offline scorer now equals the module at all 84 points to 5e-7.
- Level marginalisation: 16,384 draws per seed, 16 seeds (262,144 draws). The module default of 256 draws is too few. Saved two-seed check (`level-draw-convergence.csv`): shifts of +0.69° and +0.91° at 256 draws.
  The six-seed range quoted on 8 November has no saved table and is withdrawn.

## Smoothed drift alone (final method; headline model, Australia off, twelve identity-weighted items)
Per-environment log likelihood from 262,144 draws, Matérn 3/2 Gaussian process (length scale at its 15° bound; fixed 2, 4 and 8° give the same answer), joint bootstrap over ocean samples (400), 0.1° latitude bins, arc prior from a cubic fit.

| Case | Median (° S, 5–95 %) | Mean | North of 33° S | Tension σ (5–95 %) |
|---|---|---|---|---|
| Two ocean models (headline) | 30.0 (29.6–30.4) | 30.3 | 74 % | 1.6 (1.5–1.7) |
| GlobCurrent only | 30.0 | 30.4 | 73 % | 1.6 |
| GLORYS12 only | 29.4 | 29.2 | 89 % | 1.9 |
| No finds on Australian coasts (0.25) | 29.5 (29.1–29.8) | 29.7 | 80 % | 1.8 |
| Without Mossel Bay | 32.9 (32.1–33.6) | 32.4 | 51 % | 0.8 |
| No finds on Australian coasts (0.25), without Mossel Bay | 31.4 (30.8–32.0) | 31.3 | 63 % | 1.4 |

Highest point of the curve: 29.5° S (0.109 per degree) with the item; 34.8° S (0.104) without it (5.3° south; median 2.9°, mean 2.1°). Description: moderate tension, not significant at 5 %.

## Combined with the ruled core (two ocean models, headline)
- One-dimensional (core × smoothed likelihood, 0.1° bins): median 35.7° S, mean 34.79° S, 18 % north of 33° S. Without Mossel Bay: median 36.1, mean 35.71, 7.5 %.
- Per-point reweighting of the two-dimensional core samples (eight draw seeds): mean shift +1.43° (+1.17° to +1.68°), 23 % north of 33° S. Waypoint family final: +1.01°; evidence-combined: +0.91° (sensitivities).

## Withdrawn or corrected
- All 8 November rescored numbers, and the 9 November numbers on the evidence-combined core (+0.82° and others).
- "Prior volume" attribution of the core peak (an Occam factor, not a prior-volume effect), and the October agreement. "Mild" tension and "agrees with the literature" are not supported (README section 5).
- Reviewer warnings corrected 9 November: the debris audit lists five South African items (the fifth, the northern KwaZulu panel, is unidentified and excluded); Pete's figure labels the core modes 37.2° S and 36.1° S (not 37.4° S);
  the interrupted GlobCurrent run lasted about 32 minutes (not 20).

## Open items
1. Detection-level prior in time (ramp, provisional): Pete's decision; first-order lever (about 1° on the combined mean). Headline Australian ratio: Pete's decision.
2. Figure choice for the paper: reduced chart C with chart D beside it (recommended, not ruled).
3. Mossel Bay: explanation (early date needs fast northern paths; late finds carry less latitude information) not yet checked against arrival-time distributions (needs the 8 GB arrivals file on deskstar).
4. Ocean-sample error beyond the bootstrap; more ocean samples in the south; the headline has not been subset-tested.
5. Pléiades and surface-search coverage test: needs the AMSA daily search polygons (ATSB 2017, Tables 13 and 14).
6. Combined density for the other drift cases; second independent review of the new core input and the smoothing; Australian tiers as ramp offsets.
7. Nautilus Bay and Mpame identity basis; wide-windage class; Sandravinany and later finds (needs ocean and wind data after 31 Jan 2017).
8. Evidence-ledger and suspiciousness figures: recompute with these surfaces. Biofouling temperature term: needs per-particle temperature.
9. Copy GlobCurrent to a third drive before 24 Nov 2026.
