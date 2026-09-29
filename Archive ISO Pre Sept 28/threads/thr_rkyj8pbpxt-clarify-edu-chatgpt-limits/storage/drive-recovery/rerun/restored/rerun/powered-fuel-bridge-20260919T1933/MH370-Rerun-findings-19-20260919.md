# MH370 Rerun checkpoint 19: feed-resolved powered fuel bridge

Created 2026-09-19T19:38:30Z. This checkpoint advances only the core estimator. Hydroacoustics remains excluded.

## Result

The checkpoint-18 aggregate fuel transform has been extended into a feed-resolved powered fuel adapter. The new code composes the affine mass map directly from the actual radar-to-anchor powered segments, reconstructs both radar feed quantities from the canonical 18:28:05.9 anchor latent, and then independently propagates those feeds forward over the same segments.

The propagated state must land on the sampled anchor fuel and feed allocation within 1e-7 kg. A discontinuous clock, invalid feed allocation, non-depleting path, or feed exhaustion before the anchor fails closed.

This removes a potential hidden inconsistency in a future bridge: the historical model's zero-likelihood fuel-anchor reset can no longer conceal a radar-to-anchor mass mismatch.

## Exact construction

For a path-composed gross-mass map `M_anchor = r M_radar + c`, the adapter:

1. samples only the canonical anchor total fuel;
2. inverts the composed path map to obtain aggregate radar fuel;
3. computes total powered burn from radar to anchor;
4. assigns that burn backward to the two radar feeds using the declared engine-flow shares;
5. carries reserve and unusable fuel unchanged under the no-jettison baseline;
6. propagates the resulting radar state forward with the production fuel law; and
7. accepts only if both feed quantities and aggregate anchor fuel are recovered.

The affine map is generated from the powered segments and selected fuel model. It is not an independently fitted parameter. The anchor fuel remains the prior coordinate, so no second Jacobian or radar-fuel prior is introduced.

## Validation

- Full affected Rust suites: 89 end-of-flight tests and 72 estimator tests passed; 161 total, zero failures.
- Nine focused bridge-source tests passed, including equal and unequal feed shares.
- The production declared-broad fuel family with a sampled 1.07 flow scale landed exactly on the anchor.
- Five independent Python tests passed.
- Independent two-segment Martin reference:
  - duration: 353.9 s;
  - retained fraction: 0.9970605439575337;
  - affine offset: -13.818779926529974 kg;
  - example anchor fuel: 33,524.10488196 kg;
  - induced radar fuel: 34,150.858620282146 kg;
  - powered burn: 626.7537383221497 kg;
  - aggregate, feed, and mass-balance errors: 0.0 kg.

Those numeric values are a deterministic validation fixture, not an inferred MH370 fuel estimate.

## Scientific significance

Checkpoint 19 closes the feed-allocation and hidden-reset portion of the physical bridge boundary. It ensures the bridge cannot gain apparent feasibility by starting with an arbitrary radar fuel state and silently replacing it at 18:28:05.9.

It does not yet test whether two-ended guidance resolves the 18:39/19:41 proposal bottleneck. The segments used for the exact controls are supplied powered-fuel operating points, not samples from a full stochastic aircraft trajectory proposal.

## Next work

1. Implement the aircraft-path proposal from the conditional 18:22:12 state through 18:28:05.9 and onward, emitting the exact fuel segments consumed by this adapter.
2. Attach checkpoint 13's endpoint/path/fuel-time proposal ratio without applying SATCOM or fuel evidence twice.
3. Test the combined proposal in exact synthetic recovery under both 00:15–00:17 and 00:15–00:19 conditional supports.
4. Compare multiple seeds and matched budgets with the forward estimator using support rate, row ESS, root ESS, evidence dispersion, marginal CDF differences, and coverage.
5. Only after successful synthetic recovery run physical sensitivity trials, including broader radar-boundary uncertainty.

## Reproduction

From `source/`:

```text
export RUSTUP_HOME=/workspace/scratch/c386ceede7a0/.rustup
export CARGO_HOME=/workspace/scratch/c386ceede7a0/.cargo
export PATH="$CARGO_HOME/bin:$PATH"
export CARGO_TARGET_DIR=/tmp/mh370-checkpoint19-target
cargo test -p mh370-end-of-flight -p mh370-estimator
cd ..
python3 validate_powered_fuel_path.py
python3 -m unittest discover -s . -p 'test_*.py' -v
```

Rust 1.98.0 (`88d9e12ae 2026-08-18`) was used. Exact environment hashes remain:

- ERA5: `73a14bf7e931da9f4f3f034b77ac24b9514fdef727b82eb9e30c67df938489f4`
- IGRF: `ad71fa679c7933858e8748fa34b124f4e405921b337c92aeb7efeb1002ac6ac1`

## Limitations

- No full stochastic aircraft bridge has run.
- No endpoint has been treated as an observation.
- The configured radar locus remains a conditional airway-interpolation hypothesis.
- The fuel tests validate exact accounting, not the posterior adequacy of a path proposal.
- No calibrated location probability or solved location is claimed.

