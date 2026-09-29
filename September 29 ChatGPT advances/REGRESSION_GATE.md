# Fuel integration regression gate — 29 September 2026

## Required invariant

With fuel disabled, a fixed-seed run must reproduce the September 28 estimator exactly.  The disabled branch must:

1. call the historical `Aircraft::propagate(to, params, env, rng)` exactly once;
2. make no additional RNG draws;
3. add no likelihood term;
4. change no output columns or hand-off selection;
5. serialize to the same `Aircraft` state and leave the RNG at the same next word.

`code/integration_design.rs` encodes this as `fuel_off_is_bit_for_bit_the_historical_propagation`.

## Fuel-on integration requirement

The scientifically valid fuel-on implementation must advance fuel inside the existing 5/10 s kinematic loop in `flight::Aircraft::propagate`, not once per SATCOM/filter interval.  Each fuel increment must use the same step's instantaneous:

- Mach;
- altitude;
- atmospheric temperature;
- gross mass = non-fuel mass + remaining fuel;
- `dt`.

Fuel state is carried per particle and cloned/resampled with that particle.  The pre-00:11 filter predicts total-fuel exhaustion; it does not use the 00:19 log-on as a fuel constraint.  Left/right imbalance and engine flame-out separation belong to the EOF stage.

## Fuel prior / calibration design

- anchor: 43,800 kg at 17:06:43;
- particle flow calibration factor: approximately N(1.009, 0.018), subject to final source-table implementation;
- do not tune the fuel state to 00:17:30 or the 00:19 log-on;
- widen model uncertainty outside the validated performance-table envelope.

## Current execution status

Source/design work is committed on branch `sept-29-chatgpt-advances`.  The connected GitHub interface in this session permits source edits and inspection of existing Actions runs but does not expose a general workflow-dispatch/compile command.  Therefore no Rust test is recorded as passed merely from source inspection.

The real Ulich workbook (`ulich-9M-MRO-fuel-model-v5.6-public.xlsm`) is also not currently accessible in this session.  Synthetic flow tables are suitable for plumbing/regression tests only; they are not suitable for a scientific MH370 fuel-on posterior or A/B PDF.

## Milestone definition

The milestone is complete only when:

- the fuel-off fixed-seed regression passes;
- the real Ulich performance table is ingested and provenance recorded;
- fuel-on propagation runs at the kinematic step;
- 00:11 output carries remaining fuel and predicted exhaustion state;
- fuel-off and fuel-on 00:11 posterior PDFs plus ESS/evidence/stability diagnostics are produced and compared.
