# Provisional fuel A/B execution gate

Purpose: exercise the end-to-end fuel plumbing before the Ulich 9M-MRO workbook is available. **These outputs are engineering diagnostics, not scientific MH370 results.**

## Inputs

- Flight-specific zero-fuel weight: 174,369 kg (Malaysian investigation report).
- Fuel anchor: 43,800 kg at 17:06:43 UTC.
- Initial gross mass for the provisional model: 218,169 kg.
- Particle fuel-flow multiplier: N(1.009, 0.018), sampled from the independent fuel RNG stream.
- Fuel-flow surface: provisional B777-200ER long-range-cruise interpolation adapter committed on this branch. Replace with `ulich-9M-MRO-fuel-model-v5.6-public.xlsm` before scientific inference.

## Required A/B

Run the same cases, seeds and particle counts twice:

A. `fuel.enabled = false`
B. `fuel.enabled = true`, provisional table

Fuel OFF is the regression reference and MUST reproduce the September 28 output exactly for a fixed seed. A mismatch is a code defect and invalidates the fuel-on comparison.

## Diagnostics to emit

For every replicate and autopilot stratum:

- final log evidence / normalization constant;
- ESS at every observation epoch and minimum ESS;
- resampling count and epochs;
- weighted 00:11 latitude/longitude moments and quantiles;
- weighted remaining-fuel moments and quantiles (fuel ON);
- weighted predicted exhaustion-time moments and quantiles (fuel ON);
- fraction exhausted by 00:11 (expected to be near zero; flag if not);
- posterior correlation of remaining fuel with latitude, Mach and altitude;
- count/fraction of table evaluations outside the provisional table envelope.

Across matched OFF/ON runs report:

- exact byte/hash equality for the OFF regression artifact;
- change in log evidence;
- change in minimum ESS and resampling count;
- 00:11 posterior displacement (NM) and latitude-quantile shifts;
- distribution of predicted exhaustion time and location;
- sensitivity to flow factor at mean and mean +/- 1.8%.

## Acceptance gate

The provisional plumbing milestone passes only if:

1. Fuel OFF is bit-for-bit identical to the historical fixed-seed baseline.
2. Fuel ON consumes no historical RNG words and remains deterministic for fixed seed.
3. Fuel is advanced on each exact kinematic integration step, not once per SATCOM interval.
4. Fuel state survives particle cloning/resampling and is present in the 00:11 handoff.
5. No 00:19 observation is used to condition the pre-00:11 fuel state.
6. Any provisional-table extrapolation is counted and reported rather than silently accepted.

## Current execution limitation

The present ChatGPT runtime has neither `rustc` nor `cargo`, and this repository has no `.github/workflows` directory on `sept-29-chatgpt-advances`; therefore this session cannot yet execute the Rust A/B. The branch is being prepared so that once a Rust runner is available the remaining work is execution/debugging rather than model design.
