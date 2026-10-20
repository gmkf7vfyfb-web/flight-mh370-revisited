# MH370 Rerun — checkpoint 13

Created 2026-09-19 14:44 UTC, after publishing the checkpoint-12 milestone handoff.

## Outcome

The validated continuous endpoint/time measure has now been translated into an isolated full-aircraft **boundary module** in the recovered Rust source. This is the first aircraft-source implementation of the bridge measure, but it is not yet a physical bridge sampler or executed aircraft result.

The module calculates

`W_parent × p(endpoint)/q(endpoint) × p(path)/q(path) × p_anchor(F(T))|dF/dT|/q_T(T) × product(L_satcom)`

and makes the failure-sensitive parts explicit:

- `q(endpoint)` must include a strictly positive prior-predictive mixture, so an observation-informed guide cannot remove target support;
- the endpoint is a proposal, not an observed crash location;
- anchor fuel at 18:28:05.9 remains the canonical latent coordinate while the path-dependent mass map connects it to 18:22:12;
- the bridge must replace the legacy fuel-window likelihood rather than multiply it a second time;
- a duplicate BTO or BFO factor for the same contact fails closed;
- 00:19 BTO/BFO fails closed for the through-00:11 target;
- both 00:15–00:17 and 00:15–00:19 time hypotheses use exact radar-clock offsets.

## Validation

Seven new independent numerical/source-contract tests pass. Five embedded Rust controls were also written for the exact density identity, duplicate/future observation rejection, double-fuel-conditioning rejection, radar/anchor round trip and time windows, but cannot run without the Rust compiler.

Regression controls also pass:

- 5 checkpoint-12 continuous bridge controls;
- 8 checkpoint-11 radar/fuel boundary controls;
- 24 retained-parent and joint-block controls.

Total executed: 44 passed, 0 failed. One incorrect `unittest` path invocation failed before test collection and is retained in `failed-test-command.json`; rerunning from the correct working directories passed without changing code or data.

## Limitations

Rust 1.98.0 remains unavailable, so the module is uncompiled and its embedded tests are unexecuted. It is not yet connected to an aircraft backward integrator, nuisance-state proposal or endpoint geometry builder. No physical bridge, MH370 posterior probability or location result is claimed. Hydroacoustics remains excluded.

## Next gate

Restore Rust 1.98.0; compile all embedded tests; connect this boundary module to an isolated aircraft two-ended proposal while retaining the recovered BTO/BFO calibration and nuisance states; then run synthetic recovery under both time windows before interpreting MH370 data.
