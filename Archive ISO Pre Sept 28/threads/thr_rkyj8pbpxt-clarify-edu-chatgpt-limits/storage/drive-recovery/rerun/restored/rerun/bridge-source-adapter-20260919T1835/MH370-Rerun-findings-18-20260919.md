# MH370 Rerun checkpoint 18: powered bridge-source adapter

Created 2026-09-19T18:40:20Z. This checkpoint advances the core estimator only. Hydroacoustics is excluded.

## Result

A compiled Rust adapter now joins the conditional final-radar boundary at 18:22:12 UTC to the broad model's canonical fuel latent at 18:28:05.9 UTC. It keeps the historical 18:01:49 clock origin, the radar boundary, and the fuel anchor as three distinct roles.

The adapter is a validated source boundary, not yet a full-aircraft bridge sampler. It does not produce or calibrate a crash-location posterior.

## Implemented invariants

- The configured 6.578 N, 96.340 E boundary is accepted only with checkpoint 17's explicit `conditional_airway_interpolation` role. It cannot be relabelled an authenticated raw-radar measurement.
- The broad historical clock maps 18:22:12 to 1,223.0 seconds and 18:28:05.9 to 1,576.9 seconds. Their exact separation is 353.9 seconds.
- The sampled fuel coordinate remains total onboard fuel at 18:28:05.9. Given the powered path's affine mass map, the adapter deterministically inverts that coordinate to aggregate fuel at radar.
- For `M_anchor = r M_radar + c`, the induced radar-fuel density is `r / (F_max-F_min)`. Because the sampler stays in the anchor-fuel coordinate, the extra coordinate correction is exactly zero. Multiplying by the induced density again would apply the same fuel prior twice.
- The 00:15–00:17 and 00:15–00:19 ranges are represented as conditional proposal supports, not observations. In the historical clock they are respectively [22,391, 22,511] seconds and [22,391, 22,631] seconds.
- The adapter rejects a 4 Hz BFO deviation and requires the historical broad branch's 7 Hz measurement calibration.
- The no-jettison baseline fails closed if disabled.
- Mach and altitude remain broad uncertain coordinates; the adapter changes only the source time/position/direction boundary.

## Validation

- Exact adapter tests: 5 passed.
- Full affected Rust suites: 89 end-of-flight plus 68 estimator tests passed; 157 total, zero failures.
- Independent Python arithmetic tests: 5 passed.
- Independent transformed-density integral: 0.9999999999999999.
- Example affine-map round-trip error: 0.0 kg.
- Exact environment hashes were retained by hard link:
  - ERA5: `73a14bf7e931da9f4f3f034b77ac24b9514fdef727b82eb9e30c67df938489f4`
  - IGRF: `ad71fa679c7933858e8748fa34b124f4e405921b337c92aeb7efeb1002ac6ac1`

## Scientific interpretation

This closes an important implementation ambiguity: uncertain radar fuel is not a second independent fuel prior. It is the path-induced image of the anchor-fuel latent. The endpoint and exhaustion time likewise remain proposal variables. These distinctions are necessary to avoid double conditioning when the two-ended proposal is attached to the aircraft dynamics.

The checkpoint does not show that a two-ended proposal resolves the 18:39/19:41 bottleneck. That requires generating powered paths, applying the exact endpoint/path/fuel-time proposal ratios from checkpoint 13, and comparing seeds and matched budgets against the forward estimator.

## Next work

1. Add the powered-path proposal that produces the radar-to-anchor affine mass map and a full `BroadFlightState` without a zero-likelihood fuel reset hiding a mass mismatch.
2. Connect that state to the checkpoint-13 support-preserving endpoint mixture and exact bridge weight.
3. Run exact synthetic recovery first, including deliberate double-conditioning and 4 Hz failure controls.
4. Only after recovery, run matched-seed physical comparisons for both conditional exhaustion windows and report row ESS, root ESS, support, evidence dispersion, marginal CDF differences, and coverage.
5. Broaden the radar-locus sensitivity beyond the narrow configured airway interpolation before any physical interpretation.

## Reproduction

From `source/`:

```text
export RUSTUP_HOME=/workspace/scratch/c386ceede7a0/.rustup
export CARGO_HOME=/workspace/scratch/c386ceede7a0/.cargo
export PATH="$CARGO_HOME/bin:$PATH"
export CARGO_TARGET_DIR=/tmp/mh370-checkpoint18-target
cargo test -p mh370-end-of-flight -p mh370-estimator
cd ..
python3 validate_bridge_source.py
python3 -m unittest discover -s . -p 'test_*.py' -v
```

Rust 1.98.0 (`88d9e12ae 2026-08-18`) was used.

## Limitations

- No full-aircraft bridge run has been made.
- The affine mass map must come from the proposed powered path; it is not a free fitted parameter.
- Aggregate radar fuel does not by itself identify left/right feed allocation. That allocation must be propagated consistently when constructing the full state.
- The 6.578 N, 96.340 E locus and its 2 NM / 2 degree scales remain a conditional sensitivity, not authenticated radar data.
- No calibrated location probability or solved location is claimed.

