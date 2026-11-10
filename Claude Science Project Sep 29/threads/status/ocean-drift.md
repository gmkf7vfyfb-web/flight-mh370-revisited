# Ocean drift: status (updated 10 November 2026, early morning)

Read after `threads/master-prompts/ocean-drift.md`. Replace entries when they change; history is in git and in `coordination/OCEAN_DRIFT.md`.
Details: `results/drift/drift-level-prior-correction-2026-11-09/README.md` (sections 1 to 11) and `windage-wide-run-and-sbc-smoke-2026-11-09.md` (same folder).

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

## Run in progress
- **Wide-windage run** (job 27b6e292, started 9 Nov 23:44 UTC): stage 1 finished 10 Nov 03:26 UTC (12 legs, all exit 0); stage 2 ends about 05:00 UTC. Exterior class only, `c_wind` log-normal median 1.2 %, σ(log) 0.5, truncated 0.3 to 5 %; binary `bin-wide` (module option `restrict_to_classes`, default off, byte-identical on the smoke set; module commit 48120ea6). Output `~/mh370/drift/coef/runs/wide-*`.
- **Rescoring** of the wide legs (job ce85be22, starts when the wide run ends): module rescorer, R3 configuration; then hybrid coefficients (`offline/build_hybrid.py`: flaperon and interior classes from the production rescoring), smoothing and tension; report Mossel Bay with and without the wide class.
- **Overnight chain** (job 6496b915, starts when the wide run ends, about 13 h, approved by Pete 10 Nov; replaces 5159a954): run 0 higher-windage sensitivity (exterior class median 2.4 %, σ(log) 0.35; 84 + 42 points; 18 legs; Pete asked for a higher range as a minimum); run 1 ocean-error length scale 50 and 200 km (12 legs); run 2 particle-noise check, master seed 23 (4 legs); run 3 extra ocean samples, seeds 233–248, three classes (6 legs). Stops if free disk space is below 3 GB or two legs fail in a row; deletes nothing.
- **Stokes drift:** implicit treatment kept (judgement, README section 12): WAVERYS gives 1.23 to 1.30 % of the 10 m wind, against 1.2 % assumed.

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

Highest point of the curve: 29.5° S (0.109 per degree) with the item; 34.8° S (0.104) without it (5.3° south; median 2.9°, mean 2.1°). Tension: quote ln S, p and σ only (no adjective; see the Mossel Bay section).

## Mossel Bay item (README section 9)
- Not ruled by Pete: the date, the identity weights and the tension wording. Earlier "Pete's ruling" labels were wrong. Pete's position: follow the evidence.
- ATSB Update 2 gives the find date as 22 Mar 2016. 23 Dec 2015 is the date of a photograph supplied to the ATSB on 17 May 2016 (added by addendum 23 May 2016); the report does not say how the photograph was matched to the part or dated.
- Date alternatives (drift alone, two ocean models): 23 Dec 2015 median 30.0° S, p 0.109; 22 Mar 2016 median 30.8° S, p 0.151; item excluded 32.9° S, p 0.407. Identity weights all 1 or 1 / 0.9 / 0.7: median 30.0 or 30.1° S (no effect).
- The item alone prefers 30° S to 36° S by 6.7 : 1 (December) or 3.3 : 1 (March). The full drift likelihood prefers 30° S to 36° S by 2.4 : 1 (headline), 1.6 : 1 (March), 0.85 : 1 (item excluded): the drift likelihood is broad, so the highest point is unstable.
- Tension: quote ln S, d, p and the dependence on the item; no adjective. Simulation-based calibration of p: smoke test only (Gaussian toy worlds: nominal p 0.1091 corresponds to a false-alarm rate of 0.10 to 0.18; code-path check, not evidence); not yet done with the real generator.
- Logic of the date (README 10.1): ATSB and the Malaysian team both give 22 Mar 2016 as the date found; 23 Dec 2015 is a photograph that appears to show the same part. If the photograph is accepted, arrival is on or before 23 Dec 2015 and the March date has no role; the March case is the hypothesis that the photograph is not this item. Photograph accepted: median 30.0° S (delay 60 d), 30.8° S (barnacle mark).
- Arrival timing from all 164.8 million stored beachings (README 10.2, validated against 35,851 module coefficients to 2.2e-8): the model predicts late arrival at Mossel Bay from every source latitude. Core-weighted, the probability that the predicted find date is as early as the cowling's is 0.04 (equal detection levels) or 0.02 (provisional ramp). The Paindane flap fairing is also early (0.07 / 0.03). Early arrivals come from the upper part of the sampled windage range; eddy diffusivity does not explain them.
- The production run has no refloat (no beaching has a departure time).

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
3. Mossel Bay model checks (README 9.5, 10.4, 11): arrival-time distribution done (10.2); wide-windage class run done by about 05:00 UTC 10 Nov (README 11, 12). Open: its rescoring; higher-windage scenario (queued first overnight); ocean-error length scale 50 and 200 km (queued); particle-noise check (queued); extra ocean samples (queued); effectiveness of the importance splitting in the tail; Agulhas leakage; identity of the photographed object with Part No. 3 (original photograph and metadata); two-episode treatment (photograph and March find as two stays of one item, refloat on); simulation-based calibration of the p-value (smoke test done, README 11; real-generator test not built). Date: Pete follows the evidence and does not rule.
4. Ocean-sample error beyond the bootstrap; more ocean samples in the south; the headline has not been subset-tested.
5. Pléiades and surface-search coverage test: needs the AMSA daily search polygons (ATSB 2017, Tables 13 and 14).
6. Combined density for the other drift cases; second independent review of the new core input and the smoothing; Australian tiers as ramp offsets.
7. Nautilus Bay and Mpame identity basis; Sandravinany and later finds (needs ocean and wind data after 31 Jan 2017).
8. Evidence-ledger and suspiciousness figures: recompute with these surfaces. Biofouling temperature term: needs per-particle temperature.
9. Copy GlobCurrent to a third drive before 24 Nov 2026.
