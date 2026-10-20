# MH370 Rerun checkpoint 9 — retained-parent aircraft-block implementation

Created 2026-09-19T10:44:12Z.

## Outcome

The first aircraft-source implementation of the checkpoint-8 estimator is now
complete in an isolated candidate tree. It is opt-in and targets the existing
BTO-terminated block whose exact ordered contacts are `m1839` at 2286 s and
`m1941` at 5953 s from the broad-reference origin.

The source audit resolves an important boundary point: 18:39 and 19:41 were
already processed as one observation block, so the current cruise filter does
not resample between them. The missing operation was not merely “defer
resampling”; it was to generate multiple complete block paths while preserving
the diverse population entering the block.

The new retained-parent pool therefore gives every finite-mass incoming
particle exactly `K` complete block proposals. Candidate `(i,k)` carries

`W_i / K * p(path | i) / q(path | i) * L_1839 * L_1941`.

The BFO bias is updated by the existing model after the 18:39 likelihood and
before the 19:41 transition and likelihood. All candidates are scored before
fixed-size output selection; the existing exact candidate-target/output-
proposal correction is retained. No ancestor-selection guide, observation,
fuel factor, terminal factor, or hydroacoustic factor was added.

## Why this differs from the archived failed proposals

The retired `transition_candidates_per_block` path first sampled candidate
ancestors from the weighted population. It could therefore discard actual
incoming parents before evaluating the difficult block. The new schedule
iterates over every finite-mass current parent and draws `K` paths from each.
It also does not resample inside the 18:39–19:41 block.

This directly implements checkpoint 8's correction: multiple candidates
augment the fixed parent bank rather than replacing parent diversity.

## Controls

- 16 independent exact-probability and source-contract tests pass.
- The earlier 73-test precompiled particle-filter baseline still passes.
- The exact source contract verifies that the contact IDs match one complete
  block, each likelihood is applied once, the proposal uses `W_i/K`, and
  hydroacoustic/terminal factors remain absent.
- A `K=1` request is canonicalized to the unchanged ordinary filter path, so it
  uses the original RNG domains and algorithm. An empty configuration is also
  omitted when serializing, preserving old resolved-config structure.
- `K=4` is supplied as the first physical candidate configuration; it keeps
  the original 170,000 incoming roots and adds four complete paths per parent.

## Compile and replay gate

This source has not been compiled. The recovered runtime still lacks `rustc`
and `cargo`; the required toolchain is Rust 1.98.0. The new embedded Rust tests
and runner wiring therefore remain source-reviewed rather than executable
evidence.

After restoring Rust 1.98.0:

```bash
cd candidate-20260919T1034/source
mkdir -p inputs/environment
cp ../../recovered-environment/mh370-era5-grid.bin inputs/environment/
cp ../../recovered-environment/mh370-igrf14-grid.bin inputs/environment/
cargo test --offline -p mh370-particle-filter retained_parent
cargo test --offline -p mh370-runner cruise_commands
cargo build --offline --release -p mh370-runner
```

Then run the base and `K=1` configs with the same new executable and seed. The
posterior, particles, checkpoint weights, ancestry, and evidence must match
exactly before any `K=4` result is interpreted. Configuration/provenance names
and elapsed-time metadata are expected to differ.

Only after that gate should the `K=4` physical candidate be run, preserving the
incoming parent count. Its transition-pool audit file must be checked for
configured/generated candidates, candidate row ESS, candidate root ESS,
largest row/root weights, evidence increment, and output-selection correction.
Multiple seeds and a fixed-total-evaluation comparison remain required.

## Files and hashes

- Source patch: `candidate-20260919T1034/retained-parent-aircraft-source.patch`,
  SHA-256 `525d813568f4fe1ef3d35b86fe3f268d1899aba48d96a74536da1213bac31285`.
- K=1 config: SHA-256
  `c84bbc63cb3c731269c15fd7a498ea7a483d48698cc91d8f9999be79a5ade4a4`.
- K=4 config: SHA-256
  `500f7dcc8ce30df4df470f6e8f92c671b36e9fd9890e80277285a34d8b730625`.
- Exact MH370 ERA5: 337,328,648 bytes, SHA-256
  `73a14bf7e931da9f4f3f034b77ac24b9514fdef727b82eb9e30c67df938489f4`.
- Exact MH370 IGRF: 12,497,900 bytes, SHA-256
  `ad71fa679c7933858e8748fa34b124f4e405921b337c92aeb7efeb1002ac6ac1`.

## Scientific boundary

This is an implementation milestone, not validation of a replacement
estimator. No new physical posterior, evidence comparison, coverage result,
probability, or location is claimed. Backward/two-ended full-aircraft bridging
is still pending. Hydroacoustics remains excluded.
