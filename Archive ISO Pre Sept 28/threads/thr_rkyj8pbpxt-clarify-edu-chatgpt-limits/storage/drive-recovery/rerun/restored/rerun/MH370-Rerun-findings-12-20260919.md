# MH370 Rerun — checkpoint 12

Created 2026-09-19 13:39 UTC.

## Outcome

The first continuous-state backward/endpoint-proposal recovery suite is complete. It uses an exactly solvable position/speed process at the real SATCOM contact offsets, including the missing-BTO pattern at 18:39 and 23:15. Fuel-exhaustion time is proposed under both the user's 00:15–00:17 conditional hypothesis and the historical 00:15–00:19 sensitivity window using checkpoint 11's exact time Jacobian.

Across 64 generated flights and equal budgets of 2,048 proposals per method:

| Method | Median ESS | Median max weight | Position CDF error | Time CDF error | Median absolute log-evidence error | Position/time 90% coverage |
|---|---:|---:|---:|---:|---:|---:|
| Forward bootstrap | 7.22 | 26.0% | 0.312 | 0.293 | 0.221 | 68.8% / 76.6% |
| Uniform endpoint, exact P/Q | 320 | 0.623% | 0.0446 | 0.0436 | 0.0295 | 89.1% / 89.1% |
| Gaussian endpoint guide, exact P/Q | 1,672 | 0.0824% | 0.0187 | 0.0194 | 0.00792 | 89.1% / 89.1% |

The exact reference coverage was 90.6% for terminal position and 89.1% for exhaustion time. All methods retained finite support for every sample.

## What the uniform endpoint means

The endpoint is not treated as a measured location. The uniform rectangle is only `q(endpoint|data,T)`, mixed with 5% of the unconditional prior predictive to preserve global support. Its exact weight is

`p(data) × p(endpoint|data,T) / q(endpoint|data,T) × p_anchor(F(T)) |dF/dT| / q_T(T)`.

Observations appear once: through the observation evidence and conditional endpoint density. There is no second BTO/BFO factor and no endpoint likelihood. The Gaussian guide changes only the proposal, not the target.

## Interpretation

This continuous control supports the user's backward/two-ended idea in principle. Even a uniformly proposed endpoint works well when its proposal density is acknowledged and corrected; an observation-informed, support-preserving guide is substantially more efficient. The forward sampler's poor ESS and undercoverage reproduce the qualitative failure mode seen in the aircraft bottleneck, while the corrected backward proposals recover the exact reference.

The improvement was stable in both time windows. Median uniform-endpoint ESS was 320 in each; median Gaussian-guide ESS was 1,670 for 00:15–00:17 and 1,673 for 00:15–00:19.

## Limits and failed attempt

This is not a full-aircraft bridge. Its observations are a linear-Gaussian analogue of along-track position and speed, not physical BTO/BFO geometry, and it does not use ERA5, IGRF, Boeing performance constraints, or the recovered manoeuvre model. It validates the measure, support and recovery diagnostics only.

The first result serialization failed after computation because NumPy booleans are not directly JSON serializable. That failure is retained in `failed-attempt.json`; explicit conversion was added and the deterministic suite was rerun from the beginning without changing model or metric definitions.

Five new unit controls pass. The raw 64-trial record, code, seeds, environment, PDF/SVG figure and hashes are preserved.

## Next physical gate

1. Restore Rust 1.98.0 and compile the isolated retained-parent implementation.
2. Prove ordinary versus K=1 equality, then run K=4 with the full parent bank.
3. Port the support-preserving endpoint mixture and exact P/Q identity into a separate aircraft bridge target.
4. Validate physical synthetic recovery in both terminal-time windows before interpreting MH370 runs.

No MH370 probability or location is claimed, and hydroacoustics remains excluded.
